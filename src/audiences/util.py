import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key
from jose import jwt
from src.audiences.exception import InvalidAudience, InvalidQuery
from datetime import datetime
import os
import io
import uuid
import copy
import requests


def memory_to_s3(bucket, object_path, file_stream):
    """Takes a file and sends it to an s3 path"""
    s3 = boto3.resource('s3')
    object = s3.Object(bucket, object_path)
    object.put(Body=file_stream)
    print('%s uploaded' % object_path)


def s3_to_memory(bucket, path):
    s3 = boto3.resource('s3', region_name='us-east-1')
    bucket = s3.Bucket(bucket)
    file_stream = io.BytesIO()
    bucket.download_fileobj(path, file_stream)
    file_stream.seek(0)
    return file_stream.read().decode("utf-8")


def get_business(token):
    if token[:6] == 'Bearer':
        token = token.split()[1]

    email = jwt.get_unverified_claims(token)['email']
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    stage = os.environ['stage']
    table = dynamodb.Table('assets')
    item = table.get_item(Key={'id': email, 'asset': 'client'})
    item_js = json.loads(json.dumps(
        item, indent=4, cls=DecimalEncoder))['Item']
    return item_js['bus']


def sort_a_b(a, b):
    """Sorts list b based on list a"""
    y = [x for _, x in sorted(zip(a, b))]
    return y


def add_audiences(d, token):
    bus = get_business(token)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('audiences-list')
    items = table.query(KeyConditionExpression=Key('bus').eq(bus))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']
    audience_names = []
    audience_values = []
    for item in items:
        audience_names.append(item['name'])
        audience_values.append(item['id'])
    i = 0
    audience_values = sort_a_b(audience_names, audience_values)
    audience_names.sort()
    for a in d['Universe']['selection']['Audiences']['elements']:
        if a['label'] == 'Audiences':
            d['Universe']['selection']['Audiences']['elements'][i]['options'] = audience_names
            d['Universe']['selection']['Audiences']['elements'][i]['values'] = audience_values
        i = i + 1
    return d


def add_query_audiences(d, token):
    bus = get_business(token)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    stage = os.environ['stage']
    table = dynamodb.Table('assets')
    items = table.query(KeyConditionExpression=Key(
        'id').eq(bus + '#audience#contacts'))
    items = json.loads(json.dumps(
        items, indent=4, cls=DecimalEncoder))['Items']
    audience_names = []
    audience_values = []
    for item in items:
        if item['ui']:
            audience_names.append(
                item['name'] + ' (version: ' + item['asset'] + ')')
            audience_values.append(item['version_id'])
    i = 0
    audience_values = sort_a_b(audience_names, audience_values)
    audience_names.sort()
    audience_dict = []
    for i in range(len(audience_names)):
        audience_dict.append(
            {"title": audience_names[i], "value": audience_values[i]})
    d['universe']['audiences']['subfields']['Audience Customers']['listValues'] = audience_dict
    return d


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def create_universe(u):
    """

    Runs through methods to put Universe sql together

    Args:
        u (dict): MongoDB dict from react query tool

    Returns:
        sql (string): Universe SQL

    """
    if u == {}:
        print('Empty Universe Found')
        sql = universe_list_to_sql([], [])
    else:
        global out_list
        out_list = []
        out_u = add_conjuction(u)
        nested_universe_dict_iter(out_u)
        out_list = clean_query_list(out_list)
        query_list = []
        sub_q = []
        for i in range(len(out_list)):
            a = out_list[i]
            print(a)
            if isinstance(a, dict):
                clause_type = list(a.keys())[0]
                if clause_type == 'audiences':
                    sub_q_audience, sub_q_audience_where_clause = audience_filter(
                        a[clause_type])
                    query_list.append(sub_q_audience_where_clause)
                    sub_q.append(sub_q_audience)
                elif clause_type == 'cordial':
                    sub_q_cordial, sub_q_cordial_where_clause = cordial_filter(
                        a[clause_type])
                    query_list.append(sub_q_cordial_where_clause)
                    sub_q.append(sub_q_cordial)
                elif clause_type == 'weather':
                    sub_q_weather, sub_q_weather_where_clause = weather_filter(
                        a[clause_type])
                    query_list.append(sub_q_weather_where_clause)
                    sub_q.append(sub_q_weather)
                elif clause_type == 'weather_ml':
                    sub_q_weather_ml, sub_q_weather_ml_where_clause = weather_ml_filter(
                        a[clause_type])
                    query_list.append(sub_q_weather_ml_where_clause)
                    sub_q.append(sub_q_weather_ml)
                elif clause_type == 'transactional':
                    print('!!!!!!! Found Transactional Rule:', a[clause_type])
                    sub_q_transaction, sub_q_transaction_where_clause = transaction_filter(
                        a[clause_type])
                    query_list.append(sub_q_transaction_where_clause)
                    print('!!!')
                    print(query_list)
                    print('!!!')
                    sub_q.append(sub_q_transaction)
                else:
                    query_list.append(customer_filter(a))
            elif a not in ['(', ')', 'AND', 'OR']:
                query_list.append(customer_filter(a))
            else:
                query_list.append(a)
        sql = universe_list_to_sql(sub_q, query_list)
    return sql


