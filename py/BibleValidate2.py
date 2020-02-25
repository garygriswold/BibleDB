# This program reads all of the records in the Bible table
# And then does a retrieval of the info.json file to create
# a table of contents.  Then it does a head of the last chapter
# of each book of the Bible.
# Then it does the same last chapter of each book head for
# each damId.

import sqlite3
import boto3
import json

bookNum = { 
	"FRT":"0", "INT":"1", "GEN":"2", "EXO":"3", "LEV":"4", "NUM":"5", "DEU":"6", "JOS":"7", "JDG":"8", "RUT":"9", 
	"1SA":"10", "2SA":"11", "1KI":"12", "2KI":"13", "1CH":"14", "2CH":"15", "EZR":"16", "NEH":"17", "EST":"18", 
	"JOB":"19", "PSA":"20", "PRO":"21", "ECC":"22", "SNG":"23", "ISA":"24", "JER":"25", "LAM":"26", "EZK":"27",
	"DAN":"28", "HOS":"29", "JOL":"30", "AMO":"31", "OBA":"32", "JON":"33", "MIC":"34", "NAM":"35", "HAB":"36",
	"ZEP":"37", "HAG":"38", "ZEC":"39", "MAL":"40", "TOB":"41", "JDT":"42", "ESG":"43", "WIS":"45", "SIR":"46", 
	"BAR":"47", "LJE":"48", "S3Y":"49", "SUS":"50", "BEL":"51", "1MA":"52", "2MA":"53", "1ES":"54", "MAN":"55",
	"PS2":"56", "3MA":"57", "2ES":"58", "4MA":"59", "DAG":"66",
	"MAT":"70", "MRK":"71", "LUK":"72", "JHN":"73", "ACT":"74", "ROM":"75", "1CO":"76", "2CO":"77",
	"GAL":"78", "EPH":"79", "PHP":"80", "COL":"81", "1TH":"82", "2TH":"83", "1TI":"84", "2TI":"85", "TIT":"86",
	"PHM":"87", "HEB":"88", "JAS":"89", "1PE":"90", "2PE":"91", "1JN":"92", "2JN":"93", "3JN":"94", "JUD":"95",
	"REV":"96", "BAK":"97", "OTH":"98", "XXA":"99", "XXB":"100", "XXC":"101", "XXD":"102", "XXF":"104", 
	"GLO":"106", "CNC":"107",
	"TDX":"108", "NDX":"109" 
	}

dbpSession = boto3.Session(profile_name='FCBH_BibleApp')
dbpClient = dbpSession.client('s3')
ssSession = boto3.Session(profile_name='BibleApp')
ssClient = ssSession.client('s3')

db = sqlite3.connect('Versions.db')
cursor = db.cursor()

def validateText(bucket, textId):
	try:
		if textBucket == 'dbp-prod':
			info = dbpClient.get_object(Bucket=bucket, Key=textId + "/info.json")
		else:
			info = ssClient.get_object(Bucket=bucket, Key=textId + "/info.json")
		info2 = json.load(info["Body"])
		divisions = info2["divisions"]
	except Exception as err:
		print "ERROR:", textId, err
	for book in divisions:
		print book
		seq = bookNum[book]
		id2 = textId.split("/")[2]
		if book == 'FRT' or book == 'GLO' or book == 'BAK':
			key = "%s/%s_%s_%s.html" % (textId, id2, seq, book)
		else:
			key = "%s/%s_%s_%s_1.html" % (textId, id2, seq, book)
		try:
			#print key
			if textBucket == 'dbp-prod':
				obj = dbpClient.get_object(Bucket=textBucket, Key=key)
			else:
				obj = ssClient.get_object(Bucket=textBucket, Key=key)
		except Exception as err:
			print "ERROR:", key, err	

def validateDamId(bucket, damId):
	sql = "SELECT bookId, bookOrder, numberOfChapters FROM AudioBook WHERE damId = ?"
	values = (damId,)
	cursor.execute(sql, values)
	rows = cursor.fetchall()
	for row in rows:
		print row

sql = "SELECT bibleId, textBucket, textId, audioBucket, otDamId, ntDamId FROM Bible ORDER BY iso3"
values = ()
cursor.execute(sql, values)
rows = cursor.fetchall()

for row in rows:
	bibleId = row[0]
	print bibleId
	textBucket = row[1].replace("%R", "us-west-2")
	textId = row[2]
	if textId != None:
		validateText(textBucket, textId)

	audioBucket = row[3]
	otDamId = row[4]
	ntDamId = row[5]
#	if otDamId != None:
#		validateDamId(audioBucket, otDamId)
#	if ntDamId != None:
#		validateDamId(audioBucket, ntDamId)


#	exit()

db.close()