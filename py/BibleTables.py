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

	def __init__(self, srcType, source, typeCode, bibleId, filesetId):
		self.versionKey = None
		self.versionId = None
		self.systemId = None
		self.srcType = srcType # LPTS | S3 | DBP
		self.source = source
		self.typeCode = typeCode # text | audio | video
		self.bibleId = bibleId
		self.filesetId = filesetId
		self.key = "%s/%s/%s" % (typeCode, bibleId, filesetId)
		if typeCode == "text":
			self.s3Key = "%s/%s/%s" % (typeCode, bibleId, filesetId[:6])
		else:
			self.s3Key = self.key
		abbrev = filesetId[3:6]
		if abbrev == "WTC":
			self.abbreviation = "ERV"
		else:
			self.abbreviation = abbrev
		self.lptsStockNo = None
		self.iso3 = None
		self.script = None
		self.country = None
		self.allowAPI = False
		self.allowApp = False
		self.allowWeb = False
		self.locales = []
		self.priority = 0
		self.bucket = None
		self.filePrefix = None
		self.fileTemplate = None
		## Text only data
		self.name = None
		self.nameLocal = None
		self.numerals = None
		self.bibleZipFile = None

	def toString(self):
		permiss = []
		if self.allowAPI:
			permiss.append("api")
		if self.allowApp:
			permiss.append("app")
		if self.allowWeb:
			permiss.append("web")
		allow = " ".join(permiss)
		locales = "locales: %s" % (",".join(self.locales))
		return "%s, src=%s, allow:%s, %s_%s_%s, %s" % (self.key, self.srcType, allow, self.iso3, self.script, self.country, locales)


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
		self.countryMap = self.db.selectMap("SELECT name, iso2 FROM Countries", ())
		countryAdditions = {"Congo, Democratic Republic of the": "CD",
						"Congo, Republic of the": "CG",
						"Cote D'Ivoire": "CI",
						"Cote d'Ivoire": "CI",
						"Korea, North": "KP",
						"Korea, South": "KR",
						"Laos": "LA",
						"Micronesia, Federated States of": "FM",
						"Netherlands Antilles": "NL",
						"Russia": "RU",
						"Vatican State": "VA",
						"Vietnam": "VN",
						"Virgin Islands, US": "VI"}
		self.countryMap.update(countryAdditions)


	def process(self):
		lptsMap = self.getLPTSMap()
		print("COUNT: LPTS %d" % (len(lptsMap.keys())))

		s3Map = self.getS3Map(False) # exclude rejected 
		print("COUNT: S3 %d" % (len(s3Map.keys())))

		self.differenceMap(s3Map, lptsMap, "ERROR_11 IN S3 NOT LPTS %s", "COUNT: IN S3 NOT LPTS %d")
		self.differenceMap(lptsMap, s3Map, "ERROR_12 IN LPTS NOT s3 %s", "COUNT: IN LPTS NOT S3 %d")
		inLptsAndS3Map = self.intersectionMap(lptsMap, s3Map)
		print("COUNT: IN LPTS IN S3 %d" % (len(inLptsAndS3Map)))

		permittedMap = {}
		for key, bible in inLptsAndS3Map.items():
			#if bible.allowAPI or bible.allowApp:
			if bible.allowAPI:
				permittedMap[key] = bible
		print("COUNT: IN LPTS IN S3 WITH PERMISSION %d" % (len(permittedMap.keys())))

		shortSandsMap = self.getShortSandsMap()
		print("COUNT: Short Sands text Bibles in S3 %d" % (len(shortSandsMap.keys())))

		for key, bible in shortSandsMap.items():
			permittedBible = permittedMap.get(key)
			if permittedBible != None:
				print("ERROR_13 DBP Bible overwritten by ShortSands", permittedBible.toString())
			permittedMap[key] = bible
		print("COUNT: ShortSands added to LPTS IN S3 WITH PERMISSION %d" % (len(permittedMap.keys())))

		withLocaleMap = self.selectWithLocale(permittedMap)
		print("COUNT: IN LPTS WITH PERMISSION IN S3 AND LOCALE %d" % (len(withLocaleMap.keys())))	

		self.getNumberCode(withLocaleMap)

		bibleGroupMap = self.groupByVersion(withLocaleMap)
		print("COUNT: IN BibleId MAP %d" % (len(bibleGroupMap.keys())))

		hasTextGroupMap = self.removeNonText(bibleGroupMap) # remove Version w/o text
		print("COUNT: IN BibleId MAP with TEXT %d" % (len(hasTextGroupMap.keys())))

		self.insertVersions(hasTextGroupMap)
		self.insertVersionLocales(hasTextGroupMap)
		self.insertBibles(hasTextGroupMap)
		self.insertBibleBooks(hasTextGroupMap)

		self.setScopeByBibleBooks()

		#TBD This is not working right. Fix scope first
