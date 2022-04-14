import boto3

AWS_REGION = 'eu-central-1'
AWS_PROFILE = 'localstack'
ENDPOINT_URL = 'http://localhost:4566'

#TODO: the idea was to get a configurable client
def get():
    boto3.setup_default_session(profile_name=AWS_PROFILE)
    return boto3.client("s3", region_name=AWS_REGION, endpoint_url=ENDPOINT_URL)
