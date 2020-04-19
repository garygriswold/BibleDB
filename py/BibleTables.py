# BibleTables.py
#
# This program loads bible_sets, bibles, and bible_books
# It does comparison of bible filesets in LPTS, dbp-prod, and DBP
# 
#
import io
import os
import sys
import json
import csv
import unicodedata
import operator
from Config import *
from SqliteUtility import *
from LPTSExtractReader import *
from LookupTables import *

class Bible:

	def __init__(self, source, name, typeCode, bibleId, filesetId):
		self.source = source # LPTS | S3 | DBP
		self.name = name
		self.typeCode = typeCode # text | audio | video
		self.bibleId = bibleId
		self.filesetId = filesetId
		self.key = "%s/%s/%s" % (typeCode, bibleId, filesetId)
		self.iso3 = None
		self.script = None
		self.country = None
		self.allowApp = False
		self.allowAPI = False
		self.locales = []
		#self.scope = None

	def toString(self):
		allow = "app " if self.allowApp else ""
		allow += "api" if self.allowAPI else ""
		locales = "locales: %s" % (",".join(self.locales))
		return "%s, src=%s, iso3:%s, script:%s, country:%s, allow:%s, %s" % (self.key, self.source, self.iso3, self.script, self.country, allow, locales)



class BibleTables:

	def __init__(self, config):
		self.config = config
		self.lptsReader = LPTSExtractReader(config)
		self.db = SqliteUtility(config)
		self.scriptMap = self.db.selectMap("SELECT name, iso FROM Scripts", ())
		self.iso3Set = self.db.selectSet("SELECT iso3 FROM Languages", ())
		self.macroMap = self.db.selectMap("SELECT iso3, macro FROM Languages", ())
		self.iso1Map = self.db.selectMap("SELECT iso3, iso1 FROM Languages", ())
		self.localeSet = self.db.selectSet("SELECT distinct identifier FROM Locales", ())
		self.OTBookSet = {'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT',
			'1SA', '2SA', '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST', 'JOB',
			'PSA', 'PRO', 'ECC', 'SNG', 'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS',
			'JOL', 'AMO', 'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL'}
		self.NTBookSet = {'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO',
			'GAL', 'EPH', 'PHP', 'COL', '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM',
			'HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD', 'REV'}
		self.bibles = []
		self.bibleFilesets = []
		self.bibleFilesetLocales = []
		self.textFilesets = []
		self.audioFilesets = []
		self.textBibleBooks = []
		self.audioBibleBooks = []
		self.uniqueBibleCheck = {}


	def process(self):
		lptsMap = self.getLPTSMap()
		print("LPTS %d" % (len(lptsMap.keys())))

		s3Map = self.getS3Map(True) # incude rejected 
		print("S3 %d" % (len(s3Map.keys())))

		inS3SetNotLPTS = set(s3Map.keys()).difference(lptsMap.keys())
		print("IN S3 NOT LPTS %d" % (len(inS3SetNotLPTS)))
		for key in sorted(inS3SetNotLPTS):
			print("ERROR_11 IN S3 NOT LPTS %s" % (key))

		inLPTSNotS3 = set(lptsMap.keys()).difference(s3Map.keys())
		print("IN LPTS NOT S3 %s" % (len(inLPTSNotS3)))
		for key in sorted(inLPTSNotS3):
			print("ERROR_12 IN LPTS NOT s3 %s" % (key))

		inLptsAndS3Set = set(lptsMap.keys()).intersection(s3Map.keys())
		print("IN LPTS AND S3 %d" % (len(inLptsAndS3Set)))

		permittedMap = self.selectWithPermission(inLptsAndS3Set, lptsMap)
		print("IN LPTS WITH PERMISSION AND S3 %d" % (len(permittedMap.keys())))	

		withLocaleMap = self.selectWithLocale(permittedMap)
		print("IN LPTS WITH PERMISSION AND S3 AND LOCALE %d" % (len(withLocaleMap.keys())))	

		for item in withLocaleMap.values():
			print(item.toString())

		bibleGroupMap = self.groupByBibleId(withLocaleMap)
		print("IN BibleId MAP %d" % (len(bibleGroupMap.keys())))

		hasTextGroupMap = self.removeNonText(bibleGroupMap)
		print("IN BibleId MAP with TEXT %d" % (len(hasTextGroupMap.keys())))


	def displaySet(self, keySet):
		for key in sorted(keySet):
			print(key)


	def getLPTSMap(self):
		results = {}
		bibleMap = self.lptsReader.bibleIdMap
		for bibleId, lptsRecords in bibleMap.items():
			for (index, lptsRec) in lptsRecords:
				stockNum = lptsRec.Reg_StockNumber()
				for typeCode in {"text", "audio", "video"}:
					damIds = lptsRec.DamIds(typeCode, index)
					for damId in damIds:
						bible = Bible("LPTS", stockNum, typeCode, bibleId, damId)
						bible.iso3 = lptsRec.ISO()
						scriptName = lptsRec.Orthography(index)
						bible.script = LookupTables.scriptCode(scriptName)
						bible.country = lptsRec.Country() # convert to iso2
						if typeCode == "text":
							bible.allowAPI = (lptsRec.APIDevText() == "-1")
							bible.allowApp = (lptsRec.MobileText() == "-1")
						elif typeCode == "audio":
							bible.allowAPI = (lptsRec.APIDevAudio() == "-1")
							bible.allowApp = (lptsRec.DBPMobile() == "-1")
						elif typeCode == "video":
							bible.allowAPI = (lptsRec.APIDevVideo() == "-1")
							bible.allowApp = (lptsRec.MobileVideo() == "-1")
						if results.get(bible.key) != None:
							print("ERROR_01 Duplicate Key in LPTS %s" % (bible.key))
						else:
							results[bible.key] = bible
		return results


	def getS3Map(self, includeRejected):
		results = {}
		files1 = os.listdir(self.config.DIRECTORY_ACCEPTED)
		files2 = os.listdir(self.config.DIRECTORY_QUARANTINE)
		files = files1 + files2 if includeRejected else files1
		for file in files:
			if not file.startswith(".") and file.endswith(".csv"):
				filename = file.split(".")[0]
				(typeCode, bibleId, filesetId) = filename.split("_")
				if not filesetId.endswith("16"):
					bible = Bible("s3", filename, typeCode, bibleId, filesetId)
					if results.get(bible.key) != None:
						print("ERROR_02 Duplicate Key in bucket %s" % (bible.key))
					else:
						results[bible.key] = bible
		return results


	def selectWithPermission(self, bibleSubset, bibleMap):
		results = {}
		for key in bibleSubset:
			bible = bibleMap[key]
			if bible.allowApp or bible.allowAPI:
				results[key] = bible
		return results


	def selectWithLocale(self, bibleMap):
		results = {}
		for key, bible in bibleMap.items():
			perms = []
			perms.append((bible.iso3,))
			perms.append((bible.iso3, bible.country))
			perms.append((bible.iso3, bible.script))
			perms.append((bible.iso3, bible.script, bible.country))
			macro = self.macroMap.get(bible.iso3)
			perms.append((macro,))
			perms.append((macro, bible.country))
			perms.append((macro, bible.script))
			perms.append((macro, bible.script, bible.country))
			iso1 = self.iso1Map.get(bible.iso3)
			perms.append((iso1,))
			perms.append((iso1, bible.country))
			perms.append((iso1, bible.script))
			perms.append((iso1, bible.script, bible.country))
			locales = []
			for permutation in perms:
				if all(permutation):
					locale = "_".join(permutation)
					if locale in self.localeSet:
						locales.append(locale)
			if len(locales) > 0:
				bible.locales = locales
				results[key] = bible
		return results


	def groupByBibleId(self, bibleMap):
		results = {}
		for bible in bibleMap.values():
			bibles = results.get(bible.bibleId, [])
			bibles.append(bible)
			results[bible.bibleId] = bibles
		return results


	def removeNonText(self, bibleIdMap):
		results = {}
		for bibleId, bibles in bibleIdMap.items():
			hasText = False
			for bible in bibles:
				if bible.typeCode == "text":
					hasText = True
			if hasText:
				results[bibleId] = bibles
		return results


	##
	## Deprecated
	##


