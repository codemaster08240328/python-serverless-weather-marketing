from src.cron.QueryAthena import QueryAthena
import pandas as pd
import boto3
import json
import decimal
import os


def update_result(country, ml_key, results):
    """

    Updates result to DynamoDB with given field
    Updates status field

    Args:
        ml_key (string): sort key

    """
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    stage = os.environ['stage']
    table = dynamodb.Table('assets')
    new_item = {
        'id': f'eddiebauer#wi#10_day#{country}',
        'asset': ml_key,
        'results': results
    }
    response = table.put_item(Item=json.loads(
        json.dumps(new_item), parse_float=decimal.Decimal))

    return response


def run(event, context):
    SQL = ("""SELECT ml_key,
         lower(country) as country,
         local_date,
         sum(score * population) / sum(population) + 1 AS lift
FROM "bus"."eb_ml_scores_h3" a
JOIN
    (SELECT h3_4,
         sum(population) AS population,
         country
    FROM "bus"."eb_population" p
    JOIN
        (SELECT loc_indice,
         max(h3_4) AS h3_4,
         max(zip_country) AS country
        FROM "wx"."geo"
        GROUP BY  loc_indice) g
            ON p.loc_indice = g.loc_indice
        GROUP BY  h3_4, country) b
        ON a.h3_4 = b.h3_4
WHERE local_date > current_date
        AND local_date < date_add('day', 10, current_date)
GROUP BY  ml_key, local_date, country
UNION ALL
SELECT ml_key,
'us_ca' as country,
     local_date,
     sum(score * population) / sum(population) + 1 AS lift
FROM "bus"."eb_ml_scores_h3" a
JOIN
    (SELECT h3_4,
         sum(population) AS population,
         country
    FROM "bus"."eb_population" p
    JOIN
        (SELECT loc_indice,
         max(h3_4) AS h3_4,
         max(zip_country) AS country
        FROM "wx"."geo"
        GROUP BY  loc_indice) g
            ON p.loc_indice = g.loc_indice
        GROUP BY  h3_4, country) b
        ON a.h3_4 = b.h3_4
WHERE local_date > current_date
        AND local_date < date_add('day', 10, current_date)
GROUP BY  ml_key, local_date""")

    print('*****invoked forecast cron function.*****')
    qa = QueryAthena(query=SQL, database='bus')
    df = qa.run_query()
    df_group = df.groupby(['country', 'ml_key'])

    for index, df_s_group in df_group:
        results = list(df_s_group.T.to_dict().values())

        for item in results:
            del item['ml_key']

        print('>>> results for dynamodb')
        print(results)

        update_result(country=index[0], ml_key=index[1], results=results)

    print('*****forecast cron function ends. will invoked an hour later.*****')


if __name__ == "__main__":
    os.environ['stage'] = 'dev'
    run({},{})
