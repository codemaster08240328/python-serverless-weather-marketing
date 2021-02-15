from src.audiences.util import get_business, DecimalEncoder, validate_sql, get_current_status, modify_status, create_blank_record, getCorsHeader
from util.permission_decorator import permission_decorator
from boto3.dynamodb.conditions import Key
import datetime
import boto3
import json
import os
import decimal
import uuid
import paramiko
from io import StringIO


def validate_form(d):
    result = {'Success': 'Success'}
    if d['fixed_audience']:
        try:
            if ((d['fixed_audience_size'] == 0) | (d['fixed_audience_size'] is None)):
                result = {
                    'error': 'Fixed Audience size is True but audience size is 0'}
        except Exception as e:
            result = {
                'error': 'Fixed Audience size is True but audience size is invalid'}
    if d['control']:
        try:
            if ((d['control_size'] == 0) | (d['control_size'] is None)):
                result = {'error': 'Control is requested but control size is 0'}
        except Exception as e:
            result = {'error': 'Control is requested but control size is invalid'}
    return result


def create_audience(d, bus, creation_time, modified_time="-", id=None):
    """
    Creates a single Audience
    """
    print('Creating Audience Definition')
    d['bus'] = bus
    create = d['create_version']
    d['creation_type'] = 'static'
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    found, status, status_text, actual_audience_size = get_current_status(d)
    status, status_text = modify_status(found, status, status_text, d)
    d['actual_audience_size'] = actual_audience_size

    if not found:
        d['id'] = str(uuid.uuid4().hex)[:20]

    d['creation_time'] = creation_time
    d['modified_time'] = modified_time
    d['status_text'] = status_text
    d['status'] = status
    d['asset'] = bus + '#audience#info'

    if not d['control']:
        print('Zeroing out Control as Control is False')
        d['control_size'] = 'None'
        d['actual_control_size'] = 'None'
    elif create:
        # If running to S3, wait for audience creation to update size
        d['actual_audience_size'] = 'Running...'
        # If running to S3, wait for audience creation to update size
        d['actual_control_size'] = 'Running...'
    else:
        d['actual_control_size'] = d['control_size']

    response = table.put_item(
        Item=json.loads(json.dumps(d), parse_float=decimal.Decimal)
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Succesful Response')
        # json.dumps(response, indent=4, cls=DecimalEncoder)
        result = 'Success'
    else:
        print(response)
        print('Audience Definition Creation Failed')

        raise BaseException('Audience Definition Creation Failed')

    print('Saving audience for', d['id'])

    if create:
        print('Create is True, Running audience creation via ECS')
        create_ecs(d['id'], bus)

    return result, d['id']


def create_ecs(audience_id, bus):
    client = boto3.client('ecs')
    client.run_task(
        cluster='stormy',
        taskDefinition='audience-create:1',
        overrides={'containerOverrides': [{
            'name': 'audience_create',
            "command": ["/opt/conda/envs/audience_env/bin/python3.6", "/audience_create/create/create.py"],
            'environment': [
                {
                    'name': 'audience_id',
                    'value': audience_id
                },
                {
                    'name': 'creation_type',
                    'value': 'user'
                },
                {
                    'name': 'bus',
                    'value': bus
                },
                {
                    'name': 'stage',
                    'value': os.environ['stage']
                }
            ]}]},
        count=1,
        startedBy='Chris',
        launchType='FARGATE',
        networkConfiguration={'awsvpcConfiguration': {
            'subnets': ['subnet-033a355b7fbc902c3'],
            'securityGroups': ['sg-0beadaea9bd72ff7d'],
            'assignPublicIp': 'DISABLED'
        }},
    )


def get_ssh_key(secret_name):

    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    return get_secret_value_response['SecretString']
    # Your code goes here.


def run_ssh_command(host, key, command):

    ssh_key = key
    k = paramiko.RSAKey.from_private_key(StringIO(ssh_key))
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host = host
    print("Connecting to", host)
    c.connect(hostname=host, username="ubuntu", pkey=k)
    print("Connected to ", host)
    c.exec_command(command)
    return


@permission_decorator(permission={'action': 'view', 'resource': 'audiences'})
def getSingle(event, context):
    """
    Returns one audiences
    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    token = event['headers']['Authorization']
    bus = get_business(token)
    id = event['pathParameters']['id']

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    stage = os.environ['stage']
    table = dynamodb.Table('assets')

    try:
        response = table.get_item(
            Key={
                'id': id, 'asset': bus + '#audience#info'
            }
        )
        item = json.loads(json.dumps(response, indent=4,
                                     cls=DecimalEncoder))['Item']
        resp['statusCode'] = 200
        resp['body'] = json.dumps(item)

    except Exception as e:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Item not Found'
        })

    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def create(event, context):
    """
    Creates a new audience
    """
    print('Creating New Audience')
    token = event['headers']['Authorization']
    bus = get_business(token)

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }
    d = json.loads(event['body'])
    print('Fields Valid')

    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    valid_form = validate_form(d)

    if list(valid_form.keys())[0] == 'error':
        print('Found Invalid Form ', valid_form)

        resp['statusCode'] = 400
        resp['body'] = json.dumps(valid_form)

        return resp

    validation = validate_sql(token, d)

    if list(validation.keys())[0] == 'error':
        print('Found Invalid SQL ', validation)

        resp['statusCode'] = 400
        resp['body'] = json.dumps(validation)

        return resp

    try:
        result, audience_id = create_audience(
            d, bus, creation_time=current_time)

        resp['statusCode'] = 201
        resp['body'] = json.dumps({
            'id': audience_id
        })

    except BaseException as e:
        print(e)
        print('Audience Definition Creation Failed')
        resp['status_code'] = 400
        resp['body'] = json.dumps({
            'message': 'Creation failed'
        })

    return resp


@permission_decorator(permission={'action': 'view', 'resource': 'audiences'})
def listAll(event, context):
    """
    Returns all audiences
    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    token = event['headers']['Authorization']
    bus = get_business(token)

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    table = dynamodb.Table('assets')
    items = table.query(IndexName="assetIndex", KeyConditionExpression=Key(
        'asset').eq(bus + '#audience#info'))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']

    resp['statusCode'] = 200
    resp['body'] = json.dumps(items)

    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def delete(event, context):
    """
    Deletes a audience
    """
    print('Deleting Audience')
    d = json.loads(event['body'])

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('assets')
        items = table.query(KeyConditionExpression=Key(
            'id').eq(d['id']))['Items']

        for a in items:
            print('Deleting', a['id'], a['asset'])
            response = table.delete_item(
                Key={"id": a['id'], "asset": a['asset']})
            print(response)

        resp['statusCode'] = 200
        resp['body'] = json.dumps({
            'message': 'Success'
        })

    except Exception as e:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Audience does not exist'
        })

    return resp


