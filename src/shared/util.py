import json
import decimal
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import json
import time
import io


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def get_single_record(item_id, asset):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    response = table.get_item(
        Key={
            'id': item_id, 'asset': asset
        }
    )
    item = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']
    return item


def get_all_records_hash(item_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    items = table.query(KeyConditionExpression=Key('id').eq(item_id))
    items = json.loads(json.dumps(items, cls=DecimalEncoder))['Items']
    return items


def get_all_records_asset(asset):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    items = table.query(IndexName="assetIndex", KeyConditionExpression=Key(
        'asset').eq(asset))
    items = json.loads(json.dumps(items, cls=DecimalEncoder))['Items']
    return items


def delete_single_record(item_id, asset):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    response = table.delete_item(
        Key={"id": item_id, "asset": asset})
    return response


def delete_all_records_hash(item_id):
    items = get_all_records_hash(item_id)
    for item in items:
        delete_single_record(item['id'], item['asset'])
    return


def put_single_record(item):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    response = table.put_item(
        Item=json.loads(json.dumps(item), parse_float=decimal.Decimal)
    )
    return response


def get_all_records_scan(col, value):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    response = table.scan(FilterExpression=Attr(col).eq(value))
    items = json.loads(json.dumps(response, cls=DecimalEncoder))['Items']
    return items


def item_exists(item_id, asset):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    try:
        response = table.get_item(
            Key={
                'id': item_id, 'asset': asset
            }
        )
        item = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']
        result = True
    except Exception as e:
        result = False
    return result


def fix_reserved_keywords(update_item_list):
    ExpressionAttributeNames = {}
    res = ['name', 'status', 'rules', 'type']
    for i in range(len(update_item_list)):
        for a in res:
            if update_item_list[i].find('{} = '.format(a)) > -1:
                ExpressionAttributeNames['#{}'.format(a[:3])] = a
                update_item_list[i] = update_item_list[i].replace(
                    '{} = '.format(a), '#{} = '.format(a[:3]))

    return update_item_list, ExpressionAttributeNames


def get_secret(secret_name):

    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(get_secret_value_response['SecretString'])

    return secret


def send_email(title, content):
    ses = boto3.client('ses')
    response = ses.send_templated_email(
        Source='chris@notus.ai',
        Destination={'ToAddresses': ['chris@notus.ai']},
        ReplyToAddresses=['chris@notus.ai'],
        Template='blank',
        TemplateData=json.dumps({'body': content, 'subject': title})
    )
    print(response)


def send_text(message):
    client = boto3.client("sns", region_name="us-east-1")
    client.publish(PhoneNumber="+17163613802", Message=message)
    print('Text Sent')


class QueryAthena:
    def __init__(self, query, database):
        self.database = database
        self.folder = 'forecast_results/'
        self.bucket = 'aws-athena-query-results-453299555282-us-east-1'
        self.s3_output = 's3://' + self.bucket + '/' + self.folder
        self.region_name = 'us-east-1'
        self.query = query

    def load_conf(self, q):
        try:
            self.client = boto3.client('athena', region_name=self.region_name)
            response = self.client.start_query_execution(
                QueryString=q,
                QueryExecutionContext={
                    'Database': self.database
                },
                ResultConfiguration={
                    'OutputLocation': self.s3_output,
                }
            )
            self.filename = response['QueryExecutionId']
            print('Execution ID: ' + response['QueryExecutionId'])

        except Exception as e:
            print(e)
        return response

    def run_query(self):
        queries = [self.query]
        for q in queries:
            res = self.load_conf(q)
        try:
            query_status = None
            while query_status == 'QUEUED' or query_status == 'RUNNING' or query_status is None:
                query_status = self.client.get_query_execution(
                    QueryExecutionId=res["QueryExecutionId"])['QueryExecution']['Status']['State']
                print(query_status)
                if query_status == 'FAILED' or query_status == 'CANCELLED':
                    raise Exception(
                        'Athena query with the string "{}" failed or was cancelled'.format(self.query))
                time.sleep(1)
            print('Query "{}" finished.'.format(self.query))

            df = self.obtain_data()
            return df

        except Exception as e:
            print(e)

    def obtain_data(self):
        try:
            self.resource = boto3.resource('s3', region_name=self.region_name)

            response = self.resource \
                .Bucket(self.bucket) \
                .Object(key=self.folder + self.filename + '.csv') \
                .get()

            return pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf8')
        except Exception as e:
            print(e)
