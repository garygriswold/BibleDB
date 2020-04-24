#
# This file will download all of the objects in a bucket that are
# associated with a specific BibleId/FileId
#
import boto3
import io
import os 
from Config import *

config = Config()

searchFile = "info.json"
source = config.DIRECTORY_BUCKET_LIST + config.S3_DBP_BUCKET + ".txt"

session = boto3.Session(profile_name=config.S3_AWS_DBP_PROFILE)
client = session.client('s3')

input = io.open(source, mode="r", encoding="utf-8")
for line in input:
	line = line.split("\t")[0]
	if line.endswith(searchFile):
		filename = config.DIRECTORY_INFO_JSON + line.replace("/", ":")
		try:
			client.download_file(config.S3_DBP_BUCKET, line, filename)
			print("Done ", line)
		except:
			print("Error Failed ", line)

input.close()
