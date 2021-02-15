from datetime import datetime, timedelta
from src.shared.util import get_all_records_asset, DecimalEncoder
from src.forecast.forecast import get_data
from src.forecast.forecast import list_forecast
import json
import boto3
import base64
import os


def email_title(bus):
    title = f'Notus Marketing Spend Forecast for {bus}'
    return title


def spend_title(c_date, region, day_0_spend):
    if region == 'all':
        region = ''
    else:
        region = region.capitalize() + ' Region '
    title = region + 'Spend for ' + \
        c_date.strftime('%A') + ': $' + '{:,}'.format(int(day_0_spend))

    return title


def template_html():
    template = """{
      type: 'bar',
      data: {
        labels: [***date_labels***],
        datasets: [{
          label: 'Forecast',
          backgroundColor: 'rgba(9, 7, 171, 0.2)',
          borderColor: 'rgba(9, 7, 171, 1)',
          borderWidth: 1,
          data: [***spend***]
        }]
      },
      options: {
        title: {
          display: false,
          text: '10-Day Temperature Forecast',
          fontColor: 'black',
          fontSize: 24,
        },
        scales: {
          xAxes: [{stacked: true}],
          yAxes: [{
            stacked: true,
            ticks: {
              callback: function(value) {
                return "$" + value + "k";
              }
            }
          }],
        },
        legend: {
          position: 'bottom',
          display: false,
        },
        plugins: {
          datalabels: {
            display: true,
    		font: {
              style: 'bold'
            },
          },
        },
      },
    }"""

    return template


def unix_to_datetime(a):
    d = []
    for b in a:
        d.append(datetime.utcfromtimestamp(int(b / 1000)))

    return d


def url_to_html_barchart(bar_chart_url_1, name, cur_spend, destination):
    html = f"""<tr style="margin-top:30px">
      <td width="600" align="center" bgcolor="#FFFFFF" colspan="2" style="padding-top:25px;Margin:0;">
         <p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:24px;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;line-height:30px;font-weight: bold;color:#111111;">{destination.capitalize()}&nbsp;</p>
         <p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:24px;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;line-height:30px;color:#111111;">{name}&nbsp;</p>
         <p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:20px;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;line-height:30px;color:#111111;">Tomorrows budget: ${cur_spend}&nbsp;</p>
      </td>
    </tr>
    <tr style="border-collapse:collapse;">
      <td width="600" align="center" colspan="2" style="padding:0;Margin:0;padding-top:5px;padding-bottom:25px;"><img class="adapt-img" src="{bar_chart_url_1}" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;" width="600" height="400"></td>
    </tr>"""

    return html


def make_bar_chart(data):
    local_date = data['forecast_date']
    dates_quote = ["'" + x + "'" for x in local_date]
    local_date_string = ','.join(dates_quote)

    spend_k = data['capped_spend']
    spend = ['%.1f' % (x / 1000) for x in spend_k]
    spend_string = ','.join(spend)
    template = template_html()
    template = template.replace('***spend***', spend_string)
    template = template.replace('***date_labels***', local_date_string)
    template_encoded = str(base64.b64encode(template.encode("utf-8")), "utf-8")

    url = 'https://quickchart.io/chart?width=600&height=400&encoding=base64&c=' + template_encoded
    print(url)

    return url


def get_campaigns():
    # TODO: get campaigns using campaign endpoint.
    bus = 'eddiebauer'
    asset = asset = bus + '#' + 'spend_rules'
    items = get_all_records_asset(asset)
    return items


def get_current_spend(campaign_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('assets')
    asset = 'current_spend'
    response = table.get_item(
        Key={
            'id': campaign_id, 'asset': asset
        }
    )
    item = json.loads(json.dumps(response, cls=DecimalEncoder))['Item']

    print("item-->", item)

    return item['spend']

def run(event, context):
    print('*****invoked email service cron function.*****')
    # TODO: get email list from dynamodb, tbl_name: dev_assets
    email_list = [
        'chris@notus.ai',
    ]

    c_date = datetime.today().date() - timedelta(hours=7) + timedelta(days=1)

    print('System DateTime: ', datetime.today())
    print('PST DateTime: ', datetime.today() - timedelta(hours=7))
    print('System Date: ', datetime.today().date())
    print('Email Date: ', c_date)

    # TODO: need to discuss the param
    params = {
        'campaign_id': 'XXXcampaign_id',
        'channel': 'XXXchannel',
        'region': 'east',
        'bus': 'eddiebauer',
        'bar': 'XXXbar',
        'name': 'XXXname'
    }

    TemplateData = {}

    TemplateData['subject'] = email_title(params['bus'])

    campaigns = get_campaigns()
    print("<----campaigns----->", campaigns)

    html = ''

    for campaign in campaigns:
        fx_json = list_forecast({'body': json.dumps(campaign)}, {})
        cur_spend = '%.0f' % get_current_spend(campaign['id'])
        html = html + url_to_html_barchart(make_bar_chart(json.loads(fx_json['body'])['forecast']), campaign['name'], cur_spend, campaign['destination'])

    TemplateData['bar_chart_html_1'] = html

    print(json.dumps(TemplateData, indent=4))

    sesclient = boto3.client('ses')

    try:
        response = sesclient.send_templated_email(
            Source='chris@notus.ai',
            Destination={'ToAddresses': email_list},
            ReplyToAddresses=['chris@notus.ai'],
            Template='forecast_email_template',
            TemplateData=json.dumps(TemplateData)
        )

        print ('email sent response', response)

    except Exception as e:
        print(e)

    else:
        print('Email sent! Message ID:')
        print(response['MessageId'])

if __name__ == "__main__":
    os.environ['stage'] = 'prod'
    run({}, {})
# import sys
# sys.path.append("/Users/chrismorin/notus_code/wx-api")
