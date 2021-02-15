from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from src.permissions.permissions import get_permissions
import json


def contains(list, filter):
    for x in list:
        if filter(x):
            return True

    return False


@lambda_handler_decorator
def permission_decorator(handler, event, context, permission):
    token = event['headers']['Authorization']
    permissions = get_permissions(token)

    if contains(permissions, lambda x: x['resource'] == permission['resource'] and (x['action'] == permission['action'] or x['action'] == 'manage')):
        return handler(event, context)

    resp = {
        "statusCode": 403,
        "body": json.dumps({
            'message': "User does not have permission for this endpoint."
        })
    }

    return resp
