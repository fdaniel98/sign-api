import boto3
from dotenv import dotenv_values

config = dotenv_values(".env")


def upload_to_s3(data, name):
    s3 = 's3'
    session = boto3.Session(
        aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['AWS_SECRET_ACCESS'])
    s3 = session.resource(s3)
    res = s3.Bucket(config['AWS_BUCKET']).put_object(Key=name, Body=data)
    return res

