# LanguagesTable.py
#
# This program generates SQL statements to create and populate the Language table
# It reads SIL provided 639 tables to do this
#
# iso-639-3.txt
#	tab delimited, line 1 is heading
#	0. iso3
#	1. iso2B
#	2. iso2T
#	3. iso1
#	4. scope I=individual, M=metalanguage
#	5. type L, E, C, H, A
#	6. name
#
# iso-639-3-macrolanguages.txt
#	tab delimited, line 1 is heading
#	0. macro iso
#	1. iso
#	2. status A
#

import io
import sqlite3

macroMap = {}
# Read in macrolanguage table, and create table of macro codes iso : macro
input1 = io.open("data/iso-639-3/iso-639-3-macrolanguages.tab", mode="r", encoding="utf-8")
for line in input1:
    row = line.split("\t")
    macroMap[row[1]] = row[0]
    macroMap[row[0]] = row[0]
input1.close()

iso1Map = {}
# Read in 639 table 
input2 = io.open("data/iso-639-3/iso-639-3.tab", mode="r", encoding="utf-8")
for line in input2:
	row = line.split("\t")
	iso3 = row[0]
	if (iso3 != "Id"):
		iso1 = row[3]
		if (len(iso1) > 0):
			iso1Map[iso3] = iso1
input2.close()

values = []
input3 = io.open("data/iso-639-3/iso-639-3.tab", mode="r", encoding="utf-8")
for line in input3:
	if not line.startswith("Id"):
		row = line.split("\t")
		iso3 = row[0]
		iso1 = row[3] if row[3] != "" else None
		name = row[6]
		macro = macroMap.get(iso3)
		if macro != None and iso1 == None:
			iso1 = iso1Map.get(macro)
		#print(iso3, macro, iso1, name)
		values.append((iso3, macro, iso1, name))
input3.close()

sql = "INSERT INTO languages (iso3, macro, iso1, english_name) VALUES (?, ?, ?, ?)"
conn = sqlite3.connect("Versions.db")
cursor = conn.cursor()
cursor.executemany(sql, values)
conn.commit()





