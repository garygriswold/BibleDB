# This program reads the Bible table, and looks up the keys in dbp-prod.txt
# It reports any that it does not find.

import io
import os
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
		#self.BUCKET = config.S3_DBP_BUCKET
		#PREFIX1 = u"\n\"arn:aws:s3:::"
		#PREFIX = u",\n\"arn:aws:s3:::"
		#output = io.open("PermissionsRequest.txt", mode="w", encoding="utf-8")
		#output.write(u"\"Resource\": [")
		#output.write(PREFIX1 + BUCKET + "/*/info.json\"")

#	def getDamIdHack(audioId):
#		damId = audioId.split("/")[2]
#		damIdHacks = {"GRKAVSO1DA": "O1GRKAVS",
#		"ENGNABN2DA": "N2NABXXX",
#		"FRNTLSO2DA": "O2FRATLS",
#		"FRNTLSN2DA": "N2FRATLS",
#		"KDEDPIN1DA": "KDEPBTN1DA",
#		"PRSGNNN2DA": "N2PRSGNN"}
#		if damId in damIdHacks:
#			return damIdHacks[damId]
#		else:
#			return damId

	def loadBuckets(self):
		self.dbpProdBucket = self.loadOneBucket(config.S3_DBP_BUCKET)

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
			sql = "SELECT book, sequence, nameS3, numChapters FROM BibleBooks WHERE systemId = ? ORDER BY sequence"
			results = db.select(sql, (systemId,))
			for (bookId, sequence, nameS3, numChapters) in results:
				reference = Reference(filePrefix, fileTemplate, bookId, sequence, nameS3, numChapters)
				print(reference.toString())
				fullName = self.getFilename(reference)
				print("out", fullName)
				if bucket == config.S3_DBP_BUCKET:
					if fullName not in self.dbpProdBucket:
						print("ERROR NOT FOUND", fullName)

				#if not fullName in filenameSet:
				#	print("ERROR: missing file %s " % (fullName))


	def getFilename(self, reference):
		result = []
		inItem = False
		for char in reference.s3FileTemplate:
			print("CHAR", char)
			if char == "%":
				inItem = True
			elif not inItem:
				result.append(char)
			else:
				inItem = False
				if char == "I": # Id is last part of s3FilePrefix
					parts = reference.s3FilePrefix.split("/")
					result.append(parts[-1])
				elif char == "O": # ordinal 1 is GEN, 70 is MAT, not zero filled
					result.append(str(reference.sequence))
				elif char == "o": # 3 char ordinal A01 is GEN, zero filled
					if len(reference.sequence) == 1:
						result.append("00" + reference.sequence)
					elif len(reference.seuence) == 2:
						result.append("0" + reference.sequence)
					else:
						result.append(str(reference.sequence))
                    #if let seq3 = bookMap[reference.bookId]?.seq3 {
                    #    result.append(seq3)
                    #}
				elif char == "B": # USFM 3 char book code
					result.append(reference.bookId)
				elif char == "b": # 2 char book code
					id2 = bookMap.get(reference.bookId)
					result.append(id2)
				elif char == "N": # Book name
					result.append(reference.nameS3)
				elif char == "U": # Underline char
					filler = "_" * (12 - len(reference.nameS3))
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
		print("result", result)
		return reference.s3FilePrefix + "/" + "".join(result)