def customer_filter(rules):
    """

    Given an vanilla MongoDB dict from the react query tool, creates where clause

    Args:
        a (dict): MongoDB dicitonary from vanilla element of react-awesome-query-tool

    Returns:
        result (string): where clause snippet

    """
    for field_key in rules.keys():
        query_field = field_key_clean(field_key)
        result = make_comparison(query_field, rules[field_key])
        print(result)
        return(result)


def universe_list_to_sql(sub_q, query_list):
    """

    Assembles sql squery from template of sql and subquery/where clause inputs

    Args:
        sub_q (list): List of subqueries
        query_list (list): List of where clauses

    Returns:
        query (string): SQL statement

    """
    sub_q_string = ' '.join(sub_q)
    q_string = ' '.join(query_list)
    if len(q_string) > 0:
        q_string = 'WHERE ' + q_string
    query = f"""SELECT ml_product.customer_id
        FROM "ml"."eddiebauer_prod_product_scores" ml_product
        LEFT JOIN "source"."eddiebauer_prod_customer_attribute" customer_table
            ON customer_table.customer_id = ml_product.customer_id
        JOIN "ml"."eddiebauer_prod_propensity_scores" ml_trans
            ON ml_trans.customer_id = ml_product.customer_id
            {sub_q_string}
            {q_string}"""
    return query


def field_key_clean(field_key):
    """

    Takes keys from query tool and maps them to sql columns

    Args:
        field_key (string): dict key

    Returns:
        string: mapped/cleaned string

    """
    field_map = {
        'Test / Control': 'test_group',
        'Audience Customers': 'id',
        'Time Period': 'date',
        'Product': 'ITEM_ID',
        'age': 'age_bin',
        'Store ID': 'store_number',
        'loyalty': 'loyalty_tier'
    }
    try:
        print(field_key, 'transformed to ', field_map[field_key])
        field_key = field_map[field_key]
    except Exception as e:
        print(field_key, 'Not Found')
        field_key = field_key.lower()
    return field_key


def make_comparison(field_key, field_compare):
    """

    Creates a comparison between a variable and a value with MongoDB operators from query tool

    Args:
        field_key (string or dict): MongoDB operator or dict of operators

    Returns:
        result (string): where clause comparison snippet

    """
    if isinstance(field_compare, dict):
        comparison_way = 0
        for key in field_compare.keys():
            if key == '$lte':
                comparison_way = comparison_way + 1
            elif key == '$gte':
                comparison_way = comparison_way + 2
            else:
                comparison_way = comparison_way + 0

            field_compare[key] = string_quotes(field_compare[key])

        if len(field_compare.keys()) > 1:
            if field_key == 'date':
                result = f"{field_key} BETWEEN parse_datetime({field_compare['$gte']},'YYYY-MM-dd') AND parse_datetime({field_compare['$lte']},'YYYY-MM-dd')"
            elif field_key == 'days ahead':
                result = f"date BETWEEN date_add('day', {field_compare['$gte']}, current_date) AND date_add('day', {field_compare['$lte']}, current_date)"
            elif comparison_way == 1:
                result = f"{field_key} > {field_compare['$gt']} AND {field_key} <= {field_compare['$lte']}"
            elif comparison_way == 2:
                result = f"{field_key} >= {field_compare['$gte']} AND {field_key} < {field_compare['$lt']}"
            elif comparison_way == 3:
                result = f"{field_key} BETWEEN {field_compare['$gte']} AND {field_compare['$lte']}"
            else:
                result = f"{field_key} > {field_compare['$gt']} AND {field_key} < {field_compare['$lt']}"
        elif list(field_compare.keys())[0] in (['$in', '$nin']):
            op_key = list(field_compare.keys())[0]
            join_list = [str(x) for x in field_compare[op_key]]
            result = f"{field_key} {comparison_dict(op_key)} ({', '.join(join_list)})"
        elif list(field_compare.keys())[0] == '$exists':
            if field_compare['$exists']:
                field_compare_null = 'NOT NULL'
            else:
                field_compare_null = 'NULL'
            op_key = list(field_compare.keys())[0]
            result = f"{field_key} {comparison_dict(op_key)} {field_compare_null}"
        else:
            op_key = list(field_compare.keys())[0]
            if field_key.find('temperature') > -1:
                if field_key.find('mean') > -1:
                    field_compare[op_key] = field_compare[op_key] * 5 / 9
                else:
                    field_compare[op_key] = (field_compare[op_key] - 32) * 5 / 9 + 273.15
            result = f"{field_key} {comparison_dict(op_key)} {field_compare[op_key]}"
    elif isinstance(field_compare, list):
        field_compare = string_quotes(field_compare)
        join_list = [str(x) for x in field_compare]
        result = f"{field_key} in ({', '.join(join_list)})"
    else:
        field_compare = string_quotes(field_compare)
        result = f'{field_key} = {field_compare}'
    return result


