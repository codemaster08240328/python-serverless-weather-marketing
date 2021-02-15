import json
import re
from src.shared.util import DecimalEncoder
import boto3
import os


def enhance_store(doc_json):
    try:
        store_id = doc_json['store_id']
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('store')
        response = table.get_item(Key={'store_id': store_id})
        store_details = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']
        doc_json['store'] = store_details
    except Exception as ex:
        print(ex)
    return doc_json


def get_order_postal_code(doc_json):
    postal_code = -9999
    try:
        postal_code = doc_json['store']['postal_code']
        found = True
    except:
        try:
            postal_code = doc_json['shipping_address']['postal_code']
            found = True
        except:
            try:
                postal_code = doc_json['business_address']['postal_code']
                found = True
            except:
                found = False
    return postal_code, found


def enhance_location(doc_json, postal_code):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('geo')
        response = table.get_item(Key={'postal_code': postal_code})
        geo_details = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']
        doc_json['geo'] = geo_details
    except Exception as ex:
        print(ex)
    return doc_json


def enhance_product(doc_json):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('products' + '-' + os.environ['stage'])
    for i in range(len(doc_json['items'])):
        try:
            response = table.get_item(Key={'product_id': doc_json['items'][i]['product_id']})
            product_details = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']
            doc_json['product_attributes'] = product_details
        except Exception as ex:
            print(ex)
    return doc_json


def insert_update_order(es, record):
    table = getTable(record)
    print("Dynamo Table: " + table)

    docId = generateId(record)
    print("KEY")
    print(docId)

    # Unmarshal the DynamoDB JSON to a normal JSON
    doc_json = unmarshalJson(record['dynamodb']['NewImage'])
    doc_json = enhance_store(doc_json)
    postal_code, geo_found = get_order_postal_code(doc_json)
    if geo_found:
        doc_json = enhance_location(doc_json, postal_code)
    doc_json = enhance_product(doc_json)
    doc = json.dumps(unmarshalJson(record['dynamodb']['NewImage']))

    print("Updated document:")
    print(doc)

    # We reindex the whole document as ES accepts partial docs
    es.index(index=table,
             body=doc,
             id=docId,
             doc_type=table,
             refresh=True)

    print("Successly modified - Index: " + table + " - Document ID: " + docId)
    return doc_json


def insert_update_order_customer(es, doc_json):
    try:
        docId = doc_json['customer_id']
    except:
        print('No Customer ID found')
        return
    body = {
        "upsert": {
            "customer_id": docId,
            "orders": [doc_json]
            },

        "script": {
            "lang": "painless",
            "source": """int order_found = 0;
                for (int i = 0; i < ctx._source.orders.length; ++i) {
                        if(ctx._source.orders[i].order_id == params.order_id) {
                            ctx._source.orders[i] = params.transactions[0];
                            order_found = 1;
                        }
                        }
                if(order_found == 0) {
                    ctx._source.orders.addAll(params.transactions)
                }""",
                    "params": {
                        "order_id": doc_json['order_id'],
                        "transactions": [doc_json]
                        }
                        }
            }
    es.update(index='customer',
             body=json.dumps(body),
             id=docId)
    print("Successly added order to customer")


def remove_order_customer(es, doc_json):
    try:
        docId = doc_json['customer_id']
    except:
        print('No Customer ID found')
        return
    body = {
        "script": {
            "lang": "painless",
            "source": """for (int i = 0; i < ctx._source.orders.length; ++i) {
                    if(ctx._source.orders[i].order_id == params.order_id) {
                        ctx._source.orders.remove(i);
                        break;
                    }
                    }""",
                    "params": {
                        "order_id": doc_json['order_id'],
                        }
                        }
            }
    es.update(index='customer',
             body=json.dumps(body),
             id=docId)
    print("Successly added order to customer")



