# LocalesTable.py
#
# Before running this program, it might be necessary to update the AppleLang.txt file
# This file was created in swift by running Locale.availableLanguages and parsing it
# into locale | languageCode | scriptCode | name
# It is essential to parse out scriptCode from the identifer, because locale.scriptCode
# returns nil for the default script of each language

import io
import sqlite3


# Read in the AppleLang.txt table
values = []
input3 = io.open("data/AppleLang.txt", mode="r", encoding="utf-8")
for line in input3:
	line = line.strip()
	row = line.split("|")
	locale = row[0]
	name = row[3]

	parts = locale.split("_")
	iso1 = parts[0]
	script = parts[1] if len(parts) > 1 else None
	if script in {"Adlm","Arab","Aran","Mand","Mend","Orkh","Rohg","Samr",
				"Syrc","Syre","Syrj","Syrn","Thaa","Wole"}:
		direction = "rtl"
	else:
		direction = "ltr"
	print("%s, %s, %s" % (iso1, script, name))
	values.append((iso1, script, None, direction, name))

input3.close()

sql = "INSERT INTO locales (iso, script, country_id, direction, english_name) VALUES (?, ?, ?, ?, ?)"
conn = sqlite3.connect("Versions.db")
cursor = conn.cursor()
cursor.executemany(sql, values)
conn.commit()