def audience_filter(a):
    """

    Given an audience MongoDB dict from the react query tool
    Creates a subquery and outside where clause

    Args:
        a (dict): MongoDB dicitonary from audience element of react-awesome-query-tool

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    join_id = 'q' + str(uuid.uuid4().hex)[:10]
    rules = a['$elemMatch']

    try:
        ac = rules['Audience Customers']
    except Exception as e:
        print('Need audience Customers')
        raise InvalidQuery('Need audience Customers')
        return
    internal_where = []
    external_where = []
    for field_key in rules.keys():
        query_field = field_key_clean(field_key)
        flip_case, rules_inc = flip_if_exclude(rules[field_key])
        result = make_comparison(query_field, rules_inc)
        internal_where.append(result)
        if query_field == 'id':
            if flip_case:
                result = f'audience_{join_id} != 1'
            else:
                result = f'audience_{join_id} = 1'
            external_where.append(result)
    sub_q = audience_nested_subquery(' AND '.join(internal_where), join_id)
    sub_q_where_clause = f"({' AND '.join(external_where)})"
    return sub_q, sub_q_where_clause


def weather_filter(a):
    """

    Given an audience MongoDB dict from the react query tool
    Creates a subquery and outside where clause

    Args:
        a (dict): MongoDB dicitonary from weather element of react-awesome-query-tool

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    join_id = 'q' + str(uuid.uuid4().hex)[:10]
    rules = a['$elemMatch']
    internal_where = []
    for field_key in rules.keys():
        query_field = field_key_clean(field_key)
        result = make_comparison(query_field, rules[field_key])
        result = result.replace('date BETWEEN', 'local_date BETWEEN')
        internal_where.append(result)
    sub_q_where_clause = f'{join_id}.nested_filter = 1'
    sub_q = weather_nested_subquery(' AND '.join(internal_where), join_id)
    return sub_q, sub_q_where_clause


def weather_nested_subquery(internal_where_clause, join_id):
    """

    formats audience sql subquery string once internal
    where clause and id have been created

    Args:
        internal_where_clause (string): Where clause for weather selection
        join_id (string): unique identifier for subquery

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    result = f"""LEFT JOIN (SELECT DISTINCT h3_4, 1 as nested_filter FROM "wx"."gfs_enhanced_h3"
    WHERE {internal_where_clause}) {join_id}
    on {join_id}.h3_4 = customer_table.h3_4
    """
    return result


def weather_ml_filter(a):
    """

    Given an audience MongoDB dict from the react query tool
    Creates a subquery and outside where clause

    Args:
        a (dict): MongoDB dicitonary from weather element of react-awesome-query-tool

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    join_id = 'q' + str(uuid.uuid4().hex)[:10]
    rules = a['$elemMatch']
    internal_where = []
    for field_key in rules.keys():
        query_field = field_key_clean(field_key)
        result = make_comparison(query_field, rules[field_key])
        internal_where.append(result)
    sub_q_where_clause = f'{join_id}.nested_filter = 1'
    sub_q = weather_nested_subquery(' AND '.join(internal_where), join_id)
    return sub_q, sub_q_where_clause


def weather_ml_nested_subquery(internal_where_clause, join_id):
    """

    formats audience sql subquery string once internal
    where clause and id have been created

    Args:
        internal_where_clause (string): Where clause for weather selection
        join_id (string): unique identifier for subquery

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    result = f"""LEFT JOIN (SELECT DISTINCT h3_4, 1 as nested_filter FROM "bus"."eb_ml_scores_h3"
    WHERE {internal_where_clause}) {join_id}
    on {join_id}.h3_4 = customer_table.h3_4
    """
    return result


def cordial_filter(a):
    """

    Given an audience MongoDB dict from the react query tool
    Creates a subquery and outside where clause

    Args:
        a (dict): MongoDB dicitonary from cordial element of react-awesome-query-tool

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    join_id = 'q' + str(uuid.uuid4().hex)[:10]
    rules = a['$elemMatch']
    internal_where = []
    for field_key in rules.keys():
        query_field = field_key_clean(field_key)
        result = make_comparison(query_field, rules[field_key])
        internal_where.append(result)
    sub_q_where_clause = f'{join_id}.nested_filter = 1'
    sub_q = cordial_nested_subquery(' AND '.join(internal_where), join_id)
    return sub_q, sub_q_where_clause


