from src.shared.util import get_secret, put_single_record, send_email, send_text, get_all_records_hash
import requests
import datetime
import os
import time


def send_campaigns_to_dynamodb(d, bus):
        """
        Sends all FB campaigns to dynamodb
        """
        print('Sending Campaigns to DynamoDB')
        item = {}
        item['modified_time'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        item['id'] = f'{bus}#weather_marketing_partner#facebook'
        item['asset'] = 'ui'
        item['ui'] = True
        ui_list = []
        for a in d:
            value = a['id']
            title = a['name'].replace('/', '-')
            if len(title) > 80:
                title = title[:80] + '...'
            ui_list.append({'title': title, 'value': value})
        item['ui_value'] = ui_list
        put_single_record(item)
        print('Campaigns Sent')
        return 'Success'


def get_campaigns_from_fb(bus):
    """
    Pulls all FB campaigns for business
    """
    d = []
    notus_fb_token = get_secret('notus-fb-app')['token']
    bus_fb_account = get_secret(bus + '-fb-account')['account']
    c_fields = 'name,objective,start_time,effective_status,stop_time,users'
    fb_data = requests.get(f'https://graph.facebook.com/v7.0/act_{bus_fb_account}/campaigns?fields={c_fields}'
                           , params={'access_token': notus_fb_token}).json()
    print(fb_data)
    d.extend(fb_data['data'])
    i = 0
    while 1 == 1:
        print('Running Pull #%s for %s' % (i, bus))
        try:
            fb_data = requests.get(fb_data['paging']['next']
                                   , params={'access_token': notus_fb_token}).json()
            d.extend(fb_data['data'])
        except Exception as e:
            print(e)
            break
        if i > 10:
            break
            print('Over 250 campaigns pulled, Stopping')
        time.sleep(1)
        i = i + 1
    notus_campaigns = []
    for a in d:
        if a['name'].lower().find('notus') > -1:
            notus_campaigns.append(a)
    return notus_campaigns


def insert_fb_campaigns(event, context):
    bus_list = get_all_records_hash('master_business')
    for bus_item in bus_list:
        bus = bus_item['asset']
        d = get_campaigns_from_fb(bus)
        send_campaigns_to_dynamodb(d, bus)


if __name__ == "__main__":
    os.environ['stage'] = 'dev'
    insert_fb_campaigns({}, None)
