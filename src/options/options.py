import json
import boto3
from src.audiences.util import get_business, DecimalEncoder, getCorsHeader
from src.options.util import list_all_audience_versions, get_recap_dropdowns, unique, get_name_dict, make_variable_weekly
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
from util.permission_decorator import permission_decorator
import os


def formOptions(event, context):
    """
    Returns weather options
    """
    token = event['headers']['Authorization']
    bus = get_business(token)

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    args = {
        'name': event['queryStringParameters']['name'] if event['queryStringParameters'].get('name') is not None else None,
        'type': event['queryStringParameters']['type'] if event['queryStringParameters'].get('type') is not None else None,
        'id': event['queryStringParameters']['id'] if event['queryStringParameters'].get('id') is not None else None
    }

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    if args.get('id') is not None:
        table = dynamodb.Table('assets')
        asset_id = bus + '#' + args.get('id')
        print(asset_id)
        items = table.query(KeyConditionExpression=Key(
            'id').eq(asset_id))['Items']
        items = json.loads(json.dumps(items, indent=4, cls=DecimalEncoder))
        return_items = []
        for a in items:
            print('Checking', a['id'], a['asset'], 'for display')
            if a['ui']:
                return_items.append(a['ui_value'])
        items = return_items

    type = args.get('type')

    if (type == 'time_periods') or (type == 'weather_variables') or (type == 'weather_direction') or (type == 'map_variables'):
        table = dynamodb.Table('weather-selector')
        items = table.get_item(Key=({'name': type}))
        items = json.loads(json.dumps(
            items, indent=4, cls=DecimalEncoder))['Item']
    elif type == 'weather_thresholds':
        if args.get('name') is not None:
            table = dynamodb.Table('weather-thresholds')
            items = table.get_item(Key=({'name': args.get('name')}))
            items = json.loads(json.dumps(
                items, indent=4, cls=DecimalEncoder))['Item']
        else:
            resp['statusCode'] = 400
            resp['body'] = json.dumps({
                'message': 'Name Invalid'
            })

            return resp

    elif type == 'audience_versions':
        v = list_all_audience_versions(bus)
        f = get_recap_dropdowns(bus)
        items = {'audience_versions': v, 'breakouts': f}

    resp['statusCode'] = 200
    resp['body'] = json.dumps(items)

    return resp


@permission_decorator(permission={'action': 'view', 'resource': 'weather_maps'})
def mapOptions(event, context):
    """
    Returns Map options
    """

    args = {
        'weather_variable': event['queryStringParameters']['weather_variable'] if event['queryStringParameters'].get('weather_variable') is not None else None,
        'aggregation': event['queryStringParameters']['aggregation'] if event['queryStringParameters'].get('aggregation') is not None else None,
        'date': event['queryStringParameters']['date'] if event['queryStringParameters'].get('date') is not None else None
    }

    aggregation = args.get('aggregation')
    weather_variable = args.get('weather_variable')
    date = args.get('date')
    current_date = datetime.strptime(date, '%Y-%m-%d')
    file_name = 'https://site-obs.s3.amazonaws.com/img/maps/{date}_{var}.jpg'
    urls = []
    titles = []
    start_date = datetime.strptime('2015-02-01', '%Y-%m-%d')
    end_date = datetime.now() + timedelta(days=365)

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    if aggregation == 'daily':
        date_format = '%Y-%m-%d'
        title_format = ' for %A %d/%m/%y'
    elif aggregation == 'weekly':
        date_format = '%Y-%m-%d'
        title_format = ' for week ending %m/%d/%y'
    elif aggregation == 'monthly':
        date_format = '%Y-%m'
        title_format = ' %B %Y'
    else:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Aggregation not found'
        })

        return resp

    d = get_name_dict()
    output = {}

    if aggregation == 'weekly':
        weather_variable_week = make_variable_weekly(weather_variable)
        start_date = start_date + timedelta(days=6 - start_date.weekday())
        current_date = current_date + \
            timedelta(days=6 - current_date.weekday())

        while start_date < end_date:
            urls.append(file_name.format(date=start_date.strftime(
                date_format), var=weather_variable_week))
            titles.append(d[weather_variable] +
                          start_date.strftime(title_format))

            if start_date == current_date:
                center_url = file_name.format(date=start_date.strftime(
                    date_format), var=weather_variable_week)
            start_date = start_date + timedelta(days=7)

    else:
        while start_date < end_date:
            urls.append(file_name.format(date=start_date.strftime(
                date_format), var=weather_variable))
            titles.append(d[weather_variable] +
                          start_date.strftime(title_format))

            if start_date == current_date:
                center_url = file_name.format(date=start_date.strftime(
                    date_format), var=weather_variable)  # {}
                # output['center_image']['url'] = file_name.format(date=start_date.strftime(date_format),var=weather_variable )
                # output['center_image']['title'] = d[weather_variable]+start_date.strftime(title_format)
            start_date = start_date + timedelta(days=1)

    urls = unique(urls)
    titles = unique(titles)
    output['images'] = []
    i = 0

    for i in range(len(urls)):
        output['images'].append({"url": urls[i], "title": titles[i]})
        if urls[i] == center_url:
            output['center_index'] = i
        i = i + 1

    resp['statusCode'] = 200
    resp['body'] = json.dumps(output)

    return resp
