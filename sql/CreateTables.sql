
CREATE TABLE Region (
  country_id TEXT NOT NULL PRIMARY KEY,
  country_name TEXT NOT NULL,
  continent_id TEXT NOT NULL CHECK (continent_id IN('AF','EU','AS','NA','SA','OC','AN')),
  geoscheme_id TEXT NOT NULL CHECK (geoscheme_id IN(
		'AF-EAS','AF-MID','AF-NOR','AF-SOU','AF-WES',
		'SA-CAR','SA-CEN','SA-SOU','NA-NOR',
		'AS-CEN','AS-EAS','AS-SOU','AS-SEA','AS-WES',
		'EU-EAS','EU-NOR','EU-SOU','EU-WES',
		'OC-AUS','OC-MEL','OC-MIC','OC-POL','AN-ANT')),
  aws_region TEXT NOT NULL CHECK (aws_region IN (
    'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2',
    'eu-west-1', 'us-east-1')));

Question: Text and Audio are associated with a version, but Video, 
is not, it is only associated with a language

CREATE TABLE credentials ( -- For in-app use only??
  name TEXT PRIMARY KEY,
  access_key TEXT NOT NULL,
  secret_key TEXT NOT NULL);

-- This table exists as a table of allowed locales in the APP os, and
-- is a constraint on this data in bibles

