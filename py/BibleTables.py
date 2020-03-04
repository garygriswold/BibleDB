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
from SqliteUtility import *

ACCEPTED_DIR = "/Volumes/FCBH/files/validate/accepted/"
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


	def process(self):
		bibleMap = self.getBibleMap()
		for bibleId in sorted(bibleMap.keys()):
			infoMap = None
			filesetIds = bibleMap[bibleId]
			for filesetId in filesetIds:
				if len(filesetId) < 10:
					infoMap = self.readInfoJson(bibleId, filesetId)
					if infoMap != None:
						self.insertBibles(bibleId, infoMap)
			for filesetId in filesetIds:
				print("after for", bibleId, filesetId)
				if infoMap != None:
					self.insertFilesets(bibleId, filesetId, infoMap)
					script = self.getScriptCode(infoMap)
					self.insertFilesetLocales(bibleId, filesetId, script, infoMap)
					if len(filesetId) < 10:
						self.insertTextFilesets(bibleId, filesetId, script, infoMap)
						self.insertTextBibleBooks(bibleId, filesetId, infoMap)
					elif filesetId[8:10] == "DA":
						self.insertAudioFilesets(bibleId, filesetId, infoMap)
						self.insertAudioBibleBooks(bibleId, filesetId, infoMap)
					elif filesetId[8:10] != "VA":
						print("ERROR: Unknown fileset type %s" % (filesetId))
						self.insertVideoFilesets(bibleId, filesetId, infoMap)


	def getTextBibles(self):
		resultMap = {}
		files = os.listdir(ACCEPTED_DIR)
		for file in files:
			if file.startswith("text") and file.endswith(".csv"):
				file = file.split(".")[0]
				(typeCode, bibleId, filesetId) = file.split("_")
				#print(file, typeCode, bibleId, filesetId)
				if resultMap.get(bibleId) != None:
					hasBible = resultMap.get(bibleId)
					print("ERROR: duplicate text from bibleId %s has %s and %s" % (bibleId, hasBible, filesetId))
					sys.exit()
				else:
					resultMap[bibleId] = filesetId
		return resultMap


	def getBibleMap(self):
		resultMap = {}
		files = os.listdir(ACCEPTED_DIR)
		for file in files:
			if not file.startswith(".") and file.endswith(".csv"):
				file = file.split(".")[0]
				(typeCode, bibleId, filesetId) = file.split("_")
				#print(file, typeCode, bibleSetId, bibleId)
				bibles = resultMap.get(bibleId, [])
				bibles.append(filesetId)
				resultMap[bibleId] = bibles 
		return resultMap


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


	def insertBibles(self, bibleId, infoJson):
		iso3 = infoJson["lang"].lower()
		versionCode = bibleId[3:]
		versionName = infoJson["name"]
		englishName = infoJson["nameEnglish"]
		self.bibles.append((bibleId, iso3, versionCode, versionName, englishName))


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
		row = {}
		row["fileset_id"] = filesetId
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
		#sections = infoJson.get("sections")
		#bookChapMap = {}
		#for section in sections:
		#	bookId = section[0:3]
		#	chapt = section[3:]
		#	bookChapMap[bookId] = chapt # At end this will be the last chapter
		#if books != None and len(books) > 0:
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
		#filename = "%saudio_%s_%s.csv" % (ACCEPTED_DIR, bibleId, filesetId)
		#bookChapMap = {}
		#with open(filename) as csv_file:
		#	csv_reader = csv.reader(csv_file, delimiter=',')
		#	for file in csv_reader:
		#		bookName = file[3] # This is incorrect, bookname must be added to CVS
		#		bookId = file[4]
		#		chapt = file[5]
		#		print(bookId, chapt)
		#		bookChapMap[bookId] = (bookName, chapt) # At end will be last chapter
		#books = infoJson.get("divisions")
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
		tables = ["bibles","bible_filesets","bible_fileset_locales","text_filesets",
			"audio_filesets","text_bible_books","audio_bible_books"]
		tables.reverse()
		for table in tables:
			self.db.execute("DELETE FROM %s" % (table), ())


	def loadDB(self):
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
		print(table, columns, len(columns))
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

