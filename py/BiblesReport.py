# BiblesReport.py
#
# This program provides a human readable display of Bibles data in the Sqlite3 database
#

import csv
from Config import *
from SqliteUtility import *

class BiblesReport:

	def commandLine():
		print("do options here")
		return {}


	def __init__(self, config):
		self.config = config
		self.db = SqliteUtility(self.config)

	def processSimple1(self):
		filename = "BiblesReport.csv"
		with open(filename, 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
			sql = ("SELECT v.versionId, v.iso3, v.abbreviation, v.script, v.country, v.numerals, v.name, v.nameLocal, v.priority, l.name"
				" FROM Versions v, Languages l"
				" WHERE v.iso3 = l.iso3"
				" ORDER BY v.iso3, v.script, v.abbreviation")
			versionList = self.db.select(sql, ())
			for vers in versionList:
				locale = "%s-%s-%s" % (vers[1], vers[3], vers[4])
				writer.writerow((vers[9], vers[2], locale, vers[5], vers[6], vers[7], vers[8], vers[0]))
				sql = "SELECT locale FROM VersionLocales WHERE versionId=? ORDER BY length(locale) desc"
				localesList = self.db.select(sql, (vers[0],))
				row = [None, None]
				for loc in localesList:
					row.append(loc[0])
				writer.writerow(row)
				sql = ("SELECT systemId, mediaType, scope, bucket, filePrefix, fileTemplate"
						" FROM Bibles WHERE versionId=?")
				biblesList = self.db.select(sql, (vers[0],))
				for bib in biblesList:
					writer.writerow((None, None, bib[1], bib[2], bib[3], bib[4], bib[5], bib[0]))


				#print(row[1], row[2], row[3])
		# for each version Select from Bible






if __name__ == "__main__":
	config = Config()
	options = BiblesReport.commandLine()
	print("options")
	report = BiblesReport(config)
	report.processSimple1()