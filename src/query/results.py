import boto3
import os
import json
from src.audiences.util import DecimalEncoder, getCorsHeader


def queryRes(event, context):
    """
    Returns query result
    """
    sql_id = event['queryStringParameters']['id']

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('var')
    try:
        response = table.get_item(
            Key={
                'id': sql_id
            }
        )
        print(response)
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