@permission_decorator(permission={'action': 'view', 'resource': 'audiences'})
def getVersion(event, context):
    """
    Returns customer versions
    """
    token = event['headers']['Authorization']
    bus = get_business(token)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    id = event['pathParameters']['id']

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    try:
        try:
            items = table.query(KeyConditionExpression=Key('id').eq(
                id) & Key('asset').begins_with(bus + '#audience#contacts#'))
            print(items)
            items = items['Items']
            output = []
            for a in items:
                output.append(a['version'])
        except Exception as e:
            output = []

        resp['statusCode'] = 200
        resp['body'] = json.dumps(output)

    except Exception as e:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Item not Found'
        })

    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def createMeasure(event, context):
    """
    Endpoint to Measure Audience Results
    """
    print('Sending Measurement request to EC2')
    print('Fields Valid')

    d = json.loads(event['body'])

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    d['id'] = str(uuid.uuid4())
    response = create_blank_record(d)
    key = get_ssh_key('ec2-recap')
    run_ssh_command('10.0.1.250', key,
                    f"nohup /home/ubuntu/miniconda3/envs/measure/bin/python3.6 /home/ubuntu/wx-api/process/measure/measure.py  {d['id']} {os.environ['stage']} &")

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Succesful Response')
        # json.dumps(response, indent=4, cls=DecimalEncoder)
        resp['statusCode'] = 200
        resp['body'] = json.dumps({
            'id': d['id']
        })

    else:
        print(response)
        print('Measurement Creation Failed')
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Measurement Creation Failed'
        })

    return resp