def cordial_nested_subquery(internal_where_clause, join_id):
    """

    formats audience sql subquery string once internal
    where clause and id have been created

    Args:
        internal_where_clause (string): Where clause for cordial selection
        join_id (string): unique identifier for subquery

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    result = f"""LEFT JOIN (SELECT DISTINCT customer_id, 1 as nested_filter FROM "source"."eddiebauer_prod_cordial"
    WHERE {internal_where_clause}) {join_id}
    on {join_id}.customer_id = ml_product.customer_id
    """
    return result


def transaction_nested_subquery(internal_where_clause, join_id):
    """

    formats transaction sql subquery string once internal
    where clause and id have been created

    Args:
        internal_where_clause (string): Where clause for transaction selection
        join_id (string): unique identifier for subquery

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    result = f"""JOIN (SELECT    cust.customer_id,
          COALESCE(units, 0)     AS units_{join_id},
          COALESCE(demand, 0)       AS demand_{join_id},
          COALESCE(transactions, 0) AS transactions_{join_id}
            FROM      (
                                      SELECT DISTINCT customer_id
                                      FROM "source"."eddiebauer_prod_order_line_enhanced" ) cust
            LEFT JOIN
                      (
                               SELECT   customer_id,
                                        SUM(units)     AS units,
                                        SUM(demand) AS demand,
                                        COUNT( DISTINCT order_id)  AS transactions
                               FROM     "source"."eddiebauer_prod_order_line_enhanced" a
                               WHERE    {internal_where_clause}
                               GROUP BY a.customer_id) transaction
                ON cust.customer_id = transaction.customer_id ) {join_id}
                               on {join_id}.customer_id = ml_product.customer_id"""
    return result


def add_conjuction(u):
    """
    Checks if conjuction is needed on incomning json
    If missing creates 'AND' behavior as
    default behavior for AND does not include identifier at top level
    """
    if (list(u.keys())[0] != '$and') & (list(u.keys())[0] != '$or'):
        op_list = []
        for key in u.keys():
            op_list.append({key: u[key]})
        u = {'$and': op_list}
    return u


def nested_universe_dict_iter(a, join_type='top'):
    """

    Iterates through nested dictionary and adds
    elements to global out_list defined outside of function
    Used to build an initial list for the Universe portion of the query
    list is mostly functional at this point, but undergoes another step to fix
    some errors

    Args:
        a (dict): MongoDB dicitonary from react-awesome-query-tool
        join_type (string): Conjuction as defined from query tool for element
        *out_list* (global list): Empty global list defined outside of Function
            Global as couldn't figure out how to return result otherwise in iterative
            functon

    Returns:
        Nothing directly, but build the global out_list defined

    """
    if '$and' in a.keys():
        out_list.append('(')
        for b in a['$and']:
            nested_universe_dict_iter(b, 'AND')
        out_list.append(')')
    elif '$or' in a.keys():
        out_list.append('(')
        for b in a['$or']:
            nested_universe_dict_iter(b, 'OR')
        out_list.append(')')
    else:
        out_list.append(a)
        out_list.append(join_type)
        print(list(a.keys())[0])
        print(join_type)


def clean_query_list(out_list):
    """

    The iterative function that parses the react query tool does not make a clean
    output. This fixes some issues with conjuctions and parentheses

    Args:
        out_list: List created from parsing MongoDB portion of react-awesome-query-tool

    Returns:
        list: fixed out_list

    """
    print('pre clean')
    print(out_list)
    print('pre clean')
    for i in range(len(out_list)):
        try:
            if out_list[i] == ')' and isinstance(out_list[i + 1], dict):
                join_type = copy.copy(out_list[i + 2])
                out_list[i + 2] = out_list[i + 1]
                out_list[i + 1] = join_type
        except Exception as e:
            print('Found End')
        if out_list[i] == ')' and out_list[i - 1] in ['+', ',', 'AND', 'OR']:
            out_list[i - 1] = 'remove'
    out_list = list(filter(lambda a: a != 'remove', out_list))
    print('post clean')
    print(out_list)
    print('post clean')
    return out_list


