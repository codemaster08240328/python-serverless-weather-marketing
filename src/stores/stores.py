from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
from src.audiences.util import getCorsHeader, get_pk
from src.audiences.exception import NotExistException
from src.shared.util import DecimalEncoder
import json
import os
import boto3
import decimal


payloadSchema = {
    'type': 'object',
    'properties': {
        'store_id': {'type': 'string'}
    },
    'required': ['store_id']
}

table_name = 'store'


def put_item(payload):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    response = table.put_item(
        Item=json.loads(json.dumps(payload), parse_float=decimal.Decimal)
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        result = payload['store_id']
    else:
        print(response)
        raise Exception

    return result


def get_item(pk):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    item = {}

    try:
        response = table.get_item(
            Key={
                'store_id': pk
            }
        )

        item = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']

    except Exception as e:
        print('Error-->', e)

        raise NotExistException(
            'Error: Wrong product_id. The product does not exist in database')

    return item


def create(event, context):
    '''
    create a new store
    '''
    print('creating a new store')
    resp = {
        'statusCode': 201,
        'body': '',
        'headers': getCorsHeader()
    }

    token = event['headers']['Authorization']

    try:
        d = json.loads(event['body'])
        validate(event=d, schema=payloadSchema)

        pk = get_pk(token, d['store_id'])
        d['store_id'] = pk

        result = put_item(d)

        resp['body'] = json.dumps({
            'message': result
        })

    except SchemaValidationError as e:
        print('Schema Validation Error', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': str(e)
        })

    except Exception as e:
        print('Error', e)
        resp['statusCode'] = 500
        resp['body'] = json.dumps({
            'message': 'Server Error'
        })

    return resp


def get_single(event, context):
    resp = {
        'statusCode': 200,
        'body': '',
        'headers': getCorsHeader()
    }

    token = event['headers']['Authorization']

    cust_id = get_pk(token, event['pathParameters']['store_id'])

    try:
        item = get_item(cust_id)
        resp['body'] = json.dumps(item)

    except NotExistException as e:
        print('Error--->', str(e))
        resp['statusCode'] = 404
        resp['body'] = json.dumps({
            'message': str(e)
        })

    except Exception as e:
        print('Error', e)
        resp['statusCode'] = 500
        resp['body'] = json.dumps({
            'message': 'Server Error'
        })

    return resp


def put(event, context):
    resp = {
        'statusCode': 200,
        'body': '',
        'headers': getCorsHeader()
    }
    token = event['headers']['Authorization']

    cust_id = get_pk(token, event['pathParameters']['store_id'])

    d = json.loads(event['body'])
    d['store_id'] = cust_id

    try:
        get_item(cust_id)
        response = put_item(d)
        resp['body'] = json.dumps({
            'message': response
        })

    except NotExistException as e:
        print('Error--->', str(e))
        resp['statusCode'] = 404
        resp['body'] = json.dumps({
            'message': str(e)
        })

    except Exception as e:
        print(e)
        resp['statusCode'] = 500
        resp['body'] = json.dumps({
            'message': 'Server Error'
        })

    return resp
