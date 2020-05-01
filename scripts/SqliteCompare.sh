#!/bin/sh -v

# This is a development / test script that compares two Versions.db databases
# one is expected in ShortSands/BibleApp/Versions and the other in Desktop

#if len(sys.argv) < 2:
#	print("Usage: SqliteCompare.py  prior_database_name")
#	sys.exit()

DATABASE="Versions.db"
PRIOR_DATABASE=$1

sqlite3 $DATABASE <<END_SQL1

.output Versions_new.txt
SELECT iso3, abbreviation, script, country, numerals,
name, nameLocal, nameTranslated, priority FROM Versions
ORDER BY iso3, abbreviation, script;

-- SELECT locale, versionId FROM VersionLocales ORDER BY versionId, locale;

SELECT mediaType, scope, bucket, filePrefix, fileTemplate,
bibleZipFile, lptsStockNo FROM Bibles
ORDER BY bucket, filePrefix


END_SQL1

sqlite3 $PRIOR_DATABASE <<END_SQL2

.output Versions_orig.txt
SELECT iso3, abbreviation, script, country, numerals,
name, nameLocal, nameTranslated, priority FROM Versions
ORDER BY iso3, abbreviation, script;

-- SELECT locale, versionId FROM VersionLocales ORDER BY versionId, locale;

SELECT mediaType, scope, bucket, filePrefix, fileTemplate,
bibleZipFile, lptsStockNo FROM Bibles
ORDER BY bucket, filePrefix

END_SQL2


diff Versions_orig.txt Versions_new.txt > Versions.diff
