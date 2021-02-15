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
        'order_id': {'type': 'string'},
        'order_date': {'type': 'string'},
        'customer_id': {'type': 'string'},
        'tax': {'type': 'number'},
        'shipping': {'type': 'number'},
        'attributes': {
            'type': 'object',
            'properties': {
                'color': {'type': 'string'},
                'size': {'type': 'string'},
                'currency': {'type': 'string'}
            }
        },
        'shipping_address': {
            'type': 'object',
            'properties': {
                'address': {'type': 'string'},
                'city': {'type': 'string'},
                'state': {'type': 'string'},
                'postal_code': {'type': 'string'},
                'country': {'type': 'string'}
            }
        },
        'billing_address': {
            'type': 'object',
            'properties': {
                'address': {'type': 'string'},
                'city': {'type': 'string'},
                'state': {'type': 'string'},
                'postal_code': {'type': 'string'},
                'country': {'type': 'string'}
            }
        },
        'items': {
            'type': 'array',
            'items': [
                {"$ref": "#/definitions/Item"}
            ]
        }
    },
    'required': [
        'order_id', 'order_date', 'customer_id'
    ],
    'definitions': {
        'Item': {
            'type': 'object',
            'properties': {
                "product_id": {'type': "string"},
                "sku": {'type': "string"},
                "description": {'type': "string"},
                "quantity": {'type': 'integer'},
                "item_price": {'type': 'number'},
                "tags": {'type': 'array', 'items': {'type': 'string'}},
                "attributes": {
                    'type': 'object',
                    'properties': {
                        "brands": {'type': 'array', 'items': {'type': 'string'}},
                        "return_date": {'type': 'string'}
                    }
                }
            },
            'required': [
                'product_id', 'sku'
            ]
        }
    }
}


def create_order(payload):
    """
    Creates a single Order
    """

    newOrder = {}
    for key in payload.keys():
        if key == 'order_id':
            newOrder['pk'] = payload[key]
        else:
            newOrder[key] = payload[key]

    try:
        table_name = 'order'
        result = put_order(newOrder, table_name)

    except Exception as e:
        print(e)
        print('Order Creation Failed')
        raise Exception

    # payload_ = {}

    # for key in payload.keys():
    #     if key == 'customer_id':
    #         pk = payload[key]
    #     else:
    #         newOrder[key] = payload[key]

    # exist_orders = get_exist_customer(pk)
    # exist_orders.append(newOrder)

    # payload_['pk'] = pk
    # payload_['orders'] = exist_orders

    # try:
    #     table_name = 'customer'
    #     result = put_order(payload_, table_name)

    # except Exception as e:
    #     print(e)
    #     print('Campaign Creation Failed')
    #     raise Exception

    return result


def put_order(payload, table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)

    response = table.put_item(
        Item=json.loads(json.dumps(payload), parse_float=decimal.Decimal)
    )

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        result = payload['pk']
    else:
        print(response)
        raise Exception

    return result


def get_exist_item(id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table("orders")
    item = {}

    try:
        response = table.get_item(
            Key={
                'pk': id
            }
        )

        item = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']

    except Exception as e:
        print('Error-->', e)
        raise NotExistException(
            'Error: Wrong order_id. The order does not exist in database')

    return item


def restructureOrder(order, payload):
    for key in payload:
        print(key)
        if key == 'product_id':
            items = restructureItems(
                order['items'], getProductPayload(payload))

            print(items)
            order['items'] = items

        elif 'product_' in key:
            pass
        else:
            order[key] = payload[key]

    return order


def restructureItems(items, payload):
    new_item = {}
    exist_items = [x for x in items if x['product_id']
                   == payload['id']]
    resp_items = [x for x in items if x['product_id'] != payload['id']]

    if len(exist_items) > 0:
        for key in payload:
            exist_items[0][key] = payload[key]
        resp_items.append(exist_items[0])

    elif not 'sku' in payload:
        raise SchemaValidationError(
            'Error: the product_id not exist in the order. If you want to add a new product, please provide product_sku as well.')

    else:
        for key in payload:
            new_item[key] = payload[key]

        resp_items.append(new_item)

    return resp_items


def getProductPayload(payload):
    product_payload = {}

    for key in payload:
        if 'product_' in key:
            product_payload[key.replace('product_', '')] = payload[key]

    return product_payload


def get_exist_customer(id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('customer')
    item = {}

    result = []

    try:
        response = table.get_item(
            Key={
                'pk': id
            }
        )

        item = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']
        result = item['orders']

    except Exception as e:
        print('Error-->', e)

    finally:
        return result


def create(event, context):
    """
    Creates a new order
    """
    print('Creating New Order')
    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    token = event['headers']['Authorization']

    try:
        d = json.loads(event['body'])
        validate(event=d, schema=payloadSchema)

        pk = get_pk(token, d['order_id'])
        d['order_id'] = pk

        result = create_order(d)

        resp['statusCode'] = 201
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


def patch(event, context):
    '''
    Route: /order/{order_id}
    Method: PATCH
    Description:
        1. User can update anything in order except order id and product_id.
        2. Any key which not included in the body, will be ignored.
        3. Any key/value which not existed in the order/product will be added.
        4. If user wants to update product level key/value, he/she should provide product id.
        5. If user wants to update product level key/value, he/she must add a prefix 'product_' to key like: 'product_sku'.
    '''
    token = event['headers']['Authorization']
    order_id = get_pk(token, event['pathParameters']['order_id'])

    resp = {
        'statusCode': 200,
        'body': '',
        'headers': getCorsHeader()
    }

    try:
        existing_order = get_exist_item(order_id)
        params = json.loads(event['body'])

        new_order = restructureOrder(existing_order, params)
        table_name = 'order'

        order_id = put_order(new_order, table_name)

        resp['body'] = json.dumps({
            'message': 'successfully updated',
            'order': order_id
        })

    except NotExistException as e:
        print('Error--->', str(e))
        resp['statusCode'] = 404
        resp['body'] = json.dumps({
            'message': str(e)
        })

    except SchemaValidationError as e:
        print('Error--->', str(e))
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': str(e)
        })

    except Exception as e:
        print('Error--->', str(e))
        resp['statusCode'] = 500
        resp['body'] = json.dumps({
            'message': 'Server Error'
        })

    finally:
        return resp
