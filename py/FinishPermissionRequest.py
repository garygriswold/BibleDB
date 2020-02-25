# FinishPermissionRequest
#
# This program produces a finished permission request that will not request permission for items
# that we do not want.  In this way, it should not be necessary for FCBH to add to the request.
#
import io
import os
import sys

bookIdList = [ "FRT", "INT", "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", 
	"1SA", "2SA", "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST",
    "JOB", "PSA", "PRO", "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN",
    "HOS", "JOL", "AMO", "OBA", "JON", "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL",
    "TOB", "JDT", "ESG", "WIS", "SIR", "BAR", "LJE", "S3Y", "SUS", "BEL", "DAG",
    "1MA", "2MA", "1ES", "MAN", "PS2", "3MA", "2ES", "4MA",  
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH", "PHP", "COL",
    "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS", "1PE", "2PE",
    "1JN", "2JN", "3JN", "JUD", "REV", "OTH", "BAK", "GLO", "XXA", "XXB", "XXC", "XXF", "XXG"]

def findAll(permission):
	search = permission.split("*")
	lineSet = []
	dbprod = io.open(os.environ['HOME'] + "/ShortSands/DBL/FCBH/dbp_prod.txt", mode="r", encoding="utf-8")
	for line in dbprod:
		line = line.strip()
		if line.startswith(search[0]) and line.endswith(search[1]):
			lineSet.append(line)
	dbprod.close()
	return lineSet

def checkTextKey(key):
	parts = key.split(".")
	if parts[1] != 'html':
		return "Is not html file."
	pieces = parts[0].split("_")
	if len(pieces) != 4 and len(pieces) != 3:
		return "Is not 3 or 4 parts: " + len(pieces)
	if len(pieces[0]) != 6:
		return "First part is not 6 chars."
	sequence = float(pieces[1])
	if sequence < 0 or sequence > 106:
		return "Is not valid sequence number: " + sequence
	if not pieces[2] in bookIdList:
		return "Is not valid bookId: " + pieces[2]
	if len(pieces) > 3:
		chapter = float(pieces[3])
		if chapter < 1 or chapter > 151:
			return "Is not valid chapter: " + chapter
	return None

def checkAudioKey(key, damId):
	seqType = key[0:1]
	if seqType != "A" and seqType != "B":
		return "Sequence type must be A or B: " + seqType
	sequence = float(key[1:3])
	if sequence < 1 or sequence > 50:
		return "Is not a valid sequence number: " + sequence
	chapter = float(key[5:9].strip("_"))
	if chapter < 1 or chapter > 151:
		return "Is not a valid chapter: " + chapter
	parts = key.split("_")
	dmId = parts[len(parts) - 1].split(".")[0]
	if len(dmId) > 20:
		dmId = key[21:].split(".")[0]
	if dmId != damId:
		return "Is not correct damId: " + dmId
	return None

def getDamIdHack(damId):
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

input = io.open("PermissionsRequest.txt", mode="r", encoding="utf-8")

for line in input:
	if line[1:8] == "arn:aws":
		lineSet = set()
		line = line.strip("\n\",")
		permission = line[22:]
		lineSet = findAll(permission)
		print len(lineSet), "\t", permission
		if permission.startswith("text/"):
			for entry in lineSet:
				key = entry.split("/")[3]
				errMsg = checkTextKey(key)
				if not errMsg == None:
					print errMsg, entry
					sys.exit()

		if permission.startswith("audio/"):
			damId = permission.split("/")[2].strip("_")
			damId = getDamIdHack(damId)
			for entry in lineSet:
				key = entry.split("/")[3]
				errMsg = checkAudioKey(key, damId)
				if not errMsg == None:
					print errMsg, entry
					sys.exit()


 

