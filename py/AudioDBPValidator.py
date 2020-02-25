#
# Validate the permissions of the Audio Bibles listed in Versions.db Audio tables.
# And verify that the S3 key generation logic can correctly generate a key for
# each chapter of each book.
#
import sqlite3
import io
import boto3

dbpProd = io.open("metadata/FCBH/dbp_prod.txt", mode="r", encoding="utf-8")
session = boto3.Session(profile_name='FCBH_BibleApp')
client = session.client('s3')
target = "/Users/garygriswold/Downloads/FCBH/"

def zeroPadChapter(chapter):
	chapStr = str(chapter)
	if len(chapStr) == 1:
		return "00" + chapStr
	elif len(chapStr) == 2:
		return "0" + chapStr
	else:
		return chapStr

def generateS3Key(book, chap):
	#abbr = book[5] + book[6]
	if book[1] != "PSA":
		chap = "_" + chap[1:]
	name = book[3].replace(" ", "_")
	name = name + "____________"[0:(12 - len(name))]
	damId = book[0].split("/")[2]
	key = "%s/%s__%s_%s%s.mp3" % (book[0], book[2], chap, name, damId)
	return key

dbProdSet = set()
for line in dbpProd:
	if line[0:6] == "audio/":
		line = line.strip()
		dbProdSet.add(line)

dbpProd.close()

audioFiles = []
db = sqlite3.connect('Versions.db')
cursor = db.cursor()
sql = "SELECT bibleId, otDamId, ntDamId FROM Bible ORDER BY bibleId"
values = ()
cursor.execute(sql, values)
for row in cursor:
	audioFiles.append(row)

books = []
for audio in audioFiles:
	sql = "SELECT damId, bookId, bookOrder, bookName, numberOfChapters" \
	+ " FROM AudioBook WHERE damId IN(?, ?) ORDER BY damId, bookOrder"
	values = (audio[1], audio[2])
	cursor.execute(sql, values)
	if cursor.rowcount == 0:
		print("NO AudioBook: " + audio)
	for row in cursor:
		book = (row[0], row[1], row[2], row[3], row[4], audio[0], "UNV")#audio[2])
		books.append(book)

for book in books:
	# For each chapter of each book generate a key, and search for it in dbp_prod.txt
	numChap = int(book[4])
	for ch in range(numChap):
		chap = zeroPadChapter(ch + 1)
		key = generateS3Key(book, chap)
		#print key
		if key not in dbProdSet:
			print "NOT FOUND: " + key

	# For GEN:1, MAL:1, MAT:1, REV:1 attempt a download and report any error
	bookId = book[1] + "X" # added to disable this section
	if bookId == "GEN" or bookId == "MAL" or bookId == "MAT" or bookId == "REV":
		key = generateS3Key(book, "001")
		filename = target + book[0] + "_" + bookId
		print key
		try:
			client.download_file('dbp-prod', key, filename)
			#print "Done ", key
		except:
			print "Error Failed ", key



















