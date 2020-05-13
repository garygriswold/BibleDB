# BibleDB
# This is early stages of a new revision. The code is very unfinished, and the repository contains files from prior versions of the same projects. 
This code builds a "Card Catalog" database of a library of text, audio, and video Bibles of many languages.

This is a list of active files used by this project:

data
	iso-639-3 (directory) -- data that populated languages table
	KOGVideo (directory) -- data on King of Glory films for VideoBibles table
	AppleLang.txt -- keep only for historical reasons
	AppleLang2020.txt -- data for Locales table
	Region.txt -- data for Countries table
	ScriptCodes.txt -- data for Scripts table
	ShortsandsBibles.csv -- Bibles data from current version of the App
	USFMBookCodes.txt -- data for Books table

py
	BiblesReport.py -- Generates CSV file of Bibles for as readable report of Bibles
	BibleTables.py -- Populates tables: Agencies, Versions, VersionLocales, Bibles, and BibleBooks
	BibleValidate.py -- Verifes existance of each Bible, book and chapter file expected
	Config.py -- Config class used by programs
	DBLAuthV1.py -- (not working yet) DBL API access
	DownloadFile.py -- Utility to download one file
	DownloadInfo.py -- Utility to download info.json files
	GenPermissionRequest.py -- Generates PermissionRequest.txt
	JesusFilmImporter.py -- not yet updated to this version -- Finds all Jesus Films for languages supported
	LanguagesTable.py -- Populates languages table from iso-639-3 data
	ListBucket.py -- Produces bucket lists as a text file
	LocalesTable.py -- Populates Locales table
	LocalizableString2.py -- (not yet updated to this version) Uses Google Translate to develop translated Bible names
	LookupTables.py -- Script code lookup table for getting iso standard script codes from names
	LPTSExtractReader.py -- Class for reading LPTS extract
	NumeralsTable.py -- Populates Numerals table
	SqliteUtility.py -- Class for accessing Sqlite3 database
	TestUnicode.py -- Test program for learning Python unicodedata module

scripts
	FetchData.sh -- Script to download data needed for proces
	SqliteCompare.sh -- Script to compare two copies of an Sqlite3 database
	TypeTables.sh -- Script to populate tables: Countries, Credentials, Languages, Locales, Numerals, Books, Scripts

sql
	CreateTables.sql -- SQL script of table create statements
	Credentials.sql -- SQL script for Credentials table (not in git)
	jesus_filem.sql -- not sure I want this
	video.sql -- not sure I want this, Jesus update
	VideoUpdate.sql -- not sure I want this, KOG update


BuildDB.sh -- Overall script to execute creation and load of Versions.db database
README.md -- This file.


