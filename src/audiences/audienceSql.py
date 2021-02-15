import json
from src.audiences.util import get_business, create_universe, create_score_order, create_control_size_sql, send_query, DecimalEncoder, getCorsHeader
from util.permission_decorator import permission_decorator
from src.audiences.exception import InvalidQuery
import boto3
import os


def create_full_sql(universe_sql, score_sql, limit_size):
    """

    Combines Universe and ML sql into one statement

    Args:
        universe_sql (string): Universe SQL statement
        score_sql (string): Score SQL statement order by statement
        limit_size (int): total number of customers requested to be returned

    Returns:
        result (string): SQL of Universe and ML limited by size

    """
    # ADD demand to universe sql
    if len(score_sql) > 1:
        order_by_score_sql = " ORDER BY " + score_sql + " ASC "
    else:
        order_by_score_sql = ""
    select_add = f', "demand_table"."all_p365_demand" as demand '
    demand_join = ' JOIN "source"."eddiebauer_prod_demand_features_current" demand_table ON ml_product.customer_id = demand_table.customer_id '
    original_from = 'FROM "ml"."eddiebauer_prod_product_scores" ml_product'
    universe_sql_demand = universe_sql.replace(
        original_from, select_add + original_from + demand_join)

    result = f"""{universe_sql_demand} {order_by_score_sql} LIMIT {limit_size}"""

    return result


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def create(event, context):
    """
    Returns variables needed for Control Size
    """
    token = event['headers']['Authorization']
    bus = get_business(token)

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    if bus != 'eddiebauer':
        resp['statusCode'] = 404
        resp['body'] = json.dumps({
            'ERROR': 'Business Not Found'
        })

        return resp

    print('********Universe Payload***********')
    d = json.loads(event['body'])
    print(d)

    if "mongoDB" not in d['rules']['universe']:
        d['rules']['universe']['mongoDB'] = {}

    if "mongoDB" not in d['rules']['ml']:
        d['rules']['ml']['mongoDB'] = {}

    print('*******Universe SQL*************')

    try:
        universe_sql = create_universe(d['rules']['universe']['mongoDB'])
        print(universe_sql)

        print('*******Score SQL*************')
        score_sql = create_score_order(d['rules']['ml']['mongoDB'])
        print(score_sql)

        if d['fixed_audience']:
            limit = int(d['fixed_audience_size'])
        else:
            limit = 10000000

        print('Limit: ', limit)

        limit_size = int(limit * 1)

        print('***Control SQL***')
        control_sql = create_control_size_sql(
            universe_sql, score_sql, limit_size, d['start_date'], d['end_date'])
        print(control_sql)

        sql_id = send_query(control_sql)

        resp['statusCode'] = 201
        resp['body'] = json.dumps({
            'id': sql_id
        })

    except Exception as e:
        print('**', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': str(e)
        })

    return resp


@permission_decorator(permission={'action': 'view', 'resource': 'audiences'})
def listAll(event, context):
    """
    Returns SQL for Audience Creation for one id
    """
    print('********Rules Payload***********')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')

    token = event['headers']['Authorization']
    bus = get_business(token)
    audience_id = event['pathParameters']['id']

    resp = {
        'statusCode': '',
        'body': '',
        'headers': getCorsHeader()
    }

    try:
        response = table.get_item(
            Key={
                'id': audience_id,
                'asset': bus + '#audience#info'
            }
        )
        d = json.loads(json.dumps(response, indent=4, cls=DecimalEncoder))
        print(json.dumps(d, indent=4, sort_keys=True))
        d = d['Item']

    except Exception as e:
        print(e)

        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': 'Audience Not Found'
        })

        return resp

    if "mongoDB" not in d['rules']['universe']:
        d['rules']['universe']['mongoDB'] = {}
    if "mongoDB" not in d['rules']['ml']:
        d['rules']['ml']['mongoDB'] = {}

    try:
        universe_sql = create_universe(d['rules']['universe']['mongoDB'])
        score_sql = create_score_order(d['rules']['ml']['mongoDB'])

    except InvalidQuery as e:
        print('**', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': str(e)
        })

        return resp

    except Exception as e:
        print('**', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'message': str(e)
        })

        return resp

    if d['fixed_audience']:
        limit = int(d['fixed_audience_size'])
        if d['control']:
            limit = limit + int(d['control_size'])
    else:
        limit = 10000000

    print('Limit: ', limit)
    full_sql = create_full_sql(
        universe_sql, score_sql, limit_size=int(limit * 1.15))

    resp['statusCode'] = 200
    resp['body'] = json.dumps({"sql": full_sql}, indent=4)

    return resp


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def validate(event, context):
    """
    Returns variables needed for Control Size
    """
    print('********Universe Payload***********')
    d = json.loads(event['body'])
    print(d)

    resp = {
        'body': '',
        'statusCode': '',
        'headers': getCorsHeader()
    }

    if "mongoDB" not in d['rules']['universe']:
        d['rules']['universe']['mongoDB'] = {}

    if "mongoDB" not in d['rules']['ml']:
        d['rules']['ml']['mongoDB'] = {}

    try:
        create_universe(d['rules']['universe']['mongoDB'])
        create_score_order(d['rules']['ml']['mongoDB'])

        resp['statusCode'] = 200
        resp['body'] = json.dumps({
            'valid': 'Success'
        })

    except InvalidQuery as e:
        print('**', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'error': str(e)
        })

    except Exception as e:
        print('**', e)
        resp['statusCode'] = 400
        resp['body'] = json.dumps({
            'error': str(e)
        })

    return resp
