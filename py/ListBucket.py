#
# List Bucket
# This program lists all of the keys in a bucket into a text file
# It stores this in the metadata directory where it can be used
#

import sys
import io
import os
import boto3

DIRECTORY = "/Volumes/FCBH/bucket_data/"

if len(sys.argv) < 2:
	print("Usage: python3 py/ListBucket.py  bucket_name")
	sys.exit()

bucket = sys.argv[1]

tempFilename = DIRECTORY + bucket + "_new.txt"
finalFilename = DIRECTORY + bucket + ".txt"

out = io.open(tempFilename, mode="w", encoding="utf-8")

session = boto3.Session(profile_name='FCBH_Gary')
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
		if (size > 0):
			try:
				out.write(key.strip() + "\n")
			except Exception as err:
				print("Could not write key", str(err))

	if hasMore:
		request['ContinuationToken'] = response['NextContinuationToken']

out.close()

os.rename(tempFilename, finalFilename)

