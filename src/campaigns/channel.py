import json
from src.audiences.util import get_business, DecimalEncoder, getCorsHeader
from boto3.dynamodb.conditions import Key, Attr
from util.permission_decorator import permission_decorator
import boto3
import os


@permission_decorator(permission={'action': 'view', 'resource': 'campaign'})
def get(event, context):
    """
    Returns all campaigns in one marketing channel
    """
    token = event['headers']['Authorization']
    bus = get_business(token)

    channel = event['pathParameters']['channel']
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('campaigns')
    items = table.query(FilterExpression=Attr("channel").eq(channel),
                        KeyConditionExpression=Key('bus').eq(bus))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']

    resp = {
        'statusCode': 200,
        'body': json.dumps(items),
        'headers': getCorsHeader()
    }

    return resp
