# BibleTables.py
#
# This program loads bible_sets, bibles, and bible_books
#
import io
import os
import sys
import json
import csv
import unicodedata
import operator
from SqliteUtility import *


ACCEPTED_DIR = "/Volumes/FCBH/files/validate/accepted/"
REJECTED_DIR = "/Volumes/FCBH/files/validate/quarantine/"
INFO_JSON_DIR = "/Volumes/FCBH/info_json/"
AUDIO_BUCKET = "dbp-prod"
VIDEO_BUCKET = "dbp-vid"

class BibleTables:

	def __init__(self):
		self.db = SqliteUtility()
		self.scriptMap = self.db.selectMap("SELECT script_name, script FROM scripts", ())
		self.iso3Set = self.db.selectSet("SELECT iso3 FROM languages", ())
		self.macroMap = self.db.selectMap("SELECT iso3, macro FROM languages", ())
		self.iso1Map = self.db.selectMap("SELECT iso3, iso1 FROM languages", ())
		self.localeSet = self.db.selectSet("SELECT distinct locale FROM locales", ())
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
		bibleList = self.getBibleList({"text"})
		for rec in bibleList:
			if len(rec["fileset_id"]) != 6:
				print("ERROR0", rec["fileset_id"])
			info = self.readInfoJson(rec["bible_id"], rec["fileset_id"])
			self.getFilesetData(rec, info)
			rec["script"] = self.getScriptCode(info)
			rec["numerals"] = self.getNumberCode(info)
			#if rec.get("script") == None or len(rec["script"]) < 4:
			#	print("ERROR: NO SCRIPT")
			#if rec.get("country") == None or len(rec["country"]) < 2:
			#	print("ERROR: NO COUNTRY")
			#if rec.get("iso3") == None or len(rec["iso3"]) < 3:
			#	print("ERROR: NO LANG")
			rec["locales"] = self.matchBiblesToLocales(rec)
			if len(rec["locales"]) > 0:
				rec["scope"] = self.getScopeByCSVFile(rec["filename"])
		reducedList = self.pruneList(bibleList)
		self.mapOnUniqueKey(reducedList)


		mediaList = self.getBibleList({"audio", "video"})
		for rec in mediaList:
			rec["scope"] = self.getScopeByCSVFile(rec["filename"])
		mediaMap5 = self.getFilesetPrefixMap(mediaList, 5)
		mediaMap6 = self.getFilesetPrefixMap(mediaList, 6)
		mediaMap7 = self.getFilesetPrefixMap(mediaList, 7)
		mediaMapAll = self.getFilesetPrefixMap(mediaList, 20)

		groupMap = {}
		for rec in reducedList:
			filesetId = rec["fileset_id"]
			if len(filesetId) == 5:
				groupRecs = mediaMap5.get(filesetId)
			elif len(filesetId) == 7:
				groupRecs = mediaMap7.get(filesetId)
			else:
				groupRecs = mediaMap6.get(filesetId)
			if groupRecs != None:
				groupMap[filesetId] = groupRecs
				print("ERROR99: bible has %d media %s/%s" % (len(groupRecs), rec["bible_id"], filesetId), groupRecs)
			else:
				print("ERROR99: bible has no media %s/%s" % (rec["bible_id"], filesetId))


		#mediaMap = 
		#for item in mediaList:
		#	print(item)
			#print(rec)
			#if len(rec["locales"]) > 0:
			#	print(rec)
