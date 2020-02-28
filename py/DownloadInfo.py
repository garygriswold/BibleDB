#
# This file will download all of the objects in a bucket that are
# associated with a specific BibleId/FileId
#
import boto3
import io
import os 

searchFile = "info.json"
target = "/Volumes/FCBH/info_json/"
source = "/Volumes/FCBH/bucket_data/dbp-prod.txt"

session = boto3.Session(profile_name='FCBH_BibleApp')
client = session.client('s3')

input = io.open(source, mode="r", encoding="utf-8")
for line in input:
	line = line.strip()
	if line.endswith(searchFile):
		filename = target + line.replace("/", ":")
		try:
			client.download_file('dbp-prod', line, filename)
			print("Done ", line)
		except:
			print("Error Failed ", line)

input.close()
