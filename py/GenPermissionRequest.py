# This program reads the Bible table, and generates a permission policy for all that it finds

import io
import os
from Config import *
from SqliteUtility import *

PREFIX = "arn:aws:s3:::"


def generatePermissions(output, db, bucket):
	sql = "SELECT systemId, versionId, mediaType, filePrefix FROM Bibles WHERE bucket = ? ORDER BY systemId"
	resultSet = db.select(sql, (bucket,))
	for (systemId, versionId, mediaType, filePrefix) in resultSet:
		output.write(PREFIX + bucket + "/" + filePrefix + "/*\n")


output = io.open("PermissionsRequest.txt", mode="w", encoding="utf-8")
config = Config()
db = SqliteUtility(config)
generatePermissions(output, db, config.S3_DBP_BUCKET)
generatePermissions(output, db, config.S3_DBP_VIDEO_BUCKET)
db.close()
output.close()
