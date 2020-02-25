# This program reads the Bible table, and looks up the keys in dbp_prod.txt
# It reports any that it does not find.

import io
import os
import sqlite3

BUCKET = u"dbp-prod"
PREFIX1 = u"\n\"arn:aws:s3:::"
PREFIX = u",\n\"arn:aws:s3:::"
output = io.open("PermissionsRequest.txt", mode="w", encoding="utf-8")
output.write(u"\"Resource\": [")
output.write(PREFIX1 + BUCKET + "/*/info.json\"")

def getDamIdHack(audioId):
	damId = audioId.split("/")[2]
	damIdHacks = {"GRKAVSO1DA": "O1GRKAVS",
	"ENGNABN2DA": "N2NABXXX",
	"FRNTLSO2DA": "O2FRATLS",
	"FRNTLSN2DA": "N2FRATLS",
	"KDEDPIN1DA": "KDEPBTN1DA",
	"PRSGNNN2DA": "N2PRSGNN"}
	if damId in damIdHacks:
		return damIdHacks[damId]
	else:
		return damId


textSet = set()
audioSet = set()
input = io.open(os.environ['HOME'] + "/ShortSands/DBL/FCBH/dbp_prod.txt", mode="r", encoding="utf-8")
for line in input:

	parts = line.split("/")
	if len(parts) > 3:

		if line.startswith("text"):
			pieces = parts[3].split("_")
			key = parts[0] + "/" + parts[1] + "/" + parts[2] + "/" + pieces[0] + "_"
			textSet.add(key)

		elif line.startswith("audio"):
			key = parts[0] + "/" + parts[1] + "/" + parts[2] + "/" + parts[3][0:1]
			audioSet.add(key)

input.close()

print len(textSet), len(audioSet)

db = sqlite3.connect('Versions.db')
cursor = db.cursor()
sql = "SELECT bibleId, textBucket, textId, audioBucket, otDamId, ntDamId FROM Bible ORDER BY bibleId"
values = ()
cursor.execute(sql, values)
rows = cursor.fetchall()

for row in rows:
	bibleId = row[0]
	textBucket = row[1]
	if textBucket == BUCKET:
		textId = row[2]
		if textId != None:
			parts = textId.split("/")
			lastPart = parts[len(parts) - 1]
			if lastPart == 'KORKRV': # KKNKRV hack
				lastPart = 'KKNKRV'
			search = textId + "/" + lastPart + "_"
			if search in textSet:
				output.write(PREFIX + BUCKET + "/" + search + "*.html\"")
			else:
				print "missing text", bibleId, textId

for row in rows:
	bibleId = row[0]
	audioBucket = row[3]
	if audioBucket == BUCKET:
		otDamId = row[4]
		if otDamId != None:
			search = otDamId + "/A"
			if search in audioSet:
				#damId = otDamId.split("/")[2]
				damId = getDamIdHack(otDamId)
				output.write(PREFIX + BUCKET + "/" + search + "*" + damId + ".mp3\"")
			else:
				print "missing ot audio", bibleId, otDamId


		ntDamId = row[5]
		if ntDamId != None:
			search = ntDamId + "/B"
			if search in audioSet:
				#damId = ntDamId.split("/")[2]
				damId = getDamIdHack(ntDamId)
				output.write(PREFIX + BUCKET + "/" + search + "*" + damId + ".mp3\"")
			else:
				print "missing nt audio", bibleId, ntDamId

db.close()
output.write(u"\n],")
output.close()