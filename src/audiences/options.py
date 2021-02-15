import json
from src.audiences.util import get_business, s3_to_memory, add_audiences, add_query_audiences, getCorsHeader
from util.permission_decorator import permission_decorator


@permission_decorator(permission={'action': 'view', 'resource': 'audiences'})
def handler(event, context):
    """
    Returns fields or product json
    """
    token = event['headers']['Authorization']
    bus = get_business(token)
    type = event['queryStringParameters']['type']

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

    if type == 'fields':
        a = json.loads(s3_to_memory(
            'wx-params', 'audience_json/audience_fields.json'))
        a = add_audiences(a, token)
        resp['statusCode'] = 200
    elif type == 'product':
        a = json.loads(s3_to_memory(
            'wx-params', 'product_json/product_tree.json'))
        resp['statusCode'] = 200
    elif type == 'query_fields':
        a = json.loads(s3_to_memory(
            'wx-params', 'audience_json/audience_query_fields.json'))
        a = add_query_audiences(a, token)
        resp['statusCode'] = 200
    elif type == 'output_fields':
        a = {'output_fields': ['EmailAddressHash_SHA256',
                               'EmailAddressHash_MD5', 'ClientCustId', 'CMSCustID']}
        resp['statusCode'] = 200
    else:
        a = {'ERROR': 'type not found'}
        resp['statusCode'] = 404

    resp['body'] = json.dumps(a)

    return resp
