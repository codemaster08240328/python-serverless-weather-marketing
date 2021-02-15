from src.shared.util import get_secret
from src.elastics.util import insert_document, remove_document, modify_document, upsert_customer
from elasticsearch import Elasticsearch
import json
import boto3

reserved_fields = ["uid", "_id", "_type", "_source", "_all", "_parent",
                   "_fieldnames", "_routing", "_index", "_size", "_timestamp", "_ttl"]

def handler(event, context):
    secret = get_secret('elastic-root')

    es = Elasticsearch(
        [secret['host']],
        http_auth=(secret['user'], secret['password']),
        scheme='https',
        port=secret['port']
    )

    print("Cluster info:")
    print(es.info())

    # Loop over the DynamoDB Stream records
    for record in event['Records']:

        try:

            if record['eventName'] == "INSERT":
                upsert_customer(es, record)
            elif record['eventName'] == "REMOVE":
                remove_document(es, record)
            elif record['eventName'] == "MODIFY":
                upsert_customer(es, record)

        except Exception as e:
            print("Failed to process:")
            print(json.dumps(record))
            print("ERROR: " + repr(e))
            continue
