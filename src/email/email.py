import pandas as pd
import boto3
from datetime import datetime, timedelta
import base64
from pyathena import connect
from pyathena.pandas_cursor import PandasCursor
import json
import os
from make_weather_grid import make_city_html
from jinja2 import Template
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def athena_to_pandas(SQL, file=False):
    """Takes SQL, runs it on Athena and creates a PD dataframe from it"""
    print('Running/Downloading Athena Query')
    if file:
        with open(SQL, 'r') as f:
            SQL = f.read()
    cursor = connect(s3_staging_dir='s3://aws-athena-query-results-453299555282-us-east-1',
                     region_name='us-east-1',
                     cursor_class=PandasCursor).cursor()
    df = cursor.execute(SQL).as_pandas()
    print('Query Complete')
    return df


def format_values_pos(x):
    if x > 0:
            t = "'+" + str('%.1f' % x) + "'"
    else:
        t = ''
    return t


def format_values_neg(x):
    if x > 0:
            t = ''
    else:
        t = "'" + str('%.1f' % x) + "'"
    return t


def template_html():
    template = """{
      type: 'bar',
      data: {
        labels: [***date_labels***],
        datasets: [{
          label: 'Colder',
          backgroundColor: 'rgba(9, 7, 171, 0.2)',
          borderColor: 'rgba(9, 7, 171, 1)',
          borderWidth: 1,
          data: [***neg_data***]
        }, {
          label: 'Warmer',
          backgroundColor: 'rgba(171, 7, 9, 0.2)',
          borderColor: 'rgba(171, 7, 9, 1)',
          borderWidth: 1,
          data: [***pos_data***]
        }]
      },
      options: {
        title: {
          display: false,
          text: '10-Day Temperature Forecast',
          fontColor: 'black',
          fontSize: 24,
        },
        legend: {
          position: 'bottom',
        },
        scales: {
          xAxes: [{stacked: true}],
          yAxes: [{
            stacked: true,
            ticks: {
              callback: function(value) {
                return value < 0 ? value + "F": "+" + value + "F";
              }
            }
          }],
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


def make_bar_chart(df, var):
    date_list = df.local_date.dt.strftime('%a %m/%d').values
    dates_quote = ["'" + x + "'" for x in date_list]
    dates_string = ','.join(dates_quote)
    pos_data = df[var].apply(format_values_pos).values
    neg_data = df[var].apply(format_values_neg).values
    pos_data_string = ','.join(pos_data)
    neg_data_string = ','.join(neg_data)
    template = template_html()
    template = template.replace('***pos_data***', pos_data_string)
    template = template.replace('***neg_data***', neg_data_string)
    template = template.replace('***date_labels***', dates_string)
    template_encoded = str(base64.b64encode(template.encode("utf-8")), "utf-8")
    url = 'https://quickchart.io/chart?width=600&height=400&encoding=base64&c=' + template_encoded
    return url


def email_df(current_date, days, region):
    start_date = current_date.strftime('%Y-%m-%d')
    end_date = (current_date + timedelta(days=days)).strftime('%Y-%m-%d')
    if region == 'west':
        wc = "and zip_state in ('AK', 'AR', 'AZ', 'CA', 'CO', 'IA', 'ID', 'IL', 'Il', 'IN', 'KS'\
        , 'MI', 'MN', 'MO', 'MT', 'ND', 'NE', 'NM', 'NV', 'OK', 'OR', 'SD', 'TX', 'UT', 'WA', 'WI', 'WY')"
    elif region == 'east':
        wc = "and zip_state not in ('AK', 'AR', 'AZ', 'CA', 'CO', 'IA', 'ID', 'IL', 'Il', 'IN', 'KS'\
        , 'MI', 'MN', 'MO', 'MT', 'ND', 'NE', 'NM', 'NV', 'OK', 'OR', 'SD', 'TX', 'UT', 'WA', 'WI', 'WY')"
    else:
        wc = ""
    SQL = """Select local_date_part as local_date,
     sum(maximum_temperature_ly*demand)/sum(demand) as maximum_temperature_ly,
     sum(maximum_temperature_mean*demand)/sum(demand) as maximum_temperature_mean,
     sum(maximum_temperature*demand)/sum(demand) as maximum_temperature
     from wx.gfs_enhanced a
     join bus.eb_population b
     on a.loc_indice = b.loc_indice
     where local_date_part >= '{start_date}'
     and local_date_part <= '{end_date}'
     {region_clause}
     group by local_date_part order by local_date asc""".format(start_date=start_date, end_date=end_date, region_clause=wc)
    df = athena_to_pandas(SQL)
    df.local_date = pd.to_datetime(df.local_date)
    return df


def df_val(df, date, var, sign=False):
    val = df[df.local_date.dt.date == date][var].values[0]
    if (val > 0) & sign:
        s = '+%.1f' % val
    else:
        s = '%i' % val
    return s


def metric_to_english(df):
    for a in df.columns.values:
        if a.find('temperature') > -1:
            if (a.find('_mean') > -1) | (a.find('_ly') > -1):
                df[a] = df[a] * 9 / 5
            else:
                df[a] = (df[a] - 273.15) * 9 / 5 + 32
        if a.find('precip') > -1:
            df[a] = df[a] / 25.4
        if a.find('snow') > -1:
            df[a] = df[a] * 10
    return df


def temp_bg(val):
    if float(val) > 0:
        # c = 'background-image: linear-gradient(to top left, #660000, red)'
        c = 'background-color: #B61C1C'
    else:
        # c = 'background-image: linear-gradient(to top left, #00004d, blue)'
        c = 'background-color: #231CB6'
    return c


def add_map_links(c_date, dict, region):
    map_url = 'https://site-obs.s3.amazonaws.com/img/maps/'
    dict['map_day_t_0'] = map_url + c_date.strftime('%Y-%m-%d') + '_maximum_temperature.jpg'
    dict['map_day_t_0_title'] = 'Max Temperature on ' + c_date.strftime('%A, %b %d')
    if region == 'all':
        region = ''
    else:
        region = '_' + region
    img_name_ly = '_maximum_temperature_ly{}.jpg'.format(region)
    img_name_mean = '_maximum_temperature_mean{}.jpg'.format(region)
    img_name = '_maximum_temperature{}.jpg'.format(region)
    for i in range(6):
        m_date = c_date + timedelta(days=i)
        dict['map_day_t_{}'.format(i)] = map_url + m_date.strftime('%Y-%m-%d') + img_name
        dict['map_day_t_{}_title'.format(i)] = 'Max Temperature for ' + m_date.strftime('%A, %b %d')
        dict['map_day_t_ly_{}'.format(i)] = map_url + m_date.strftime('%Y-%m-%d') + img_name_ly
        dict['map_day_t_ly_{}_title'.format(i)] = 'Temperature vs LY for ' + m_date.strftime('%A, %b %d')
        dict['map_day_t_both_{}_title'.format(i)] = 'Temperature Comparison Maps for ' + m_date.strftime('%A, %b %d')
        dict['map_day_t_mean_{}'.format(i)] = map_url + m_date.strftime('%Y-%m-%d') + img_name_mean
        dict['map_day_t_mean_{}_title'.format(i)] = 'Temperature vs Normal for ' + m_date.strftime('%A, %b %d')

    dict['map_t_next_7'.format(i)] = map_url + c_date.strftime('%Y-%m-%d') + '_maximum_temperature_f7{}.jpg'.format(region)
    dict['map_t_ly_next_7'.format(i)] = map_url + c_date.strftime('%Y-%m-%d') + '_maximum_temperature_f7_ly{}.jpg'.format(region)
    dict['map_t_mean_next_7'.format(i)] = map_url + c_date.strftime('%Y-%m-%d') + '_maximum_temperature_f7_mean{}.jpg'.format(region)
    dict['map_t_next_7_title'.format(i)] = 'Temperature Next 7 Days'
    dict['map_t_ly_next_7_title'.format(i)] = 'Temperature vs LY next 7 days'
    dict['map_t_ly_last_7'.format(i)] = map_url + c_date.strftime('%Y-%m-%d') + '_maximum_temperature_p7_ly{}.jpg'.format(region)
    dict['map_t_mean_last_7'.format(i)] = map_url + c_date.strftime('%Y-%m-%d') + '_maximum_temperature_p7_mean{}.jpg'.format(region)
    dict['map_t_ly_last_7_title'.format(i)] = 'Temperature vs LY last 7 days'
    dict['map_t_last_7'.format(i)] = map_url + c_date.strftime('%Y-%m-%d') + '_maximum_temperature_p7{}.jpg'.format(region)
    dict['map_t_last_7_title'.format(i)] = 'Temperature Last 7 Days'
    dict['map_t_both_next_7_title'.format(i)] = 'Temperature Map for Next 7 days'
    dict['map_t_both_last_7_title'.format(i)] = 'Temperature Map for Last 7 days'
    dict['map_t_ly_last_7_title'.format(i)] = 'Temperature vs LY last 7 days'
    dict['map_t_ly_sales_last_7_title'] = 'Sales vs LY last 7 days'
    dict['map_t_ly_sales_last_7'] = 'https://site-obs.s3.amazonaws.com/img/maps/'
    return dict


def download_email_list_csv(path):
    print('Downloading Email File')
    s3 = boto3.client('s3')
    s3.download_file('wx-params', path, '/tmp/email.csv')
    print('File downloaded')


def download_sales_map(region):
    print('Downloading Sales Map')
    s3 = boto3.client('s3')
    print('/eb/maps/sales_past_7_{}.jpg'.format(region))
    s3.download_file('bus-files', 'eb/maps/sales_past_7_{}.jpg'.format(region), '/tmp/sales_past_7.jpg')
    print('File downloaded')



def email_title(c_date, region):
    if region == 'all':
        region = ''
    else:
        region = region.capitalize() + ' Region '
    title = region + 'Notus Temperature Forecast for ' + c_date.strftime('%A, %b %d')
    return title


def img_width_height(region, size):
    if size == 1:
        if region == 'all':
            width = 600
            height = 395
        elif region == 'west':
            width = 600
            height = 527
        elif region == 'east':
            width = 600
            height = 718
    elif size == 2:
        if region == 'all':
            width = 300
            height = 197
        elif region == 'west':
            width = 300
            height = 263
        elif region == 'east':
            width = 300
            height = 359
    return width, height


def upper_left_title(region):
        if region == 'all':
            t = 'All Regions'
        else:
            t = region.capitalize() + ' Region'
        return t


def get_email_dict(region):
    c_date = datetime.today().date() - timedelta(hours=17)
    print('System DateTime: ', datetime.today())
    print('PST DateTime: ', datetime.today() - timedelta(hours=17))
    print('System Date: ', datetime.today().date())
    print('Email Date: ', c_date)
    days = 10
    df = email_df(c_date, days, region)
    df = metric_to_english(df)
    TemplateData = {}
    TemplateData['maximum_temperature_mean'] = df_val(df, c_date, 'maximum_temperature_mean', True)
    TemplateData['maximum_temperature_mean_bg'] = temp_bg(TemplateData['maximum_temperature_mean'])
    TemplateData['maximum_temperature_ly'] = df_val(df, c_date, 'maximum_temperature_ly', True)
    TemplateData['maximum_temperature_ly_bg'] = temp_bg(TemplateData['maximum_temperature_ly'])
    TemplateData['maximum_temperature'] = df_val(df, c_date, 'maximum_temperature')
    TemplateData['bar_chart_url_1'] = make_bar_chart(df, 'maximum_temperature_ly')
    TemplateData['bar_chart_url_2'] = make_bar_chart(df, 'maximum_temperature_mean')
    img_width_2, img_height_2 = img_width_height(region, 2)
    TemplateData['image_width_2'] = img_width_2
    TemplateData['image_height_2'] = img_height_2
    img_width_1, img_height_1 = img_width_height(region, 1)
    TemplateData['image_width_1'] = img_width_1
    TemplateData['image_height_1'] = img_height_1
    TemplateData['subject'] = email_title(c_date, region)
    TemplateData['upper_left_title'] = upper_left_title(region)
    TemplateData['max_t_city'] = make_city_html('max_t', region)
    TemplateData['max_t_mean_city'] = make_city_html('max_t_mean', region)
    TemplateData = add_map_links(c_date, TemplateData, region)
    return TemplateData



def send_daily_email(s3_email_path, region):
    download_sales_map(region)
    download_email_list_csv(s3_email_path)
    email_list = pd.read_csv('/tmp/email.csv')
    t = Template(open("region_template.html", "r").read())
    email_dict = get_email_dict(region)
    SENDER = "chris@notus.ai"
    AWS_REGION = "us-east-1"
    ATTACHMENT = "/tmp/sales_past_7.jpg"
    BODY_TEXT = "Hello,\r\nPlease enable html to view."
    BODY_HTML = t.render(email_dict)
    CHARSET = "utf-8"
    client = boto3.client('ses', region_name=AWS_REGION)
    msg = MIMEMultipart('mixed')
    msg['Subject'] = email_dict['subject']
    msg['From'] = SENDER
    msg['Bcc'] = ','.join(list(email_list.email.values)) #Doesn't get used, is only a place holder
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    att = MIMEImage(open(ATTACHMENT, 'rb').read())
    att.add_header('Content-Disposition', 'inline', filename=os.path.basename(ATTACHMENT))
    att.add_header('Content-ID', '<sales_map_7>')
    msg.attach(msg_body)
    msg.attach(att)
    chunk_size = 45
    bcc_list = [email_list.email.values[i * chunk_size:(i + 1) * chunk_size] for i in range((len(email_list.email.values) + chunk_size - 1) // chunk_size)]
    for bcc in bcc_list:
        msg.replace_header('Bcc', ','.join(bcc))
        try:
            #Provide the contents of the email.
            response = client.send_raw_email(
                Source=SENDER,
                RawMessage={
                    'Data':msg.as_string(),
                }
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])


# os.environ['email_file'] = 'email_csv_path'
# os.environ['region'] = 'all'
if __name__ == "__main__":
    email_file = os.environ['email_file']
    region = os.environ['region']
    send_daily_email(email_file, region)
