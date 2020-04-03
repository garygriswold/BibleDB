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
#from operator import attrgetter
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
		self.bibles = []
		self.bibleFilesets = []
		self.bibleFilesetLocales = []
		self.textFilesets = []
		self.audioFilesets = []
		self.textBibleBooks = []
		self.audioBibleBooks = []
		self.uniqueBibleCheck = {}


	def process(self):
		bibleMap = self.getBibleMap()
		bibleMap = self.pruneBibleMap(bibleMap)
		for bibleId in sorted(bibleMap.keys()):
			print("bible", bibleId)
			infoMaps = []
			filesets = bibleMap[bibleId]
			for (filesetId, typeCode) in filesets:
				#print("fileset", typeCode, filesetId)
				if len(filesetId) < 10:
					#print(typeCode, bibleId, filesetId)
					infoMap = self.readInfoJson(bibleId, filesetId)
					if infoMap != None:
						infoMaps.append(infoMap)
			#print("call insertBibles", bibleId)
			self.insertBibles(bibleId, infoMaps)
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


	## create hashMap of bibleId and list of (filesetId, typeCode)
	def getBibleMap(self):
		resultMap = {}
		files1 = os.listdir(ACCEPTED_DIR)
		files2 = os.listdir(REJECTED_DIR)
		files = files1 + files2
		for file in files:
			if not file.startswith(".") and file.endswith(".csv"):
				file = file.split(".")[0]
				(typeCode, bibleId, filesetId) = file.split("_")
				#print(file, typeCode, bibleSetId, bibleId)
				bibles = resultMap.get(bibleId, [])
				bibles.append((filesetId, typeCode))
				resultMap[bibleId] = bibles 
		return resultMap


	## remove bibleId's that have no text files
	def pruneBibleMap(self, bibleMap):
		for bibleId in sorted(bibleMap.keys()):
			filesets = bibleMap[bibleId]
			hasText = False
			for (filesetId, typeCode) in filesets:
				if typeCode == "text":
					hasText = True
			if not hasText:
				del bibleMap[bibleId]
		return bibleMap


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


		#id
		#name is localName
		#nameEnglish is same or 
		#dir is direction
		#lang = iso
		#fontClass
		#script is script
		#audioDirectory
		#numbers
		#countryCode
		#divisionNames chapters in localnames
		#divisions
		#sections


	def getScriptCode(self, infoJson):
		bookNames = infoJson["divisionNames"]
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
						if scriptCode != None:
							print(scriptCode)
							return scriptCode
		return None


	def getNumberCode(self, infoJson):
		numbers = infoJson["numbers"]
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

