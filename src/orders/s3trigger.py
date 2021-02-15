import json
from src.audiences.util import s3_to_memory
from src.orders.orders import create_order


def handler(event, context):
    print(event)
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']

    listJson = s3_to_memory(s3_bucket, s3_key).splitlines()

    for item in listJson:
        try:
            create_order(json.loads(item))
            print('Order Creation Success.')
        except Exception as e:
            print('<-- Order Creation Error -->')
            print(str(e))
