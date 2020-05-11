#!/bin/sh -ve

export FCBH_PROJ=$HOME/FCBH/dbp-etl/
export BIBLE_DB_PROJ=$HOME/ShortSands/BibleDB/

cd $BIBLE_DB_PROJ

sh scripts/FetchData.sh

rm Versions.db

sqlite3 Versions.db < sql/CreateTables.sql

sh scripts/TypeTables.sh

cd $FCBH_PROJ
time python3 load/Validate.py test bucketlists

cd $BIBLE_DB_PROJ
time python3 py/BibleTables.py dev > bibleTables.out

time python3 py/BiblesReport.py dev > biblesReport.out

# Validate Bible Table keys against bucket contents
time python3 py/BibleValidate.py dev > bibleValidate.out
grep ERROR bibleValidate.out

# Generate PermissionsRequest.txt
time python3 py/GenPermissionsRequest.py dev

exit


# Validate the lookup of info.json files and the last chapter.
# This can be run after permission has been granted.
python py/BibleValidate2.py

# Create A Copy of DB before Deletions
cp Versions.db VersionsFull.db

# Remove Languages and Bibles that are not used.
sqlite Versions.db <<END_SQL
select count(*) from Language;
select count(*) from Bible;

-- See those Bibles that will be kept, because we have a Language record for them
select bibleId, iso3, iso1, script from Bible where iso1 || script in (select iso1 || script from Language)
union
select bibleId, iso3, iso1, script from Bible where iso1 in (select iso1 from Language) 
order by iso1;

-- See those Bibles that will be deleted, because we do not have a Language record for them
select bibleId, iso3, iso1, script from Bible where iso1 not in (select iso1 from Language)
and iso1 || script not in (select iso1 || script from Language)
order by iso1;

-- Delete them
delete from Bible where iso1 not in (select iso1 from Language)
and iso1 || script not in (select iso1 || script from Language);

select count(*) from Bible;
select count(*) from Language;

-- See those Languages that will be kept, because we have a Bible for it.
select * from Language where iso1 || script in (select iso1 || script from Bible)
union
select * from Language where iso1 in (select iso1 from Bible);

-- See those Languages that will be deleted,
select * from Language where iso1 not in (select iso1 from Bible)
and iso1 || script not in (select iso1 || script from Bible)
order by iso1;

-- Delete them
delete from Language where iso1 not in (select iso1 from Bible)
and iso1 || script not in (select iso1 || script from Bible);

select count(*) from Language;
vacuum;
END_SQL

# Validate the lookup of info.json files and the last chapter
python py/BibleValidate2.py

# Use Google Translate to improve the Bible names
python py/TranslateBibleNames.py
sqlite Versions.db < sql/LocalizedBibleNames.sql
sqlite Versions.db <<END_SQL2
UPDATE Bible SET localizedName = name WHERE localizedName is NULL;
END_SQL2

###################### Audio Player ######################

# Generate AudioBook table by parse of dbp-prod
python py/AudioDBImporter.py

sqlite Versions.db < sql/AudioBookTable.sql

# Generate AudioChapter table by DBP API
python py/AudioDBPChapter.py

sqlite Versions.db < sql/AudioChapterTable.sql

# Validate the generated keys
python py/AudioDBPValidator.py

# patch problems in damId selection
sqlite Versions.db <<END_SQL7
UPDATE Bible SET otDamId='ENGWEBO2DA', ntDamId='ENGWEBN2DA' WHERE bibleId='ENGWEB'
update AudioBook set damId='ENGWEBN2DA' where damId='EN1WEBN2DA';
update AudioBook set damId='ENGWEBO2DA' where damId='EN1WEBO2DA';
END_SQL7

###################### Video Player ######################

# Pulls data from JFP web service, and generates JesusFilm table
python py/JesusFilmImporter.js

sqlite Versions.db < sql/jesus_film.sql

# Create Video table by extracting data from Jesus Film Project
python py/VideoTable.py

sqlite Versions.db < sql/video.sql

# Erase video descriptions in English for non-English languages
sqlite Versions.db <<END_SQL5
update Video set description=null where languageId != '529' and mediaId='1_jf-0-0' and description = (select description from Video where languageId='529' and mediaId='1_jf-0-0');
update Video set description=null where languageId != '529' and mediaId='1_wl-0-0' and description = (select description from Video where languageId='529' and mediaId='1_wl-0-0');
update Video set description=null where languageId != '529' and mediaId='1_cl-0-0' and description = (select description from Video where languageId='529' and mediaId='1_cl-0-0');
vacuum;
END_SQL5

# Edit VideoUpdate.sql for changes in ROCK videos
sqlite Versions.db < sql/VideoUpdate.sql

# Loads KOG Descriptions into Video table
python py/VideoUpdate.py

# Add a table that contols the sequence of Video Presentation in App
sqlite Versions.db <<END_SQL6
DROP TABLE IF EXISTS VideoSeq;
CREATE TABLE VideoSeq (mediaId TEXT PRIMARY KEY, sequence INT NOT NULL);
INSERT INTO VideoSeq VALUES ('1_jf-0-0', 1);
INSERT INTO VideoSeq VALUES ('1_cl-0-0', 2);
INSERT INTO VideoSeq VALUES ('1_wl-0-0', 3);
INSERT INTO VideoSeq VALUES ('KOG_OT', 4);
INSERT INTO VideoSeq VALUES ('KOG_NT', 5);
END_SQL6

###################### String Localization ######################

# Make certain that all desired languages are included in xCode project
# Make certain that py/LocalizableStrings2.py contains a google lang code for each
# Using xCode project, Editor -> Export Localization, put into Downloads
# Select only the languages that need work, which might be all

python py/LocalizableStrings2.py

# Using xCode project, Editor -> Import Localization, import each converted language


