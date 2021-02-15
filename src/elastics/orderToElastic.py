from src.shared.util import get_secret
from src.elastics.util import insert_update_order, remove_document, insert_update_order_customer, remove_order_customer
from elasticsearch import Elasticsearch
import json
import boto3

reserved_fields = ["uid", "_id", "_type", "_source", "_all", "_parent",
                   "_fieldnames", "_routing", "_index", "_size", "_timestamp", "_ttl"]


# Process DynamoDB Stream records and insert the object in ElasticSearch
# Use the Table name as index and doc_type name
# Force index refresh upon all actions for close to realtime reindexing
# Use IAM Role for authentication
# Properly unmarshal DynamoDB JSON types. Binary NOT tested.
def handler(event, context):
    secret = get_secret('elastic-root')
    # Connect to ES
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
                doc_json = insert_update_order(es, record)
                insert_update_order_customer(es, doc_json)
            elif record['eventName'] == "REMOVE":
                remove_document(es, record)
                remove_order_customer(es, doc_json)
            elif record['eventName'] == "MODIFY":
                doc_json = insert_update_order(es, record)
                insert_update_order_customer(es, doc_json)

        except Exception as e:
            print("Failed to process:")
            print(json.dumps(record))
            print("ERROR: " + repr(e))
            continue
