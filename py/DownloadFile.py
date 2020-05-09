#
# This file will download one file by name
#
import boto3
import io
import os 
from Config import *

if len(sys.argv) < 4:
	print("Usage: python3 py/DownloadFile.py  config_profile  bucket_name  object_key")
	sys.exit()

config = Config()
bucket = sys.argv[2]
objectKey = sys.argv[3]

if "shortsands" in bucket:
	directory = ""#config.DIRECTORY_MY_INFO_JSON
	session = boto3.Session(profile_name=config.S3_AWS_MY_PROFILE)
else:
	directory = ""#config.DIRECTORY_DBP_INFO_JSON
	session = boto3.Session(profile_name=config.S3_AWS_DBP_PROFILE)

client = session.client('s3')

filename = directory + objectKey.replace("/", "_")
client.download_file(bucket, objectKey, filename)
print("Done ", filename)

