import os
import urllib
import pysftp
import json
import boto3
import paramiko
from io import StringIO, TextIOWrapper
from datetime import datetime


def checkEnvExist(keys):
    for key in keys:
        if not key in os.environ:
            return False

    return True


def get_file_name():
    cur_date_time = datetime.now().strftime('%d-%m-%Y_%H-%M')

    return f"orderChunk_{cur_date_time}"


def get_ssh_key(secret_name):

    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    
    return get_secret_value_response['SecretString']


def importFromUrl(url):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())

    return data


def importFromSFTP():
    path = os.environ['path']

    username = os.environ['username']
    server = os.environ['server']
    port = os.environ['port']

    fileName = path.split('/')[-1]

    if 'password' in os.environ:
        with pysftp.Connection(server, username=username, password=os.environ['password'], port=port) as sftp:
            sftp.get(path, fileName)
    elif 'ssh_key' in os.environ:
        ssh_key = get_ssh_key(os.environ['ssh_key'])
        ssh_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key))

        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None

            with pysftp.Connection(host=server, username=username, private_key=ssh_key, port=port, cnopts=cnopts) as sftp:
                sftp.get(path, fileName)

            print('---connection success---')
        except Exception as e:
            print('---connection error---')
            print(e)

    with open(fileName, 'r') as myfile:
        data = []

        for line in myfile.readlines():
            data.append(json.loads(line))

    return json.loads(data)


def importFromS3():
    client = boto3.client(
        's3',
        aws_access_key_id=os.environ['aws_access_key_id'],
        aws_secret_access_key=os.environ['aws_secret_access_key']
    )
    result = client.get_object(
        Bucket=os.environ['aws_bucket'], Key=os.environ['path'])

    text = result['Body'].iter_lines()
    data = []

    for line in text:
        data.append(json.loads(line))

    return data


def memory_to_s3(bucket, object_path, file_stream):
    """Takes a file and sends it to an s3 path"""
    s3 = boto3.resource('s3')
    object = s3.Object(bucket, object_path)
    object.put(Body=file_stream)
    print('%s uploaded' % object_path)


def sendS3(dataList):
    baseFileName = get_file_name()
    bucketName = 'aws-order-chunks'
    bus = os.environ['bus']

    path = datetime.today().strftime('%d-%m-%Y')

    chunk = ''
    fCount = 0
    for i in range(len(dataList)):
        pk = f'{bus}|{id}'
        dataList[i]['order_id'] = pk
        chunk = chunk + json.dumps(dataList[i]) + '\n'

        if (i + 1) % 5000 == 0:
            fCount = (i + 1) // 5000
            memory_to_s3(bucketName, object_path=f"{path}/{baseFileName}_{fCount-1}.json",
                         file_stream=chunk)

            chunk = ''

    memory_to_s3(bucketName, object_path=f"{path}/{baseFileName}_{fCount}.json",
                 file_stream=chunk)


def main():
    if not checkEnvExist(['transport']):
        print('Should set transport env!')
        return

    transport = os.environ['transport']

    if transport == 'HTTPS' or transport == 'HTTP':
        if not checkEnvExist(['url', 'bus']):
            print('Env URL not setted!')
            return

        data = importFromUrl(os.environ['url'])        

    elif transport == 'FTP' or transport == 'SFTP':
        if not checkEnvExist(['port', 'server', 'username', 'path', 'bus']):
            print('Required Environment variables not setted!')
            return

        data = importFromSFTP()

    elif transport == 'S3':
        if not checkEnvExist(['aws_access_key_id', 'aws_secret_access_key', 'aws_bucket', 'aws_region', 'path', 'bus']):
            print('Required Environment variables not setted!')
            return
        
        data = importFromS3()
    
    else:
        pass

    sendS3(data)
    

if __name__ == '__main__':
    main()