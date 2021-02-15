from jose import jwt
from src.audiences.util import DecimalEncoder, getCorsHeader
import decimal
import os
import boto3
import json

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': True,
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
}


def get_permissions(token):
    if token[:6] == 'Bearer':
        token = token.split()[1]
    email = jwt.get_unverified_claims(token)['email'].lower()
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    item = table.get_item(Key={'id': email, 'asset': 'client'})
    item_js = json.loads(json.dumps(
        item, indent=4, cls=DecimalEncoder))['Item']
    return item_js['permissions']


def getPerm(event, context):
    """
    Returns user permissions
    """
    token = event['headers']['Authorization']
    permissions = get_permissions(token)

    resp = {
        'statusCode': 200,
        'body': json.dumps(permissions),
        'headers': getCorsHeader()
    }

    return resp


def addPerm(event, context):
    d = json.loads(event['body'])
    resource = d['resource']
    action = d['action']
    token = event['headers']['Authorization']

    if token[:6] == 'Bearer':
        token = token.split()[1]

    email = jwt.get_unverified_claims(token)['email']

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    cur_permissions = get_permissions(token)
    cur_permissions.append({
        'action': action,
        'resource': resource
    })

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')

    try:
        table.put_item(Item={'id': email, 'asset': 'client',
                             'bus': 'eddiebauer', 'permissions': cur_permissions})
        resp['statusCode'] = 200
        resp['body'] = json.dumps({
            'message': 'Successfully add'
        })
    except Exception as e:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Bad request'
        })

    return resp
