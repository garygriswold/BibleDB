# Before running this program, it might be necessary to update the AppleLang.txt file
# This file was created in swift by running Locale.availableLanguages and parsing it
# into locale | languageCode | scriptCode | name
# It is essential to parse out scriptCode from the identifer, because locale.scriptCode
# returns nil for the default script of each language

import io

out = io.open("sql/language.sql", mode="w", encoding="utf-8")

out.write(u"DROP TABLE IF EXISTS Language;\n")
out.write(u"CREATE TABLE Language (\n")
out.write(u"  iso1 TEXT NOT NULL,\n")
out.write(u"  script TEXT NOT NULL,\n")
out.write(u"  name TEXT NOT NULL,\n")
out.write(u"  PRIMARY KEY (iso1, script));\n")
prefix = "INSERT INTO Language VALUES"

# Read in the AppleLang.txt table
input3 = io.open("metadata/AppleLang.txt", mode="r", encoding="utf-8")
for line in input3:
	line = line.strip()
	row = line.split("|")
	locale = row[0]
	name = row[3]

	parts = locale.split("_")
	iso1 = parts[0]
	script = parts[1] if len(parts) > 1 else ''

	out.write("%s ('%s', '%s', '%s');\n" % (prefix, iso1, script, name))

input3.close()
out.close()
