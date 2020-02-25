#
# List Bucket
# This program lists all of the keys in a bucket into a text file
# It stores this in the metadata directory where it can be used
#

import boto3
#import io

#out = io.open("metadata/FCBH/dbp_prod.txt", mode="w", encoding="utf-8")

session = boto3.Session(profile_name='FCBH_Gary')
client = session.client('s3')

request = { 'Bucket':'dbp-prod', 'MaxKeys':1000 }
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
				print key
			except Exception as err:
				print "Could not write key", str(err)

	if hasMore:
		request['ContinuationToken'] = response['NextContinuationToken']

#out.close()

