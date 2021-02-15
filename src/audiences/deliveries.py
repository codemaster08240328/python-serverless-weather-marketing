import json
from src.audiences.util import get_business, DecimalEncoder, getCorsHeader
from util.permission_decorator import permission_decorator
from boto3.dynamodb.conditions import Key

from jose import jwt
import datetime
import os
import boto3
import decimal


def create_delivery(d, bus, email):
    """
    Creates a new Delivery
    """
    entry_json = {}
    entry_json['creation_time'] = datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    entry_json['id'] = d['id']
    entry_json['user'] = email
    entry_json['asset'] = bus + '#audience#delivery#' + d['destination']
    entry_json['schedule'] = d['schedule']
    entry_json['schedule_string'] = d['schedule_string']
    entry_json['destination'] = d['destination']
    entry_json['version'] = d['version']
    entry_json['initial_delivery'] = d['initial_delivery']

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    response = table.put_item(
        Item=json.loads(json.dumps(entry_json), parse_float=decimal.Decimal)
    )

    if d['schedule'] == 'Immediate':
        print('Immediate Delivery Found, Running ECS Task')
        deliver_ecs(d['id'], bus, d['destination'], d['version'], 'user')
    elif d['initial_delivery']:
        print('Initial Delivery Found, Running Create then delivery')
        deliver_ecs(d['id'], bus, d['destination'], d['version'], 'scheduled')
    return response


def deliver_ecs(audience_id, bus, destination, version, creation_type):
    client = boto3.client('ecs')
    client.run_task(
        cluster='stormy',
        taskDefinition='audience-create:1',
        overrides={'containerOverrides': [{
            'name': 'audience_create',
            "command": ["/opt/conda/envs/audience_env/bin/python3.6", "/audience_create/deliver/send.py"],
            'environment': [
                {
                    'name': 'audience_id',
                    'value': audience_id
                },
                {
                    'name': 'version',
                    'value': version
                },
                {
                    'name': 'bus',
                    'value': bus
                },
                {
                    'name': 'destination',
                    'value': destination
                },
                {
                    'name': 'stage',
                    'value': os.environ['stage']
                },
                {
                    'name': 'creation_type',
                    'value': creation_type
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


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def create(event, context):
    """
    Endpoint to publish Delivery
    """
    print('Creating New Delivery')
    token = event['headers']['Authorization']
    bus = get_business(token)

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    if token[:6] == 'Bearer':
        token = token.split()[1]

    email = jwt.get_unverified_claims(token)['email']
    d = json.loads(event['body'])
    print('Fields Valid')

    response = create_delivery(d, bus, email)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Succesful Response')
        # json.dumps(response, indent=4, cls=DecimalEncoder)
        resp['statusCode'] = 201
        resp['body'] = json.dumps({
            'message': 'Success'
        })
    else:
        print(response)
        print('Delivery Creation Failed')
        # abort(400, 'Delivery Creation Failed')
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Delivery creation failed'
        })

    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def delete(event, context):
    """
    Deletes a delivery
    """
    print('Deleting Delivery')
    d = json.loads(event['body'])

    token = event['headers']['Authorization']
    bus = get_business(token)
    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        stage = os.environ['stage']
        table = dynamodb.Table('assets')

        asset = bus + '#audience#delivery#' + d['destination']
        response = table.delete_item(Key={"id": d['id'], "asset": asset})
        print(response)
        resp['statusCode'] = 200
        resp['body'] = json.dumps({
            'message': 'Success'
        })

    except Exception as e:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Audience Delivery does not exist'
        })

    return resp


@permission_decorator(permission={'action': 'view', 'resource': 'audiences'})
def listAll(event, context):
    """
    Endpoint to Pull all deliveries for given audience
    """
    print('Pulling all Deliveries')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    stage = os.environ['stage']
    table = dynamodb.Table('assets')

    token = event['headers']['Authorization']
    bus = get_business(token)
    id = event['pathParameters']['id']

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    try:
        items = table.query(KeyConditionExpression=Key('id').eq(
            id) & Key('asset').begins_with(bus + '#audience#delivery'))
        print(items)
        items = items['Items']
        output = []
        for a in items:
            output.append({'schedule_string': a['schedule_string'],
                           'schedule': a['schedule'],
                           'destination': a['destination'],
                           'id': a['id']})

        resp['statusCode'] = 200
    except Exception as e:
        output = []
        resp['statusCode'] = 500

    output = json.loads(json.dumps(output, indent=4, cls=DecimalEncoder))
    resp['body'] = json.dumps(output)

    return resp