#	def process1(self):
#		bibleList = self.getBibleList({"text"})
#		for rec in bibleList:
#			if len(rec["fileset_id"]) != 6:
#				print("ERROR0", rec["fileset_id"])
#			info = self.readInfoJson(rec["bible_id"], rec["fileset_id"])
#			self.getFilesetData(rec, info)
#			rec["script"] = self.getScriptCode(info)
#			rec["numerals"] = self.getNumberCode(info)
#			rec["locales"] = self.matchBiblesToLocales(rec)
#			if len(rec["locales"]) > 0:
#				rec["scope"] = self.getScopeByCSVFile(rec["filename"])
#		reducedList = self.pruneList(bibleList)
#		self.testUniqueKeys(reducedList)
#
#		self.getPermissionsData2(reducedList)
#
#		mediaList = self.getBibleList({"audio", "video"})
#		for rec in mediaList:
#			rec["scope"] = self.getScopeByCSVFile(rec["filename"])
#		mediaMap5 = self.getFilesetPrefixMap(mediaList, 5)
#		mediaMap6 = self.getFilesetPrefixMap(mediaList, 6)
#		mediaMap7 = self.getFilesetPrefixMap(mediaList, 7)
#		mediaMapAll = self.getFilesetPrefixMap(mediaList, 20)
#
#		groupMap = {}
#		for rec in reducedList:
#			filesetId = rec["fileset_id"]
#			if len(filesetId) == 5:
#				groupRecs = mediaMap5.get(filesetId)
#			elif len(filesetId) == 7:
#				groupRecs = mediaMap7.get(filesetId)
#			else:
#				groupRecs = mediaMap6.get(filesetId)
#			if groupRecs != None:
#				groupMap[filesetId] = groupRecs
#				print("ERROR89: bible has %d media %s/%s" % (len(groupRecs), rec["bible_id"], filesetId), groupRecs)
#			else:
#				print("ERROR89: bible has no media %s/%s" % (rec["bible_id"], filesetId))
#
#		#self.getPermissionsData(groupMap)
#		self.insertVersions(groupMap)
#
#
#	def process2(self):
#		permissionsMap = {"APIDevText": "allowTextAPI",
#				"APIDevAudio": "allowAudioAPI",
#				"APIDevVideo": "allowVideoAPI",
#				"MobileText": "allowTextAPP",
#				"DBPMobile": "allowAudioAPP",
#				"MobileVideo": "allowVideoAPP"}
#		bibleList = []
#		permittedList = []
#		bibleMap = self.lptsReader.bibleIdMap
#		for bibleId, lptsRecords in bibleMap.items():
#			for (index, lptsRec) in lptsRecords:
#				stockNum = lptsRec.Reg_StockNumber()
#				#print(bibleId, index, stockNum)
#				#for typeCode in {"text", "audio", "video"}:
#				for typeCode in {"text"}:
#					damIds = lptsRec.DamIds(typeCode, index)
#					for damId in damIds:
#						rec = {}
#						rec["bible_id"] = bibleId
#						rec["fileset_id"] = damId
#						rec["typeCode"] = typeCode
#						#print(bibleId, damId, stockNum)
#
#						rec["iso3"] = lptsRec.ISO()
#						scriptName = lptsRec.Orthography(index)
#						rec["script"] = LookupTables.scriptCode(scriptName)
#						rec["country"] = lptsRec.Country()
#						rec["locales"] = self.matchBiblesToLocales(rec)
#						rec["scope"] = "NTOT" ## Dummy value
#						bibleList.append(rec)
#
#						permissionSet = set()
#						for lptsPermiss in permissionsMap.keys():
#							if lptsRec.record.get(lptsPermiss) == "-1":
#								permissionSet.add(permissionsMap[lptsPermiss])
#						rec["permissions"] = permissionSet
#						if len(permissionSet) > 0:
#							permittedList.append(rec)
#		reduced1List = self.pruneList(bibleList)
#		reduced2List = self.pruneList(permittedList)
#		for rec in reduced2List:
#			print(rec)
#		print("TOTAL %d  PERMITTED %d  LOCALE %d  PERMITTED+LOCALE %d"
#			% (len(bibleList), len(permittedList), len(reduced1List), len(reduced2List)))
#
#
#	## create bible list of (typeCode, bibleId, filesetId from cvs files)
#	def getBibleList(self, selectSet):
#		results = []
#		files1 = os.listdir(self.config.DIRECTORY_ACCEPTED)
#		files2 = os.listdir(self.config.DIRECTORY_QUARANTINE)
#		#files = files1 + files2
#		files = files1 # ONLY ACCEPTED ARE BEING USED. Is this OK?
#		for file in files:
#			if not file.startswith(".") and file.endswith(".csv"):
#				filename = file.split(".")[0]
#				(typeCode, bibleId, filesetId) = filename.split("_")
#				if typeCode in selectSet:
#					record = {}
#					record["filename"] = file
#					record["typeCode"] = typeCode
#					record["bible_id"] = bibleId
#					record["fileset_id"] = filesetId
#					results.append(record)
#		return results

    ## read and parse a info.json file for a bibleId, filesetId
	def readInfoJson(self, bibleId, filesetId):
		info = None
		filename = "%stext:%s:%s:info.json" % (self.config.DIRECTORY_INFO_JSON, bibleId, filesetId)
		if os.path.isfile(filename):
			fp = io.open(filename, mode="r", encoding="utf-8")
			data = fp.read()
			try:
				info = json.loads(data)
			except Exception as err:
				print("ERROR: Json Error in %s:%s:info.json " % (bibleId, filesetId), err)
			fp.close()
		else:
			print("ERROR: info.json NOT FOUND,", bibleId, filesetId)
		return info


    # extract fileset data from info.json data
	def getFilesetData(self, rec, info):
		rec["abbreviation"] = rec["fileset_id"][3:]
		if info != None:
			iso3 = info["lang"].lower()
			rec["nameLocal"] = info["name"]
			rec["name"] = info["nameEnglish"]
			rec["country"] = info["countryCode"] if info["countryCode"] != '' else None
		else:
			iso3 = rec["fileset_id"][:3].lower()
			rec["nameLocal"] = None
			rec["name"] = None
			rec["country"] = None
		if rec["fileset_id"] in {"GUDBSC", "KORKRV", "MDAWBT"}:
			iso3 = rec["fileset_id"][:3].lower()
		if rec["fileset_id"][:3].lower() != iso3:
			if rec["bible_id"][:3].lower() != iso3:
				print("WARN: iso %s and name %s are not the same in %s/%s" % (iso3, rec["fileset_id"][:3], rec["bible_id"], rec["fileset_id"]))
		corrections = {
		"ACCNNT/ACCNNT": "acr",
		"AVRIBT/AVRIBT": "gor",
		"DEUL12/GERL12": "deu",
		"DTPAKK/KZJAKK": "dtp",
		"ELLELL/GRKSFT": "ell",
		"KANWTC/ERVWTC": "kan",
		"KINSIX/RUAICG": "kin",
		"KMRKLA/KM1KLA": "kmr",
		#"QUJPCM/QUJPCM": "?",
		"SDMGFA/SDMGFA": "gef",
		"TURBLI/TRKWTC": "tur",
		"TURBST/TRKBST": "tur",
		"TZESBM/TZESBM": "tzo",
		"TZHBSM/TZBSBM": "tzh",
		"TZOCHM/TZCSBM": "tzo",
		"YUEUNV/YUHUNV": "yue",
		"ZLMTMV/MLYBSM": "zsm",
		"ZLMTMV/ZLMBSM": "zsm",
		"AZEBSAC/AZ1BSA": "azj",
		"SDMSGV/SDMSGV": "gef"}
		change = corrections.get(rec["bible_id"] + "/" + rec["fileset_id"])
		if change != None:
			iso3 = change
		if iso3 == None or iso3 not in self.iso3Set:
			print("WARN: iso %s is unknown for %s/%s" % (iso3, rec["bible_id"], rec["fileset_id"]))
		rec["iso3"] = iso3


	## extract script code from book name text in info.json
	def getScriptCode(self, info):
		if info != None:
			bookNames = info["divisionNames"]
			if bookNames != None:
				for bookName in bookNames:
					for bookChar in bookName:
						name = unicodedata.name(bookChar)
						if name != None:
							parts = name.split(" ")
							if parts[0] == "TAI" and len(parts) > 1:
								firstPart = parts[0] + " " + parts[1]
							else:
								firstPart = parts[0]
							scriptCode = self.scriptMap.get(firstPart)
							return scriptCode
		return None


	## extract numerals code from numbers in info.json
	def getNumberCode(self, info):
		if info != None:
			numbers = info["numbers"]
			for number in numbers:
				for digit in number:
					name = unicodedata.name(digit)
					if name != None or name == "":
						return "western-arabic"
					elif name.startswith("ARABIC-INDIC"):
						return "eastern-arabic"
					elif name.startswith("EXTENDED ARABIC-INDIC"):
						return "extended eastern-arabic"
					else:
						return name.lower()
		return None


