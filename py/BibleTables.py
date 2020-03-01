# BibleTables.py
#
# This program loads bible_sets, bibles, and bible_books
#
import io
import os
import json
import csv

ACCEPTED_DIR = "/Volumes/FCBH/files/validate/accepted/"
INFO_JSON_DIR = "/Volumes/FCBH/info_json/"

class BibleTables:

	def __init__(self):
		# open database
		insertBibleSets = []
		insertBibles = []
		insertBibleCountries = []
		insertBibleBooks = []


	def process(self):
		bibleSetMap = self.getBibleSetMap()
		for bibleSetId in bibleSetMap.keys():
			bibles = bibleSetMap[bibleSetId]
			for bibleId in bibles:
				#print(bibleSetId, bibleId)
				if len(bibleId) < 10:
					infoMap = self.readInfoJson(bibleSetId, bibleId)
					#print(infoMap)
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
				(typeCode, bibleSetId, bibleId) = file.split("_")
				#print(file, typeCode, bibleSetId, bibleId)
				if resultMap.get(bibleSetId) != None:
					hasBible = resultMap.get(bibleSetId)
					print("ERROR: duplicate text from bibleSetId %s has %s and %s" % (bibleSetId, hasBible, bibleId))
					sys.exit()
				else:
					resultMap[bibleSetId] = bibleId
				#bibles = resultMap.get(bibleSetId, [])
				#bibles.append(bibleId)
				#resultMap[bibleSetId] = bibles 
		return resultMap


	def getBibleSetMap(self):
		resultMap = {}
		files = os.listdir(ACCEPTED_DIR)
		for file in files:
			if not file.startswith(".") and file.endswith(".csv"):
				file = file.split(".")[0]
				(typeCode, bibleSetId, bibleId) = file.split("_")
				#print(file, typeCode, bibleSetId, bibleId)
				bibles = resultMap.get(bibleSetId, [])
				bibles.append(bibleId)
				resultMap[bibleSetId] = bibles 
		return resultMap


	def readInfoJson(self, bibleSetId, bibleId):
		bible = {}
		filename = "%stext:%s:%s:info.json" % (INFO_JSON_DIR, bibleSetId, bibleId)
		if os.path.isfile(filename):
			fp = io.open(filename, mode="r", encoding="utf-8")
			data = fp.read()
			try:
				info = json.loads(data)
				#print(info)
				bible[bibleSetId] = info
			except Exception as err:
				print("Json Error in %s:%s:info.json " % (bibleSetId, bibleId), err)
				bible[bibleSetId] = "Parse Error"

			fp.close()
		else:
			print("NOT FOUND,", bibleSetId, bibleId)
			bible[bibleSetId] = "Not Found"

		#name is localName
		#englishName is same
		#dir is direction
		#lang = iso
		#fontClass
		#script is script
		#numbers
		#countryCode
		#countries ? array
		#allCountries ? array
		#divisionNames chapters in localnames



if __name__ == "__main__":
	tables = BibleTables()
	tables.process()

"""
bible_set
  bible_set_id TEXT NOT NULL PRIMARY KEY, -- (fcbh bible_id)
  iso3 TEXT NOT NULL, -- I think iso3 and version code are how I associate items in a set
  version_code TEXT NOT NULL, -- (e.g. KJV)
  version_name TEXT NOT NULL, -- from info.json
  english_name TEXT NOT NULL, -- from info.json
  localized_name TEXT NULL, -- from google translate
  version_priority INT NOT NULL DEFAULT 0, -- affects position in version list, manually set
  FOREIGN KEY (iso3) REFERENCES languages (iso3)

bibles
  bible_id TEXT NOT NULL PRIMARY KEY, -- (fcbh fileset_id)
  bible_set_id TEXT NOT NULL,
  type_code TEXT NOT NULL CHECK (type_code IN('audio', 'drama', 'video', 'text')),
  size_code TEXT NOT NULL, -- NT,OT, NTOT, NTP, etc.
  bucket TEXT NOT NULL,
  iso TEXT NOT NULL,
  script TEXT NULL, -- only required for text
  numerals_id TEXT NULL, -- get this from info.json, should there be an index, and this a foreign key.
  font TEXT NOT NULL, -- info.json
  owner_id TEXT NOT NULL, -- source unknown
  copyright_year INT NOT NULL, 
  filename_template TEXT NOT NULL,
  FOREIGN KEY (bible_set_id) REFERENCES bible_sets (bible_set_id),
  -- can there be a foreign key to locale.  Would it be useful or correct without country?
  FOREIGN KEY (numerals_id) REFERENCES numerals (numerals_id),
  FOREIGN KEY (owner_id) REFERENCES bible_owners (owner_id)

bible_countries
  bible_id TEXT NOT NULL,
  country_id TEXT NOT NULL,
  PRIMARY KEY (bible_id, country_id),
  FOREIGN KEY (bible_id) REFERENCES bibles (bible_id),
  FOREIGN KEY (country_id) REFERENCES regions (country_id)

bible_books
  bible_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  book_order INT NOT NULL,
  book_name TEXT NOT NULL,
  book_abbrev TEXT NOT NULL, -- I cannot get this from meta-data, but I can from bible
  book_heading TEXT NOT NULL,-- I cannot get this from meta-data, but I can from bible
  num_chapters INT NOT NULL,
  PRIMARY KEY (bible_id, book_id),
  FOREIGN KEY (bible_id) REFERENCES bibles (bible_id),
  FOREIGN KEY (book_id) REFERENCES books (book_id)
"""