"""
    struct BookData {
        let seq: String
        let seq3: String
        let id2: String
    }

    let bookMap: [String: BookData] = [
        "FRT": BookData(seq: "0", seq3: "?", id2: "?"),
        "GEN": BookData(seq: "2", seq3: "A01", id2: "GN"),
        "EXO": BookData(seq: "3", seq3: "A02", id2: "EX"),
        "LEV": BookData(seq: "4", seq3: "A03", id2: "LV"),
        "NUM": BookData(seq: "5", seq3: "A04", id2: "NU"),
        "DEU": BookData(seq: "6", seq3: "A05", id2: "DT"),
        "JOS": BookData(seq: "7", seq3: "A06", id2: "JS"),
        "JDG": BookData(seq: "8", seq3: "A07", id2: "JG"),
        "RUT": BookData(seq: "9", seq3: "A08", id2: "RT"),
        "1SA": BookData(seq: "10", seq3: "A09", id2: "S1"),
        "2SA": BookData(seq: "11", seq3: "A10", id2: "S2"),
        "1KI": BookData(seq: "12", seq3: "A11", id2: "K1"),
        "2KI": BookData(seq: "13", seq3: "A12", id2: "K2"),
        "1CH": BookData(seq: "14", seq3: "A13", id2: "R1"),
        "2CH": BookData(seq: "15", seq3: "A14", id2: "R2"),
        "EZR": BookData(seq: "16", seq3: "A15", id2: "ER"),
        "NEH": BookData(seq: "17", seq3: "A16", id2: "NH"),
        "EST": BookData(seq: "18", seq3: "A17", id2: "ET"),
        "JOB": BookData(seq: "19", seq3: "A18", id2: "JB"),
        "PSA": BookData(seq: "20", seq3: "A19", id2: "PS"),
        "PRO": BookData(seq: "21", seq3: "A20", id2: "PR"),
        "ECC": BookData(seq: "22", seq3: "A21", id2: "EC"),
        "SNG": BookData(seq: "23", seq3: "A22", id2: "SS"),
        "ISA": BookData(seq: "24", seq3: "A23", id2: "IS"),
        "JER": BookData(seq: "25", seq3: "A24", id2: "JR"),
        "LAM": BookData(seq: "26", seq3: "A25", id2: "LM"),
        "EZK": BookData(seq: "27", seq3: "A26", id2: "EK"),
        "DAN": BookData(seq: "28", seq3: "A27", id2: "DN"),
        "HOS": BookData(seq: "29", seq3: "A28", id2: "HS"),
        "JOL": BookData(seq: "30", seq3: "A29", id2: "JL"),
        "AMO": BookData(seq: "31", seq3: "A30", id2: "AM"),
        "OBA": BookData(seq: "32", seq3: "A31", id2: "OB"),
        "JON": BookData(seq: "33", seq3: "A32", id2: "JH"),
        "MIC": BookData(seq: "34", seq3: "A33", id2: "MC"),
        "NAM": BookData(seq: "35", seq3: "A34", id2: "NM"),
        "HAB": BookData(seq: "36", seq3: "A35", id2: "HK"),
        "ZEP": BookData(seq: "37", seq3: "A36", id2: "ZP"),
        "HAG": BookData(seq: "38", seq3: "A37", id2: "HG"),
        "ZEC": BookData(seq: "39", seq3: "A38", id2: "ZC"),
        "MAL": BookData(seq: "40", seq3: "A39", id2: "ML"),
        "TOB": BookData(seq: "41", seq3: "?", id2: "?"),
        "JDT": BookData(seq: "42", seq3: "?", id2: "?"),
        "ESG": BookData(seq: "43", seq3: "?", id2: "?"),
        "WIS": BookData(seq: "45", seq3: "?", id2: "?"),
        "SIR": BookData(seq: "46", seq3: "?", id2: "?"),
        "BAR": BookData(seq: "47", seq3: "?", id2: "?"),
        "LJE": BookData(seq: "48", seq3: "?", id2: "?"),
        "S3Y": BookData(seq: "49", seq3: "?", id2: "?"),
        "SUS": BookData(seq: "50", seq3: "?", id2: "?"),
        "BEL": BookData(seq: "51", seq3: "?", id2: "?"),
        "1MA": BookData(seq: "52", seq3: "?", id2: "?"),
        "2MA": BookData(seq: "53", seq3: "?", id2: "?"),
        "1ES": BookData(seq: "54", seq3: "?", id2: "?"),
        "MAN": BookData(seq: "55", seq3: "?", id2: "?"),
        "3MA": BookData(seq: "57", seq3: "?", id2: "?"),
        "4MA": BookData(seq: "59", seq3: "?", id2: "?"),
        "MAT": BookData(seq: "70", seq3: "B01", id2: "MT"),
        "MRK": BookData(seq: "71", seq3: "B02", id2: "MK"),
        "LUK": BookData(seq: "72", seq3: "B03", id2: "LK"),
        "JHN": BookData(seq: "73", seq3: "B04", id2: "JN"),
        "ACT": BookData(seq: "74", seq3: "B05", id2: "AC"),
        "ROM": BookData(seq: "75", seq3: "B06", id2: "RM"),
        "1CO": BookData(seq: "76", seq3: "B07", id2: "C1"),
        "2CO": BookData(seq: "77", seq3: "B08", id2: "C2"),
        "GAL": BookData(seq: "78", seq3: "B09", id2: "GL"),
        "EPH": BookData(seq: "79", seq3: "B10", id2: "EP"),
        "PHP": BookData(seq: "80", seq3: "B11", id2: "PP"),
        "COL": BookData(seq: "81", seq3: "B12", id2: "CL"),
        "1TH": BookData(seq: "82", seq3: "B13", id2: "H1"),
        "2TH": BookData(seq: "83", seq3: "B14", id2: "H2"),
        "1TI": BookData(seq: "84", seq3: "B15", id2: "T1"),
        "2TI": BookData(seq: "85", seq3: "B16", id2: "T2"),
        "TIT": BookData(seq: "86", seq3: "B17", id2: "TT"),
        "PHM": BookData(seq: "87", seq3: "B18", id2: "PM"),
        "HEB": BookData(seq: "88", seq3: "B19", id2: "HB"),
        "JAS": BookData(seq: "89", seq3: "B20", id2: "JM"),
        "1PE": BookData(seq: "90", seq3: "B21", id2: "P1"),
        "2PE": BookData(seq: "91", seq3: "B22", id2: "P2"),
        "1JN": BookData(seq: "92", seq3: "B23", id2: "J1"),
        "2JN": BookData(seq: "93", seq3: "B24", id2: "J2"),
        "3JN": BookData(seq: "94", seq3: "B25", id2: "J3"),
        "JUD": BookData(seq: "95", seq3: "B26", id2: "JD"),
        "REV": BookData(seq: "96", seq3: "B27", id2: "RV"),
        "BAK": BookData(seq: "97", seq3: "?", id2: "?"),
        "GLO": BookData(seq: "106", seq3: "?", id2: "?")
         ]
}
"""

if __name__ == "__main__":
	config = Config()
	tables = BibleValidate(config)
	tables.loadBuckets()
	tables.process()


