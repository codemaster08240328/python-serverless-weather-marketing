import json
import boto3
from src.audiences.util import get_business, DecimalEncoder, getCorsHeader
from src.forecast.forecast import save_forecast
from src.shared.util import get_single_record, put_single_record, get_all_records_asset, delete_all_records_hash, item_exists, fix_reserved_keywords
from boto3.dynamodb.conditions import Key
from util.permission_decorator import permission_decorator
import os
import datetime
import decimal
import uuid


def create_campaign(d, bus, creation_time, modified_time="-", id=None):
    """
    Creates a single Campaign
    """
    print('Creating Campaign')

    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('assets')
        try:
            d['id_1']
        except Exception as e:
            d['id_1'] = ' '
        try:
            d['id_2']
        except Exception as e:
            d['id_2'] = ' '
        try:
            d['priority']
        except Exception as e:
            d['priority'] = 1

        if len(d['id_1']) == 0:
            d['id_1'] = ' '
        if len(d['id_2']) == 0:
            d['id_2'] = ' '
        if id is None:
            item_id = str(uuid.uuid4().hex)[:20]

        asset = bus + '#' + 'spend_rules'
        new_item = {
            'bus': bus,
            'id': item_id,
            'asset': asset,
            'name': d['name'],
            'status': 'on',
            'id_1': d['id_1'],
            'product': d['product'],
            'inflect': d['inflect'],
            'bid_modifier': d['bid_modifier'],
            'destination': d['destination'],
            'destination_id': d['destination_id'],
            'id_2': d['id_2'],
            'creation_time': creation_time,
            'modified_time': modified_time,
            'min_spend': d['min_spend'],
            'max_spend': d['max_spend'],
            'target_spend': d['target_spend'],
            'geo': d['geo']
        }

        response = table.put_item(
            Item=json.loads(json.dumps(new_item), parse_float=decimal.Decimal)
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Succesful Response')
            # json.dumps(response, indent=4, cls=DecimalEncoder)
            result = item_id
        else:
            print(response)
            print('Campaign Creation Failed')
            raise Exception

    except Exception as e:
        print(e)
        print('Campaign Creation Failed')
        raise Exception

    tomorrow = (datetime.datetime.now() - datetime.timedelta(hours=7) +
                datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    print('Saving forecast for', item_id)
    save_forecast(item_id, asset, tomorrow)

    return result


@permission_decorator(permission={'action': 'view', 'resource': 'campaign'})
def getSingle(event, context):
    """
    Returns all campaigns in one marketing channel
    """
    token = event['headers']['Authorization']
    bus = get_business(token)
    asset = bus + '#' + 'spend_rules'
    try:
        items = get_single_record(event['pathParameters']['id'], asset)
        print('Item Found')
        resp = {
            'statusCode': 200,
            'body': json.dumps(items),
            'headers': getCorsHeader()
        }
    except Exception as e:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Item not found'
        })
    return resp


@permission_decorator(permission={'action': 'view', 'resource': 'campaign'})
def listAll(event, context):
    """
    Returns all campaigns
    """
    token = event['headers']['Authorization']
    bus = get_business(token)
    asset = bus + '#' + 'spend_rules'
    items = get_all_records_asset(asset)
    resp = {
        'statusCode': 200,
        'body': json.dumps(items),
        'headers': getCorsHeader()
    }
    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'campaign'})
def create(event, context):
    """
    Creates a new campaign
    """
    print('Creating New Campaign')
    token = event['headers']['Authorization']
    bus = get_business(token)
    d = json.loads(event['body'])

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    print('Fields Valid')
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        result = create_campaign(d, bus, creation_time=current_time)

        resp['statusCode'] = 201
        resp['body'] = json.dumps({
            'message': result
        })

    except Exception as e:
        print('Error', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Campaign Creation Failed'
        })

    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'campaign'})
def update(event, context):
    """
    Updates a campaign
    """
    print('Updating Campaign')
    token = event['headers']['Authorization']
    bus = get_business(token)
    d = json.loads(event['body'])
    asset = bus + '#' + 'spend_rules'
    ie = item_exists(d['id'], asset)

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    if not ie:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Campaign does not exist'
        })

    else:
        update_item_list = []
        expression_dict = {}
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('assets')
        for a in (['name', 'status', 'id_1', 'product', 'inflect', 'bid_modifier', 'destination', 'destination_id', 'id_2', 'min_spend', 'max_spend', 'target_spend', 'geo']):
            try:
                expression_dict[':{field}_update'.format(field=a)] = d[a]
                update_item_list.append(
                    '{field} = :{field}_update'.format(field=a))
                print(a, ' Found')
            except Exception as e:
                print('error', e)
                print(a, ' Not Found')

        if len(update_item_list) > 0:
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            update_item_list.append('modified_time = :current_time')
            update_item_list, ExpressionAttributeNames = fix_reserved_keywords(
                update_item_list)
            print(update_item_list)
            print(ExpressionAttributeNames)
            expression_dict[':current_time'] = current_time

            if bool(ExpressionAttributeNames):
                response = table.update_item(
                    Key={"id": d['id'], "asset": asset},
                    UpdateExpression="set " + ','.join(update_item_list),
                    ExpressionAttributeValues=expression_dict,
                    ExpressionAttributeNames=ExpressionAttributeNames,
                    ReturnValues="UPDATED_NEW"
                )

            else:
                response = table.update_item(
                    Key={"id": d['id'], "asset": asset},
                    UpdateExpression="set " + ','.join(update_item_list),
                    ExpressionAttributeValues=expression_dict,
                    ReturnValues="UPDATED_NEW"
                )

    tomorrow = (datetime.datetime.now() - datetime.timedelta(hours=7) +
                datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    print('Saving forecast for', d['id'])
    save_forecast(d['id'], asset, tomorrow)

    resp['statusCode'] = 200
    resp['body'] = json.dumps({
        'message': 'Success'
    })

    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'campaign'})
def delete(event, context):
    """
    Deletes a campaign
    """
    print('Deleting Campaign')
    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }
    try:
        response = delete_all_records_hash(event['pathParameters']['id'])
        resp['statusCode'] = 200
        resp['body'] = json.dumps({'message': 'Success'})
    except Exception as e:
        resp['statusCode'] = 400
        resp['body'] = json.dumps({'message': 'Item not Found'})

    return resp
