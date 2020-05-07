# BibleDB
# This is early stages of a new revision. The code is very unfinished, and the repository contains files from prior versions of the same projects. 
This code builds a "Card Catalog" database of a library of text, audio, and video Bibles of many languages.

This is a list of active files used by this project:

data
	iso-639-3 (directory)
	KOGVideo (directory)
	AppleLang.txt - keep only for historical reasons
	AppleLang2020.txt
	Region.txt
	ScriptCodes.txt
	ShortsandsBibles.csv
	USFMBookCodes.txt

py
	BiblesReport.py
	BibleTables.py
	BibleValidate.py
	Config.py
	DownloadInfo.py
	LanguagesTable.py
	ListBucket.py
	LocalesTable.py
	LPTSExtractReader.py
	LookupTables.py
	NumeralsTable.py
	SqliteUtility.py
	TestUnicode.py

scripts
	FetchData.sh
	SqliteCompare.sh
	TypeTables.sh

sql
	CreateTables.sql
	Credentials.sql

.gitignore
BuildDB.sh
README.md


