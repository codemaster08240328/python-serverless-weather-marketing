import json
from src.audiences.util import get_business, create_universe, create_universe_count, send_query, getCorsHeader
from src.audiences.exception import InvalidQuery
from util.permission_decorator import permission_decorator
# TODO: Check API integration in frontend.


@permission_decorator(permission={'action': 'manage', 'resource': 'audiences'})
def handler(event, context):
    """
    Returns Universe Estimate
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
    print(d['rules']['universe'])

    try:
        if "mongoDB" not in d['rules']['universe']:
            d['rules']['universe']['mongoDB'] = {}
        universe_sql = create_universe(d['rules']['universe']['mongoDB'])
        universe_count_sql = create_universe_count(universe_sql)
        sql_id = send_query(universe_count_sql)

        resp['statusCode'] = 200
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
