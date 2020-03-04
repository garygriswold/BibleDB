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
#import sqlite3

ACCEPTED_DIR = "/Volumes/FCBH/files/validate/accepted/"
INFO_JSON_DIR = "/Volumes/FCBH/info_json/"
DATABASE = "Versions.db"
AUDIO_BUCKET = "dbp-prod"
VIDEO_BUCKET = "dbp-vid"

class BibleTables:

	def __init__(self):
		self.db = SqliteUtility()
		self.scriptMap = self.db.selectMap("SELECT script_name, script FROM scripts", ())
		self.iso3Set = self.db.selectSet("SELECT iso3 FROM languages", ())
		self.macroMap = self.db.selectMap("SELECT iso3, macro FROM languages", ())
		self.iso1Map = self.db.selectMap("SELECT iso3, iso1 FROM languages", ())
		self.insertBibles = []
		self.insertFilesets = []
		self.insertFilesetLocales = []
		self.insertBibleLocales = []
		self.insertBibleBooks = []


	def process(self):
		bibleMap = self.getBibleMap()
		for bibleId in sorted(bibleMap.keys()):
			infoMap = None
			filesetIds = bibleMap[bibleId]
			for filesetId in filesetIds:
				if len(filesetId) < 10:
					infoMap = self.readInfoJson(bibleId, filesetId)
					if infoMap != None:
						self.insertBiblesTable(bibleId, infoMap)
			for filesetId in filesetIds:
				print("after for", bibleId, filesetId)
				if infoMap != None:
					self.insertBibleFilesetsTable(bibleId, filesetId, infoMap)
					self.insertBibleFilesetLocalesTable(bibleId, filesetId, infoMap)

					#print("before script", bibleId, filesetId)
					#self.getScriptCode(infoMap)

		# for each bible, open info.json, to get required data
		# print errors for any differences
		# after processing list of bibles, store bibleset fields

		# for each bible
		# set fields, by size code requires reading books.


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

	def insertBiblesTable(self, bibleId, infoJson):
		row = {}
		row["bible_id"] = bibleId
		row["iso3"] = infoJson["lang"].lower()
		row["version_code"] = bibleId[3:]
		row["version_name"] = infoJson["name"]
		row["english_name"] = infoJson["nameEnglish"]
		self.insertBibles.append(row)


	def insertBibleFilesetsTable(self, bibleId, filesetId, infoJson):
		row = {}
		row["fileset_id"] = filesetId
		row["bible_id"] = bibleId
		row["size_code"] = "TO BE DONE" # must open file
		if filesetId[8:10] == "VD":
			row["bucket"] = VIDEO_BUCKET
		else:
			row["bucket"] = AUDIO_BUCKET
		row["owner_id"] = 0 # TO BE DONE
		row["copyright_year"] = "" # TO BE DONE
		row["filename_template"] = "" # TO BE DONE, must open file, or do manually
		self.insertFilesets.append(row)

	def insertBibleFilesetLocalesTable(self, bibleId, filesetId, infoJson):
		row = {}
		row["fileset_id"] = filesetId
		iso3 = infoJson["lang"].lower()
		script = self.getScriptCode(infoJson)
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
			sys.exit()
			self.appendInserts(filesetId, iso1Lang, script, country)


	def appendInserts(self, filesetId, lang, script, country):
		self.insertFilesetLocales.append({"fileset_id": filesetId, "locale": lang})
		if country != None:
			locale = lang + "_" + country
			self.insertFilesetLocales.append({"fileset_id": filesetId, "locale": locale})
		if script != None:
			locale = lang + "_" + script
			self.insertFilesetLocales.append({"fileset_id": filesetId, "locale": locale})
		if script != None and country != None:
			locale = lang + "_" + script + "_" + country
			self.insertFilesetLocales.append({"fileset_id": filesetId, "locale": locale})		

		# for each country
		# lookup iso by iso, country
		# if script is not null lookup by iso, script, country

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


if __name__ == "__main__":
	tables = BibleTables()
	tables.process()

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

