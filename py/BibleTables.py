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
		self.srcType = srcType # LPTS | S3 | DBP
		self.source = source
		self.typeCode = typeCode # text | audio | video
		self.bibleId = bibleId
		self.filesetId = filesetId
		self.key = "%s/%s/%s" % (typeCode, bibleId, filesetId)
		self.abbreviation = filesetId[3:]
		self.iso3 = None
		self.script = None
		self.country = None
		self.allowApp = False
		self.allowAPI = False
		self.locales = []
		self.scope = None
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

		for item in withLocaleMap2.values():
			print(item.toString(), item.scope)

		bibleGroupMap = self.groupByBibleId(withLocaleMap)
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


	## not used, but might be useful
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


	def removeDupBibles(self, bibleIdMap):
		results = {}
		for bibleId in sorted(bibleIdMap.keys()):
			textSet = set()
			audioSet = set()
			dramaSet = set()
			values = []
			for bible in bibleIdMap[bibleId]:
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
			results[bibleId] = values
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
		for bibleId in sorted(bibleIdMap.keys()):
			isoSet = set()
			abbrevSet = set()
			scriptSet = set()
			numeralsSet = set()
			nameSet = set()
			nameLocalSet = set()
			for bible in bibleIdMap[bibleId]:
				print("version", bible.key)
				if bible.typeCode == "text":
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
			iso3 = ",".join(isoSet) if len(isoSet) > 0 else None
			abbreviation = ",".join(abbrevSet) if len(abbrevSet) > 0 else None
			script = ",".join(scriptSet) if len(scriptSet) > 0 else None
			numerals = ",".join(numeralsSet) if len(numeralsSet) > 0 else None
			name = ",".join(nameSet) #if len(nameSet) > 0 else None
			nameLocal = ",".join(nameLocalSet) #if len(nameLocalSet) > 0 else None
			values.append((bibleId, iso3, abbreviation, script, numerals, name, nameLocal))
		self.insert("Bibles", ("bibleId", "iso3", "abbreviation", "script",
				"numerals", "name", "nameLocal"), values)


	def insertVersionLocales(self, bibleIdMap):
		values = []
		for bibleId in sorted(bibleIdMap.keys()):
			locales = set()
			for bible in bibleIdMap[bibleId]:
				for locale in bible.locales:
					locales.add(locale)
			for locale in locales:
				values.append((locale, bibleId))
		self.insert("BibleLocales", ("locale", "bibleId"), values)


	def insertBibles(self, bibleIdMap):
		values = []
		for bibleId in sorted(bibleIdMap.keys()):
			for bible in bibleIdMap[bibleId]:
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
				if bible.typeCode == "video":
					bucket = self.config.S3_DBP_VIDEO_BUCKET
				else:
					bucket = self.config.S3_DBP_BUCKET
				value = (bible.filesetId, bible.bibleId, mediaType, bible.scope,
					bucket, bitrate)
				values.append(value)
		self.insert("BibleFilesets", ("filesetId","bibleId","mediaType","scope",
			"bucket", "bitrate"), values)
		## skipping agency, copyrightYear, filenameTemplate


	def insertVideoFilesets(self, bibleId, filesetId, infoJson):
		print("video filesets to be done")


	def insertBibleBooks(self, bibleIdMap):
		values = []
		self.pkeyCheck = set()
		for bibleId in sorted(bibleIdMap.keys()):
			for bible in bibleIdMap[bibleId]:
				nameLocalMap = self.getLocalBookNames(bible.typeCode, bibleId, bible.filesetId)
				filename = self.getCSVFilename(bible.typeCode, bibleId, bible.filesetId)
				priorRow = None
				with open(filename, newline='\n') as csvfile:
					reader = csv.DictReader(csvfile)
					for row in reader:
						if priorRow != None:
							if row["book_id"] != priorRow["book_id"]:
								self.appendBook(values, bible, priorRow, nameLocalMap)
						priorRow = row
					self.appendBook(values, bible, priorRow, nameLocalMap)
		self.insert("BibleBooks", ("filesetId", "book", "sequence",
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
		value = ((bible.filesetId, bookId, row["sequence"], nameLocal, 
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
		tables = ["Bibles", "BibleLocales", "BibleFilesets", "BibleBooks"]
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



