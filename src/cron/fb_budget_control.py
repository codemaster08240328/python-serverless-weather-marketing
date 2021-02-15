import requests
import decimal
import json
import os
from src.shared.util import get_secret, get_all_records_asset, send_email, send_text, get_single_record, get_all_records_hash


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def get_campaign_details(fb_secret, item):
    campaign_details = requests.get('https://graph.facebook.com/v4.0/act_{act}/adsets?campaign_id={campaign_id}&fields=name'
                                    .format(act=fb_secret['account'], campaign_id=item['id_1'])
                                    , params={'access_token': fb_secret['token']}).json()
    return campaign_details


def set_budget(item, spend, secret):
    daily_budget = int(spend)
    print('Updating FB Campaign ID: {c_id} with spend: ${spend}'.format(c_id=item['destination_id'], spend=daily_budget))
    result = requests.post('https://graph.facebook.com/v7.0/{c_id}'.format(c_id=item['destination_id'])
                           , json={'daily_budget': daily_budget * 100, 'access_token': secret['token']}).json()
    print('Campaign Spend Result: ', result)
    content = json.dumps(result, indent=2)
    if result == {'success': True}:
        title = ('Budget of ${spend} Succeeded for {bus} facebook campaign {c_id}'
                 .format(c_id=item['id_1'], bus=item['bus'], spend=daily_budget))
    else:
        title = ('Budget of ${spend} Failed for {bus} facebook campaign {c_id}'
                 .format(c_id=item['id_1'], bus=item['bus'], spend=daily_budget))
        send_text(title)
    send_email(title, content)


def get_spend(item_id):
    try:
        spend = get_single_record(item_id, 'current_spend')['spend']
    except Exception as e:
        spend = None
    return spend


def send_fb_budget(event, context):
    bus_list = get_all_records_hash('master_business')
    for bus_item in bus_list:
        try:
            bus = bus_item['asset']
            print('Running for business: ', bus)
            fb_secret = get_secret('notus-fb-app')
            items = get_all_records_asset(bus + '#' + 'spend_rules')
            for item in items:
                if ((item['destination'] == 'facebook') & (item['status'] == 'on')):
                    print(f'Running Weather campaign id: {item["id"]} for Facebook campaign id: {item["destination_id"]}')
                    spend = get_spend(item['id'])
                    if spend is not None:
                        print('Loading Spend ${spend}'.format(spend=spend))
                        set_budget(item, spend, fb_secret)
                        # campaign_details = get_campaign_details(fb_secret, item)
                    else:
                        message = 'Found {} with no Forecast'.format(item['id'])
                        print(message)
                        send_text(message)
                        send_email(message, message)
        except Exception as e:
            print(e)
            send_text('There was a failure running Facebook updates')
            send_email('There was a failure running Facebook updates for {bus}'.format(bus=bus), 'Fail')


if __name__ == "__main__":
    os.environ["stage"] = "prod"
    send_fb_budget({}, None)
