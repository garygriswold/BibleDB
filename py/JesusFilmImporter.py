# This is a command line program that accesses the Jesus Film API, and
# populates the tables JesusFilm and Video with data of the API.
#
# It first finds all country codes in the World using the Region table
# so that it can lookup in the API for all countries.
# Next, it finds all of the sil codes (3 char lang codes) that is used in the
# Bible App.  So, that it will extract data only for those languages.
# Next, it pulls the language code data from the JesusFilm Api for all
# country codes and selecting languages.
#
# 28672 Mar 20 12:37 Versions.db It contains only Video table
# 143360 Mar 20 13:36 Versions.db
# Jesus Film is 114,688
# Jan 11, 2019, rewrite in python

import io
#import urllib2
import json
from urllib.request import urlopen
from Config import *
from SqliteUtility import *

out = io.open("sql/jesus_film.sql", mode="w", encoding="utf-8")
out.write(u"DROP TABLE IF EXISTS JesusFilm;\n")
out.write(u"CREATE TABLE JesusFilm (\n")
out.write(u"  country TEXT NOT NULL,\n")
out.write(u"  iso3 TEXT NOT NULL,\n")
out.write(u"  languageId TEXT NOT NULL,\n")
out.write(u"  population INT NOT NULL,\n")
out.write(u"  PRIMARY KEY(country, iso3, languageId));\n")

config = Config()
db = SqliteUtility(config)
sql = "SELECT iso2 FROM Countries ORDER BY iso2"
countries = db.selectList(sql, ())
print(countries)
for country in countries:

	#response = urlopen("http://www.google.com/")
	#html = response.read()
	#print(html)

	url = "https://api.arclight.org/v2/media-countries/" + country + "?expand=mediaLanguages&metadataLanguageTags=en"
	url += "&apiKey=585c557d846f52.04339341"
	results = None
	try:
		response = urlopen(url)
		html = response.read()
		results = json.loads(html)
		#response = json.loads(answer.read())
	except Exception as err:
		print("Could not process", country, str(err))

	embedded = results["_embedded"]
	print("EMBEDDED", embedded)
	sys.exit()
#	if embedded != None:
#		jfpLangs = embedded["mediaLanguages"]
#		for lang in jfpLangs:
#			iso3 = lang["iso3"]
#			languageId = lang["languageId"]
#			population = lang["counts"]["countrySpeakerCount"]["value"]
#			sql = "INSERT INTO JesusFilm (country, iso3, languageId, population) VALUES ('%s','%s','%s',%s);\n"
#			out.write(sql % (country, iso3, languageId, population))


out.close()
db.close()

