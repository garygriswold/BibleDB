#
# List Bucket
# This program lists all of the keys in a bucket into a text file
# It stores this in the metadata directory where it can be used
#

import sys
import io
import os
import boto3
import datetime
from Config import *

if len(sys.argv) < 3:
	print("Usage: python3 py/ListBucket.py  config_profile  bucket_name")
	sys.exit()

config = Config()
bucket = sys.argv[2]

tempFilename = config.DIRECTORY_BUCKET_LIST + bucket + "_new.txt"
finalFilename = config.DIRECTORY_BUCKET_LIST + bucket + ".txt"

out = io.open(tempFilename, mode="w", encoding="utf-8")

if "shortsands" in bucket:
	session = boto3.Session(profile_name=config.S3_AWS_MY_PROFILE)
else:
	session = boto3.Session(profile_name=config.S3_AWS_DBP_PROFILE)
client = session.client('s3')

request = { 'Bucket':bucket, 'MaxKeys':1000 }
# Bucket, Delimiter, EncodingType, Market, MaxKeys, Prefix

hasMore = True
while hasMore:
	response = client.list_objects_v2(**request)
	hasMore = response['IsTruncated']
	contents = response['Contents']
	for item in contents:
		key = item['Key']
		size = item['Size']
		datetime = item['LastModified']
		try:
			out.write("%s\t%s\t%s\n" % (key.strip(), size, datetime))
		except Exception as err:
			print("Could not write key", str(err))

	if hasMore:
		request['ContinuationToken'] = response['NextContinuationToken']

out.close()

os.rename(tempFilename, finalFilename)
