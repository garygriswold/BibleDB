#
# The purpose of this program is to generate the Audio meta data tables,
# including AudioVersion, Audio, and AudioBook.  AudioChapter is separately
# created.
#
import sqlite3
import io
import sys

# Build a map of bibles and damId's to collect
# This table controls what Audio versions will be included, and what
# text versions that are associated with
#versions = {}
versions = set()
db = sqlite3.connect('Versions.db')
cursor = db.cursor()
sql = "SELECT bibleId, otDamId, ntDamId FROM Bible ORDER BY bibleId"
values = ()
cursor.execute(sql, values)
rows = cursor.fetchall()
for row in rows:
	otDamId = row[1]
	ntDamId = row[2]
	if otDamId != None:
		versions.add(otDamId)
	if ntDamId != None:
		versions.add(ntDamId)

db.close()

def usfmBookId(bookName):
	books = {
		'Genesis':   	'GEN',
		'Exodus':  		'EXO',
		'Leviticus':   	'LEV',
		'Numbers':   	'NUM',
		'Deuteronomy':  'DEU',
		'Joshua':  		'JOS',
		'Judges':  		'JDG',
		'Ruth':  		'RUT',
		'1Samuel':  	'1SA',
		'2Samuel':  	'2SA',
		'1Kings':  		'1KI',
		'2Kings':  		'2KI',
		'1Chronicles':  '1CH',
		'2Chronicles':  '2CH',
		'Ezra':  		'EZR',
		'Nehemiah':   	'NEH',
		'Esther':  		'EST',
		'Job':   		'JOB',
		'Psalms':    	'PSA',
		'Proverbs':  	'PRO',
		'Ecclesiastes': 'ECC',
		'SongofSongs':  'SNG',
		'Isaiah':   	'ISA',
		'Jeremiah':   	'JER',
		'Lamentations': 'LAM',
		'Ezekiel':  	'EZK',
		'Daniel':   	'DAN',
		'Hosea':   		'HOS',
		'Joel':  		'JOL',
		'Amos':  		'AMO',
		'Obadiah':  	'OBA',
		'Jonah': 		'JON',
		'Micah':   		'MIC',
		'Nahum':   		'NAM',
		'Habakkuk':   	'HAB',
		'Zephaniah':  	'ZEP',
		'Haggai':   	'HAG',
		'Zechariah':  	'ZEC',
		'Malachi':   	'MAL',
		'Matthew':  	'MAT',
		'Mark':  		'MRK',
		'Luke':  		'LUK',
		'John':  		'JHN',
		'Acts':  		'ACT',
		'Romans':   	'ROM',
		'1Corinthians': '1CO',
		'2Corinthians': '2CO',
		'Galatians':   	'GAL',
		'Ephesians':   	'EPH',
		'Philippians':  'PHP',
		'Colossians':   'COL',
		'1Thess':		'1TH',
		'2Thess':		'2TH',
		'1Timothy':  	'1TI',
		'2Timothy':  	'2TI',
		'Titus': 		'TIT',
		'Philemon':  	'PHM',
		'Hebrews':   	'HEB',
		'James':   		'JAS',
		'1Peter':  		'1PE',
		'2Peter':  		'2PE',
		'1John': 		'1JN',
		'2John': 		'2JN',
		'3John': 		'3JN',
		'Jude':  		'JUD',
		'Revelation':   'REV',
		# Spanish
		'Exodo': 		'EXO',
		'Levitico': 	'LEV',
		'Numeros': 		'NUM',
		'Deuteronomio':	'DEU',
		'Josue': 		'JOS',
		'Jueces': 		'JDG',
		'Rut': 			'RUT',
		'1Reyes': 		'1KI',
		'2Reyes': 		'2KI',
		'1Cronicas': 	'1CH',
		'2Cronicas': 	'2CH',
		'Esdras': 		'EZR',
		'Nehemias': 	'NEH',
		'Ester': 		'EST',
		'Salmos': 		'PSA',
		'Proverbios': 	'PRO',
		'Eclesiastes': 	'ECC',
		'Cantaras': 	'SNG',
		'Isaias': 		'ISA',
		'Jeremias': 	'JER',
		'Lamentacione': 'LAM',
		'Ezequiel': 	'EZK',
		'Oseas': 		'HOS',
		'Abdias': 		'OBA',
		'Jonas': 		'JON',
		'Miqueas': 		'MIC',
		'Habacuc': 		'HAB',
		'Sofonias': 	'ZEP',
		'Hageo': 		'HAG',
		'Zacarias': 	'ZEC',
		'Malaquias': 	'MAL',
		'San Mateo':	'MAT',
		'San Marcos':	'MRK',
		'San Lucas':	'LUK',
		'San Juan':		'JHN',
		'Hechos':		'ACT',
		'Romanos':		'ROM',
		'1Corintios':	'1CO',
		'2Corintios':	'2CO',
		'Galatas':		'GAL',
		'Efesios':		'EPH',
		'Filipenses':	'PHP',
		'Colosenses':	'COL',
		'1Tes':			'1TH',
		'2Tes':			'2TH',
		'1Timoteo':		'1TI',
		'2Timoteo':		'2TI',
		'Tito':			'TIT',
		'Filemon':		'PHM',
		'Hebreos':		'HEB',
		'Santiago':		'JAS',
		'1San Pedro':	'1PE',
		'2San Pedro':	'2PE',
		'1San Juan':	'1JN',
		'2San Juan':	'2JN',
		'3San Juan':	'3JN',
		'Judas':		'JUD',
		'Apocalipsis':	'REV',
		# Portuguese
		'S Mateus':		'MAT',
		'S Marcos':		'MRK',
		'S Lucas':		'LUK',
		'S Joao':		'JHN',
		'Atos':			'ACT',
		'Colossenses':	'COL',
		'1Tess':		'1TH',
		'2Tess':		'2TH',
		'Hebreus':		'HEB',
		'S Tiago':		'JAS',
		'1Pedro':		'1PE',
		'2Pedro':		'2PE',
		'1S Joao':		'1JN',
		'2S Joao':		'2JN',
		'3S Joao':		'3JN',
		'S Judas':		'JUD',
		'Apocalipse':	'REV',
		# Indonesian
		'Matius':		'MAT',
		'Markus':		'MRK',
		'Lukas':		'LUK',
		'Yohanes':		'JHN',
		'Kisah Rasul':	'ACT',
		'Roma':			'ROM',
		'1Korintus':	'1CO',
		'2Korintus':	'2CO',
		'Galatia':		'GAL',
		'Efesus':		'EPH',
		'Filipi':		'PHP',
		'Kolose':		'COL',
		'1Tesalonika':	'1TH',
		'2Tesalonika':	'2TH',
		'1Timotius':	'1TI',
		'2Timotius':	'2TI',
		'Ibrani':		'HEB',
		'Yakobus':		'JAS',
		'1Petrus':		'1PE',
		'2Petrus':		'2PE',
		'1Yohanes':		'1JN',
		'2Yohanes':		'2JN',
		'3Yohanes':		'3JN',
		'Yudas':		'JUD',
		'Wahyu':		'REV',
		# Maasina Fulfulde
		'Matthieu':		'MAT',
		'Marc':			'MRK',
		'Luc':			'LUK',
		'Jean':			'JHN',
		'Actes':		'ACT',
		'Romains':		'ROM',
		'1Corinthiens':	'1CO',
		'2Corinthiens':	'2CO',
		'Galates':		'GAL',
		'Ephesiens':	'EPH',
		'Philippiens':	'PHP',
		'Colossiens':	'COL',
		'1Thess':		'1TH',
		'2Thess':		'2TH',
		'1Timothee':	'1TI',
		'2Timothee':	'2TI',
		'Tite': 		'TIT',
		'Philemon': 	'PHM',
		'Hebreux': 		'HEB',
		'Jacques': 		'JAS',
		'1Pierre': 		'1PE',
		'2Pierre': 		'2PE',
		'1Jean':		'1JN',
		'2Jean':		'2JN',
		'3Jean':		'3JN',
		'Jude':			'JUD',
		'Apocalypse': 	'REV'
	}
	result = books.get(bookName, None)
	return result

