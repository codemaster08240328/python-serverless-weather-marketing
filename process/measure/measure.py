import boto3
import time
from math import sqrt
import numpy as np
import scipy.stats as t
import pandas as pd
import json
import decimal
import io
import sys


def recap_selects(d):
    selects = []
    groupby = []
    i = 0
    for a in d:
        i = i + 1
        if a['dimension'] == 'superset':
            selects.append(f"'All' as dimension_{i}")
        else:
            selects.append(f'{a["dimension"]}.{a["slice"]} as dimension_{i}')
            groupby.append(f'{a["dimension"]}.{a["slice"]}')
    if len(selects) > 0:
        selects_string = ','.join(selects) + ','
    else:
        selects_string = ''
    if len(groupby) > 0:
        groupby_string = ','.join(groupby) + ','
    else:
        groupby_string = ''
    return selects_string, groupby_string


def get_level_subset(d, i):
    a = d[:i] + [{'dimension': 'superset'}] * (len(d) - i)
    return a


def get_recap_df(event):
    sql_list = []
    for i in range(len(event['breakouts']) + 1):
        d_sub = get_level_subset(event['breakouts'], i)
        selects_string, groupby_string = recap_selects(d_sub)
        sql_list.append(f""" SELECT
        {selects_string}
        audience.customer_id,
        audience.test_group,
        sum(coalesce(demand,0)) AS Demand,
        sum(coalesce(units,0)) AS Units,
        sum(coalesce(cogs,0)) AS Cogs,
        count(DISTINCT order_id) AS Transactions,
        count(DISTINCT case when cert_amount > 0 then order_id end) AS "Cert Redemptions"
        FROM "audience"."eddiebauer_prod_audience_versions" audience
        LEFT JOIN "source"."eddiebauer_prod_order_line_enhanced" transactions
            ON audience.customer_id = transactions.customer_id
            AND  transactions.date > CAST('{event['start_date']} 00:00:00.000' AS TIMESTAMP)
            AND transactions.date != CAST('{event['end_date']} 00:00:00.000' AS TIMESTAMP)
        LEFT JOIN "source"."eddiebauer_prod_product" product
            ON transactions.product_id = concat(cast(product.departmentid as varchar(5)), '-',cast(product.styleid as varchar(5)))
        LEFT JOIN "source"."eddiebauer_prod_customer_attribute" customer
            ON customer.customer_id = audience.customer_id
        WHERE audience.id = '{event['audience_id']}'
                AND audience.customer_id != 'L000000000'
        GROUP BY  {groupby_string} audience.test_group, audience.customer_id """)
    unioned_sql = ' UNION ALL '.join(sql_list)
    qa = QueryAthena(query=unioned_sql, database='source')
    df = qa.run_query()
    return df


class QueryAthena:

    def __init__(self, query, database):
        self.database = database
        self.folder = 'recap_results/'
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


def independent_ttest(data1, data2, alpha, len1, len2, conversion=False):
    # calculate means
    mean1, mean2 = np.mean(data1), np.mean(data2)
    # calculate standard errors
    std1, std2 = np.std(data1, ddof=1), np.std(data2, ddof=1)
    if conversion:
        se1, se2 = np.sqrt(mean1 * (1 - mean1)) / \
            np.sqrt(len1), np.sqrt(mean2 * (1 - mean2)) / np.sqrt(len2)
    else:
        se1, se2 = std1 / np.sqrt(len1), std2 / np.sqrt(len2)
    # standard error on the difference between the samples
    sed = sqrt(se1**2.0 + se2**2.0)
    # calculate the t statistic
    t_stat = (mean1 - mean2) / sed
    # degrees of freedom
    df = len(data1) + len(data2) - 2
    # calculate the critical value
    cv = t.norm.ppf(1.0 - alpha, df)
    # calculate the p-value
    p = (1.0 - t.norm.cdf(abs(t_stat), df)) * 2.0
    # return everything
    return t_stat, df, cv, p, mean1, mean2, len1, len2


def fill_zeros(short_array, long_length):
    a = list(short_array) + list(np.zeros(long_length - len(short_array)))
    return a


def signifigance(p):
    if p <= .05:
        answer = 'Yes'
    else:
        answer = 'No'
    return answer


def as_currency(amount):
    if amount >= 0:
        return '${:,.2f}'.format(amount)
    else:
        return '-${:,.2f}'.format(-amount)


def format_results(results, a):
    results['lift_percent'] = '{:.1%}'.format(results['lift_percent'])
    if a in ['Demand', 'Cogs']:
        results['lift'] = as_currency(results['lift'])
        results['test_per_customer'] = as_currency(
            results['test_per_customer'])
        results['control_per_customer'] = as_currency(
            results['control_per_customer'])
    elif a in ['Conversion Rate', 'Cert Redemption Rate']:
        results['lift'] = '{:.1%}'.format(results['lift'])
        results['test_per_customer'] = '{:.1%}'.format(
            results['test_per_customer'])
        results['control_per_customer'] = '{:.1%}'.format(
            results['control_per_customer'])
    else:
        results['lift'] = '{:.0f}'.format(results['lift'])
        results['test_per_customer'] = '{:.2f}'.format(
            results['test_per_customer'])
        results['control_per_customer'] = '{:.2f}'.format(
            results['control_per_customer'])
    return results


