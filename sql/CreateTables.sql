PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS regions;
CREATE TABLE regions (
  country_id TEXT NOT NULL PRIMARY KEY,
  continent_id TEXT NOT NULL CHECK (continent_id IN('AF','EU','AS','NA','SA','OC','AN')),
  geoscheme_id TEXT NOT NULL CHECK (geoscheme_id IN(
		'AF-EAS','AF-MID','AF-NOR','AF-SOU','AF-WES',
		'SA-CAR','SA-CEN','SA-SOU','NA-NOR',
		'AS-CEN','AS-EAS','AS-SOU','AS-SEA','AS-WES',
		'EU-EAS','EU-NOR','EU-SOU','EU-WES',
		'OC-AUS','OC-MEL','OC-MIC','OC-POL','AN-ANT')),
  aws_region TEXT NOT NULL CHECK (aws_region IN (
    'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2',
    'eu-west-1', 'us-east-1')),
  country_name TEXT NOT NULL);

-- Continent Code
-- AF|Africa
-- EU|Europe
-- AS|Asia
-- NA|North America
-- SA|South America
-- OC|Oceana
-- AN|Antartica

-- United Nations geoschema
-- AF-EAS|Eastern Africa
-- AF-MID|Middle Africa
-- AF-NOR|Northern Africa
-- AF-SOU|Southern Africa
-- AF-WES|Western Africa
-- SA-CAR|Caribbean
-- SA-CEN|Central America
-- SA-SOU|South America
-- NA-NOR|North America
-- AS-CEN|Central Asia
-- AS-EAS|Eastern Asia
-- AS-SOU|Southern Asia
-- AS-SEA|South-Eastern Asia
-- AS-WES|Western Asia
-- EU-EAS|Eastern Europe
-- EU-NOR|Northern Europe
-- EU-SOU|Southern Europe
-- EU-WES|Western Europe
-- OC-AUS|Australia and New Zealeand
-- OC-MEL|Melanesia
-- OC-MIC|Micronesia
-- OC-POL|Polynesia

-- Rules for bucket assignment:
-- 1) AF -> eu-west-1
-- 2) EU -> eu-west-1
-- 3) OC -> ap-southeast-2
-- 4) AN -> ap-southeast-2
-- 5) NA -> us-east-1
-- 6) SA -> us-east-1
-- 7) AS-WES -> eu-west-1
-- 8) AS-SOU -> ap-southeast-1
-- 9) AS-SEA -> ap-southeast-1
-- 10) AS-CEN -> ap-northeast-1
-- 11) AS-EAS -> ap-northeast-1
-- Continent Code
-- AF|Africa
-- EU|Europe
-- AS|Asia
-- NA|North America
-- SA|South America
-- OC|Oceana
-- AN|Antartica

-- United Nations geoschema
-- AF-EAS|Eastern Africa
-- AF-MID|Middle Africa
-- AF-NOR|Northern Africa
-- AF-SOU|Southern Africa
-- AF-WES|Western Africa
-- SA-CAR|Caribbean
-- SA-CEN|Central America
-- SA-SOU|South America
-- NA-NOR|North America
-- AS-CEN|Central Asia
-- AS-EAS|Eastern Asia
-- AS-SOU|Southern Asia
-- AS-SEA|South-Eastern Asia
-- AS-WES|Western Asia
-- EU-EAS|Eastern Europe
-- EU-NOR|Northern Europe
-- EU-SOU|Southern Europe
-- EU-WES|Western Europe
-- OC-AUS|Australia and New Zealeand
-- OC-MEL|Melanesia
-- OC-MIC|Micronesia
-- OC-POL|Polynesia

-- Rules for bucket assignment:
-- 1) AF -> eu-west-1
-- 2) EU -> eu-west-1
-- 3) OC -> ap-southeast-2
-- 4) AN -> ap-southeast-2
-- 5) NA -> us-east-1
-- 6) SA -> us-east-1
-- 7) AS-WES -> eu-west-1
-- 8) AS-SOU -> ap-southeast-1
-- 9) AS-SEA -> ap-southeast-1
-- 10) AS-CEN -> ap-northeast-1
-- 11) AS-EAS -> ap-northeast-1);

DROP TABLE IF EXISTS credentials;
CREATE TABLE credentials ( -- For in-app use only??
  name TEXT PRIMARY KEY,
  access_key TEXT NOT NULL,
  secret_key TEXT NOT NULL);

-- This is here primarily to be a foreign key for iso3
DROP TABLE IF EXISTS languages;
CREATE TABLE languages ( 
  iso3 TEXT NOT NULL PRIMARY KEY,
  macro TEXT NULL,
  iso1 TEXT NULL,
  english_name TEXT NOT NULL);

-- This table exists as a table of allowed locales in the APP os, and
-- is a constraint on this data in bibles
DROP TABLE IF EXISTS locales;
CREATE TABLE locales (
  iso TEXT NOT NULL, -- this can be a 2 char or 3 char iso
  script TEXT NULL, -- This should contain the valid script codes for each iso1
  country_id TEXT NULL,
  variant TEXT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('ltr', 'rtl')), -- This is associated with script code
  english_name TEXT NOT NULL,
  PRIMARY KEY (iso, country_id, script));

DROP TABLE IF EXISTS numerals;
CREATE TABLE numerals (
  numerals_id TEXT NOT NULL,
  numbers TEXT NOT NULL -- numbers are stored as text in a comma delimited array
  -- unicode_zero -- possibly, this would work, but maybe not after 9 
);

-- When we received a users locale we could attempt to match on all three if present.
-- If, not present, we could drop country code and match again, and then drop script
-- and match again.  If all matches fail we have no match.

-- A bible would have an iso code, an optional script code and many countries.
-- ???? What is the source of the country data for bibles ?? I think that is incorrect

