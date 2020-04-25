#
# This file will download all of the objects in a bucket that are
# associated with a specific BibleId/FileId
#
import boto3
import io
import os 
from Config import *

if len(sys.argv) < 3:
	print("Usage: python3 py/DownloadInfo.py  config_profile  bucket_name")
	sys.exit()

config = Config()
bucket = sys.argv[2]
if "shortsands" in bucket:
	directory = config.DIRECTORY_MY_INFO_JSON
	session = boto3.Session(profile_name=config.S3_AWS_MY_PROFILE)
else:
	directory = config.DIRECTORY_DBP_INFO_JSON
	session = boto3.Session(profile_name=config.S3_AWS_DBP_PROFILE)

searchFile = "info.json"
source = config.DIRECTORY_BUCKET_LIST + bucket + ".txt"

client = session.client('s3')

input = io.open(source, mode="r", encoding="utf-8")
for line in input:
	line = line.split("\t")[0]
	if line.endswith(searchFile):
		filename = directory + line.replace("/", ":")
		try:
			client.download_file(bucket, line, filename)
			print("Done ", line)
		except:
			print("Error Failed ", line)

input.close()
