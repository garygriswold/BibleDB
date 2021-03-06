PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Countries;
CREATE TABLE Countries (
  iso2 TEXT NOT NULL PRIMARY KEY,
  continent TEXT NOT NULL CHECK (continent IN('AF','EU','AS','NA','SA','OC','AN')),
  geoscheme TEXT NOT NULL CHECK (geoscheme IN(
		'AF-EAS','AF-MID','AF-NOR','AF-SOU','AF-WES',
		'SA-CAR','SA-CEN','SA-SOU','NA-NOR',
		'AS-CEN','AS-EAS','AS-SOU','AS-SEA','AS-WES',
		'EU-EAS','EU-NOR','EU-SOU','EU-WES',
		'OC-AUS','OC-MEL','OC-MIC','OC-POL','AN-ANT')),
  awsRegion TEXT NOT NULL CHECK (awsRegion IN (
    'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2',
    'eu-west-1', 'us-east-1')),
  name TEXT NOT NULL);

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

DROP TABLE IF EXISTS Credentials;
CREATE TABLE Credentials ( -- For in-app use only??
  name TEXT PRIMARY KEY,
  access_key TEXT NOT NULL,
  secret_key TEXT NOT NULL);

-- This is here primarily to be a foreign key for iso3
DROP TABLE IF EXISTS Languages;
CREATE TABLE Languages ( 
  iso3 TEXT NOT NULL PRIMARY KEY,
  macro TEXT NULL,
  iso1 TEXT NULL,
  name TEXT NOT NULL);

-- This table exists as a table of allowed locales in the APP os, and
-- is a constraint on this data in bibles
DROP TABLE IF EXISTS Locales;
CREATE TABLE Locales (
  identifier TEXT NOT NULL PRIMARY KEY,
  -- iso TEXT NOT NULL, -- this can be a 2 char or 3 char iso
  -- script TEXT NULL, -- This should contain the valid script codes for each iso1
  -- country TEXT NULL,
  -- variant TEXT NULL,
  -- direction TEXT NOT NULL CHECK (direction IN ('ltr', 'rtl')), -- This is associated with script code
  name TEXT NOT NULL);

DROP TABLE IF EXISTS Numerals;
CREATE TABLE Numerals (
  name TEXT NOT NULL PRIMARY KEY,
  numbers TEXT NOT NULL); -- numbers are stored as text in a comma delimited array
  -- unicode_zero -- possibly, this would work, but maybe not after 9 

DROP TABLE IF EXISTS Scripts;
CREATE TABLE Scripts (
  iso TEXT NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('ltr', 'rtl', 'ttb')),
  font TEXT NULL, -- can we put font here? How will we get it.
  name TEXT NOT NULL PRIMARY KEY);
CREATE INDEX script_code_idx ON Scripts(iso);

-- When we received a users locale we could attempt to match on all three if present.
-- If, not present, we could drop country code and match again, and then drop script
-- and match again.  If all matches fail we have no match.

-- A bible would have an iso code, an optional script code and many countries.
-- ???? What is the source of the country data for bibles ?? I think that is incorrect

DROP TABLE IF EXISTS Books;
CREATE TABLE Books ( -- This is needed as an integrity constraint
  usfm3 TEXT NOT NULL PRIMARY KEY,
  usfm2 TEXT NULL,
  sequence INT NOT NULL,
  name TEXT NOT NULL);

DROP TABLE IF EXISTS Agencies;
CREATE TABLE Agencies ( -- I think my only source for this is DBP API
  uid TEXT PRIMARY KEY NOT NULL,
  --- licensor is a LPTS field, rightsholder, contributor are 
  type TEXT NOT NULL CHECK (type IN ('rightsHolder', 'contributor', 'licensor')),
  abbr TEXT NULL,
  name TEXT NOT NULL,
  nameLocal TEXT NULL, -- I don't know if DBL has this, or LPTS either
  url TEXT NULL); 
  -- copyright_msg TEXT NOT NULL); -- what about the text:, audio:, video: copyright message
  -- could we have a message without preceeding copyright symbols. so that we prepend
  -- copyright date

