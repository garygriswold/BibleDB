#!/bin/sh -ve

# Populate Table regions
sqlite3 Versions.db <<END_SQL1
.separator '|'
.import data/Region.txt regions
END_SQL1

# Populate Table credentials
sqlite3 Versions.db < sql/Credentials.sql

# Populate Table languages
python3 py/LanguagesTable.py

# Populate Table locales
python3 py/LocalesTable.py

# Populate Table numerals
python3 py/NumeralsTable.py


