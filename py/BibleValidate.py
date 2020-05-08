# This program reads the Bible table, and looks up the keys in dbp-prod.txt
# It reports any that it does not find.

import io
import os
import csv
from Config import *
from SqliteUtility import *

class Reference:

	def __init__(self, filePrefix, s3FileTemplate, bookId, sequence, nameS3, chapter):
		self.filePrefix = filePrefix
		if filePrefix.startswith("text") and len(filePrefix) > 19:
			self.s3FilePrefix = filePrefix[:-4]
		else:
			self.s3FilePrefix = filePrefix
		self.s3FileTemplate = s3FileTemplate
		self.bookId = bookId
		self.sequence = sequence
		self.nameS3 = nameS3
		self.chapter = chapter

	def toString(self):
		return "%s/%s %s %s %s" % (self.s3FilePrefix, self.s3FileTemplate, self.bookId, self.sequence, self.chapter)


class BibleValidate:

	def __init__(self, config):
		self.config = config


	def loadBuckets(self):
		self.dbpProdBucket = self.loadOneBucket(config.S3_DBP_BUCKET)
		self.shortSandsBucket = self.loadOneBucket(config.S3_MY_BUCKET)
		self.videoBucket = self.loadOneBucket("dbp-vid-m3u8") # extraction of dbp-vid.txt


	def loadOneBucket(self, bucketName):
		bucketSet = set()
		input = io.open(self.config.DIRECTORY_BUCKET_LIST + bucketName + ".txt", mode="r", encoding="utf-8")
		for line in input:
			filename = line.split("\t")[0]
			bucketSet.add(filename)
		input.close()
		print(len(bucketSet))
		return bucketSet


	def process(self):
		db = SqliteUtility(self.config)
		bookMap = db.selectMap("SELECT usfm3, usfm2 FROM Books WHERE usfm2 IS NOT NULL", ())
		sql = "SELECT systemId, mediaType, bucket, filePrefix, fileTemplate, bibleZipFile FROM Bibles ORDER BY systemId"
		resultSet = db.select(sql, ())
		for (systemId, mediaType, bucket, filePrefix, fileTemplate, bibleZipFile) in resultSet:
			if mediaType != "video":
				sql = "SELECT book, sequence, nameS3, numChapters FROM BibleBooks WHERE systemId = ? ORDER BY sequence"
				results = db.select(sql, (systemId,))
				for (bookId, sequence, nameS3, numChapters) in results:
					for chapter in range(1, numChapters + 1):
						reference = Reference(filePrefix, fileTemplate, bookId, sequence, nameS3, chapter)
						#print(reference.toString())
						fullName = self.getFilename(reference)
						#print("out", fullName)
						if bucket == config.S3_DBP_BUCKET:
							if fullName not in self.dbpProdBucket:
								print("ERROR NOT FOUND in dbp-prod", fullName)
						elif bucket == config.S3_MY_BUCKET:
							if fullName not in self.shortSandsBucket:
								print("ERROR NOT FOUND in text-shortsands", fullName)
			else:
				filename = self.config.DIRECTORY_ACCEPTED + filePrefix.replace("/", "_") + ".csv"
				with open(filename, newline='\n') as csvfile:
					reader = csv.DictReader(csvfile)
					for row in reader:
						file = row["file_name"].split(".")[0]
						for fileType in ["_av720p.m3u8", "_av480p.m3u8", "_stream.m3u8"]:
							fullName = filePrefix + "/" + file + fileType
							if fullName not in self.videoBucket:
								print("ERROR NOT FOUND in dbp-vid", fullName)


	def getFilename(self, reference):
		result = []
		inItem = False
		for char in reference.s3FileTemplate:
			if char == "%":
				inItem = True
			elif not inItem:
				result.append(char)
			else:
				inItem = False
				if char == "I": # Id is last part of s3FilePrefix
					parts = reference.s3FilePrefix.split("/")
					result.append(parts[-1])
				elif char == "O": # sequence from BibleBooks
					result.append(str(reference.sequence))
				elif char == "B": # USFM 3 char book code
					result.append(reference.bookId)
				elif char == "b": # 2 char book code (not used May 2020)
					id2 = bookMap.get(reference.bookId)
					result.append(id2)
				elif char == "N": # Book name
					result.append(reference.nameS3)
				elif char == "U": # Underline char
					filler = "_" * (12 - len(reference.nameS3))
					result.append(filler)
				elif char == "u": # 4 extra underline char
					filler = "_" * (16 - len(reference.nameS3))
					result.append(filler)
				elif char == "C": # chapter number, not zero filled
					if reference.chapter > 0:
						result.append(str(reference.chapter))
					else:
						del result[-1] # remove the underscore that would preceed chapter
				elif char == "c": # chapter number, 2 char zero filled, Psalms 3 char
					chapStr = str(reference.chapter)
					if reference.bookId == "PSA":
						if len(chapStr) == 1:
							result.append("00" + chapStr)
						elif len(chapStr) == 2:
							result.append("0" + chapStr)
						else:
							result.append(chapStr)
					else:
						if len(chapStr) == 1:
							result.append("_0" + chapStr)
						else:
							result.append("_" + chapStr)
				else:
					print("ERROR: Unknown format char %s" % (char))
		return reference.s3FilePrefix + "/" + "".join(result)


if __name__ == "__main__":
	config = Config()
	tables = BibleValidate(config)
	tables.loadBuckets()
	tables.process()


