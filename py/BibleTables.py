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
		self.abbreviation = filesetId[3:6]
		self.iso3 = None
		self.script = None
		self.country = None
		self.allowApp = False
		self.allowAPI = False
		self.locales = []
		self.scope = None
		self.priority = 0
		self.bucket = None
		self.filePrefix = None
		self.fileTemplate = None
		## Text only data
		self.name = None
		self.nameLocal = None
		self.numerals = None

	def toString(self):
		allow = "app " if self.allowApp else ""
		allow += "api" if self.allowAPI else ""
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

		inS3SetNotLPTS = set(s3Map.keys()).difference(lptsMap.keys())
		print("COUNT: IN S3 NOT LPTS %d" % (len(inS3SetNotLPTS)))
		for key in sorted(inS3SetNotLPTS):
			print("ERROR_11 IN S3 NOT LPTS %s" % (key))

		inLPTSNotS3 = set(lptsMap.keys()).difference(s3Map.keys())
		print("COUNT: IN LPTS NOT S3 %s" % (len(inLPTSNotS3)))
		for key in sorted(inLPTSNotS3):
			print("ERROR_12 IN LPTS NOT s3 %s" % (key))

		inLptsAndS3Set = set(lptsMap.keys()).intersection(s3Map.keys())
		print("COUNT: IN LPTS IN S3 %d" % (len(inLptsAndS3Set)))

		inLptsAndS3Map = self.rebuildMapFromSet(inLptsAndS3Set, lptsMap)
		print("COUNT: IN LPTS IN S3 REBUILT %d" % (len(inLptsAndS3Map.keys())))

		permittedMap = {}
		for key, bible in inLptsAndS3Map.items():
			if bible.allowAPI or bible.allowApp:
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

		for key, bible in withLocaleMap.items():
			if bible.typeCode == "text":
				info = self.readInfoJson(bible.bibleId, bible.filesetId)
				self.getFilesetData(bible, info)
				scriptCode = self.getScriptCode(info)
				if bible.script != None and bible.script != scriptCode:
					print("ERROR_05 %s script in LPTS %s, computed %s" % (bible.key, bible.script, scriptCode))
				if scriptCode != None and scriptCode != 'Latn': # Latn is often an error
					bible.script = scriptCode
				bible.numerals = self.getNumberCode(bible.script, bible.iso3)

		withLocaleMap2 = self.selectWithLocale(withLocaleMap)
		print("COUNT: IN LPTS WITH PERMISS IN S3 AND REPEAT LOCALE %d" % (len(withLocaleMap2)))

		self.getScopeByCSVFile(withLocaleMap2)

		#for item in withLocaleMap2.values():
		#	print(item.toString(), item.scope)

		bibleGroupMap = self.groupByVersion(withLocaleMap)
		print("COUNT: IN BibleId MAP %d" % (len(bibleGroupMap.keys())))

		hasTextGroupMap = self.removeNonText(bibleGroupMap) # remove Version w/o text
		print("COUNT: IN BibleId MAP with TEXT %d" % (len(hasTextGroupMap.keys())))

		dupBiblesRemovedMap = self.removeDupBibles(hasTextGroupMap)
		print("COUNT: IN BibleId MAP with TEXT, DUPS REMOVED %d" % (len(dupBiblesRemovedMap.keys())))

		self.insertVersions(dupBiblesRemovedMap)
		self.insertVersionLocales(dupBiblesRemovedMap)
		self.insertBibles(dupBiblesRemovedMap)
		self.insertBibleBooks(dupBiblesRemovedMap)

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
						bible.iso3 = lptsRec.ISO()
						scriptName = lptsRec.Orthography(index)
						bible.script = LookupTables.scriptCode(scriptName)
						if typeCode == "video":
							bible.bucket = self.config.S3_DBP_VIDEO_BUCKET
						else:
							bible.bucket = self.config.S3_DBP_BUCKET
						bible.filePrefix = bible.key
						countryName = lptsRec.Country()
						if countryName not in {None, "Region-wide"}:
							bible.country = self.countryMap[countryName] # fail fast
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


	def getShortSandsMap(self):
		results = {}
		with open("data/shortsands_bibles.csv", newline='\n') as csvfile:
			reader = csv.reader(csvfile)
			for (sqliteName, abbr, iso3, scope, versionPriority, name, englishName,
				localizedName, textBucket, textId, keyTemplate, 
				audioBucket, otDamId, ntDamId, ios1, script, country) in reader:
					bestFileset = self._findBestFileset(textId, otDamId, ntDamId)
					bibleId = bestFileset.split("/")[1]
					filesetId = textId.split("/")[2]
					bible = Bible("SS", "shortsands", "text", bibleId, filesetId)
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
		prefSeq = [ntDamId, otDamId, textId]
		for did in (otDamId, ntDamId, textId):
			if did != None and did != "":
				return did
		return None # should not happen


	def rebuildMapFromSet(self, bibleSubset, bibleMap):
		results = {}
		for key in bibleSubset:
			bible = bibleMap[key]
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


	def groupByVersion(self, bibleMap):
		results = {}
		for bible in bibleMap.values():
			bible.versionKey = "%s-%s-%s" % (bible.iso3, bible.abbreviation, bible.script)
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


    ## read and parse a info.json file for a bibleId, filesetId
	def readInfoJson(self, bibleId, filesetId):
		info = None
		filename = "%stext:%s:%s:info.json" % (self.config.DIRECTORY_DBP_INFO_JSON, bibleId, filesetId)
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
	def getFilesetData(self, bible, info):
		if info != None:
			bible.nameLocal = info["name"]
			bible.name = info["nameEnglish"]
			country = info["countryCode"] if info["countryCode"] != '' else None
			if bible.country == None:
				bible.country = country
			if country != None and country != bible.country:
				print("ERROR_03 %s in LPTS %s in info.json %s" % (bible.key, bible.country, country))
			iso3 = info["lang"].lower()
			if iso3 != bible.iso3:
				print("ERROR_04 %s in LPTS iso %s in info.json %s" % (bible.key, bible.iso3, iso3))


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


	def getNumberCode(self, script, iso3):
		if script == "Arab":
			if iso3 in {"fas", "pes" }:
				return "persian"
			elif iso3 == "urd": 
				return "urdu"
			else:
				return "eastern-arabic"
		if script == "Deva":
			if iso3 == "ben":
				return "bengali"
			elif iso3 == "kan":
				return "kannada"
			else:
				return "devanagari"
		numerals = {
			"Gujr": "gujarati",
			"Guru": "gurmukhi",
			"Hani": "chinese",
			"Khmr": "khmer",
			"Laoo": "lao",
			"Limb": "limbu",
			"Mlym": "malayalam",
			"Mymr": "burmese",
			"Orya": "oriya",
			"Syrc": "syriac",
			"Taml": "tamil",
			"Telu": "telugu",
			"Thai": "thai"}
		return numerals.get(script, "western-arabic")


	## compute size code for each 
	def getScopeByCSVFile(self, bibleMap):
		for bible in bibleMap.values():
			filename = self.getCSVFilename(bible.typeCode, bible.bibleId, bible.filesetId)
			if filename != None:
				bookIdSet = set()
				with open(filename, newline='\n') as csvfile:
					reader = csv.DictReader(csvfile)
					for row in reader:
						bookIdSet.add(row["book_id"])
				bible.scope = self.getScope(bookIdSet)


	def getCSVFilename(self, typeCode, bibleId, filesetId):
		filename = "%s_%s_%s.csv" % (typeCode, bibleId, filesetId)
		filePath = self.config.DIRECTORY_ACCEPTED + filename
		if os.path.isfile(filePath):
			return filePath
		filePath = self.config.DIRECTORY_QUARANTINE + filename
		if os.path.isfile(filePath):
			return filePath
		return None


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
			nameSet = set()
			nameLocalSet = set()
			for bible in bibleIdMap[versionKey]:
				bible.versionId = versionId
				if bible.typeCode == "text":
					versionKeyList.append(bible.versionKey)
					isoSet.add(bible.iso3)
					abbrevSet.add(bible.abbreviation)
					if bible.script != None:
						scriptSet.add(bible.script)
					if bible.numerals != None:
						numeralsSet.add(bible.numerals)
					if bible.name != None:
						nameSet.add(bible.name)
					if bible.nameLocal != None:
						nameLocalSet.add(bible.nameLocal)
			if len(versionKeyList) > 1:
				print("ERROR versionKey is not set correctly")
				sys.exit()
			iso3 = ",".join(isoSet) if len(isoSet) > 0 else None
			abbreviation = ",".join(abbrevSet) if len(abbrevSet) > 0 else None
			script = ",".join(scriptSet) if len(scriptSet) > 0 else None
			numerals = ",".join(numeralsSet) if len(numeralsSet) > 0 else None
			name = ",".join(nameSet) #if len(nameSet) > 0 else None
			nameLocal = ",".join(nameLocalSet) #if len(nameLocalSet) > 0 else None
			values.append((versionId, iso3, abbreviation, script, numerals, name, nameLocal))
		self.insert("Versions", ("versionId", "iso3", "abbreviation", "script",
				"numerals", "name", "nameLocal"), values)


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
				value = (bible.systemId, bible.versionId, mediaType, bible.scope,
						bitrate, bible.bucket, bible.filePrefix)
				values.append(value)
		self.insert("Bibles", ("systemId","versionId","mediaType","scope",
			"bitrate", "bucket", "filePrefix"), values)
		## skipping agency, copyrightYear, filenameTemplate


	def insertBibleBooks(self, bibleIdMap):
		values = []
		self.pkeyCheck = set()
		for versionKey in sorted(bibleIdMap.keys()):
			for bible in bibleIdMap[versionKey]:
				nameLocalMap = self.getLocalBookNames(bible.typeCode, bible.bibleId, bible.filesetId)
				filename = self.getCSVFilename(bible.typeCode, bible.bibleId, bible.filesetId)
				if filename != None:
					priorRow = None
					with open(filename, newline='\n') as csvfile:
						reader = csv.DictReader(csvfile)
						for row in reader:
							if priorRow != None:
								if row["book_id"] != priorRow["book_id"]:
									self.appendBook(values, bible, priorRow, nameLocalMap)
							priorRow = row
						self.appendBook(values, bible, priorRow, nameLocalMap)
				else:
					print("WOW NO BOOKS", bible.bibleId, bible.filesetId, bible.bucket)
		self.insert("BibleBooks", ("systemId", "book", "sequence",
  				"nameLocal", "nameS3", "numChapters"), values)


	def getLocalBookNames(self, typeCode, bibleId, filesetId):
		result = {}
		if typeCode == "text":
			info = self.readInfoJson(bibleId, filesetId)
			if info != None:
				books = info["divisions"]
				names = info["divisionNames"]
				if len(books) != len(names):
					print("ERROR_07 books and names not equal in %s/%s/%s" % (typeCode, bibleId, filesetId))
					sys.exit()
				for index in range(len(books)):
					book = books[index]
					result[book] = names[index]
		return result


	def appendBook(self, values, bible, row, nameLocalMap):
		bookId = row["book_id"]
		nameLocal = nameLocalMap.get(bookId)
		value = ((bible.systemId, bookId, row["sequence"], nameLocal, 
			row["book_name"], row["chapter_start"]))
		values.append(value)
		if row["verse_start"] != "1":
			print("ERROR_08 verse_start should be 1 in %s" % (bible.key))
		key = bible.filesetId + "/" + bookId
		if key in self.pkeyCheck:
			print("ERROR_09 duplicate %s in %s" % (key, bible.bibleId))
		self.pkeyCheck.add(key)


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



