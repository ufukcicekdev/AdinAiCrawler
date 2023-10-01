import os
import boto3
from logger import log_to_db
from dotenv import load_dotenv

# Load the .env file
load_dotenv()



AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_STORAGE_DICT_PATH = os.getenv('AWS_STORAGE_DICT_PATH')




def upload_file_to_s3(local_file_path, remote_file_name):
    try:
        s3.upload_file(local_file_path, AWS_STORAGE_BUCKET_NAME, remote_file_name, ExtraArgs={'ACL': 'public-read'})
    except Exception as e:
        log_to_db('ERROR', str(e))



# Create a Boto3 client
session = boto3.session.Session()
s3 = session.client('s3',
                   region_name=AWS_S3_REGION_NAME,
                   endpoint_url=AWS_S3_ENDPOINT_URL,
                   aws_access_key_id=AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)