#		dupBiblesRemovedMap = self.removeDupBibles(hasTextGroupMap)
#		dupBiblesRemovedMap = hasTextGroupMap
#		print("COUNT: IN BibleId MAP with TEXT, DUPS REMOVED %d" % (len(dupBiblesRemovedMap.keys())))


		### ERRROR the 16 bit rate audios are missing from the LPTS SET
		### Do I want them?


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
						bible.lptsStockNo = lptsRec.Reg_StockNumber()
						bible.iso3 = lptsRec.ISO()
						countryName = lptsRec.Country()
						if countryName not in {None, "Region-wide"}:
							bible.country = self.countryMap[countryName] # fail fast
						if bible.iso3 == "spa":
							if bible.abbreviation == "RVC":
								bible.country = "ES"
							elif bible.abbreviation in {"ERV", "BDA", "NVI", "R60"}:
								bible.country = "419"
						scriptName = lptsRec.Orthography(index)
						bible.script = LookupTables.scriptCode(scriptName)
						if bible.script == None or bible.script == "" or bible.script == "Hani":
							if bible.bibleId == "CMNUN1":
								bible.script = "Hans"
							elif bible.bibleId == "CMNUNV":
								bible.script = "Hant"
								bible.country = "HK"
							elif bible.bibleId == "DIVWYI":
								bible.script = "Thaa"
							elif bible.bibleId == "HAUCLV":
								bible.script = "Latn"
							elif bible.bibleId == "UIGUMK":
								bible.script = "Arab"
							elif bible.bibleId == "YUEUNV":
								bible.script = "Hant"
							elif bible.iso3 in {"eng", "ind", "por", "spa"}:
								bible.script = "Latn"
							else:
								print("ERROR_19 script is blank or Hani %s" % (bible.toString()))
						if bible.bibleId == "HAKTHV":
							bible.script = "Hant"
						if typeCode == "video":
							bible.bucket = self.config.S3_DBP_VIDEO_BUCKET
						else:
							bible.bucket = self.config.S3_DBP_BUCKET
						bible.filePrefix = bible.key
						if typeCode == "text":
							bible.allowAPI = (lptsRec.APIDevText() == "-1")
							bible.allowApp = (lptsRec.MobileText() == "-1")
							bible.allowWeb = (lptsRec.HubText() == "-1")
						elif typeCode == "audio":
							bible.allowAPI = (lptsRec.APIDevAudio() == "-1")
							bible.allowApp = (lptsRec.DBPMobile() == "-1")
							bible.allowWeb = (lptsRec.DBPWebHub() == "-1")
						elif typeCode == "video":
							bible.allowAPI = (lptsRec.APIDevVideo() == "-1")
							bible.allowApp = (lptsRec.MobileVideo() == "-1")
							bible.allowWeb = (lptsRec.WebHubVideo() == "-1")
						if typeCode == "text":
							bible.name = lptsRec.Version()
							if bible.name == None or bible.name == "":
								bible.name = lptsRec.Volumne_Name()
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


	## Report errors on those Bibles that are in primary, but not secondary
	def differenceMap(self, primaryMap, secondaryMap, errMsg, countMsg):
		secondaryS3Map = {}
		for secBible in secondaryMap.values():
			secondaryS3Map[secBible.s3Key] = secBible
		missingCount = 0
		for primBible in primaryMap.values():
			primS3Key = primBible.s3Key
			secBible = secondaryS3Map.get(primS3Key)
			if secBible == None:
				missingCount += 1
				print(errMsg % (primBible.key))
		print(countMsg % (missingCount))


	def intersectionMap(self, lptsMap, s3Map):
		results = {}
		for lptsBible in lptsMap.values():
			lptsKey = lptsBible.s3Key
			s3Bible = s3Map.get(lptsKey)
			if s3Bible != None:
				results[lptsBible.key] = lptsBible
		return results


	def getShortSandsMap(self):
		results = {}
		with open("data/ShortsandsBibles.csv", newline='\n') as csvfile:
			reader = csv.reader(csvfile)
			for (bibleZipFile, abbr, iso3, scope, versionPriority, name, englishName,
				localizedName, textBucket, textId, keyTemplate, 
				audioBucket, otDamId, ntDamId, ios1, script, country) in reader:
					bestFileset = self._findBestFileset(textId, otDamId, ntDamId)
					bibleId = bestFileset.split("/")[1]
					filesetId = textId.split("/")[2]
					bible = Bible("SS", "shortsands", "text", bibleId, filesetId)
					bible.bibleZipFile = bibleZipFile
					bible.abbreviation = abbr
					bible.iso3 = iso3
					bible.script = script
					bible.country = country
					bible.allowApp = True
					bible.allowAPI = True
					if scope == "B":
						bible.scope = "NTOT"
					elif scope == "N":
						bible.scope = "NT"
					bible.priority = versionPriority
					bible.bucket = "text-%R-shortsands"
					bible.filePrefix = textId
					bible.fileTemplate = keyTemplate
					bible.name = englishName
					bible.nameLocal = name
					results[bible.key] = bible
		return results


	def _findBestFileset(self, textId, otDamId, ntDamId):
		return textId
		#prefSeq = [ntDamId, otDamId, textId]
		#for did in (otDamId, ntDamId, textId):
		#	if did != None and did != "":
		#		return did
		#return None # should not happen


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


	def groupByVersion(self, bibleMap):
		results = {}
		for bible in bibleMap.values():
			# putting script in key looses audios and videos that have no script
			# bible.versionKey = "%s-%s-%s" % (bible.iso3, bible.abbreviation, bible.script)
			bible.versionKey = "%s-%s" % (bible.iso3, bible.abbreviation)
			bibleList = results.get(bible.versionKey, [])
			bibleList.append(bible)
			results[bible.versionKey] = bibleList
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


    ## deprecated.  I should actual listings from buckets
    ## And I should get local chapter names from USX files.
	def readInfoJson(self, bibleId, filesetId):
		info = None
		filename = "%stext:%s:%s:info.json" % (self.config.DIRECTORY_DBP_INFO_JSON, bibleId, filesetId[:6])
		if not os.path.isfile(filename):
			filename = "%stext:%s:%s:info.json" % (self.config.DIRECTORY_MY_INFO_JSON, bibleId, filesetId[:6])
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


	def getNumberCode(self, bibleMap):
		for key, bible in bibleMap.items():
			if bible.typeCode == "text":
				iso3 = bible.iso3
				script = bible.script
				if script == "Arab":
					if iso3 in {"fas", "pes" }:
						bible.numerals = "persian"
					elif iso3 == "urd": 
						bible.numerals = "urdu"
					else:
						 bible.numerals = "arabic"
				elif script == "Deva":
					if iso3 == "ben":
						bible.numerals = "bengali"
					elif iso3 == "kan":
						bible.numerals = "kannada"
					else:
						bible.numerals = "devanagari"
				else:
					numerals = {
						"Beng": "bengali",
						"Cyrl": "western",
						"Ethi": "western",
						"Grek": "western",
						"Gujr": "gujarati",
						"Guru": "gurmukhi",
						"Hani": "chinese",
						"Hant": "chinese",
						"Hans": "chinese",
						"Jpan": "western",
						"Khmr": "khmer",
						"Kore": "korean",
						"Knda": "kannada",
						"Laoo": "lao",
						"Latn": "western",
						"Limb": "limbu",
						"Mlym": "malayalam",
						"Mymr": "burmese",
						"Orya": "oriya",
						"Syrc": "syriac",
						"Taml": "tamil",
						"Telu": "telugu",
						"Thaa": "western",
						"Thai": "thai"}
					bible.numerals = numerals.get(script)
					if bible.numerals == None:
						print("ERROR_18 unknown script %s for iso %s in getNumberCode" % (script, iso3))


	def getCSVFilename(self, s3FilePrefix):
		filename = s3FilePrefix.replace("/", "_") + ".csv"
		filePath = self.config.DIRECTORY_ACCEPTED + filename
		if os.path.isfile(filePath):
			return filePath
		filePath = self.config.DIRECTORY_QUARANTINE + filename
		if os.path.isfile(filePath):
			return filePath
		return None


	def removeDupBibles(self, bibleIdMap):
		results = {}
		for versionKey in sorted(bibleIdMap.keys()):
			textSet = set()
			audioSet = set()
			dramaSet = set()
			values = []
			for bible in bibleIdMap[versionKey]:
				if bible.typeCode == "text":
					textSet.add(bible)
				elif bible.typeCode == "audio":
					if bible.filesetId[7:8] == "1":
						audioSet.add(bible)
					else:
						dramaSet.add(bible)
				else:
					values.append(bible)
			self._removeDups(values, textSet)
			self._removeDups(values, audioSet)
			self._removeDups(values, dramaSet)
			results[versionKey] = values
		return results


	def _removeDups(self, values, bibleSet):
		hasNTOT = None
		for bible in bibleSet:
			if bible.scope == "NTOT":
				hasNTOT = bible
		if hasNTOT:
			values.append(hasNTOT)
		else:
			for bible in bibleSet:
				values.append(bible)


	def insertVersions(self, bibleIdMap):
		values = []
		versionId = 0
		for versionKey in sorted(bibleIdMap.keys()):
			versionId += 1
			versionKeyList = []
			isoSet = set()
			abbrevSet = set()
			scriptSet = set()
			numeralsSet = set()
			countrySet = set()
			nameSet = set()
			nameLocalSet = set()
			for bible in bibleIdMap[versionKey]:
				bible.versionId = versionId
				if bible.typeCode == "text":
					versionKeyList.append(bible.key)
					isoSet.add(bible.iso3)
					abbrevSet.add(bible.abbreviation)
					if bible.script != None:
						scriptSet.add(bible.script)
					if bible.numerals != None:
						numeralsSet.add(bible.numerals)
					if bible.country != None:
						countrySet.add(bible.country)
					if bible.name != None and bible.name != "":
						nameSet.add(bible.name)
					if bible.nameLocal != None and bible.nameLocal != "":
						nameLocalSet.add(bible.nameLocal)
			if len(versionKeyList) > 1:
				print("ERROR_17 multiple texts for versionKey=%s." % (versionKey), versionKeyList)
			iso3 = ":".join(isoSet) if len(isoSet) > 0 else None
			abbreviation = ":".join(abbrevSet) if len(abbrevSet) > 0 else None
			script = ":".join(scriptSet) if len(scriptSet) > 0 else None
			numerals = ":".join(numeralsSet) if len(numeralsSet) > 0 else None
			country = ":".join(countrySet) if len(countrySet) > 0 else None
			name = max(nameSet, key=len)
			nameLocal = ":".join(nameLocalSet) #if len(nameLocalSet) > 0 else None
			values.append((versionId, iso3, abbreviation, script, country, numerals, name, nameLocal))
		self.insert("Versions", ("versionId", "iso3", "abbreviation", "script",
				"country", "numerals", "name", "nameLocal"), values)


	def insertVersionLocales(self, bibleIdMap):
		values = []
		for versionKey in sorted(bibleIdMap.keys()):
			locales = set()
			versionIdSet = set()
			for bible in bibleIdMap[versionKey]:
				versionIdSet.add(bible.versionId)
				for locale in bible.locales:
					locales.add(locale)
			if len(versionIdSet) > 1:
				print("FATAL ERROR in versionId set")
				sys.exit()
			versionId = list(versionIdSet)[0]
			for locale in locales:
				values.append((locale, versionId))
		self.insert("VersionLocales", ("locale", "versionId"), values)


	def insertBibles(self, bibleIdMap):
		values = []
		systemId = 0
		for versionKey in sorted(bibleIdMap.keys()):
			for bible in bibleIdMap[versionKey]:
				mediaType = bible.typeCode
				bitrate = None
				if bible.typeCode == "audio":
					if bible.filesetId[7:8] == "2":
						mediaType = "drama"
					lastTwo = bible.filesetId[10:12]
					if lastTwo.isdigit():
						bitrate = int(lastTwo)
					else:
						bitrate = 64
				systemId += 1
				bible.systemId = systemId
				value = (bible.systemId, bible.versionId, mediaType, bitrate,
						bible.bucket, bible.filePrefix, bible.bibleZipFile,
						bible.lptsStockNo)
				values.append(value)
		self.insert("Bibles", ("systemId","versionId","mediaType", "bitrate",
			"bucket", "filePrefix", "bibleZipFile", "lptsStockNo"), values)
		## skipping agency, copyrightYear, filenameTemplate


	def insertBibleBooks(self, bibleIdMap):
		shortSandsBookMap = self.readShortsandsBucket()
		values = []
		for versionKey in sorted(bibleIdMap.keys()):
			for bible in bibleIdMap[versionKey]:
				bookList = shortSandsBookMap.get(bible.key)
				if bookList == None:
					bookList = self.readCVSFileBooks(bible)
				if bookList == None:
					print("ERROR_?? books not found for %s" % (bible.toString()))
					sys.exit()
				else:
					for (sequence, bookId, chapter) in bookList:
						# ?? Add nameS3 of audio files
						value = (bible.systemId, bookId, sequence, None, None, chapter)
						values.append(value)
		self.insert("BibleBooks", ("systemId", "book", "sequence",
  				"nameLocal", "nameS3", "numChapters"), values)


	def readCVSFileBooks(self, bible):
		filename = self.getCSVFilename(bible.s3Key)
		if filename == None:
			return None
		results = {}
		with open(filename, newline='\n') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				key = "%s/%s" % (row["sequence"], row["book_id"])
				chaptStr = row["chapter_start"]
				if chaptStr.isdigit():
					chapter = int(chaptStr)
					currChapter = results.get(key, 0)
					if chapter > currChapter:
						results[key] = chapter
		results2 = []
		for key, chapter in results.items():
			(sequence, bookId) = key.split("/")
			results2.append((sequence, bookId, chapter))
		results3 = sorted(results2, key=lambda tup: tup[0])
		return results3


	# Returns a map text/bibleId/filesetId : [(sequence, bookId, chapter)]
	def readShortsandsBucket(self):
		results = {}
		filePath = self.config.DIRECTORY_BUCKET_LIST + self.config.S3_MY_BUCKET + ".txt"
		fp = io.open(filePath, mode="r", encoding="utf-8")
		for line in fp:
			fileRef = line.split("\t")[0]
			if fileRef.endswith(".html"):
				fileRef = fileRef.split(".")[0]
				(typeCode, bibleId, filesetId, filename) = fileRef.split("/")
				parts = filename.split("_")
				sequence = parts[1]
				bookId = parts[2]
				key = "%s/%s/%s/%s/%s" % (typeCode, bibleId, filesetId, sequence, bookId)
				chapter = int(parts[3]) if len(parts) > 3 else 0
				currChapter = results.get(key, 0)
				if chapter > currChapter:
					results[key] = chapter
		fp.close()
		results2 = {}
		for key, chapter in results.items():
			(typeCode, bibleId, filesetId, seqStr, bookId) = key.split("/")
			sequence = int(seqStr)
			key = "%s/%s/%s" % (typeCode, bibleId, filesetId)
			chapters = results2.get(key, [])
			chapters.append((sequence, bookId, chapter))
			results2[key] = chapters
		for key, values in results2.items():
			results2[key] = sorted(values, key=lambda tup: tup[0])
		return results2


	## compute size code for each Bible from the Biblebooks table
	def setScopeByBibleBooks(self):
		sql = "SELECT systemId FROM Bibles where systemId NOT IN (SELECT systemId FROM BibleBooks)"
		resultSet = self.db.selectList(sql, ())
		for item in resultSet:
			print("ERROR_15 systemId %s has no books" % (item))
		if len(resultSet) > 0:
			sys.exit()
		values = []
		sql = ("SELECT systemId, mediaType, filePrefix FROM Bibles")
		resultSet = self.db.select(sql, ())
		for (systemId, mediaType, filePrefix) in resultSet:
			print(systemId, mediaType, filePrefix)
			sql2 = ("SELECT book FROM BibleBooks WHERE systemId=?")
			bookSet = self.db.selectSet(sql2, (str(systemId),))
			scopeCode = filePrefix[-4:-3] if len(filePrefix) > 19 else "C"
			print(scopeCode)
			ntScope = None
			otScope = None
			if scopeCode in {"C", "N", "P"}:
				ntScope = self.getNewTestamentScope(bookSet)
			if scopeCode in {"C", "O", "P"}:
				otScope = self.getOldTestamentScope(bookSet)
			if scopeCode not in {"C", "N", "O", "P"}:
				print("ERROR_16 Unexpected type in %s" % (filePrefix))
				sys.exit()
			values.append((ntScope, otScope, systemId))			
		update = "UPDATE Bibles SET ntScope = ?, otScope = ? WHERE systemId = ?"
		self.db.executeBatch(update, values)


	def getNewTestamentScope(self, bookIdSet):
		ntBooks = bookIdSet.intersection(self.NTBookSet)
		count = len(ntBooks)
		if count >= 27:
			return "NT"
		elif count >= 0:
			return "NP"
		else:
			return None


	def getOldTestamentScope(self, bookIdSet):
		otBooks = bookIdSet.intersection(self.OTBookSet)
		count = len(otBooks)
		if count >= 39:
			return "OT"
		elif count >= 0:
			return "OP"
		else:
			return None


	def unloadDB(self):
		print("unloadDB")
		tables = ["Versions", "VersionLocales", "Bibles", "BibleBooks"]
		tables.reverse()
		for table in tables:
			self.db.execute("DELETE FROM %s" % (table), ())


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
	tables.unloadDB()
	tables.process()