#	def matchBiblesToLocales(self, rec):
#		iso3 = rec["iso3"]
#		script = rec["script"]
#		country = rec["country"]
#		perms = []
#		perms.append((iso3,))
#		perms.append((iso3, country))
#		perms.append((iso3, script))
#		perms.append((iso3, script, country))
#		macro = self.macroMap.get(iso3)
#		perms.append((macro,))
#		perms.append((macro, country))
#		perms.append((macro, script))
#		perms.append((macro, script, country))
#		iso1 = self.iso1Map.get(iso3)
#		perms.append((iso1,))
#		perms.append((iso1, country))
#		perms.append((iso1, script))
#		perms.append((iso1, script, country))
#		locales = []
#		for permutation in perms:
#			if all(permutation):
#				locale = "_".join(permutation)
#				if locale in self.localeSet:
#					locales.append(locale)
#		return locales


	## compute size code for each 
	def getScopeByCSVFile(self, filename):
		bookIdSet = set()
		with open(self.config.DIRECTORY_ACCEPTED + filename, newline='\n') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				bookIdSet.add(row["book_id"])
		return self.getScope(bookIdSet)


	def getScope(self, bookIdSet):
		otBooks = bookIdSet.intersection(self.OTBookSet)
		ntBooks = bookIdSet.intersection(self.NTBookSet)
		hasNT = len(ntBooks)
		hasOT = len(otBooks)
		if hasNT >= 27:
			if hasOT >= 39:
				return "NTOT"#"C"
			elif hasOT > 0:
				return "NTOTP"
			else:
				return "NT"

		elif hasNT > 0:
			if hasOT >= 39:
				return "OTNTP"
			elif hasOT > 0:
				return "NTPOTP"
			else:
				return "NTP"

		else:
			if hasOT >= 39:
				return "OT"
			elif hasOT > 0:
				return "OTP"
			else:
				return "P"