DROP TABLE IF EXISTS books;
CREATE TABLE books( -- This is needed as an integrity constraint
  book_id TEXT NOT NULL PRIMARY KEY,
  english_name
);

DROP TABLE IF EXISTS bible_owners;
CREATE TABLE bible_owners ( -- I think my only source for this is DBP API
  owner_id TEXT PRIMARY KEY NOT NULL,
  english_name TEXT NOT NULL,
  localized_name TEXT NOT NULL,
  copyright_msg TEXT NOT NULL); -- what about the text:, audio:, video: copyright message
  -- could we have a message without preceeding copyright symbols. so that we prepend
  -- copyright date

-- When the first 3 chars of a bible_id is not a valid language code, it should be found here.
-- This table does not need to exist in final database
-- It could be a lookup table in a program instead
DROP TABLE IF EXISTS language_corrections;
CREATE TABLE language_corrections (
  fcbh_iso3 TEXT NOT NULL PRIMARY KEY,
  iso3 TEXT NOT NULL,
  FOREIGN KEY (iso3) REFERENCES languages(iso3));

DROP TABLE IF EXISTS bible_sets;
CREATE TABLE bible_sets (
  bible_set_id TEXT NOT NULL PRIMARY KEY, -- (fcbh bible_id)
  iso3 TEXT NOT NULL, -- I think iso3 and version code are how I associate items in a set
  version_code TEXT NOT NULL, -- (e.g. KJV)
  version_name TEXT NOT NULL, -- from info.json
  english_name TEXT NOT NULL, -- from info.json
  localized_name TEXT NULL, -- from google translate
  version_priority INT NOT NULL DEFAULT 0, -- (affects position in version list, manually set)
  FOREIGN KEY (iso3) REFERENCES languages (iso3));

-- The locale table is searched in three steps. iso-script-country, iso-script, iso
-- Or, should is also try iso-country

-- iso is not needed in table_set, because once, I have a bible, I use it to find a set,
-- and I use that to find an audio or video, and I may consider country in the 

-- If, I do this, I need to make certain that video is in the right set.

DROP TABLE IF EXISTS bibles;
CREATE TABLE bibles( -- set_id -- or call this bible
  bible_id TEXT NOT NULL PRIMARY KEY, -- (fcbh fileset_id)
  bible_set_id TEXT NOT NULL,
  type_code TEXT NOT NULL CHECK (type_code IN('audio', 'drama', 'video', 'text')),
  size_code TEXT NOT NULL, -- NT,OT, NTOT, NTP, etc.
  bucket TEXT NOT NULL,
  iso TEXT NOT NULL,
  script TEXT NULL, -- only required for text
  numerals_id TEXT NULL, -- get this from info.json, should there be an index, and this a foreign key.
  font TEXT NOT NULL, -- info.json
  owner_id TEXT NOT NULL, -- source unknown
  copyright_year INT NOT NULL, 
  filename_template TEXT NOT NULL,
  FOREIGN KEY (bible_set_id) REFERENCES bible_sets (bible_set_id),
  -- can there be a foreign key to locale.  Would it be useful or correct without country?
  FOREIGN KEY (numerals_id) REFERENCES numerals (numerals_id),
  FOREIGN KEY (owner_id) REFERENCES bible_owners (owner_id)
);

DROP TABLE IF EXISTS bible_countries;
-- This table is used to select specific bibles, esp
-- audio bibles, when there are differnt versions for different countries
CREATE TABLE bible_countries (
  bible_id TEXT NOT NULL,
  country_id TEXT NOT NULL,
  PRIMARY KEY (bible_id, country_id),
  FOREIGN KEY (bible_id) REFERENCES bibles (bible_id),
  FOREIGN KEY (country_id) REFERENCES regions (country_id)
);

DROP TABLE IF EXISTS bible_videos;
CREATE TABLE bible_videos ( -- these columns could be in bibles table
  bible_id TEXT NOT NULL PRIMARY KEY,
  title TEXT NOT NULL,
  lengthMS INT NOT NULL,
  HLS_URL TEXT NOT NULL,
  description TEXT NULL -- could this be in bibles
);

-- This table is being repeated for each bible in a set, book_name, book_abbrev, book_heading
-- and possibly num_chapters are redundant
-- It would suffice to have a table associated with the bible_set, and then have
-- a reduced table that contained which books were in a set
DROP TABLE IF EXISTS bible_books;
CREATE TABLE bible_books(
  bible_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  book_order INT NOT NULL,
  book_name TEXT NOT NULL,
  book_abbrev TEXT NOT NULL, -- I cannot get this from meta-data, but I can from bible
  book_heading TEXT NOT NULL,-- I cannot get this from meta-data, but I can from bible
  num_chapters INT NOT NULL,
  PRIMARY KEY (bible_id, book_id),
  FOREIGN KEY (bible_id) REFERENCES bibles (bible_id),
  FOREIGN KEY (book_id) REFERENCES books (book_id)
);
-- It would be nice to associate text, and audio, and video closely
-- Would it help to do that by having the bibles share a bible_books table.
-- I am not sure it would matter, the App code would request Text by book_id/chapter
-- and audio and video would do the same.

DROP TABLE IF EXISTS bible_timestamps;
CREATE TABLE bible_timestamps(
  bible_id TEXT NOT NULL,
  book_id TEXT NOT NULL,
  chapter INT NOT NULL,
  verse_positions TEXT NOT NULL,-- this is not normalized, but this is more efficient.
  PRIMARY KEY (bible_id, book_id, chapter),
  FOREIGN KEY (bible_id, book_id) REFERENCES bible_set_books (bible_id, book_id)
);

-- Use logical keys, because the database will always be recreated, not updated.
 

