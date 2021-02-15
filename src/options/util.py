import boto3
import os
import json
from boto3.dynamodb.conditions import Key, Attr
from src.audiences.util import DecimalEncoder, sort_a_b


def make_variable_weekly(a):
    if a.find('_ly') > -1:
        a = a.replace('_ly', '_p7_ly')
    elif a.find('_mean') > -1:
        a = a.replace('_mean', '_p7_mean')
    else:
        a = a + '_p7'
    return a


def unique(list1):

    # intilize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def get_name_dict():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('weather-selector')
    items = table.get_item(Key=({'name': 'map_variables'}))
    result = {}
    for d in items['Item']['options']:
        result.update(d)
    inverted_dict = dict([[v, k] for k, v in result.items()])
    return inverted_dict


def list_all_audience_versions(bus):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    items = table.query(KeyConditionExpression=Key(
        'id').eq(bus + '#audience#contacts'))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']
    audience_names = []
    audience_values = []
    for item in items:
        if item['ui']:
            audience_names.append(
                item['name'] + ' (version: ' + item['asset'] + ')')
            audience_values.append(item['version_id'])
    i = 0
    audience_values = sort_a_b(audience_names, audience_values)
    audience_names.sort()
    audience_dict = []
    for i in range(len(audience_names)):
        audience_dict.append(
            {"title": audience_names[i], "value": audience_values[i]})
    return audience_dict


def get_recap_dropdowns(bus):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    items = table.query(KeyConditionExpression=Key(
        'id').eq(bus + '#audience#recap_breakouts'))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']
    return items[0]['ui_fields']