#	## prune list of Bibles based upon multiple criteria
#	def pruneList(self, records):
#		results = []
#		for rec in records:
#			locales = rec.get("locales")
#			if locales != None and len(locales) > 0:
#				results.append(rec)
#				if rec["scope"] not in {"NTOT","NTOTP","NT","OTNTP","OT"}:
#					print("\nSCOPE: DROP ?", rec)
#		return results		
#

	def testUniqueKeys(self, records):
		results1 = {}
		results2 = {}
		results3 = {}
		for rec in records:
			print(rec)
			print("LANG:", rec["bible_id"], rec["fileset_id"], rec["iso3"], rec.get("script"), rec.get("country"), rec["locales"])
			records1 = results1.get(rec["bible_id"], [])
			if len(records1) > 0:
				print("\nWARN: bible_id DUP", rec, records1)
			records1.append(rec)
			results1[rec["bible_id"]] = records1
			if len(rec["fileset_id"]) != 6:
				print("\nERROR: filesetid len not 6", rec)
			records2 = results2.get(rec["fileset_id"], [])
			if len(records2) > 0:
				print("\nWARN: fileset_id DUP", rec, records2)
			records2.append(rec)
			results2[rec["fileset_id"]] = records2
			key = rec["iso3"] + "/" + rec["abbreviation"]
			records3 = results3.get(key, [])
			if len(records3) > 0:
				print("\nWARN: iso/abbrev DUP", rec, records2)
			records3.append(rec)
			results3[key] = records3