def transaction_filter(a):
    """

    Given an audience MongoDB dict from the react query tool
    Creates a subquery and outside where clause

    Args:
        a (dict): MongoDB dicitonary from audience element of react-awesome-query-tool

    Returns:
        sub_q (string): sql subquery
        sub_q_where_clause: sql where clause snippet

    Raises:
        InvalidQuery: Required Query elements are not present

    """
    join_id = 'q' + str(uuid.uuid4().hex)[:10]
    try:
        a['$elemMatch']['Product'] = [
            x.split('-')[-1] for x in a['$elemMatch']['Product']]
        a['$elemMatch']['Product'] = [
            int(x.replace("'", "")) for x in a['$elemMatch']['Product']]
    except Exception as e:
        pass
    rules = a['$elemMatch']

    if validate_transaction(rules):
        print('Found Valid Ruleset')

    else:
        print('!!!INVALID TRANSACTION RULE!!!')
        print('Transaction Rule Sets need a Time Period and at least one metric to measure against (Transactions etc.)')

        raise InvalidQuery(
            'Transaction Rule Sets need a Time Period and at least one metric to measure against (Transactions etc.)')

    internal_where = []
    external_where = []
    for field_key in rules.keys():
        query_field = field_key_clean(field_key)
        if query_field not in ['transactions', 'demand', 'units']:
            result = make_comparison(query_field, rules[field_key])
            internal_where.append(result)
        else:
            result = make_comparison(
                f'{query_field}_{join_id}', rules[field_key])
            external_where.append(result)
    sub_q = transaction_nested_subquery(' AND '.join(internal_where), join_id)
    print('&&&')
    print(external_where)
    print('&&&')
    sub_q_where_clause = f"({' AND '.join(external_where)})"
    print('@@@')
    print(sub_q_where_clause)
    print('@@@')
    return sub_q, sub_q_where_clause


def string_quotes(a):
    """

    Adds single quotes to a variable

    Args:
        a (list or string):

    Returns:
        quoted a

    """
    if isinstance(a, list):
        for i in range(len(a)):
            if isinstance(a[i], str):
                a[i] = "'" + a[i].replace("'", "") + "'"
    elif isinstance(a, str):
        a = "'" + a.replace("'", "") + "'"
    return a


def comparison_dict(a):
    """

    Maps MongoDB operators to SQL operators

    Args:
        a (string): MongoDB operator

    Returns:
        string: SQL operator

    """
    d = {'$eq': '=',
         '$gt': '>',
         '$gte': '>=',
         '$in': 'IN',
         '$lt': '<',
         '$lte': '<=',
         '$ne': '!=',
         '$nin': 'NOT IN',
         '$exists': 'IS'}
    return d[a]


def flip_if_exclude(field_compare):
    """

    If a query needs to exclude an audience, most efficent way
    is to join the audience in a subquery and then join in the outside where clause
    Allows to have more complicated logic in the nested query tool

    Args:
        field_compare (string or dict): MongoDB operator

    Returns:
        bool: True if the operator was negative and was flipped
        string: the flipped MongoDB operator

    """
    out_compare = {}
    if isinstance(field_compare, dict):
        op_key = list(field_compare.keys())[0]
        if op_key == '$ne':
            out_compare['$eq'] = field_compare[op_key]
            result = True
        elif op_key == '$nin':
            out_compare['$in'] = field_compare[op_key]
            result = True
        else:
            out_compare = field_compare
            result = False
    else:
        out_compare = field_compare
        result = False
    return result, out_compare


def audience_nested_subquery(internal_where_clause, join_id):
    """

    formats audience sql subquery string once internal
    where clause and id have been created

    Args:
        internal_where_clause (string): Where clause for audience selection
        join_id (string): unique identifier for subquery

    Returns:
        string: sql subquery
        sub_q_where_clause: sql where clause snippet

    """
    result = f"""JOIN (SELECT    cust.customer_id, COALESCE(audience, 0) as audience_{join_id}
            FROM      (SELECT DISTINCT customer_id
    FROM  "source"."eddiebauer_prod_order_line_enhanced" ) cust
    LEFT JOIN (SELECT DISTINCT customer_id, 1 as audience FROM "bus"."eb_prod_audience_versions"
    WHERE {internal_where_clause}) inc
    ON inc.customer_id = cust.customer_id
    ) {join_id}
    on {join_id}.customer_id = ml_product.customer_id
    """
    return result


def validate_transaction(a):
    """

    Checks if the minimmum number of variables are entered if a Transaction element is selected

    Args:
        a (dict): MongoDB dicitonary from transaction element of react-awesome-query-tool

    Returns:
        bool: True if minimmum number of fields met

    """
    or_cond = False
    time_period_cond = False
    for essential in ['Transactions', 'Demand', 'Units']:
        try:
            a[essential]
            or_cond = True
        except Exception as e:
            pass
    for essential in ['Time Period', 'Days Ahead']:
        try:
            a[essential]
            time_period_cond = True
        except Exception as e:
            pass
    return time_period_cond & or_cond


