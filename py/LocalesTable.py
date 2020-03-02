# LocalesTable.py
#
# Before running this program, it might be necessary to update the AppleLang.txt file
# This file was created in swift by running the program below.
# It is essential to parse out scriptCode from the identifer, because locale.scriptCode
# returns nil for the default script of each language
#
#import UIKit
#let me = Locale.current
#var idents:[String] = Locale.availableIdentifiers
#idents.sort()
#for item in idents {
#    let parts:[String] = item.components(separatedBy: "_")
#    let lang = parts[0]
#    var script: String? = nil
#    if parts.count > 1 {
#        if parts[1].count == 4 {
#            script = parts[1]
#        }
#    }
#    let loc = Locale(identifier: item)
#    let name: String? = me.localizedString(forIdentifier: item)
#    print("\(item)\t\(loc.languageCode!)\t\(loc.scriptCode ?? "")\t\(loc.variantCode ?? "")\t\(loc.regionCode ?? "")\t\(name ?? "")")
#}

import io
import sqlite3


# Read in the AppleLang.txt table
values = []
input3 = io.open("data/AppleLang2020.txt", mode="r", encoding="utf-8")
for line in input3:
	line = line.strip()
	(locale, lang, script, country, variant, name) = line.split("\t")
	if script == "":
		script = None
	if country == "":
		country = None
	if variant == "":
		variant = None
	if script in {"Adlm","Arab","Aran","Mand","Mend","Orkh","Rohg","Samr",
				"Syrc","Syre","Syrj","Syrn","Thaa","Wole"}:
		direction = "rtl"
	else:
		direction = "ltr"
	#print("%s,%s,%s" % (lang, script, name))
	values.append((locale, lang, script, country, variant, direction, name))

input3.close()

sql = "INSERT INTO locales (locale, iso, script, country_id, variant, direction, english_name) VALUES (?, ?, ?, ?, ?, ?, ?)"
conn = sqlite3.connect("Versions.db")
cursor = conn.cursor()
cursor.executemany(sql, values)
conn.commit()
