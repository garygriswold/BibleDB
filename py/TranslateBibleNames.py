#
# This program is for translating Bible names that are in English
# into the language of that Bible.  It is strange that so many
# Bible names are only in English
#
import httplib
import sys
import io
import json
import sqlite3

# submits a request to Google for translation
def getTranslation(body):
	conn = httplib.HTTPSConnection("translation.googleapis.com")
	path = "/language/translate/v2?key=AIzaSyAl5-Sk0A8w7Qci93-SIwerWS7lvP_6d_4"
	headers = {"Content-Type": "application/json; charset=utf-8"}
	content = body.encode('utf-8')
	try:
		conn.request("POST", path, content, headers)
		response = conn.getresponse()
		#print response.status, response.reason
		return response
	except Exception, err:
		print "Error: ", str(err), body
		return None

# This function adjusts some names, because they were translating poorly
# Especially the word 'Version' is a problem
def fixEnglishName(bibleId):
	names = {}
	return names.get(bibleId)

# Some Bibles has already translated names in the name field, which is
# better than the name that is gotten by translating the english name
# For those, the name should be used
def useName(bibleId):
	useName = ["ERV-AWA.db", "ERV-ORI.db"]
	return bibleId in useName


out = io.open("sql/LocalizedBibleNames.sql", mode="w", encoding="utf-8")
db = sqlite3.connect('Versions.db')
cursor = db.cursor()
sql = "SELECT bibleId, iso3, name, englishName, iso1"
sql += " FROM Bible"
sql += " ORDER BY bibleId"
values = ( )
cursor.execute(sql, values)
for row in cursor:
	bibleId = row[0]
	iso3 = row[1]
	name = row[2]
	englishName = row[3]
	checkName = fixEnglishName(bibleId)
	if checkName != None:
		englishName = checkName
	iso1 = row[4]
	#language = row[5]
	translated = None
	if iso1 == "en":
		translated = englishName
	elif iso1 != None:
		if englishName == None or englishName.strip() == '':
			print "ERROR no EnglishName for", bibleId
		request = u'{ "source":"en", "target":"%s", "q":"%s" }' % (iso1, englishName)
		response = getTranslation(request)
		if response != None:
			if response.status == 200:
				obj = json.JSONDecoder().decode(response.read())
				translations = obj["data"]["translations"]
				translated = translations[0]['translatedText']
				if englishName == translated:
					print "200, but no translation ", bibleId, iso3, iso1, name, englishName
			elif response.status == 400:
				#print "400", bibleId, name, englishName
				if name != englishName:
					translated = name
				else:
					print "400", name, englishName
					out.write("-- 400 matching names %s (%s) {%s}\n" % (bibleId, englishName, name))
			else:
				print "ERROR", response.status, bibleId, name, englishName
				out.write("ERROR %s %s" % response.status, name)
		else:
			print "ERROR in translation", bibleId, request
			out.write("ERROR in translation %s \n" % (bibleId))
	else:
		translated = None
		print "No iso1 code for Translation ", bibleId
	if useName(bibleId):
		translated = name
	if translated != None:
		backTranslated = None
		request2 = u'{ "source":"%s", "target":"en", "q":"%s" }' % (iso1, translated)
		response2 = getTranslation(request2)
		if response2.status == 200:
			obj2 = json.JSONDecoder().decode(response2.read())
			translations2 = obj2["data"]["translations"]
			backTranslated = translations2[0]['translatedText']	
		if translated.find("'") >= 0 and translated.find("''") < 0:
			translated = translated.replace("'", "''") 
		out.write("UPDATE Bible set localizedName = '%s' WHERE bibleId = '%s'; -- %s [%s] (%s) {%s}\n" % 
		(translated, bibleId, iso1, backTranslated, englishName, name))

db.close()
out.close()




