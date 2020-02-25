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
input1 = io.open("metadata/iso-639-3/iso-639-3-macrolanguages.txt", mode="r", encoding="utf-8")
for line in input1:
    row = line.split("\t")
    if not row[1] in ['yue']: # put language codes we want to keep here
    	macroMap[row[1]] = row[0]
    	macroMap[row[0]] = row[0]
input1.close()

iso1Map = {}
# Read in 639 table 
input2 = io.open("metadata/iso-639-3/iso-639-3.txt", mode="r", encoding="utf-8")
for line in input2:
	row = line.split("\t")
	iso3 = row[0]
	if (iso3 != "Id"):
		iso1 = row[3]
		if (len(iso1) > 0):
			iso1Map[iso3] = iso1
input2.close()

out = io.open("sql/Bible_lang.sql", mode="w", encoding="utf-8")

db = sqlite3.connect('Versions.db')
cursor = db.cursor()
sql = "SELECT bibleId, iso3, script FROM Bible ORDER BY bibleId"
values = ()
cursor.execute(sql, values)
rows = cursor.fetchall()
for row in rows:
	bibleId = row[0]
	iso3 = row[1]
	script = row[2]
	# lookup iso1
	iso1 = iso1Map.get(iso3, None)
	if iso1 == None:
		macro = macroMap.get(iso3, None)
		if macro != None:
			iso1 = iso1Map.get(macro, None)
	if iso1 == None:
		iso1 = iso3
	#print("%s  iso3=%s  iso1=%s  mac=%s" % (bibleId, iso3, iso1, macro))
	out.write("UPDATE Bible SET iso1='%s' WHERE bibleId='%s';\n" % (iso1, bibleId))
out.close()