#			#print("bible", bibleId)
#			infoMaps = []
#			filesets = bibleMap[bibleId]
#			for (filesetId, typeCode) in filesets:
#				#print("fileset", typeCode, filesetId)
#				if len(filesetId) < 10:
#					#print(typeCode, bibleId, filesetId)
#					infoMap = self.readInfoJson(bibleId, filesetId)
#					if infoMap != None:
#						infoMaps.append(infoMap)
#			#print("call insertBibles", bibleId)
#			self.insertBibles(bibleId, infoMaps)
# temp comment out
#			for filesetId in filesetIds:
#				print("after for", bibleId, filesetId)
#				infoMap = self.readInfoJson(bibleId, filesetId)
#				if infoMap != None:
#					self.insertFilesets(bibleId, filesetId, infoMap)
#					script = self.getScriptCode(infoMap)
#					self.insertFilesetLocales(bibleId, filesetId, script, infoMap)
#					if len(filesetId) < 10:
#						self.insertTextFilesets(bibleId, filesetId, script, infoMap)
#						self.insertTextBibleBooks(bibleId, filesetId, infoMap)
#					elif filesetId[8:10] == "DA":
#						self.insertAudioFilesets(bibleId, filesetId, infoMap)
#						self.insertAudioBibleBooks(bibleId, filesetId, infoMap)
#					elif filesetId[8:10] != "VA":
#						print("ERROR: Unknown fileset type %s" % (filesetId))
#						self.insertVideoFilesets(bibleId, filesetId, infoMap)
#


	## create bible list of (typeCode, bibleId, filesetId from cvs files)
	def getBibleList(self, selectSet):
		results = []
		files1 = os.listdir(ACCEPTED_DIR)
		files2 = os.listdir(REJECTED_DIR)
		#files = files1 + files2
		files = files1 # ONLY ACCEPTED ARE BEING USED. Is this OK?
		for file in files:
			if not file.startswith(".") and file.endswith(".csv"):
				filename = file.split(".")[0]
				(typeCode, bibleId, filesetId) = filename.split("_")
				if typeCode in selectSet:
					record = {}
					record["filename"] = file
					record["type_code"] = typeCode
					record["bible_id"] = bibleId
					record["fileset_id"] = filesetId
					results.append(record)
		return results


    ## read and parse a info.json file for a bibleId, filesetId
	def readInfoJson(self, bibleId, filesetId):
		info = None
		filename = "%stext:%s:%s:info.json" % (INFO_JSON_DIR, bibleId, filesetId)
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
			rec["name_local"] = info["name"]
			rec["name"] = info["nameEnglish"]
			rec["country"] = info["countryCode"] if info["countryCode"] != '' else None
		else:
			iso3 = rec["fileset_id"][:3].lower()
			rec["name_local"] = None
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


	def matchBiblesToLocales(self, rec):
		iso3 = rec["iso3"]
		script = rec["script"]
		country = rec["country"]
		perms = []
		perms.append((iso3,))
		perms.append((iso3, country))
		perms.append((iso3, script))
		perms.append((iso3, script, country))
		macro = self.macroMap.get(iso3)
		perms.append((macro,))
		perms.append((macro, country))
		perms.append((macro, script))
		perms.append((macro, script, country))
		iso1 = self.iso1Map.get(iso3)
		perms.append((iso1,))
		perms.append((iso1, country))
		perms.append((iso1, script))
		perms.append((iso1, script, country))
		locales = []
		for permutation in perms:
			if all(permutation):
				locale = "_".join(permutation)
				if locale in self.localeSet:
					locales.append(locale)
		return locales


	## compute size code for each 
	def getScopeByCSVFile(self, filename):
		bookIdSet = set()
		with open(ACCEPTED_DIR + filename, newline='\n') as csvfile:
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


	## prune list of Bibles based upon multiple criteria
	def pruneList(self, records):
		results = []
		for rec in records:
			locales = rec.get("locales")
			if locales != None and len(locales) > 0:
				results.append(rec)
				if rec["scope"] not in {"NTOT","NTOTP","NT","OTNTP","OT"}:
					print("\nSCOPE: DROP ?", rec)
		return results		


	def mapOnUniqueKey(self, records):
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


	def getFilesetPrefixMap(self, records, keyLength):
		result = {}
		for rec in records:
			prefix = rec["fileset_id"][:keyLength]
			recs2 = result.get(prefix, [])
			recs2.append(rec)
			result[prefix] = recs2
		return result


	def insertBibles(self, bibleId, infoMaps):
		versionCode = bibleId[3:]
		iso3s = {}
		versionNames = {}
		englishNames = {}
		for info in infoMaps:
			self.addOne(iso3s, info["lang"].lower())
			self.addOne(versionNames, info["name"])
			self.addOne(englishNames, info["nameEnglish"])
		iso3 = self.getBest("iso3", iso3s)
		versionName = self.getBest("versionName", versionNames)
		englishName = self.getBest("englishName", englishNames)
		values = (bibleId, iso3, versionCode, versionName, englishName)
		duplicate = self.uniqueBibleCheck.get(bibleId)
		if duplicate != None:
			print("Duplicate %s and %s" % (",".join(duplicate), ",".join(values)))
		else:
			self.uniqueBibleCheck[bibleId] = values
			self.bibles.append(values)	


	def addOne(self, hashMap, item):
		if item != None:
			count = hashMap.get(item, 0)
			hashMap[item] = count + 1


	def getBest(self, name, hashMap):
		upper = 0
		best = None
		for (value, count) in hashMap.items():
			if count > upper:
				upper = count
				best = value
		if len(hashMap.keys()) > 1:
			print("map", hashMap)
			print("best", best)
		return best
		#print(name, hashMap)
		#desc = sorted(hashMap.items(), key=operator.itemgetter(1))
		#print(name, desc)
		#return ("ds")
		#return desc.keys()[0]


	def insertFilesets(self, bibleId, filesetId, infoJson):
		sizeCode = "To be done"
		if filesetId[8:10] == "VD":
			bucket = VIDEO_BUCKET
		else:
			bucket = AUDIO_BUCKET
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


	#temp
	#dbp_bible_id
	#iso3
	#version_code
	#version_name
	#english_name
	#dbp_fileset_id
	#type_code
	#size_code
	#bucket - not needed, always dbp-prod
	#owner_id (if I can get it)
	#copyright_year (if I can get it
	#script
	#numerals_id
	#font

	#DBL Names

	#name
	#nameLocal
	#abbreviation
	#abbreviationLocal
	#scope
	#description
	#dateCompleted
	#systemid_gbc (dbl_id_gbc)
	#systemid_csetid (dbl_id_csetid)
	#systemid_fullname dbl_id_fullname)
	#systemid_name (dbl_id_name)
	#rightsholder (uid)
	#contributor (uid)
	#iso
	#script
	#numerals
	#country

	#book (code, seq, long, short, abbr)


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
		tables = ["bibles","bible_filesets","bible_fileset_locales","text_filesets",
			"audio_filesets","text_bible_books","audio_bible_books"]
		tables.reverse()
		for table in tables:
			self.db.execute("DELETE FROM %s" % (table), ())


	def loadDB(self):
		print("loadDB")
		self.insert("bibles", ("bible_id","iso3","version_code","version_name",
			"english_name"), self.bibles)
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
	tables = BibleTables()
	tables.process()
	tables.unloadDB()
	tables.loadDB()

