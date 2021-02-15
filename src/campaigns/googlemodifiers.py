import json
from src.audiences.util import get_business, getCorsHeader
from src.shared.util import get_all_records_asset, get_single_record
from util.permission_decorator import permission_decorator
import copy


@permission_decorator(permission={'action': 'view', 'resource': 'campaign'})
def get(event, context):
    """
    Returns all campaigns in one marketing channel
    """
    token = event['headers']['Authorization']
    bus = get_business(token)
    asset = f'{bus}#spend_rules'
    spend_rules = get_all_records_asset(asset)
    modifier_list = []
    for spend_rule in spend_rules:
        if spend_rule['status'] == 'on':
            if spend_rule['destination'] == 'google':
                print(spend_rule['id'])
                modifiers = {}
                modifiers['campaign_id'] = spend_rule['destination_id']
                modifiers['spend'] = int(get_single_record(spend_rule['id'], 'current_spend')['spend'])
                modifiers['bid_modifier'] = get_single_record(spend_rule['id'], 'google#bid_modifiers')['bid_modifiers']
                modifier_list.append(copy.copy(modifiers))
    resp = {
        'statusCode': 200,
        'body': json.dumps(modifier_list),
        'headers': getCorsHeader()
    }

    return resp
