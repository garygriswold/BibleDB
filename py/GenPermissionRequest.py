# This program reads the Bible table, and generates a permission policy for all that it finds

import io
import os
import csv
from Config import *
from SqliteUtility import *

PREFIX = "arn:aws:s3:::"


def generatePermissions(results, db, bucket):
	sql = "SELECT systemId, versionId, mediaType, filePrefix FROM Bibles WHERE bucket = ? ORDER BY systemId"
	resultSet = db.select(sql, (bucket,))
	for (systemId, versionId, mediaType, filePrefix) in resultSet:
		results.add(bucket + "/" + filePrefix)


def generateLegacyPermissions(results, bucket):
	with open("data/ShortsandsBibles.csv", newline='\n') as csvfile:
		reader = csv.reader(csvfile)
		for (bibleZipFile, abbr, iso3, scope, versionPriority, name, englishName,
			localizedName, textBucket, textId, keyTemplate, 
			audioBucket, otDamId, ntDamId, ios1, script, country) in reader:
				if otDamId != None and otDamId != "":
					results.add(bucket + "/" + otDamId)
				if ntDamId != None and ntDamId != "":
					results.add(bucket + "/" + ntDamId)



config = Config()
db = SqliteUtility(config)
results = set()
generatePermissions(results, db, config.S3_DBP_BUCKET)
generatePermissions(results, db, config.S3_DBP_VIDEO_BUCKET)
generateLegacyPermissions(results, config.S3_DBP_BUCKET)
db.close()
output = io.open("PermissionsRequest.txt", mode="w", encoding="utf-8")
for objectKey in sorted(results):
	output.write(PREFIX + objectKey + "/*\n")	
output.close()
