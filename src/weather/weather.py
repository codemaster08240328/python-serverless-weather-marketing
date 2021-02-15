import boto3
import os
import json
from src.audiences.util import DecimalEncoder, getCorsHeader
from util.permission_decorator import permission_decorator


@permission_decorator(permission={'action': 'view', 'resource': 'weather_charts'})
def formOption(event, context):
    """
    Returns weather options
    """

    weather_variable = event['queryStringParameters']['weather_variable']
    year = event['queryStringParameters']['year']

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('weather-values')

    try:
        response = table.get_item(
            Key={
                'var_name': weather_variable,
                'year_select': int(year)
            }
        )
        item = json.loads(json.dumps(response, indent=4,
                                     cls=DecimalEncoder))['Item']

        resp['statusCode'] = 200
        resp['body'] = json.dumps(item)

    except Exception as e:
        print(e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Item not Found'
        })

    return resp