DROP TABLE IF EXISTS Versions;
CREATE TABLE Versions (
  versionId INT NOT NULL PRIMARY KEY,
  iso3 TEXT NOT NULL, -- I think iso3 and version code are how I associate items in a set
  abbreviation TEXT NOT NULL, -- (e.g. KJV)
  script TEXT NOT NULL,
  country TEXT NOT NULL,
  numerals TEXT NOT NULL,
  name TEXT NOT NULL, -- from LPTS
  nameLocal TEXT NOT NULL, -- Possibly from google translate and eliminate nameTranslated
  nameTranslated TEXT NULL, -- from google translate
  priority INT NOT NULL DEFAULT 0, -- affects position in version list, manually set
  FOREIGN KEY (iso3) REFERENCES Languages (iso3));
CREATE UNIQUE INDEX versions_iso_abbrev ON Versions(iso3, abbreviation);

DROP TABLE IF EXISTS VersionLocales;
CREATE TABLE VersionLocales (
  locale TEXT NOT NULL,
  versionId INT NOT NULL,
  PRIMARY KEY (locale, versionId), -- lookup by locale is most frequent
  FOREIGN KEY (versionId) REFERENCES Versions (versionId),
  FOREIGN KEY (locale) REFERENCES Locales (identifier));

DROP TABLE IF EXISTS Bibles;
CREATE TABLE Bibles (
  systemId INT NOT NULL PRIMARY KEY, -- use fileset_id for now or GUID
  versionId INT NOT NULL,
  mediaType TEXT NOT NULL CHECK (mediaType IN ('audio', 'drama', 'video', 'text')),
  ntScope TEXT NULL CHECK (ntScope IN ('NT', 'NP')),
  otScope TEXT NULL CHECK (otScope IN ('OT', 'OP')),
  bitrate INT NULL CHECK (bitrate IN (16, 32, 64, 128)),
  agencyUid TEXT NULL, -- is null, after dups are removed, sure why text/YUEUNV/YUHUNVO2ET has none
  bucket TEXT NOT NULL,
  filePrefix TEXT NOT NULL,
  fileTemplate TEXT NULL, -- video files have no fileTemplate
  bibleZipFile TEXT NULL,
  lptsStockNo TEXT NULL,
  copyright TEXT NOT NULL, -- possibly reduce to copyright year
  FOREIGN KEY (versionId) REFERENCES Versions (versionId),
  FOREIGN KEY (agencyUid) REFERENCES Agencies (uid));

DROP TABLE IF EXISTS VideoBibles;
CREATE TABLE VideoBibles (
  systemId INT NOT NULL PRIMARY KEY,
  title TEXT NOT NULL,
  lengthMs INT NOT NULL,
  hlsUrl TEXT NOT NULL,
  description TEXT NULL, -- could this be in bibles
  FOREIGN KEY (systemId) REFERENCES Bibles (systemId));

DROP TABLE IF EXISTS BibleBooks;
CREATE TABLE BibleBooks (
  systemId INT NOT NULL,
  book TEXT NOT NULL,
  sequence INT NOT NULL,
  nameLocal TEXT NULL, -- The bookname used in table of contents
  nameS3 TEXT NULL, -- bookname in S3 files
  numChapters INT NOT NULL,
  PRIMARY KEY (systemId, book),
  FOREIGN KEY (systemId) REFERENCES Bibles (systemId),
  FOREIGN KEY (book) REFERENCES Books (usfm3));

-- duration would need to be stored for each audio file, identified by fileset_id, book_id, 

DROP TABLE IF EXISTS BibleTimestamps;
CREATE TABLE BibleTimestamps(
  systemId INT NOT NULL,
  book TEXT NOT NULL,
  chapter INT NOT NULL,
  versePositions TEXT NOT NULL,-- this is not normalized, but this is more efficient.
  PRIMARY KEY (systemId, book, chapter),
  FOREIGN KEY (systemId, book) REFERENCES BibleBooks (systemId, book));

-- Use logical keys, because the database will always be recreated, not updated.

CREATE VIEW BiblesView AS
SELECT v.versionId, v.iso3, v.abbreviation, v.script, v.name, b.systemId, b.scope, b.bucket, b.filePrefix
FROM Versions v, Bibles b
WHERE v.versionId=b.versionId;





 