def send_query(sql):
    """

    Sends sql to a lambda that will run in athena and update a dynamodb entry

    Args:
        sql (string): Sql to run

    Returns:
        sql_id (string): Unique SQL identifier a user can use to get result from DynamoDB

    """
    sql_id = str(uuid.uuid4())
    create_blank_query_record(sql_id)
    payload = {}
    payload['sql'] = sql
    payload['db'] = 'bus'
    payload['sql_id'] = sql_id
    payload = json.dumps(payload)
    client = boto3.client('lambda')
    print('Running', sql)
    client.invoke(
        FunctionName=f'arn:aws:lambda:us-east-1:453299555282:function:audience-{os.environ["stage"]}-run_sql',
        LogType='None',
        InvocationType='Event',
        Payload=payload
    )
    return sql_id


def create_universe_count(sql):
    """

    Changes Universe query to only return a count of customers as
    opposed to the customers themselves

    Args:
        sql (string): Universe SQL

    Returns:
        sql (string): Universe Count SQL

    """
    sql = 'SELECT COUNT(*) as result' + sql[33:]
    return sql


def create_blank_query_record(sql_id):
    """

    Creates a blank dynamodb record with given id.
    Initializes status and result fields

    Args:
        sql_id (string): unique identifier

    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('var')
    new_item = {
        'id': sql_id,
        'result': 'Not Returned',
        'status': 'Running'
    }
    response = table.put_item(Item=json.loads(
        json.dumps(new_item), parse_float=decimal.Decimal))


def create_blank_record(payload):
    """

    Creates a blank dynamodb record with given id.
    Initializes status and result fields

    Args:
        record_id (string): unique identifier

    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('var')
    new_item = {
        'id': payload['id'],
        'result': 'Not Returned',
        'status': 'Running',
        'payload': payload
    }
    response = table.put_item(Item=json.loads(
        json.dumps(new_item), parse_float=decimal.Decimal))
    return response







def create_score_order(u):
    """

    Assembles an order by clause using scoring part of react query tool output

    Args:
        u (dict): MongoDB dict from react query tool

    Returns:
        sql (string): order by clause of scoring variables

    """
    global out_list
    out_list = []
    if u != {}:
        out_u = add_conjuction(u)
        nested_score_dict_iter(out_u)
        out_list = clean_query_list(out_list)
        for i in range(len(out_list)):
            a = out_list[i]
            if isinstance(a, dict):
                ml_type = list(a.keys())[0]
                if ml_type == 'transact_probability':
                    out_list[i] = create_transact_score(a[ml_type])
                if ml_type == 'churn':
                    out_list[i] = create_churn_score(a[ml_type])
                if ml_type == 'clv':
                    out_list[i] = create_clv_score(a[ml_type])
    sql = score_list_to_sql(out_list)
    sql = sql.strip()

    return sql


def nested_score_dict_iter(a, join_type='top'):
    """

    Iterates through nested dictionary and adds
    elements to global out_list defined outside of function
    Used to build an initial list for the Universe portion of the query
    list is mostly functional at this point, but undergoes another step to fix
    some errors

    Args:
        a (dict): MongoDB dicitonary from react-awesome-query-tool
        join_type (string): Conjuction as defined from query tool for element
        *out_list* (global list): Empty global list defined outside of Function
            Global as couldn't figure out how to return result otherwise in iterative
            functon

    Returns:
        Nothing directly, but build the global out_list defined

    """
    if '$and' in a.keys():
        out_list.append('(')
        for b in a['$and']:
            nested_score_dict_iter(b, '+')
        out_list.append(')')
    elif '$or' in a.keys():
        out_list.append('ARRAY_MAX(ARRAY [')
        for b in a['$or']:
            nested_score_dict_iter(b, ',')
        out_list.append(')')
    else:
        out_list.append(a)
        out_list.append(join_type)
        print(list(a.keys())[0])
        print(join_type)


def create_transact_score(a):
    """

    Takes a propensity selection from react-awesome-query-tool with subquery rules
    and creates sql to produce ranked list of customers using that score,

    Args:
        a: MongoDB dicitonary from propensity element of react-awesome-query-tool

    Returns:
        string: sql to produce ranked list of customers using that score

    Raises:
        InvalidQuery: If query conditions are not met.

    """
    score_time_period = get_time_period(a)
    channels = get_channels(a)
    importance = get_importance(a)
    products = get_products(a)
    products = [int(x.replace("'", "")) for x in products]
    metric = 'trans_demand'
    new_classes_channel = []
    for channel in channels:
        new_classes_channel = new_classes_channel + \
            [f'"ml_trans"."{channel}_y_{score_time_period}_{metric}" *  "ml_product"."{x}"' for x in products]
    new_classes_channel_string = f'( {importance} * rank() OVER (partition by 1 order by ({" + ".join(new_classes_channel)}) DESC))'
    return new_classes_channel_string


