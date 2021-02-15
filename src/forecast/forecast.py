import json
import boto3
from src.audiences.util import get_business, getCorsHeader, DecimalEncoder
from src.shared.util import get_single_record, put_single_record
from util.permission_decorator import permission_decorator
import os


def get_data(ml_key, geo):
    ### connect dynamodb using boto3 ###
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    stage = os.environ['stage']
    table = dynamodb.Table('assets')

    ### get data from db ###
    item = table.get_item(
        Key={'id': f'eddiebauer#wi#10_day#{geo}', 'asset': ml_key})
    item_js = json.loads(json.dumps(
        item, indent=4, cls=DecimalEncoder))['Item']

    print(item_js)
    return item_js


# @permission_decorator(permission={'action': 'view', 'resource': 'campaign'})
def list_forecast(event, context):
    """
    Returns forecast of records
    """
    print('Running Forecast')

    d = json.loads(event['body'])

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    result = {
        'forecast': {
            'forecast_date': [],
            'unlimited_spend': [],
            'capped_spend': []
        },
        'next_7_day_spend': 0,
    }

    min_spend = d['min_spend']
    max_spend = d['max_spend']
    target_spend = d['target_spend']
    ml_key = d['product']
    inflect = d['inflect']
    geo = d['geo']

    try:
        db_res = get_data(ml_key, geo)

        db_res['results'].sort(key=lambda x: x['local_date'])
        ind = 0

        for item in db_res['results']:
            result['forecast']['forecast_date'].append(item['local_date'])

            unlimited_spend = target_spend * \
                (1 + (inflect * (item['lift'] - 1)))
            result['forecast']['unlimited_spend'].append(
                max(unlimited_spend, 0))

            if unlimited_spend < min_spend:
                capped_spend = min_spend
            elif unlimited_spend > max_spend:
                capped_spend = max_spend
            else:
                capped_spend = unlimited_spend

            result['forecast']['capped_spend'].append(max(capped_spend, 0))

            if ind < 7:
                result['next_7_day_spend'] += max(capped_spend, 0)
                ind += 1

        print(result)

        resp['statusCode'] = 200
        resp['body'] = json.dumps(result)

    except Exception as e:
        print(e)
        resp['statusCode'] = 404
        resp['body'] = json.dumps({
            'message': 'Can not find any matched item to provided production'
        })

    return resp


def save_forecast(item_id, asset, fx_date):
    forecast_record = get_single_record(item_id, asset)
    print(forecast_record)
    response = list_forecast({'body': json.dumps(forecast_record)}, {})
    forecast = json.loads(response['body'])
    spend = forecast['forecast']['capped_spend'][0]  # should change to fx_date
    item = {'id': item_id, 'asset': 'current_spend', 'spend': spend}
    response = put_single_record(item)
    print(response)
    return