bookOut = io.open("sql/AudioBookTable.sql", mode="w", encoding="utf-8")
bookOut.write(u"DROP TABLE IF EXISTS AudioBook;\n")
bookOut.write(u"CREATE TABLE AudioBook(\n")
bookOut.write(u"  damId TEXT NOT NULL REFERENCES Audio(damId),\n")
bookOut.write(u"  bookId TEXT NOT NULL,\n")
bookOut.write(u"  bookOrder TEXT NOT NULL,\n")
bookOut.write(u"  bookName TEXT NOT NULL,\n")
bookOut.write(u"  numberOfChapters INTEGER NOT NULL,\n")
bookOut.write(u"  PRIMARY KEY (damId, bookId));\n")


lastDamId = None
lastUsfm = None
bookLine = None

EXCLUDE = ['GRKAVSO1DA'] # exclude because we do not have OT text

dbpProd = io.open("metadata/FCBH/dbp_prod.txt", mode="r", encoding="utf-8")
for line in dbpProd:
	line = line.strip()
	parts = line.split("/")
	numParts = len(parts)
	if parts[0] == 'audio' and parts[numParts -1][-4:] == ".mp3":
		bibleId = parts[1]
		damId = "audio/" + parts[1] + "/" + parts[2]
		if numParts == 4 and damId in versions and damId not in EXCLUDE:

			# Write AudioBookRow
			book = parts[3]
			damId2 = book[21:31].replace("_", " ").strip()
			if damId2 == parts[2]:
				order = book[0:3]
				chapter = book[5:8]
				chapter = chapter.replace("_", "")
				name = book[9:21]
				name = name.replace("_", " ").strip()
				usfm = usfmBookId(name)
				if usfm == None:
					print "ERROR", line, name
				if usfm != lastUsfm or damId != lastDamId:
					if bookLine != None:
						bookOut.write(bookLine)
					lastUsfm = usfm
					lastDamId = damId
				bookLine = u"REPLACE INTO AudioBook VALUES('%s', '%s', '%s', '%s', '%s');\n" % (damId, usfm, order, name, chapter)

				# Validate Key Generation Logic
				checkChapter = chapter
				if len(checkChapter) < 3:
					checkChapter = "_" + checkChapter
				checkName = name.replace(" ", "_")
				checkName = checkName + "_______________"[0: 12 - len(name)]
				generated = "%s/%s__%s_%s%s.mp3" % (damId, order, checkChapter, checkName, damId2)
				if line != generated:
					print "ERROR"
					print line
					print generated


dbpProd.close()
bookOut.write(bookLine)
bookOut.close()