def metric_dict(df, a, test_count, holdout_count, conversion=False):
    test_values = fill_zeros(df[df.test_group == 'test'][a].values, test_count)
    holdout_values = fill_zeros(
        df[df.test_group == 'holdout'][a].values, holdout_count)
    # p_value = scipy.stats.ttest_ind(df[df.test_group == 'test'][a], df[df.test_group == 'holdout'][a], equal_var=False).pvalue
    t_stat, dof, cv, p_value, test_mean, holdout_mean, test_customers, holdout_customers = independent_ttest(
        data1=test_values, data2=holdout_values, alpha=.05, len1=test_count, len2=holdout_count, conversion=conversion)
    print(test_mean, 'metric mean test', a, 'p-value', p_value,
          'lift', (test_mean - holdout_mean) / test_mean)
    results = {}
    results['lift_percent'] = float((test_mean - holdout_mean) / test_mean)
    results['signifigance'] = signifigance(p_value)
    if a.find('Rate') > -1:
        results['lift'] = decimal.Decimal(test_mean - holdout_mean)
    else:
        results['lift'] = decimal.Decimal(df[df.test_group == 'test'][a].sum(
        ) - df[df.test_group == 'test'][a].sum() / ((test_mean - holdout_mean) / test_mean + 1))
    results['test_per_customer'] = decimal.Decimal(test_mean)
    results['control_per_customer'] = decimal.Decimal(holdout_mean)
    results = format_results(results, a)
    return results


def escalate_id(r_id):
    r_id_list = r_id.split(' | ')
    if len(r_id_list) > 1:
        if r_id.find('All') == -1:
            r_id_list = r_id_list[:-1]
        else:
            for i in range(1, len(r_id_list)):
                if r_id_list[i] == 'All':
                    r_id_list[i - 1] = 'All'
                    break
        parent_id = ' | '.join(r_id_list)
    else:
        parent_id = 'All'
    return parent_id


def loop_metrics(df_slice, dimensions, metrics, test_count, holdout_count):
    results = []
    for a in metrics:
        if df_slice[a].sum() > 0:
            if a in ['Conversion Rate', 'Cert Redemption Rate']:
                results_dict = metric_dict(
                    df_slice, a, test_count, holdout_count, conversion=True)
            else:
                results_dict = metric_dict(
                    df_slice, a, test_count, holdout_count)
            if len(dimensions) > 0:
                result_id = a + ' | ' + \
                    ' | '.join(list(df_slice[dimensions].max().values))
            else:
                result_id = a
            results_dict['ID'] = result_id.replace(' | All', '')
            results_dict['Parent_ID'] = escalate_id(
                result_id).replace(' | All', '')
            results.append(results_dict)
    return results


def return_results(result_id, result):
    """

    Returns result to DynamoDB with given field
    Updates status field

    Args:
        result_id (string): unique identifier

    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(stage + '-sql-result')
    new_item = {
        'id': result_id,
        'result': result,
        'status': 'Complete'
    }
    response = table.put_item(Item=json.loads(
        json.dumps(new_item), parse_float=decimal.Decimal))
    return response


def make_dimensions(d):
    dimensions = []
    for i in range(len(d)):
        dimensions.append(f'dimension_{i + 1}')
    return dimensions


def get_payload(d_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(stage + '-sql-result')
    response = table.get_item(
        Key={
            'id': d_id
        }
    )
    payload = response['Item']['payload']
    return payload


d_id =  sys.argv[1] #'ff9f01c3-1b57-420f-866d-3911a9125c86' #
stage =  sys.argv[2] #'dev' #
# payload = {'end_date': "2020-09-29",
# 'audience_id': "efb566ab084c48b0a293#2020-09-09T17:57:17Z",
# 'breakouts': [],
# 'end_date': "2020-09-29",
# 'id': "bdf9e719-a9d2-434a-a533-9d5d37af5e44",
# 'start_date': "2020-09-01"}
print('Running', d_id, 'in', stage)
payload = get_payload(d_id)
dimensions = make_dimensions(payload['breakouts'])
print(dimensions)
t_now = time.time()
df = get_recap_df(payload)
print('DF made in', time.time() - t_now)
t_now = time.time()
df.loc[df.Transactions > 0, 'Conversion Rate'] = 1
df['Conversion Rate'].fillna(0, inplace=True)
df.loc[df['Cert Redemptions'] > 0, 'Cert Redemption Rate'] = 1
df['Cert Redemption Rate'].fillna(0, inplace=True)
metrics = ['Demand', 'Units', 'Cogs', 'Transactions',
           'Conversion Rate', 'Cert Redemption Rate']
test_count = len(df[df.test_group == 'test']['customer_id'].unique())
holdout_count = len(df[df.test_group == 'holdout']['customer_id'].unique())
results = []
for a in dimensions:
    df[a].fillna('None', inplace=True)
df.fillna(0, inplace=True)
if len(dimensions) > 0:
    df_slices = df.groupby(dimensions)
else:
    df_slices = [(1, df)]
for r, df_slice in df_slices:
    name = ' | '.join(list(df_slice[dimensions].max().values))
    print('Running', name)
    results.extend(loop_metrics(df_slice, dimensions,
                                metrics, test_count, holdout_count))
print('Recap made in', time.time() - t_now)
response = return_results(payload['id'], results)
print(response)