"""
manual language corrections:
WARN: iso grt and name GUDBSC not the same in bible GUDBSCI  gud
WARN: iso kkn and name KORKRV not the same in bible KORKRV  kor
WARN: iso mad and name MDAWBT not the same in bible MDAWBT  mda
WARN: iso mad and name MDAWBT not the same in bible MDAWBT  mdc
"""
"GUDBSC", "KORKRV", "MDAWBT", 

"""
CREATE TABLE language_corrections (
  fcbh_iso3 TEXT NOT NULL PRIMARY KEY,
  iso3 TEXT NOT NULL,
  FOREIGN KEY (iso3) REFERENCES languages(iso3));

CREATE TABLE bibles (
  bible_id TEXT NOT NULL PRIMARY KEY, -- (fcbh bible_id)
  iso3 TEXT NOT NULL, -- I think iso3 and version code are how I associate items in a set
  version_code TEXT NOT NULL, -- (e.g. KJV)
  version_name TEXT NOT NULL, -- from info.json
  english_name TEXT NOT NULL, -- from info.json
  localized_name TEXT NULL, -- from google translate
  version_priority INT NOT NULL DEFAULT 0, -- affects position in version list, manually set
  FOREIGN KEY (iso3) REFERENCES languages (iso3));

CREATE TABLE bible_filesets (
  fileset_id TEXT NOT NULL PRIMARY KEY,
  bible_id TEXT NOT NULL,
  -- type_code TEXT NOT NULL CHECK (type_code IN('audio', 'drama', 'video', 'text')),
  size_code TEXT NOT NULL, -- NT,OT, NTOT, NTP, etc.
  bucket TEXT NOT NULL,
  owner_id TEXT NOT NULL, -- source unknown
  copyright_year INT NOT NULL, 
  filename_template TEXT NOT NULL,
  FOREIGN KEY (bible_id) REFERENCES bibles (bible_id)
  FOREIGN KEY (owner_id) REFERENCES bible_owners (owner_id));

DROP TABLE IF EXISTS bible_fileset_locales;
CREATE TABLE bible_fileset_locales (
  locale TEXT NOT NULL,
  fileset_id TEXT NOT NULL,
  PRIMARY KEY (locale, fileset_id),
  FOREIGN KEY (fileset_id) REFERENCES bible_filesets (fileset_id),
  FOREIGN KEY (locale) REFERENCES locales (locale));

DROP TABLE IF EXISTS text_filesets;
CREATE TABLE text_filesets (
  fileset_id TEXT NOT NULL PRIMARY KEY, -- this allows multiple texts per bible,
  script TEXT NULL, -- 
  numerals_id TEXT NULL, -- get this from info.json, should there be an index, and this a foreign key.
  font TEXT NOT NULL, -- info.json
  FOREIGN KEY (fileset_id) REFERENCES bible_filesets (fileset_id),
  FOREIGN KEY (numerals_id) REFERENCES numerals (numerals_id));

DROP TABLE IF EXISTS audio_filesets;
CREATE TABLE audio_filesets (
  fileset_id NOT NULL PRIMARY KEY,
  audio_type TEXT NOT NULL CHECK (audio_type IN ('drama', 'nondrama')),
  bitrate INT NOT NULL CHECK (bitrate IN (16, 32, 64, 128)),
  FOREIGN KEY (fileset_id) REFERENCES bible_filesets (fileset_id));

DROP TABLE IF EXISTS video_filesets;
CREATE TABLE video_filesets (
  fileset_id TEXT NOT NULL PRIMARY KEY,
  title TEXT NOT NULL,
  lengthMS INT NOT NULL,
  HLS_URL TEXT NOT NULL,
  description TEXT NULL, -- could this be in bibles
  FOREIGN KEY (fileset_id) REFERENCES bible_filesets (fileset_id));

DROP TABLE IF EXISTS text_bible_books;
CREATE TABLE text_bible_books (
  fileset_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  sequence INT NOT NULL,
  localized_name TEXT NOT NULL, -- The bookname used in table of contents
  num_chapters INT NOT NULL,
  PRIMARY KEY (fileset_id, book_id),
  FOREIGN KEY (fileset_id) REFERENCES text_bible_filesets (fileset_id),
  FOREIGN KEY (book_id) REFERENCES books (book_id));

DROP TABLE IF EXISTS audio_bible_books;
CREATE TABLE audio_bible_books (
  fileset_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  sequence INT NOT NULL,
  s3_name TEXT NOT NULL, -- The bookname used in S3 files
  num_chapters INT NOT NULL,
  PRIMARY KEY (fileset_id, book_id),
  FOREIGN KEY (fileset_id) REFERENCES audio_bible_filesets (fileset_id),
  FOREIGN KEY (book_id) REFERENCES books (book_id));
"""

