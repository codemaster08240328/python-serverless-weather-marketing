import pandas as pd
import boto3
import json
import decimal


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def df_to_dynamo(table_name, df, batch_size=50):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    df_list = json.loads(df.to_json(orient='records'))
    df_chunks = divide_chunks(df_list, batch_size)
    with table.batch_writer() as batch:
        for chunk in df_chunks:
            for item in chunk:
                batch.put_item(
                    Item=json.loads(json.dumps(item), parse_float=decimal.Decimal)
                )


#####Populate Location Table#####
geo = pd.read_csv('geo.csv', sep='|')
geo.rename(columns={'zip': 'postal_code'}, inplace=True)
geo.postal_code = geo.postal_code.astype('str')
table_name = 'geo'
df_to_dynamo(table_name, geo, batch_size=50)
