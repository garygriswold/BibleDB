# NumeralsTable.py
#
# This table populates the numerals table from the numerals data in info.json
#

import io
import os
import sys
import sqlite3
import json
import unicodedata

DIRECTORY = "/Volumes/FCBH/info_json/"

numberMap = {}
files = os.listdir(DIRECTORY)
for file in files:
	if not file.startswith(".") and file.endswith("info.json"):
		#print(file)
		input = io.open(DIRECTORY + file, mode="r", encoding="utf-8")
		data = input.read()
		try:
			info = json.loads(data)
			numbers = info["numbers"]
			number9 = numbers[9]
			name = unicodedata.name(number9)
			#print(file, name)
			name = name.replace("DIGIT NINE", "").strip()
			if len(name) == 0:
				name = "western-arabic"
			elif name == "ARABIC-INDIC":
				name = "eastern-arabic"
			elif name == "EXTENDED ARABIC-INDIC":
				name = "extended eastern-arabic"
			else:
				name = name.lower()
			numberMap[name] = numbers
			#bibles = numberMap.get(name, [])
			#bibles.append(file)
			#numberMap[name] = bibles
			#print(file, number9, unicodedata.name(number9), name)
		except Exception as err:
			print("Could not parse", err)

		input.close()

values = []
for name, numbers in numberMap.items():
	print(name, numbers)
	print(",".join(numbers))
	values.append((name, ",".join(numbers)))

sql = "INSERT INTO numerals (numeral_id, numbers) VALUES (?, ?)"
conn = sqlite3.connect("Versions.db")
cursor = conn.cursor()
cursor.executemany(sql, values)
conn.commit()