#	def getFilesetPrefixMap(self, records, keyLength):
#		result = {}
#		for rec in records:
#			prefix = rec["fileset_id"][:keyLength]
#			recs2 = result.get(prefix, [])
#			recs2.append(rec)
#			result[prefix] = recs2
#		return result
#
#
#	def getPermissionsData(self, groupMap):
#		permissionsMap = {"APIDevText": "allowTextAPI",
#						"APIDevAudio": "allowAudioAPI",
#						"APIDevVideo": "allowVideoAPI",
#						"MobileText": "allowTextAPP",
#						"DBPMobile": "allowAudioAPP",
#						"MobileVideo": "allowVideoAPP"}
#		for filesetId, records in groupMap.items():
#			for rec in records:
#				permissionSet = set()
#				lptsResults = self.lptsReader.getFilesetRecords(filesetId)
#				if lptsResults == None or len(lptsResults) == 0:
#					print("ERROR99 %s has no LPTS Record" % (rec["fileset_id"]))
#				elif len(lptsResults) > 1:
#					print("ERROR98 %s has %d LPTS Records" % (rec["fileset_id"], len(lptsResults)))
#				if lptsResults != None:
#					for status, lptsRecord in lptsResults:
#						if status in {"Live", "live"}:
#							for lptsPermiss in permissionsMap.keys():
#								if lptsRecord.record.get(lptsPermiss) == "-1":
#									permissionSet.add(permissionsMap[lptsPermiss])
#				rec["permissions"] = permissionSet
#				print("LPTS ", filesetId, permissionSet)
#
#
#	def getPermissionsData2(self, records):
#		permissionsMap = {"APIDevText": "allowTextAPI",
#						"APIDevAudio": "allowAudioAPI",
#						"APIDevVideo": "allowVideoAPI",
#						"MobileText": "allowTextAPP",
#						"DBPMobile": "allowAudioAPP",
#						"MobileVideo": "allowVideoAPP"}
#		permissionCount = 0
#		for rec in records:
#			permissionSet = set()
#			filesetId = rec["fileset_id"]
#			lptsResults = self.lptsReader.getFilesetRecords(filesetId)
#			if lptsResults == None or len(lptsResults) == 0:
#				print("ERROR99 %s has no LPTS Record" % (filesetId))
#			elif len(lptsResults) > 1:
#				print("ERROR98 %s has %d LPTS Records" % (filesetId, len(lptsResults)))
#			if lptsResults != None:
#				for status, lptsRecord in lptsResults:
#					if status not in {"Live", "live"}:
#						for lptsPermiss in permissionsMap.keys():
#							if lptsRecord.record.get(lptsPermiss) == "-1":
#								permissionSet.add(permissionsMap[lptsPermiss])
#			rec["permissions"] = permissionSet
#			if len(permissionSet) > 0:
#				permissionCount += 1
#				print("ERROR95 %s has permissions" % (filesetId))
#			else:
#				print("ERROR97 %s has no permission" % (filesetId))
#			print("LPTS ", filesetId, permissionSet)
#		print("PERMISSION %d TOTAL RECS %d" % (permissionCount, len(records)))

	def insertVersions(self, biblesMap):
		values = []
		for biblesMapKey, bibles in biblesMap.items():
			isoSet = set()
			abbrevSet = set()
			nameSet = set()
			nameLocalSet = set()
			for rec in bibles:
				if rec["typeCode"] == "text":
					print(rec)
					sys.exit()
					isoSet.add(rec["iso3"])
					abbrevSet.add(rec["abbreviation"])
					nameSet.add(rec["name"])
					nameLocalSet.add(rec["nameLocal"])
			iso3 = ",".join(isoSet)
			abbreviation = ",".join(abbrevSet)
			nameSet = ",".join(nameSet)
			nameLocalSet = ",".join(nameLocalSet)
			values.append((iso3, abbreviation, nameSet, nameLocalSet))
		self.insert("versions", ("iso3","abbreviation","name", "nameLocal"), values)
		#versionCode = bibleId[3:]
		#iso3s = {}
		#versionNames = {}
		#englishNames = {}
		#for info in infoMaps:
		#	self.addOne(iso3s, info["lang"].lower())
		#	self.addOne(versionNames, info["name"])
		#	self.addOne(englishNames, info["nameEnglish"])
		#iso3 = self.getBest("iso3", iso3s)
		#versionName = self.getBest("versionName", versionNames)
		#englishName = self.getBest("englishName", englishNames)
		#values = (bibleId, iso3, versionCode, versionName, englishName)
		#duplicate = self.uniqueBibleCheck.get(bibleId)
		#if duplicate != None:
		#	print("Duplicate %s and %s" % (",".join(duplicate), ",".join(values)))
		#else:
		#	self.uniqueBibleCheck[bibleId] = values
		#	self.bibles.append(values)	


	#def addOne(self, hashMap, item):
	#	if item != None:
	#		count = hashMap.get(item, 0)
	#		hashMap[item] = count + 1


	#def getBest(self, name, hashMap):
	#	upper = 0
	#	best = None
	#	for (value, count) in hashMap.items():
	#		if count > upper:
	#			upper = count
	#			best = value
	#	if len(hashMap.keys()) > 1:
	#		print("map", hashMap)
	#		print("best", best)
	#	return best
		#print(name, hashMap)
		#desc = sorted(hashMap.items(), key=operator.itemgetter(1))
		#print(name, desc)
		#return ("ds")
		#return desc.keys()[0]