def create_churn_score(a):
    """

    Takes a churn score selection selection from react-awesome-query-tool with subquery rules
    and creates sql to produce ranked list of customers using that score,

    Args:
        a: MongoDB dicitonary from churn element of react-awesome-query-tool

    Returns:
        string: sql to produce ranked list of customers using that score

    Raises:
        InvalidQuery: If query conditions are not met.

    """
    channels = get_channels(a)
    importance = get_importance(a)
    churn_channel = []
    for channel in channels:
        churn_channel.append(f'ml_trans."{channel}_y_0_365_trans"')
    churn_string = ' + '.join(churn_channel)
    if a['$elemMatch']['Churn Risk'] == 'high':
        order = 'ASC'
    else:
        order = 'DESC'
    churn_rank_string = f'( {importance} * rank() OVER (partition by 1 order by ({churn_string}) {order}))'
    return churn_rank_string


def create_clv_score(a):
    """

    Takes a clv score selection selection from react-awesome-query-tool with subquery rules
    and creates sql to produce ranked list of customers using that score,

    Args:
        a: MongoDB dicitonary from clv element of react-awesome-query-tool

    Returns:
        string: sql to produce ranked list of customers using that score

    Raises:
        InvalidQuery: If query conditions are not met.

    """
    channels = get_channels(a)
    importance = get_importance(a)
    clv_channel = []
    for channel in channels:
        clv_channel.append(f'ml_trans."{channel}_y_0_365_trans_demand"')
    clv_string = ' + '.join(clv_channel)
    if a['$elemMatch']['CLV'] == 'low':
        order = 'ASC'
    else:
        order = 'DESC'
    clv_rank_string = f'( {importance} * rank() OVER (partition by 1 order by ({clv_string}) {order}))'
    return clv_rank_string


def score_list_to_sql(out_list):
    """

    Converts list of order by score elements into sql order by

    Args:
        out_list (list): List of score order by sql snippets and conjuctions

    Returns:
        score_string (string): order by clause of scoring variables

    """
    score_string = ' '.join(out_list)
    score_string
    while score_string.find('(ARRAY') > -1:
        array_loc = score_string.find('(ARRAY')
        score_string = score_string.replace('(ARRAY', '(A**AY', 1)
        p_loc = find_parentheses(score_string)
        score_string = score_string[:p_loc[array_loc]] + \
            '])' + score_string[p_loc[array_loc] + 1:]
    score_string = score_string.replace('(A**AY', '(ARRAY')
    return score_string


def find_parentheses(s):
    """ Find and return the location of the matching parentheses pairs in s.

    Given a string, s, return a dictionary of start: end pairs giving the
    indexes of the matching parentheses in s. Suitable exceptions are
    raised if s contains unbalanced parentheses.

    """

    stack = []
    parentheses_locs = {}
    for i, c in enumerate(s):
        if c == '(':
            stack.append(i)
        elif c == ')':
            try:
                parentheses_locs[stack.pop()] = i
            except IndexError:
                raise IndexError('Too many close parentheses at index {}'
                                 .format(i))
    if stack:
        raise IndexError('No matching close parenthesis to open parenthesis '
                         'at index {}'.format(stack.pop()))
    return parentheses_locs


def get_channels(a):
    """

    Takes a Channel selection using "in" operator and converts to list,
    if not found returns all available options as default

    Args:
        a: MongoDB dicitonary from channel element of react-awesome-query-tool

    Returns:
        list: Channels

    """
    try:
        result = a['$elemMatch']['Channel']['$in']
    except Exception as e:
        print('No Channel found, defaulting to all')
        result = ['Retail', 'Direct', 'Outlet']
    return result


def get_importance(a):
    """

    Takes an Importance selection from react-awesome-query-tool
    using "equal" (blank) operator and returns value,
    if not found returns default importance

    Args:
        a: MongoDB dicitonary from importance element of react-awesome-query-tool

    Returns:
        integer: Importance

    """
    try:
        result = a['$elemMatch']['Importance']
    except Exception as e:
        print('No Importance found, defaulting to 3')
        result = 3
    return result


