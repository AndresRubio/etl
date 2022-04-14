from botocore.exceptions import ClientError

from aws import client
from monitoring import log


class S3Handler:

    def __init__(self, bucket_name):
        self.client = client.get()
        self.bucket_name = bucket_name

    def create_bucket(self):

        try:
            response = self.client.create_bucket(Bucket=self.bucket_name)
        except ClientError:
            print('Could not create S3 bucket locally.')
            raise
        else:
            return response

    def upload_file(self, file_name, key):
        try:
            response = self.client.upload_file(file_name, self.bucket_name, key)
        except ClientError:
            log.error('Could not upload file to S3 bucket.')
            raise
        else:
            return response

    def put(self, file, key):
        self.client.put_object(Body=file, Bucket=self.bucket_name, Key=key)

    def get_content(self, key: str, encoding: str = 'utf-8'):
        return self.client.get_object(Bucket=self.bucket_name, Key=key)['Body'].read().decode(encoding)

    def delete_bucket(self):
        try:
            log.info(f'Deleting all objects in the bucket {self.bucket_name}')
            s3_objects = self.client.list_objects_v2(Bucket=self.bucket_name)['Contents']
            [self.client.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
             for obj in s3_objects]
            self.client.delete_bucket(Bucket=self.bucket_name)
        except:
            log.error('Could not delete all S3 bucket objects.')
            raise

    def delete_folder(self, folder: str):
        folder = folder if folder.endswith('/') else folder + '/'
        for key in self.list_keys(folder):
            self.delete_file(key)

    def delete_file(self, key: str):
        self.client.delete_object(Bucket=self.bucket_name, Key=key)