CREATE TABLE locale (
  iso TEXT NOT NULL, -- this can be a 2 char or 3 char iso
  script TEXT NULL, -- This should contain the valid script codes for each iso1
  country TEXT NULL,
  -- are there other variants that I should consider?
  direction TEXT NOT NULL CHECK (direction IN ('ltr', 'rtl') -- This is associated with script code
  name TEXT NOT NULL,
  PRIMARY KEY (iso, script, country));

CREATE TABLE numerals (
  numeral_code,
  sequence,
  number, -- This is the number taken from the info.json
  -- possibly instead of a normalized table, this should be an array of numbrs
  unicode_zero -- possibly, this would work, but maybe not after 9 
)


When we received a users locale we could attempt to match on all three if present.
If, not present, we could drop country code and match again, and then drop script
and match again.  If all matches fail we have no match.

A bible would have an iso code, an optional script code and many countries.
???? What is the source of the country data for bibles ?? I think that is incorrect

CREATE TABLE bible_owners (
  owner_id TEXT PRIMARY KEY NOT NULL,
  english_name TEXT NOT NULL,
  localized_name TEXT NOT NULL,
  copyright_msg TEXT NOT NULL, -- what about the text:, audio:, video: copyright message
  -- could we have a message without preceeding copyright symbols. so that we prepend
  -- copyright date

  owner_url TEXT NOT NULL); -- I won't use.  How is this populated?

CREATE TABLE bible_sets(
  bible_set_id PRIMARY KEY (fcbh bible_id)
  version_code (e.g. KJV)
  version_name -- from info.json
  english_name -- from info.json
  localized_name -- from google translate
  description -- do I have a source for version description, or just video
  version_priority (affects position in version list, manually set)
  iso 3?-- I might not need this here?, or should this be iso3, which is what is in info.json
  FOREIGN KEY (iso) REFERENCES locale (iso1) -- I might not need this here?
  );

-- The locale table is searched in three steps. iso-script-country, iso-script, iso
-- Or, should is also try iso-country

-- iso is not needed in table_set, because once, I have a bible, I use it to find a set,
-- and I use that to find an audio or video, and I may consider country in the 

-- If, I do this, I need to make certain that video is in the right set.

CREATE TABLE bibles( set_id -- or call this bible
  bible_id PRIMARY KEY (fcbh fileset_id)
  bible_set_id TEXT NOT NULL
  type_code TEXT NOT NULL CHECK (type_code IN('audio', 'drama', 'video', 'text'))
  size_code TEXT NOT NULL, -- NT,OT, NTOT, NTP, etc.
  bucket TEXT NOT NULL
  iso
  script -- only required for text
  numerals -- get this from info.json, should there be an index, and this a foreign key.
  -- ?? numeral is not unique for script, but it should be possible to break ties with country
  iso3 -- info.json, should this be considered an iso-country
  font -- info.json
  copyright_year
  owner_id 
  filename_template --
  FOREIGN KEY (bible_set_id) REFERENCES bible_sets (bible_set_id)
  FOREIGN KEY (owner_id) REFERENCES bible_owners (owner_id)
);

CREATE TABLE bible_countries( -- This table is used to select specific bibles, esp
	-- audio bibles, when there are differnt versions for different countries
  bible_id
  country_id
  PRIMARY KEY (bible_id, country_id),
  FOREIGN KEY bible_id REFERENCES bibles (bible_id)
);

CREATE TABLE bible_videos( -- this could be in bibles table
  bible_id PRIMARY KEY
  title TEXT NOT NULL,
  lengthMS INT NOT NULL,
  HLS_URL TEXT NOT NULL,
  description TEXT NULL, -- could this be in bibles
)

CREATE TABLE bible_books(
  bible_id
  book_id
  book_order
  book_name
  book_abbrev -- I cannot get this from meta-data, but I can from bible
  book_heading -- I cannot get this from meta-data, but I can from bible
  num_chapters
  PRIMARY KEY (bible_id, book_id)
  FOREIGN KEY (bible_id) REFERENCES bibles (bible_id)
  FOREIGN KEY (book_id) REFERENCES books (book_id)
)

CREATE TABLE books( -- This is needed as an integrity constraint
	book_id PRIMARY KEY
	english_name
)

CREATE TABLE bible_timestamps(
  bible_id
  book_id
  chapter
  verse_positions -- this is not normalized, but this is more efficient.
  PRIMARY KEY (bible_id, book_id, chapter)
  FOREIGN KEY (bible_id, book_id) REFERENCES bible_set_books (bible_id, book_id)
)

-- Use logical keys, because the database will always be recreated, not updated.
 


 ---- Release 2.1

XCREATE TABLE AudioBook(
X  damId TEXT NOT NULL REFERENCES Audio(damId),
X  bookId TEXT NOT NULL,
X  bookOrder TEXT NOT NULL,
X  bookName TEXT NOT NULL,
X  numberOfChapters INTEGER NOT NULL,
X  PRIMARY KEY (damId, bookId));

XCREATE TABLE AudioChapter(
X  damId TEXT NOT NULL REFERENCES Audio(damId),
X  bookId TEXT NOT NULL,
X  chapter INTEGER NOT NULL,
X  versePositions TEXT NOT NULL,
X  PRIMARY KEY (damId, bookId, chapter),
X  FOREIGN KEY (damId, bookId) REFERENCES AudioBook(damId, bookId));

CREATE TABLE Bible(
X  bibleId TEXT NOT NULL PRIMARY KEY,
X  abbr TEXT NOT NULL,
X  iso3 TEXT NOT NULL REFERENCES Language(iso3),
X  scope TEXT NOT NULL CHECK (scope IN('B', 'N')),
X  versionPriority INT NOT NULL,
X  name TEXT NULL,
X  englishName TEXT NOT NULL,
X  localizedName TEXT NULL,
X  textBucket TEXT NOT NULL,
X  textId TEXT NOT NULL,
X  keyTemplate TEXT NOT NULL,
X  audioBucket TEXT NULL,
X  otDamId TEXT NULL,
X  ntDamId TEXT NULL,
X  iso1 TEXT NULL,
X  script TEXT NULL,
X  country TEXT NULL REFERENCES Country(code));
XCREATE INDEX bible_iso1_idx on Bible(iso1, script);

XCREATE TABLE Credential (
X  name TEXT PRIMARY KEY,
X  access_key TEXT NOT NULL,
X  secret_key TEXT NOT NULL);

CREATE TABLE JesusFilm (
  country TEXT NOT NULL,
  iso3 TEXT NOT NULL,
  languageId TEXT NOT NULL,
  population INT NOT NULL,
  PRIMARY KEY(country, iso3, languageId));

XCREATE TABLE Language (
X  iso1 TEXT NOT NULL,
X  script TEXT NOT NULL,
X  name TEXT NOT NULL,
X  PRIMARY KEY (iso1, script));

XCREATE TABLE Owner (
X  ownerCode TEXT PRIMARY KEY NOT NULL,
X  englishName TEXT NOT NULL,
X  localOwnerName TEXT NOT NULL,
X  ownerURL TEXT NOT NULL);

CREATE TABLE Region (
  countryCode TEXT NOT NULL PRIMARY KEY,
  continentCode TEXT NOT NULL CHECK (continentCode IN('AF','EU','AS','NA','SA','OC','AN')),
  geoschemeCode TEXT NOT NULL CHECK (geoschemeCode IN(
		'AF-EAS','AF-MID','AF-NOR','AF-SOU','AF-WES',
		'SA-CAR','SA-CEN','SA-SOU','NA-NOR',
		'AS-CEN','AS-EAS','AS-SOU','AS-SEA','AS-WES',
		'EU-EAS','EU-NOR','EU-SOU','EU-WES',
		'OC-AUS','OC-MEL','OC-MIC','OC-POL','AN-ANT')),
  awsRegion TEXT NOT NULL REFERENCES AWSRegion(awsRegion),
  countryName TEXT NOT NULL);
CREATE INDEX Region_awsRegion_index ON Region(awsRegion);

CREATE TABLE Video (
  languageId TEXT NOT NULL,
  mediaId TEXT NOT NULL,
  mediaSource TEXT NOT NULL,
  title TEXT NOT NULL,
  lengthMS INT NOT NULL,
  HLS_URL TEXT NOT NULL,
  description TEXT NULL,
  PRIMARY KEY (languageId, mediaId)); 

XCREATE TABLE VideoSeq (
X  mediaId TEXT PRIMARY KEY, 
X  sequence INT NOT NULL); 

====== Release 2.0 ====

CREATE TABLE Audio(
  damId TEXT NOT NULL PRIMARY KEY,
  dbpLanguageCode TEXT NOT NULL,
  dbpVersionCode TEXT NOT NULL,
  collectionCode TEXT NOT NULL,
  mediaType TEXT NOT NULL);

AudioBook same as 2.1
AudioChapter same as 2.1

CREATE TABLE AudioVersion(
  ssVersionCode TEXT NOT NULL PRIMARY KEY,
  dbpLanguageCode TEXT NOT NULL,
  dbpVersionCode TEXT NOT NULL);

CREATE TABLE Country (
  countryCode TEXT NOT NULL PRIMARY KEY,
  primLanguage TEXT NOT NULL,
  englishName TEXT NOT NULL,
  localCountryName TEXT NOT NULL);

CREATE TABLE CountryVersion (
  countryCode TEXT REFERENCES Country(countryCode),
  versionCode TEXT REFERENCES Version(versionCode),
PRIMARY KEY(countryCode, versionCode));
CREATE INDEX CountryVersion_versionCode_index ON CountryVersion(versionCode); 

CREATE TABLE DefaultVersion (
  langCode TEXT NOT NULL PRIMARY KEY,
  filename TEXT NOT NULL REFERENCES Version(filename));
CREATE INDEX DefaultVersion_filename_index ON DefaultVersion(filename); 

CREATE TABLE Identity(
  versionCode TEXT NOT NULL PRIMARY KEY,
  filename TEXT NOT NULL, bibleVersion TEXT NOT NULL,
  datetime TEXT NOT NULL,
  appVersion TEXT NOT NULL,
  publisher TEXT NOT NULL);

CREATE TABLE InstalledVersion (
  versionCode NOT NULL PRIMARY KEY REFERENCES Version(versionCode),
  startDate NOT NULL,
  endDate NULL);

CREATE TABLE JesusFilm (
  countryCode TEXT NOT NULL,
  silCode TEXT NOT NULL,
  languageId TEXT NOT NULL,
  langCode TEXT NOT NULL,
  langName TEXT NOT NULL,
  population INT NOT NULL,
  PRIMARY KEY(countryCode, silCode, languageId));

CREATE TABLE Language (
  silCode TEXT PRIMARY KEY NOT NULL,
  langCode TEXT NOT NULL,
  direction TEXT NOT NULL CHECK(direction IN('ltr', 'rtl')),
  englishName TEXT NOT NULL,
  localLanguageName TEXT NOT NULL
);

Owner same as 2.1

CREATE TABLE Region (
  countryCode TEXT NOT NULL PRIMARY KEY,
  continentCode TEXT NOT NULL CHECK (continentCode IN('AF','EU','AS','NA','SA','OC','AN')),
  geoschemeCode TEXT NOT NULL CHECK (geoschemeCode IN(
		'AF-EAS','AF-MID','AF-NOR','AF-SOU','AF-WES',
		'SA-CAR','SA-CEN','SA-SOU','NA-NOR',
		'AS-CEN','AS-EAS','AS-SOU','AS-SEA','AS-WES',
		'EU-EAS','EU-NOR','EU-SOU','EU-WES',
		'OC-AUS','OC-MEL','OC-MIC','OC-POL','AN-ANT')),
  awsRegion TEXT NOT NULL REFERENCES AWSRegion(awsRegion),
  countryName TEXT NOT NULL);
CREATE INDEX Region_awsRegion_index ON Region(awsRegion);

CREATE TABLE Translation (
  source TEXT NOT NULL,
  target TEXT NOT NULL,
  translated TEXT NOT NULL,
PRIMARY KEY(target, source)); -- select where target=? is primary query

CREATE TABLE Version (
  versionCode TEXT NOT NULL PRIMARY KEY,
  silCode TEXT NOT NULL REFERENCES Language(silCode),
  ownerCode TEXT NOT NULL REFERENCES Owner(ownerCode),
  versionAbbr TEXT NOT NULL,
  localVersionName TEXT NOT NULL,
  scope TEXT NOT NULL CHECK (scope IN('BIBLE','BIBLE_NT','BIBLE_PNT')),
  filename TEXT UNIQUE,
  hasHistory TEXT CHECK (hasHistory IN('T','F')),
  isQaActive TEXT CHECK (isQaActive IN('T','F')),
  versionDate TEXT NOT NULL,
  copyright TEXT NULL,
  introduction TEXT NULL);
CREATE INDEX Version_silCode_index ON Version(silCode);
CREATE INDEX Version_ownerCode_index ON Version(ownerCode);

CREATE TABLE Video (
  languageId TEXT NOT NULL,
  mediaId TEXT NOT NULL,
  silCode TEXT NOT NULL,
  langCode TEXT NOT NULL,
  title TEXT NOT NULL,
  lengthMS INT NOT NULL,
  HLS_URL TEXT NOT NULL,
  MP4_1080 TEXT NULL, -- deprecated remove at next revision (GNG 6/2017)
  MP4_720 TEXT NULL, -- deprecated  remove at next revision
  MP4_540 TEXT NULL, -- deprecated remove at next revision
  MP4_360 TEXT NULL, -- deprecated remove at next revision
  longDescription TEXT NULL,
  PRIMARY KEY (languageId, mediaId));
CREATE INDEX Video_langCode ON Video (langCode);


----- Bible Schema ----

CREATE TABLE chapters(
  reference text not null primary key, 
  xml text not null, 
  html text not null);

CREATE TABLE charset(
  hex text not null,
  char text not null,
  count int not null);

CREATE TABLE concordance(
  word text primary key not null,
  refCount integer not null,
  refList text not null,
  refPosition text null,
  refList2 text null);

CREATE TABLE identity(
	versionCode TEXT NOT NULL PRIMARY KEY,
	filename TEXT NOT NULL,
	bibleVersion TEXT NOT NULL,
	datetime TEXT NOT NULL,
	appVersion TEXT NOT NULL,
	publisher TEXT NOT NULL);

CREATE TABLE styleIndex( -- used in validation only
  style text not null,
  usage text not null,
  book text not null,
  chapter integer null,
  verse integer null);

CREATE TABLE styleUse( -- used for validation, I think
  style text not null, 
  usage text not null, 
  primary key(style, usage));

CREATE TABLE tableContents(
  code text primary key not null, 
  heading text not null, title text not null, 
  name text not null, 
  abbrev text not null, 
  lastChapter integer not null, 
  priorBook text null, 
  nextBook text null, 
  chapterRowId integer not null);

CREATE TABLE verses(
  reference text not null primary key, 
  xml text not null, 
  html text not null);
