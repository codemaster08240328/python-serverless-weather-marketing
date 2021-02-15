import json
import boto3
from src.audiences.util import getCorsHeader, get_business
from src.audiences.exception import InvalidPayload
from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError


payloadSchema = {
    'type': 'object',
    'properties': {
        'source': {
            'type': 'object',
            'properties': {
                'transport': {
                    'type': 'string',
                    'enum': ['HTTPS', 'HTTP', 'FTP', 'SFTP', 'S3', 'GCS']
                },
                'url': {'type': 'string'},
                'port': {'type': 'integer'},
                'server': {'type': 'string'},
                'username': {'type': 'string'},
                'password': {'type': 'string'},
                'path': {'type': 'string'},
                'aws_access_key_id': {'type': 'string'},
                'aws_secret_access_key': {'type': 'string'},
                'aws_bucket': {'type': 'string'},
                'aws_region': {'type': 'string'}
            },
            'required': ['transport']
        },
        'confirmEmail': {'type': 'string'}
    },
    'required': ['source']
}


def checkKeyExist(obj, keys):
    for key in keys:
        if not key in obj:
            return False

    return True


def create_ecs(env):
    client = boto3.client('ecs')
    client.run_task(
        cluster='stormy',
        taskDefinition='split-order',
        overrides={'containerOverrides': [{
            'name': 'split-order-file',
            "command": ["python3", "run.py"],
            'environment': env
        }]},
        count=1,
        startedBy='Chris',
        launchType='FARGATE',
        networkConfiguration={'awsvpcConfiguration': {
            'subnets': [os.environ['ECS_PRIVATE_SUBNET_1_ID']],
            'securityGroups': ['sg-0beadaea9bd72ff7d'],
            'assignPublicIp': 'DISABLED'
        }},
    )



def importJson(source, token):
    if source['transport'] == 'HTTPS' or source['transport'] == 'HTTP':
        if not checkKeyExist(source, ['url']):
            raise InvalidPayload(
                'You should provide url if the transport is HTTPS or HTTP.')

        bus = {
            'name': 'bus',
            'value': get_business(token)
        }

        transport = {
            'name': 'transport',
            'value': source['transport']
        }

        url = {
            'name': 'url',
            'value': source['url']
        }

        create_ecs([bus, transport, url])

    elif source['transport'] == 'FTP' or source['transport'] == 'SFTP':
        if not checkKeyExist(source, ['port', 'server', 'username', 'password', 'path']):
            if not checkKeyExist(source, ['port', 'server', 'username', 'ssh_key', 'path']):
                raise InvalidPayload(
                    'You should provide port, server, username, authentication and path if the transport is FTP or SFTP.')

        path = {
            'name': 'path',
            'value': source['path']
        }

        username = {
            'name': 'username',
            'value': source['username']
        }

        server = {
            'name': 'server',
            'value': source['server']
        }

        port = {
            'name': 'port',
            'value': source['port']
        }

        bus = {
            'name': 'bus',
            'value': get_business(token)
        }

        transport = {
            'name': 'transport',
            'value': source['transport']
        }

        if 'password' in source:
            password = {
                'name': 'password',
                'value': source['password']
            }

            create_ecs([server, port, path, username, password, bus, transport])

        elif 'ssh_key' in source:
            ssh_key = {
                'name': 'password',
                'value': source['password']
            }

            create_ecs([username, port, path, server, ssh_key, bus, transport])

    elif source['transport'] == 'S3':
        if not checkKeyExist(source, ['aws_access_key_id', 'aws_secret_access_key', 'aws_bucket', 'aws_region', 'path']):
            raise InvalidPayload(
                'You should provide aws_access_key_id, aws_secret_access_key, aws_bucket, aws_region and path if the transport is S3')

        aws_access_key = {
            'name': 'aws_access_key_id',
            'value': source['aws_access_key_id']
        }

        aws_secret_key = {
            'name': 'aws_secret_access_key',
            'value': source['aws_secret_access_key']
        }

        aws_bucket = {
            'name': 'aws_bucket',
            'value': source['aws_bucket']
        }

        path = {
            'name': 'path',
            'value': source['path']
        }

        bus = {
            'name': 'bus',
            'value': get_business(token)
        }

        transport = {
            'name': 'transport',
            'value': 'S3'
        }

        aws_region = {
            'name': 'aws_region',
            'value': source['aws_region']
        }

        create_ecs([aws_access_key, aws_secret_key, aws_bucket, path, bus, transport, aws_region])

    else:
        if not checkKeyExist(source, ['path']):
            raise InvalidPayload(
                'You should provide path if the transport is GCP')

        data = {}

        return data


def create(event, context):
    """
    Import order json file
    """
    print('Importing order json')

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    token = event['headers']['Authorization']

    try:
        d = json.loads(event['body'])
        validate(event=d, schema=payloadSchema)

        print('Payload Schema Validation Success!')

        source = d['source']
        importJson(source, token)

        resp['statusCode'] = 200
        resp['body'] = json.dumps({
            'message': 'Successfully created order'
        })

    except SchemaValidationError as e:
        print('Schema Validation Error', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': str(e)
        })

    except InvalidPayload as e:
        print('Payload is not valid', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': str(e)
        })

    except Exception as e:
        print('Error', str(e))
        resp['statusCode'] = 500
        resp['body'] = json.dumps({
            'message': 'Server Error'
        })

    return resp
