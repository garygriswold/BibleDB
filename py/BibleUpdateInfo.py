# This program updates the Bible table with data from info.json that could not
# be gotten from the Bibles query.
# direction, script, country

import io
import sqlite3
import json

source = os.environ['HOME'] + "/ShortSands/DBL/FCBH_info/"

out = io.open("sql/bible_update.sql", mode="w", encoding="utf-8")

db = sqlite3.connect('Versions.db')
cursor = db.cursor()
sql = "SELECT bibleId, textBucket, textId FROM Bible ORDER BY bibleId"
values = ()
cursor.execute(sql, values)
rows = cursor.fetchall()
for row in rows:
	bibleId = row[0]
	textBucket = row[1]
	textId = row[2]

	try:
		filename = textId.replace("/", ":") + ":info.json"
		#filename = textKey = "text:" + bibleId + ":" + textId + ":info.json"
		#print("open", filename)
		input = io.open(source + filename, mode="r", encoding="utf-8")
		data = input.read()
		bible = json.loads(data)

		#bid = bible["id"]
		#if bid != bibleId:
		#	print("bibleId and internal id not equal", bibleId, bid)

		# convert script to iso 15924 code
		script = bible['script']

		validScripts = [None, 'Arab', 'Beng', 'Bugi', 'Cans', 'Cyrl', 'Deva', 'Ethi', 'Geor', 
		'Hans', 'Hant', 'Java', 'Kore', 'Latn', 'Orya', 'Syrc', 'Taml', 'Thai' ]

		if script not in validScripts:
			if script == 'Latin':
				script = 'Latn'
			elif script == 'Cyrillic':
				script = 'Cyrl'
			elif script == 'Arabic':
				script = 'Arab'
			elif script == 'Devangari':
				script = 'Deva'
			elif script == 'Devanagari (Nagari)':
				script = 'Deva'
			elif script == 'CJK':
				script = None
			elif script.strip() == '':
				script = None
			else:
				print "ERROR: unknown script code", script, filename
		script = script if script != None else ''

		country = bible['countryCode']
		country = "'" + country.upper() + "'" if len(country) > 0 else 'null'

		sql = "UPDATE Bible SET script='%s', country=%s WHERE bibleId='%s';\n"
		out.write(sql % (script, country, bibleId))

	except Exception, err:
		print "Could not parse info.json", filename, str(err)

out.close()
