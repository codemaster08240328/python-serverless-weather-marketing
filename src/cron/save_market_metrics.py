from src.shared.util import get_all_records_asset, get_all_records_hash, put_single_record
from src.forecast.forecast import save_forecast
import datetime
import pandas as pd # for athena query
import os
import json
import boto3
import time
import io


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


def bid_modifier_sql(geo, ml_key):
    if geo == 'us':
        SQL = f"""SELECT google_id_county as gid, avg(score) * 4  + 1 as bm FROM "bus"."eb_ml_scores_h3" a
            join wx.geo b
            on a.h3_4 = b.h3_4
            WHERE 	ml_key = '{ml_key}'
            and local_date = current_date
            and google_id_county != ''
            and zip_country = 'US'
            group by google_id_county"""
    elif geo == 'ca':
        SQL = f"""SELECT google_id_postal_code as gid, avg(score) * 4 + 1 as bm FROM "bus"."eb_ml_scores_h3" a
            join wx.geo b
            on a.h3_4 = b.h3_4
            WHERE 	ml_key = '{ml_key}'
            and local_date = current_date
            and google_id_postal_code != ''
            and zip_country = 'CA'
            group by google_id_postal_code"""
    elif geo == 'us_ca':
        SQL = f"""SELECT google_id_postal_code as gid, avg(score) * 4  + 1 as bm FROM "bus"."eb_ml_scores_h3" a
            join wx.geo b
            on a.h3_4 = b.h3_4
            WHERE 	ml_key = '{ml_key}'
            and local_date = current_date
            and google_id_postal_code != ''
            and zip_country = 'CA'
            group by google_id_postal_code
            UNION ALL
            SELECT google_id_county as gid, avg(score) * 4  + 1 as bm FROM "bus"."eb_ml_scores_h3" a
            join wx.geo b
            on a.h3_4 = b.h3_4
            WHERE 	ml_key = '{ml_key}'
            and local_date = current_date
            and google_id_county != ''
            and zip_country in ('US', 'CA')
            group by google_id_county"""
    return SQL


def google_df_to_list(df):
    g_list = []
    for i, r in df.iterrows():
        g_list.append('')


def get_bid_modifiers(geo, ml_key):
    SQL = bid_modifier_sql(geo, ml_key)
    qa = QueryAthena(query=SQL, database='bus')
    df = qa.run_query()
    df.loc[df.bm < -1, 'bm'] = -.99
    df.gid = df.gid.astype('int')
    return json.loads(df.to_json(orient="records"))


def save_metrics(event, context):
    bus_list = get_all_records_hash('master_business')
    for bus_item in bus_list:
        bus = bus_item['asset']
        items = get_all_records_asset(f'{bus}#spend_rules')
        for item in items:
            tomorrow = (datetime.datetime.now() - datetime.timedelta(hours=7) +
                        datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            print('Saving forecast for', item['id'])
            save_forecast(item['id'], f'{bus}#spend_rules', tomorrow)
            if item['destination'] == 'google':
                bid_modifier_item = {}
                bid_modifier_item['id'] = item['id']
                bid_modifier_item['bid_modifiers'] = get_bid_modifiers(item['geo'], item['product'])
                bid_modifier_item['asset'] = 'google#bid_modifiers'
                response = put_single_record(bid_modifier_item)
                print('Saving modifiers for Google ID', bid_modifier_item['id'])
                print(response)

if __name__ == "__main__":
    import sys
    sys.path.append("/Users/chrismorin/notus_code/wx-api")
    os.environ['stage'] = 'prod'
    save_metrics({}, {})
