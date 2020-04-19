# BibleDB
# This is early stages of a new revision. The code is very unfinished, and the repository contains files from prior versions of the same projects. 
This code builds a "Card Catalog" database of a library of text, audio, and video Bibles of many languages.

This is a list of active files used by this project:

data
	AppleLang.txt - keep only for historical reasons
	AppleLang2020.txt
	Region.txt
	ScriptCodes.txt
	USFMBookCodes.txt

py
	BibleTables.py
	Config.py
	DownloadInfo.py
	LanguagesTable.py
	ListBucket.py
	LPTSExtractReader.py
	LocalesTable.py
	LookupTables.py (only needed if getting script from LPTS)
	NumeralsTable.py
	SqliteUtility.py
	TestUnicode.py

scripts
	FetchData.sh
	TypeTables.sh

sql
	CreateTables.sql
	Credentials.sql

.gitignore
BuildDB.sh
README.md