# Process MODIFY events
def modify_document(es, record):
    table = getTable(record)
    print("Dynamo Table: " + table)

    docId = generateId(record)
    print("KEY")
    print(docId)

    # Unmarshal the DynamoDB JSON to a normal JSON
    doc = json.dumps(unmarshalJson(record['dynamodb']['NewImage']))

    print("Updated document:")
    print(doc)

    # We reindex the whole document as ES accepts partial docs
    es.index(index=table,
             body=doc,
             id=docId,
             doc_type=table,
             refresh=True)

    print("Successly modified - Index: " + table + " - Document ID: " + docId)


# Process REMOVE events
def remove_document(es, record):
    table = getTable(record)
    print("Dynamo Table: " + table)

    docId = generateId(record)
    print("Deleting document ID: " + docId)

    es.delete(index=table,
              id=docId,
              doc_type=table,
              refresh=True)

    print("Successly removed - Index: " + table + " - Document ID: " + docId)


# Process INSERT events
def upsert_customer(es, record):
    table = getTable(record)
    print("Dynamo Table: " + table)

    # Unmarshal the DynamoDB JSON to a normal JSON
    doc_json = unmarshalJson(record['dynamodb']['NewImage'])
    try:
        enhance_location(doc_json, doc_json['postal_code'])
    except:
        print('Location not Found')
    doc = json.dumps(doc_json)

    print("Upsert to Index:")
    print(doc)

    body = {"doc": doc, "doc_as_upsert": True}
    docId = generateId(record)
    es.update(index='customer',
                 body=json.dumps(body),
                 id=docId)
    print("Successly inserted - Index: " + table + " - Document ID: " + newId)



# Process INSERT events
def insert_document(es, record):
    table = getTable(record)
    print("Dynamo Table: " + table)

    # Create index if missing
    if es.indices.exists(table) == False:
        print("Create missing index: " + table)

        es.indices.create(table,
                          body='{"settings": { "index.mapping.coerce": true } }')

        print("Index created: " + table)

    # Unmarshal the DynamoDB JSON to a normal JSON
    doc = json.dumps(unmarshalJson(record['dynamodb']['NewImage']))

    print("New document to Index:")
    print(doc)

    newId = generateId(record)
    es.index(index=table,
             body=doc,
             id=newId,
             doc_type=table,
             refresh=True)

    print("Successly inserted - Index: " + table + " - Document ID: " + newId)


# Return the dynamoDB table that received the event. Lower case it
def getTable(record):
    p = re.compile('arn:aws:dynamodb:.*?:.*?:table/([0-9a-zA-Z_-]+)/.+')
    m = p.match(record['eventSourceARN'])
    if m is None:
        raise Exception("Table not found in SourceARN")
    return m.group(1).lower()


# Generate the ID for ES. Used for deleting or updating item later
def generateId(record):
    keys = unmarshalJson(record['dynamodb']['Keys'])

    # Concat HASH and RANGE key with | in between
    newId = ""
    i = 0
    for key, value in list(keys.items()):
        if (i > 0):
            newId += "|"
        newId += str(value)
        i += 1

    return newId


# Unmarshal a JSON that is DynamoDB formatted
def unmarshalJson(node):
    data = {}
    data["M"] = node
    return unmarshalValue(data, True)


# ForceNum will force float or Integer to
def unmarshalValue(node, forceNum=False):
    for key, value in list(node.items()):
        if (key == "NULL"):
            return None
        if (key == "S" or key == "BOOL"):
            return value
        if (key == "N"):
            if (forceNum):
                return int_or_float(value)
            return value
        if (key == "M"):
            data = {}
            for key1, value1 in list(value.items()):
                if key1 in reserved_fields:
                    key1 = key1.replace("_", "__", 1)
                data[key1] = unmarshalValue(value1, True)
            return data
        if (key == "BS" or key == "L"):
            data = []
            for item in value:
                data.append(unmarshalValue(item))
            return data
        if (key == "SS"):
            data = []
            for item in value:
                data.append(item)
            return data
        if (key == "NS"):
            data = []
            for item in value:
                if (forceNum):
                    data.append(int_or_float(item))
                else:
                    data.append(item)
            return data


# Detect number type and return the correct one
def int_or_float(s):
    try:
        return int(s)
    except ValueError:
        return float(s)
