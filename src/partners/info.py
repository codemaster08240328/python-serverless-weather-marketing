import boto3
from src.audiences.util import DecimalEncoder, get_business, getCorsHeader
from boto3.dynamodb.conditions import Key, Attr
import json
import os


def facebook_list(bus):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('fb-detail')
    items = table.query(KeyConditionExpression=Key('bus').eq(bus))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']
    status = [x['effective_status'] for x in items]
    active_indices = [i for i, x in enumerate(status) if x == "ACTIVE"]
    paused_indices = [i for i, x in enumerate(status) if x == "PAUSED"]
    sorted_indices = active_indices + paused_indices
    sorted_result = [items[i] for i in sorted_indices]

    return sorted_result


def tradedesk_list(bus):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('tradedesk-detail')
    items = table.query(KeyConditionExpression=Key('bus').eq(bus))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']

    return items


def sitespect_list(bus):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('sitespect-detail')
    items = table.query(KeyConditionExpression=Key('bus').eq(bus))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']

    return items


def listAll(event, context):
    """
    Returns weather options
    """

    type = event['queryStringParameters']['type']
    token = event['headers']['Authorization']
    bus = get_business(token)
    resp = {
        'statusCode': '',
        'body': '',
        'headers', getCorsHeader()
    }

    if (type == 'facebook'):
        result = facebook_list(bus)

        resp['statusCode'] = 200
        resp['body'] = json.dumps(result)

    elif (type == 'tradedesk'):
        result = tradedesk_list(bus)

        resp['statusCode'] = 200
        resp['body'] = json.dumps(result)

    elif (type == 'sitespect'):
        result = sitespect_list(bus)
        resp['statusCode'] = 200
        resp['body'] = json.dumps(result)
    else:
        items = None
        resp['statusCode'] = 200
        resp['body'] = json.dumps(items)

    return resp