def get_products(a):
    """

    Takes a Product selection from react-awesome-query-tool and returns value,
    if not found returns defaults to all products

    Args:
        a: MongoDB dicitonary from product element of react-awesome-query-tool

    Returns:
        list: Products

    """
    try:
        b = a['$elemMatch']['Product']
        result = [x.split('-')[-1] for x in b]
    except Exception as e:
        print('No Product found, defaulting to all')
        result = (['1', '2', '3', '5', '6', '7', '8', '9', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61',
                   '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '96', '97', '100', '101', '103', '104', '110', '113', '114', '115', '116', '117', '131', '132', '133', '135', '136', '138', '139', '140', '141', '192', '193', '194', '195'])
    return result


def get_time_period(a):
    """

    Takes a Time Period selection from react-awesome-query-tool and calls score_day_range
    method to convert into usable underscored string a model will be name with,

    Args:
        a: MongoDB dicitonary from time period element of react-awesome-query-tool

    Returns:
        string: Underscored date range

    Raises:
        InvalidQuery: Propensity calc requires a time period.

    """
    try:
        time_period = a['$elemMatch']['Days Ahead']
        print(time_period)
        score_time_period = score_day_range(time_period)

    except Exception as e:
        print('No Time Period Found for Propensity.  Time period is required')

        raise InvalidQuery(
            'No Time Period Found for Propensity.  Time period is required')

    return score_time_period


def score_day_range(item):
    """

    Converts a date range from react-awesome-query-tool MongoDB output
    to an underscored date range that can be built into a string of a named model

    Args:
        item: MongoDB dicitonary from date range element of react-awesome-query-tool

    Returns:
        string: Underscored date range

    """
    start_delta = item['$gte']
    end_delta = item['$lte']
    start_day = min([0, 30], key=lambda x: abs(x - start_delta))
    end_day = min([30, 60, 90, 120, 150], key=lambda x: abs(x - end_delta))
    if start_day == end_day:
        end_day = end_day + 30
    out_string = f'{start_day}_{end_day}'
    if out_string == '0_150':
        out_string = '0_120'
    return out_string


def create_control_size_sql(universe_sql, score_sql, limit_size, start_date, end_date):
    """

    Combines Universe and ML sql into one statement,
    calculates vars needed for control size estimation

    Args:
        universe_sql (string): Universe SQL statement
        score_sql (string): Score SQL statement order by statement
        limit_size (int): total number of customers requested to be returned
        start_date (string): User inputted date of start of expected measurement
        end_date (string): User inputted date of end of expected measurement

    Returns:
        result (string): SQL of Universe and ML limited by size

    """
    # ADD demand to universe sql
    if len(score_sql) > 1:
        order_by_score_sql = " ORDER BY " + score_sql + " ASC "
    else:
        order_by_score_sql = ""
    control_time_period = control_date_range(start_date, end_date)
    select_add = f', "ml_trans"."all_y_{control_time_period}_trans_demand" as trans_demand '
    original_from = 'FROM "ml"."eddiebauer_prod_product_scores" ml_product'
    universe_sql_demand = universe_sql.replace(
        original_from, select_add + original_from)
    result = f"""SELECT SUM(trans_demand) / 100 / {limit_size} as conversion, SUM(trans_demand) as demand, count(*) as audience_size   FROM ({universe_sql_demand} {order_by_score_sql} LIMIT {limit_size}) a"""
    return result


def control_date_range(start_date, end_date):
    """

    Converts a date range from html form output
    to an underscored date range that can be built into a string of a named model

    Args:
        start_date (string): User inputted date of start of expected measurement
        end_date (string): User inputted date of end of expected measurement

    Returns:
        string: Underscored date range

    """
    start_date = datetime.strptime(start_date, '%m/%d/%Y')
    end_date = datetime.strptime(end_date, '%m/%d/%Y')
    today_date = datetime.now()
    start_delta = (start_date - today_date).days
    end_delta = (end_date - today_date).days
    start_day = min([0, 30], key=lambda x: abs(x - start_delta))
    end_day = min([30, 60, 90, 120, 150], key=lambda x: abs(x - end_delta))
    if start_day == end_day:
        end_day = end_day + 30
    out_string = f'{start_day}_{end_day}'
    if out_string == '0_150':
        out_string = '0_120'
    return out_string


def validate_sql(token, d):
    if token[:6] == 'Bearer':
        token = token.split()[1]
    print('@@@@@@@@@@@@Validation@@@@@@@@@@@@')
    validation = requests.post(f'{os.environ["stage_url"]}/audience_universe/validate', headers={
                               'Authorization': f'Bearer {token}'}, json=d).json()
    print(validation)

    return validation


def get_current_status(d):
    """
    Returns current status text
    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')

    try:
        response = table.get_item(
            Key={
                'id': d['id'], 'asset': d['bus'] + '#audience#info'
            }
        )
        item = json.loads(json.dumps(response, indent=4,
                                     cls=DecimalEncoder))['Item']
        print('Found', d['id'], 'Not creating new ID')

        return True, item['status'], item['status_text'], item['actual_audience_size']
    except Exception as e:

        return False, '', '', 'Not Created'


def modify_status(found, status, status_text, item):
    if found:
        status = 'Saved'
    elif not found:
        status = 'Saved'
        status_text = 'Saved'

    if item['create_version']:
        print('Create on Save was yes')
        status_text = 'Creating'
        status = 'Creating'

    return status, status_text


def getCorsHeader():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    }

    return headers


def get_pk(token, id):
    bus = get_business(token)

    return f'{bus}|{id}'