###
### deprecated code follows
###

	def insertFilesets(self, bibleId, filesetId, infoJson):
		sizeCode = "To be done"
		if filesetId[8:10] == "VD":
			bucket = self.config.S3_DBP_VIDEO_BUCKET
		else:
			bucket = self.config.S3_DBP_BUCKET
		ownerId = 0 # TO BE DONE
		copyrightYear = "" # TO BE DONE
		filenameTemplate = "" # TO BE DONE, must open file, or do manually
		self.bibleFilesets.append((filesetId, bibleId, sizeCode, bucket, ownerId, 
			copyrightYear, filenameTemplate))


	def insertFilesetLocales(self, bibleId, filesetId, script, infoJson):
		#row = {}
		#row["fileset_id"] = filesetId
		iso3 = infoJson["lang"].lower()
		#script = self.getScriptCode(infoJson)
		country = infoJson["countryCode"]
		if country == "":
			country = None
		print(bibleId, filesetId, iso3, script, country)
		if iso3 in self.iso3Set:
			# Some of these inserted iso3 codes will not be in locale, check how many
			self.appendInserts(filesetId, iso3, script, country)
		macroLang = self.macroMap.get(iso3)
		if macroLang != None:
			print("Insert macro", macroLang)
			self.appendInserts(filesetId, macroLang, script, country)
		iso1Lang = self.iso1Map.get(iso3)
		if iso1Lang != None:
			print("Insert iso1", iso1Lang)
			self.appendInserts(filesetId, iso1Lang, script, country)


	def appendInserts(self, filesetId, lang, script, country):
		self.bibleFilesetLocales.append({"fileset_id": filesetId, "locale": lang})
		if country != None:
			locale = lang + "_" + country
			self.bibleFilesetLocales.append({"fileset_id": filesetId, "locale": locale})
		if script != None:
			locale = lang + "_" + script
			self.bibleFilesetLocales.append({"fileset_id": filesetId, "locale": locale})
		if script != None and country != None:
			locale = lang + "_" + script + "_" + country
			self.bibleFilesetLocales.append({"fileset_id": filesetId, "locale": locale})		


	def insertTextFilesets(self, bibleId, filesetId, script, infoJson):
		numeralsId = self.getNumberCode(infoJson)
		font = infoJson["fontClass"]
		self.textFilesets.append((filesetId, script, numeralsId, font))


	def insertAudioFilesets(self, bibleId, filesetId, infoJson):
		if filesetId[7:10] == "1DA":
			audioType = "nondrama"
		elif filesetId[7:10] == "2DA":
			audioType = "drama"
		else:
			print("ERROR: audio fileset %s has unknown type" % (filesetId))
			audioType = "unknown" # or None
		bitrate = filesetId[10:12]
		if bitrate == "":
			bitrate = "64"
		self.audioFilesets.append((filesetId, audioType, bitrate))


	def insertVideoFilesets(self, bibleId, filesetId, infoJson):
		print("video filesets to be done")


	def insertTextBibleBooks(self, bibleId, filesetId, infoJson):
		bookChapMap = self.getBookNamesChapters("text", bibleId, filesetId)
		bookIds = self.getBookSequence("text", bibleId, filesetId)
		bookNameMap = {}
		books = infoJson.get("divisions") 
		names = infoJson.get("divisionNames")
		for index in range(len(books)):
			bookNameMap[books[index]] = names[index]
		for index in range(len(bookIds)):
			bookId = bookIds[index]
			name = bookNameMap.get(index)
			bookData = bookChapMap.get(bookId)
			numChapters = bookData[1] if bookData != None else None
			#numChapters = bookChapMap[bookId]
			self.textBibleBooks.append((filesetId, bookId, index + 1, name, numChapters))
		else:
			print("ERROR: filesets %s/%s has no books info in info.json" % (bibleId, filesetId))


	def insertAudioBibleBooks(self, bibleId, filesetId, infoJson):
		bookChapMap = self.getBookNamesChapters("audio", bibleId, filesetId)
		books = self.getBookSequence("audio", bibleId, filesetId)
		print(books)
		for index in range(len(books)):
			bookId = books[index]
			bookData = bookChapMap.get(bookId)
			if bookData != None:
				(bookName, chapt) = bookData
				self.audioBibleBooks.append((filesetId, bookId, index + 1, bookName, chapt))


	def getBookNamesChapters(self, typeCode, bibleId, filesetId):
		filename = "%s%s_%s_%s.csv" % (ACCEPTED_DIR, typeCode, bibleId, filesetId)
		bookChapMap = {}
		with open(filename) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for file in csv_reader:
				bookName = file[3] # This is incorrect, bookname must be added to CVS
				bookId = file[4]
				chapt = file[5]
				bookChapMap[bookId] = (bookName, chapt) # At end will be last chapter
		return bookChapMap


	def getBookSequence(self, typeCode, bibleId, filesetId):
		filename = "%s%s_%s_%s.csv" % (ACCEPTED_DIR, typeCode, bibleId, filesetId)
		bookSet = set()
		bookList = []
		with open(filename) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for file in csv_reader:
				bookId = file[4]
				if not bookId in bookSet:
					bookSet.add(bookId)
					bookList.append(bookId)
		return bookList


	def unloadDB(self):
		print("unloadDB")
		tables = ["versions"]
		#tables = ["bibles","bible_filesets","bible_fileset_locales","text_filesets",
		#	"audio_filesets","text_bible_books","audio_bible_books"]
		tables.reverse()
		for table in tables:
			self.db.execute("DELETE FROM %s" % (table), ())


	def loadDB(self):
		print("loadDB")
		#self.insert("bibles", ("bible_id","iso3","version_code","version_name",
		#	"english_name"), self.bibles)
		self.insert("bible_filesets", ("fileset_id","bible_id","size_code", 
			"bucket","owner_id","copyright_year","filename_template"), self.bibleFilesets)
		self.insert("bible_fileset_locales", ("locale","fileset_id"), self.bibleFilesetLocales)
		self.insert("text_filesets", ("fileset_id","script","numerals_id","font"), self.textFilesets)
		self.insert("audio_filesets", ("fileset_id","audio_type","bitrate"), self.audioFilesets)
		self.insert("text_bible_books", ("fileset_id","book_id","sequence","localized_name","num_chapters"), self.textBibleBooks)
		self.insert("audio_bible_books", ("fileset_id","book_id","sequence","s3_name","num_chapters"), self.audioBibleBooks)


	def insert(self, table, columns, values):
		print(table, columns, len(values))
		if len(values) > 0:
			places = ['?'] * len(columns)
			print(places, len(places))
			sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(columns), ",".join(places))
			self.db.executeBatch(sql, values)


if __name__ == "__main__":
	config = Config()
	tables = BibleTables(config)
	#tables.unloadDB()
	tables.process()



