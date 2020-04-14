#!/bin/sh -ve

# Populate Table regions
sqlite3 Versions.db <<END_SQL1
.separator '|'
.import data/Region.txt Countries
END_SQL1

# Populate Table credentials
sqlite3 Versions.db < sql/Credentials.sql

# Populate Table languages
python3 py/LanguagesTable.py

# Populate Table locales
python3 py/LocalesTable.py

# Populate Table numerals
python3 py/NumeralsTable.py

# Populate Table books
sqlite3 Versions.db <<END_SQL2
.separator '|'
.import data/USFMBookCodes.txt Books
END_SQL2

# Populate Table scripts
sqlite3 Versions.db <<END_SQL3
.separator '|'
.import data/ScriptCodes.txt Scripts
update scripts set font=null where font='';
END_SQL3

