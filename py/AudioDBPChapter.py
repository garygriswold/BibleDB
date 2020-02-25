# This program collects verse meta data for all books and chapters that have this data
#

import io
import sqlite3
import urllib2
import json

HOST = "https://dbt.io/";
KEY = "key=b37964021bdd346dc602421846bf5683&v=2";

output = io.open("sql/AudioChapterTable.sql", mode="w", encoding="utf-8")
output.write(u"DROP TABLE IF EXISTS AudioChapter;\n")
output.write(u"CREATE TABLE AudioChapter(\n")
output.write(u"  damId TEXT NOT NULL REFERENCES Audio(damId),\n")
output.write(u"  bookId TEXT NOT NULL,\n")
output.write(u"  chapter INTEGER NOT NULL,\n")
output.write(u"  versePositions TEXT NOT NULL,\n")
output.write(u"  PRIMARY KEY (damId, bookId, chapter),\n")
output.write(u"  FOREIGN KEY (damId, bookId) REFERENCES AudioBook(damId, bookId));\n")

def getOsisBookCode(bookCode):
	books = {
		'GEN': 'Gen',
		'EXO': 'Exod',
		'LEV': 'Lev',
		'NUM': 'Num',
		'DEU': 'Deut',
		'JOS': 'Josh',
		'JDG': 'Judg',
		'RUT': 'Ruth',
		'1SA': '1Sam',
		'2SA': '2Sam',
		'1KI': '1Kgs',
		'2KI': '2Kgs',
		'1CH': '1Chr',
		'2CH': '2Chr',
		'EZR': 'Ezra',
		'NEH': 'Neh',
		'EST': 'Esth',
		'JOB': 'Job',
		'PSA': 'Ps',
		'PRO': 'Prov',
		'ECC': 'Eccl',
		'SNG': 'Song',
		'ISA': 'Isa',
		'JER': 'Jer',
		'LAM': 'Lam',
		'EZK': 'Ezek',
		'DAN': 'Dan',
		'HOS': 'Hos',
		'JOL': 'Joel',
		'AMO': 'Amos',
		'OBA': 'Obad',
		'JON': 'Jonah',
		'MIC': 'Mic',
		'NAM': 'Nah',
		'HAB': 'Hab',
		'ZEP': 'Zeph',
		'HAG': 'Hag',
		'ZEC': 'Zech',
		'MAL': 'Mal',
		'MAT': 'Matt',
		'MRK': 'Mark',
		'LUK': 'Luke',
		'JHN': 'John',
		'ACT': 'Acts',
		'ROM': 'Rom',
		'1CO': '1Cor',
		'2CO': '2Cor',
		'GAL': 'Gal',
		'EPH': 'Eph',
		'PHP': 'Phil',
		'COL': 'Col',
		'1TH': '1Thess',
		'2TH': '2Thess',
		'1TI': '1Tim',
		'2TI': '2Tim',
		'TIT': 'Titus',
		'PHM': 'Phlm',
		'HEB': 'Heb',
		'JAS': 'Jas',
		'1PE': '1Pet',
		'2PE': '2Pet',
		'1JN': '1John',
		'2JN': '2John',
		'3JN': '3John',
		'JUD': 'Jude',
		'REV': 'Rev'   
	}
	result = books[bookCode]
	if result == None:
		print "ERROR no OSIS code for", bookCode
	return result

def getVerseNumbers(damId, osisCode, chapter):
	chapStr = str(chapter)
	dam_id = damId.split('/')[2]
	url = HOST + "audio/versestart?" + KEY + "&dam_id=" + dam_id + "&osis_code=" + osisCode + "&chapter_number=" + chapStr
	try:
		response = urllib2.urlopen(url)
		data = response.read()
	except Exception, err:
		print "ERROR", damId, osisCode, chapter, verses, err
		return False	
	try:
		if data != None and len(data) > 0:
			verses = json.loads(data)
			lastVerseId = int(verses[-1:][0]["verse_id"])
			array = [None] * (lastVerseId + 1)
			array[0] = 0
			for verse in verses:
				num = int(verse["verse_id"])
				pos = float(verse["verse_start"])
				array[num] = pos

			for idx in range(1, len(array)):
				if array[idx] == None:
					array[idx] = array[idx - 1]

			numbers = json.dumps(array)
			numbers = numbers.replace(" ", "")
			output.write("INSERT INTO AudioChapter VALUES('%s', '%s', '%s', '%s');\n" % (damId, bookId, chapter, numbers))
			return True
	except Exception, err:
		print "ERROR", damId, osisCode, chapter, verses, err
		return False

db = sqlite3.connect('Versions.db')
cursor = db.cursor()
sql = "SELECT damId, bookId, numberOfChapters FROM AudioBook ORDER BY damId, bookOrder"
#sql = "SELECT damId, bookId, numberOfChapters FROM AudioBook WHERE damId like '%ENGESVN2DA' ORDER BY damId, bookOrder"
values = ()
cursor.execute(sql, values)
rows = cursor.fetchall()
for row in rows:
	damId = row[0]
	bookId = row[1]
	osisCode = getOsisBookCode(bookId)
	numberOfChapters = row[2]

	print damId, bookId, osisCode, numberOfChapters
	ok = getVerseNumbers(damId, osisCode, 1)
	if ok and numberOfChapters > 1:
		for chap in range(2, (numberOfChapters + 1)):
			getVerseNumbers(damId, osisCode, chap)

db.close()
output.close()
exit()

