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
        'product_id': {'type': 'string'},
        'product_name': {'type': 'string'},
        'ticket': {'type': 'number'},
        'upc_code': {'type': 'string'},
        'brand': {'type': 'string'},
        'live': {'type': 'boolean'},
        'tags': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': ['product_id'],
}


def create_product(payload):
    """
    Creates a single Product
    """

    try:
        table_name = 'product'
        result = put_item(payload, table_name)

    except Exception as e:
        print(e)
        print('Product Creation Failed')
        raise Exception

    return result


def put_item(payload, table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    response = table.put_item(
        Item=json.loads(json.dumps(payload), parse_float=decimal.Decimal)
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        result = payload['product_id']
    else:
        print(response)
        raise Exception

    return result


def get_item(pk, table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    item = {}

    try:
        response = table.get_item(
            Key={
                'product_id': pk
            }
        )

        item = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']

    except Exception as e:
        print('Error-->', e)

        raise NotExistException(
            'Error: Wrong product_id. The product does not exist in database')

    return item


def create(event, context):
    """
    Creates a new product
    """
    print('Creating New Product')
    resp = {
        'statusCode': 201,
        'body': '',
        'headers': getCorsHeader()
    }

    token = event['headers']['Authorization']

    try:
        d = json.loads(event['body'])
        validate(event=d, schema=payloadSchema)

        pk = get_pk(token, d['product_id'])
        d['product_id'] = pk

        result = create_product(d)

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
    """
    Getting a product
    """
    print('Getting Single Product with ID.')

    resp = {
        'statusCode': 200,
        'body': '',
        'headers': getCorsHeader()
    }

    token = event['headers']['Authorization']

    product_id = get_pk(token, event['pathParameters']['product_id'])
    table_name = 'product'

    try:
        item = get_item(product_id, table_name)
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

    product_id = get_pk(token, event['pathParameters']['product_id'])
    table_name = 'product'


    d = json.loads(event['body'])
    d['product_id'] = product_id

    try:
        get_item(product_id, table_name)
        response = put_item(d, table_name)
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
