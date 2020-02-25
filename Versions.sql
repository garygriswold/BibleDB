PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Translation;
DROP TABLE IF EXISTS InstalledVersion;
DROP TABLE IF EXISTS DefaultVersion;
DROP TABLE IF EXISTS CountryVersion;
DROP TABLE IF EXISTS DownloadURL;
DROP TABLE IF EXISTS Region;
DROP TABLE IF EXISTS AWSRegion;
DROP TABLE IF EXISTS Version;
DROP TABLE IF EXISTS Owner;
DROP TABLE IF EXISTS Language;
DROP TABLE IF EXISTS Country;


CREATE TABLE Country (
countryCode TEXT NOT NULL PRIMARY KEY,
primLanguage TEXT NOT NULL,
englishName TEXT NOT NULL,
localCountryName TEXT NOT NULL
);
INSERT INTO Country VALUES ('WORLD', 'en', 'World', 'World');
-- INSERT INTO Country VALUES ('US', 'en', 'United States', 'United States');
-- INSERT INTO Country VALUES ('MX', 'es', 'Mexico', 'Méjico');


CREATE TABLE Language (
silCode TEXT PRIMARY KEY NOT NULL,
langCode TEXT NOT NULL,
direction TEXT NOT NULL CHECK(direction IN('ltr', 'rtl')),
englishName TEXT NOT NULL,
localLanguageName TEXT NOT NULL
);
-- World Languages
INSERT INTO Language VALUES ('awa', 'awa', 'ltr', 'Awadhi', 'Awadhi'); -- no translation
INSERT INTO Language VALUES ('ben', 'bn', 'ltr', 'Bengali', 'বাঙালি');
INSERT INTO Language VALUES ('bul', 'bg', 'ltr', 'Bulgarian', 'български език');
INSERT INTO Language VALUES ('cmn', 'zh', 'ltr', 'Chinese', '汉语, 漢語');
INSERT INTO Language VALUES ('eng', 'en', 'ltr', 'English', 'English');
INSERT INTO Language VALUES ('hin', 'hi', 'ltr', 'Hindi', 'हिंदी');
INSERT INTO Language VALUES ('hrv', 'hr', 'ltr', 'Croatian', 'hrvatski');
INSERT INTO Language VALUES ('hun', 'hu', 'ltr', 'Hungarian', 'Magyar');
INSERT INTO Language VALUES ('ind', 'id', 'ltr', 'Indonesian', 'Bahasa Indonesia');
INSERT INTO Language VALUES ('kan', 'kn', 'ltr', 'Kannada', 'ಕನ್ನಡ');
INSERT INTO Language VALUES ('mar', 'mr', 'ltr', 'Marathi', 'मराठी');
INSERT INTO Language VALUES ('nep', 'ne', 'ltr', 'Nepali', 'नेपाली');
INSERT INTO Language VALUES ('ori', 'or', 'ltr', 'Oriya', 'Oriya'); -- no translation
INSERT INTO Language VALUES ('pan', 'pa', 'ltr', 'Punjabi', 'ਪੰਜਾਬੀ ਦੇ');
INSERT INTO Language VALUES ('por', 'pt', 'ltr', 'Portuguese', 'Português');
INSERT INTO Language VALUES ('rus', 'ru', 'ltr', 'Russian', 'русский');
INSERT INTO Language VALUES ('srp', 'sr', 'ltr', 'Serbian', 'Српски');
INSERT INTO Language VALUES ('spa', 'es', 'ltr', 'Spanish', 'Español');
INSERT INTO Language VALUES ('tam', 'ta', 'ltr', 'Tamil', 'தமிழ் மொழி');
INSERT INTO Language VALUES ('tha', 'th', 'ltr', 'Thai', 'ภาษาไทย');
INSERT INTO Language VALUES ('ukr', 'uk', 'ltr', 'Ukrainian', 'українська мова');
INSERT INTO Language VALUES ('vie', 'vi', 'ltr', 'Vietnamese', 'Tiếng Việt');
-- Right to Left Languages
INSERT INTO Language VALUES ('arb', 'ar', 'rtl', 'Arabic', 'العربية');
INSERT INTO Language VALUES ('pes', 'fa', 'rtl', 'Persian', 'فارسی');
INSERT INTO Language VALUES ('urd', 'ur', 'rtl', 'Urdu', 'اردو زبان');


CREATE TABLE Owner (
ownerCode TEXT PRIMARY KEY NOT NULL,
englishName TEXT NOT NULL,
localOwnerName TEXT NOT NULL,
ownerURL TEXT NOT NULL
);
INSERT INTO Owner VALUES ('BLI', 'Bible League International', 'Bible League International', 'www.bibleleague.org');
INSERT INTO Owner VALUES ('CRSWY', 'Crossway', 'Crossway', 'www.crossway.org');
INSERT INTO Owner VALUES ('EBIBLE', 'eBible.org', 'eBible.org', 'www.ebible.org');
INSERT INTO Owner VALUES ('ELAM', 'Elam Ministries', 'Elam Ministries', 'www.kalameh.com/shop');
INSERT INTO Owner VALUES ('SPN', 'Bible Society of Spain', 'Sociedad Bíblica de España', 'www.unitedbiblesocieties.org/society/bible-society-of-spain/');
INSERT INTO Owner VALUES ('WBT', 'Wycliffe Bible Translators', 'Wycliffe Bible Translators', 'www.wycliffe.org');


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
introduction TEXT NULL
);
CREATE INDEX Version_silCode_index ON Version(silCode);
CREATE INDEX Version_ownerCode_index ON Version(ownerCode);

-- America
INSERT INTO Version VALUES ('ERV-ENG', 'eng', 'BLI', 'ERV-ENG', 'Holy Bible: Easy-to-Read Version (ERV), International Edition', 'BIBLE', 'ERV-ENG.db', 'T', 'F', '2016-10-01', 'Holy Bible: Easy-to-Read Version (ERV), International Edition © 2013, 2016 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-POR', 'por', 'BLI', 'ERV-POR', 'Novo Testamento: Versão Fácil de Ler', 'BIBLE_NT', 'ERV-POR.db', 'T', 'F', '2016-10-10',
'Novo Testamento: Versão Fácil de Ler (VFL) © 1999, 2014 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-SPA', 'spa', 'BLI', 'ERV-SPA', 'La Biblia: La Palabra de Dios para todos', 'BIBLE', 'ERV-SPA.db', 'T', 'F', '2016-10-08',
'La Biblia: La Palabra de Dios para todos (PDT) © 2005, 2015 Bible League International', NULL);
INSERT INTO Version VALUES ('ESV', 'eng', 'CRSWY', 'ESV', 'English Standard Version', 'BIBLE', 'ESV.db', 'T', 'F', '2020-01-01',
'English Standard Version®, copyright © 2001 by Crossway Bibles, a publishing ministry of Good News Publishers. Used by permission. All rights reserved.', NULL);
INSERT INTO Version VALUES ('KJVPD', 'eng', 'EBIBLE', 'KJV', 'King James Version', 'BIBLE', 'KJVPD.db', 'T', 'F', '2016-09-06', 
'King James Version 1611 (KJV), Public Domain, eBible.org.', NULL);
INSERT INTO Version VALUES ('WEB', 'eng', 'EBIBLE', 'WEB', 'World English Bible', 'BIBLE', 'WEB.db', 'T', 'F', '2016-09-06', 
'World English Bible (WEB), Public Domain, eBible.org.', NULL);
INSERT INTO Version VALUES ('WEB_SHORT', 'eng', 'EBIBLE', 'WEB', 'WEB Genesis and Titus for testing', 'BIBLE_PNT', 'WEB_SHORT.db', 'T', 'F', '2016-09-06',
'', NULL);

-- East Asia
INSERT INTO Version VALUES ('ERV-CMN', 'cmn', 'BLI', 'ERV-CMN', '圣经–普通话本', 'BIBLE', 'ERV-CMN.db', 'T', 'F', '2016-10-12',
'圣经–普通话本（普通话）© 1999，2015 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-IND', 'ind', 'BLI', 'ERV-IND', 'Perjanjian Baru: Versi Mudah Dibaca', 'BIBLE_NT', 'ERV-IND.db', 'T', 'F', '2016-10-12',
'Perjanjian Baru: Versi Mudah Dibaca (VMD) © 2003 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-NEP', 'nep', 'BLI', 'ERV-NEP', 'Nepali Holy Bible: Easy-to-Read Version', 'BIBLE', 'ERV-NEP.db', 'T', 'F', '2016-10-17',
'Nepali Holy Bible: Easy-to-Read Version (ERV) © 2004 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-THA', 'tha', 'BLI', 'ERV-THA', 'พระ​คริสต​ธรรม​คัมภีร์ ฉบับ​อ่าน​เข้า​ใจ​ง่าย', 'BIBLE', 'ERV-THA.db', 'T', 'F', '2016-10-12',
'พระคริสต​ธรรม​คัมภีร์: ฉบับ​อ่าน​เข้า​ใจ​ง่าย (ขจง) © 2015 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-VIE', 'vie', 'BLI', 'ERV-VIE', 'Thánh Kinh: Bản Phổ thông', 'BIBLE', 'ERV-VIE.db', 'T', 'F', '2016-10-12',
'Thánh Kinh: Bản Phổ thông (BPT) © 2010 Bible League International', NULL);

-- Middle East
INSERT INTO Version VALUES ('ARBVDPD', 'arb', 'EBIBLE', 'ARBVD', 'الكتاب المقدس ترجمة فان دايك', 'BIBLE', 'ARBVDPD.db', 'F', 'F', '2016-09-06',
'Arabic Bible: Van Dyck Translation (ARBVD), Public Domain, eBible.org', NULL);
INSERT INTO Version VALUES ('ERV-ARB', 'arb', 'BLI', 'ERV-ARB', 'بِعَهْدَيْهِ القَدِيمِ وَالجَدِيد الكِتَابُ المُقَدَّسُ', 'BIBLE', 'ERV-ARB.db', 'T', 'F', '2016-10'
,'الكِتاب المُقَدَّس: التَّرْجَمَةُ العَرَبِيَّةُ المُبَسَّطَةُ (ت ع م) © 2009, 2016 رَابِطَةُ الكِتَابِ المُقَدَّسِ الدَّوْلِيَّة (Bible League International)',
NULL);
INSERT INTO Version VALUES('NMV', 'pes', 'ELAM', 'NMV', 'ترجمۀ هزارۀ نو', 'BIBLE', 'NMV.db', 'F', 'F', '2016-09-06',
'The Persian New Millennium Version © 2014, is a production of Elam Ministries. All rights reserved', NULL);

-- India
INSERT INTO Version VALUES ('ERV-AWA', 'awa', 'BLI', 'ERV-AWA', 'पवित्तर बाइबिल, Easy-to-Read Version', 'BIBLE', 'ERV-AWA.db', 'T', 'F', '2016-10-17',
'Awadhi Holy Bible: Easy-to-Read Version (ERV) © 2005 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-BEN', 'ben', 'BLI', 'ERV-BEN', 'পবিত্র বাইবেল, Easy-to-Read Version', 'BIBLE', 'ERV-BEN.db', 'T', 'F', '2016-10-17',
'Bengali Holy Bible: Easy-to-Read Version (ERV) © 2001, 2016 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-HIN', 'hin', 'BLI', 'ERV-HIN', 'पवित्र बाइबल, Easy-to-Read Version', 'BIBLE', 'ERV-HIN.db', 'T', 'F', '2016-10-17',
'Hindi Holy Bible: Easy-to-Read Version (ERV) © 1995 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-KAN', 'kan', 'BLI', 'ERV-KAN', 'Kannada: Easy-to-Read Version', 'BIBLE', 'ERV-KAN.db', 'T', 'F', '2016-10-17',
'Kannada: Easy-to-Read Version (ERV). © 1997 Bible League International.', NULL);
INSERT INTO Version VALUES ('ERV-MAR', 'mar', 'BLI', 'ERV-MAR', 'Marathi: Easy-to-Read Version', 'BIBLE', 'ERV-MAR.db', 'T', 'F', '2016-10-17',
'Marathi: Easy-to-Read Version (ERV). © 1998 Bible League International.', NULL);
INSERT INTO Version VALUES ('ERV-ORI', 'ori', 'BLI', 'ERV-ORI', 'ପବିତ୍ର ବାଇବଲ, Easy-to-Read Version', 'BIBLE', 'ERV-ORI.db', 'F', 'F', '2016-10-17',
'Oriya Holy Bible: Easy-to-Read Version (ERV) © 2004 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-PAN', 'pan', 'BLI', 'ERV-PAN', 'Punjabi: Easy-to-Read Version', 'BIBLE', 'ERV-PAN.db', 'F', 'F', '2016-10-17',
'Punjabi: Easy-to-Read Version (ERV). © 2002 Bible League International.', NULL);
INSERT INTO Version VALUES ('ERV-TAM', 'tam', 'BLI', 'ERV-TAM', 'பரிசுத்த பைபிள், Easy-to-Read Version', 'BIBLE', 'ERV-TAM.db', 'T', 'F', '2016-10-17',
'Tamil Holy Bible: Easy-to-Read Version (ERV) © 1998 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-URD', 'urd', 'BLI', 'ERV-URD', 'Urdu: Easy-to-Read Version', 'BIBLE', 'ERV-URD.db', 'T', 'F', '2016-10-17',
'Urdu: Easy-to-Read Version (ERV). © 2003 Bible League International.', NULL);

-- Eastern Europe
INSERT INTO Version VALUES ('ERV-BUL', 'bul', 'BLI', 'ERV-BUL', 'Новият завет, съвременен превод', 'BIBLE_NT', 'ERV-BUL.db', 'T', 'F', '2016-10-17',
'Новият завет: съвременен превод (СПБ) © 2000 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-HRV', 'hrv', 'BLI', 'ERV-HRV', 'Novi zavjet, Suvremeni prijevod', 'BIBLE_NT', 'ERV-HRV.db', 'T', 'F', '2016-10-17',
'Novi zavjet: Suvremeni prijevod (SHP) © 2002 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-HUN', 'hun', 'BLI', 'ERV-HUN', 'Biblia Egyszerű fordítás', 'BIBLE', 'ERV-HUN.db', 'T', 'F', '2016-10-17',
'BIBLIA: Egyszerű fordítás (EFO) © 2012 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-RUS', 'rus', 'BLI', 'ERV-RUS', 'Святая Библия Современный перевод', 'BIBLE', 'ERV-RUS.db', 'T', 'F', '2016-10-17',
'Библия: Современный перевод (РСП) © Bible League International, 1993, 2014', NULL);
INSERT INTO Version VALUES ('ERV-SRP', 'srp', 'BLI', 'ERV-SRP', 'Библија Савремени српски превод', 'BIBLE', 'ERV-SRP.db', 'T', 'F', '2016-10-17',
'Библија: Савремени српски превод (ССП) © 2015 Bible League International', NULL);
INSERT INTO Version VALUES ('ERV-UKR', 'ukr', 'BLI', 'ERV-UKR', 'Новий Заповіт Сучасною Мовою', 'BIBLE_NT', 'ERV-UKR.db', 'T', 'F', '2016-10-17',
'Новий Заповіт: Сучасною мовою (УСП) © Bible League International, 1996', NULL);

CREATE TABLE AWSRegion(
awsRegion TEXT NOT NULL PRIMARY KEY,
s3TextBucket TEXT NULL,
regionName TEXT NOT NULL	
);
INSERT INTO AWSRegion VALUES ('us-east-1', 		'shortsands-na-va', 'US East (N. Virginia)');
INSERT INTO AWSRegion VALUES ('us-east-2', 		NULL, 				'US East (Ohio)');
INSERT INTO AWSRegion VALUES ('us-west-1', 		NULL, 				'US West (N. California)');
INSERT INTO AWSRegion VALUES ('us-west-2', 		NULL, 				'US West (Oregon)');
INSERT INTO AWSRegion VALUES ('ca-central-1', 	NULL, 				'Canada (Central)');
INSERT INTO AWSRegion VALUES ('eu-west-1', 		'shortsands-eu-ie', 'EU (Ireland)');
INSERT INTO AWSRegion VALUES ('eu-central-1', 	NULL, 				'EU (Frankfurt)');
INSERT INTO AWSRegion VALUES ('eu-west-2', 		NULL, 				'EU (London)');
INSERT INTO AWSRegion VALUES ('ap-northeast-1', 'shortsands-as-jp', 'Asia Pacific (Tokyo)');
INSERT INTO AWSRegion VALUES ('ap-northeast-2', NULL, 				'Asia Pacific (Seoul)');
INSERT INTO AWSRegion VALUES ('ap-southeast-1', 'shortsands-as-sg', 'Asia Pacific (Singapore)');
INSERT INTO AWSRegion VALUES ('ap-southeast-2', 'shortsands-oc-au', 'Asia Pacific (Sydney)');
INSERT INTO AWSRegion VALUES ('ap-south-1', 	NULL, 				'Asia Pacific (Mumbai)');
INSERT INTO AWSRegion VALUES ('sa-east-1', 		NULL, 				'South America (São Paulo)');

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
countryName TEXT NOT NULL	
);
CREATE INDEX Region_awsRegion_index ON Region(awsRegion);

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
.separator '|'
.import data/Region.txt Region


-- This table is removed April 18, 2018, replaced by AWS plugin
-- This table is populate by Versions/js/VersionAdapter
-- CREATE TABLE DownloadURL(
--	filename TEXT NOT NULL,
--	awsRegion TEXT NOT NULL REFERENCES AWSRegion(awsRegion),
--	signedURL TEXT NOT NULL,
--	PRIMARY KEY(filename, awsRegion)
-- );
-- CREATE INDEX DownloadURL_awsRegion_index ON DownloadURL(awsRegion);

CREATE TABLE CountryVersion (
countryCode TEXT REFERENCES Country(countryCode),
versionCode TEXT REFERENCES Version(versionCode),
PRIMARY KEY(countryCode, versionCode)
);
CREATE INDEX CountryVersion_versionCode_index ON CountryVersion(versionCode);

INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-ARB'); -- Arabic
INSERT INTO CountryVersion VALUES ('WORLD', 'ARBVDPD'); -- Arabic
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-AWA'); -- Awadi
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-BEN'); -- Bengali
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-BUL'); -- Bulgarian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-CMN'); -- Chinese
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-HRV'); -- Croatian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-ENG'); -- English
INSERT INTO CountryVersion VALUES ('WORLD', 'KJVPD'); -- English
INSERT INTO CountryVersion VALUES ('WORLD', 'WEB'); -- English
INSERT INTO CountryVersion VALUES ('WORLD', 'NMV'); -- Farsi/Persian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-HIN'); -- Hindi
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-HUN'); -- Hungarian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-IND'); -- Indonesian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-KAN'); -- Kannada
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-MAR'); -- Marathi
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-NEP'); -- Nepali
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-ORI'); -- Oriya
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-POR'); -- Portuguese
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-PAN'); -- Punjabi
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-RUS'); -- Russian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-SPA'); -- Spanish
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-SRP'); -- Serbian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-TAM'); -- Tamil
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-THA'); -- Thai
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-UKR'); -- Ukrainian
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-URD'); -- Urdu
INSERT INTO CountryVersion VALUES ('WORLD', 'ERV-VIE'); -- Vietnamese


CREATE TABLE DefaultVersion (
langCode TEXT NOT NULL PRIMARY KEY,
filename TEXT NOT NULL REFERENCES Version(filename)
);
CREATE INDEX DefaultVersion_filename_index ON DefaultVersion(filename);

INSERT INTO DefaultVersion VALUES ('ar', 'ERV-ARB.db'); -- Arabic
INSERT INTO DefaultVersion VALUES ('bg', 'ERV-BUL.db'); -- Bulgarian
INSERT INTO DefaultVersion VALUES ('bn', 'ERV-BEN.db'); -- Bengali
INSERT INTO DefaultVersion VALUES ('ca', 'ERV-SPA.db'); -- Catalan (Spanish)
INSERT INTO DefaultVersion VALUES ('cs', 'ERV-ENG.db'); -- Czech (English)
INSERT INTO DefaultVersion VALUES ('da', 'ERV-ENG.db'); -- Danish (English)
INSERT INTO DefaultVersion VALUES ('de', 'ERV-ENG.db'); -- German (English)
INSERT INTO DefaultVersion VALUES ('el', 'ERV-ENG.db'); -- Greek (English)
INSERT INTO DefaultVersion VALUES ('en', 'ERV-ENG.db'); -- English
INSERT INTO DefaultVersion VALUES ('es', 'ERV-SPA.db'); -- Spanish
INSERT INTO DefaultVersion VALUES ('fa', 'NMV.db');     -- Persian
INSERT INTO DefaultVersion VALUES ('fi', 'ERV-RUS.db'); -- Finnish (Russian)
INSERT INTO DefaultVersion VALUES ('fr', 'ERV-ENG.db'); -- French (English)
INSERT INTO DefaultVersion VALUES ('he', 'ERV-ENG.db'); -- Hebrew (English)
INSERT INTO DefaultVersion VALUES ('hi', 'ERV-HIN.db'); -- Hindi
INSERT INTO DefaultVersion VALUES ('hr', 'ERV-HRV.db'); -- Croatia
INSERT INTO DefaultVersion VALUES ('hu', 'ERV-HUN.db'); -- Hungarian
INSERT INTO DefaultVersion VALUES ('id', 'ERV-IND.db'); -- Indonesian
INSERT INTO DefaultVersion VALUES ('it', 'ERV-SPA.db'); -- Italian (Spanish)
INSERT INTO DefaultVersion VALUES ('ja', 'ERV-ENG.db'); -- Japanese (English)
INSERT INTO DefaultVersion VALUES ('kn', 'ERV-KAN.db'); -- Kannada
INSERT INTO DefaultVersion VALUES ('ko', 'ERV-CMN.db'); -- Korean (Chinese)
INSERT INTO DefaultVersion VALUES ('mr', 'ERV-MAR.db'); -- Marathi
INSERT INTO DefaultVersion VALUES ('ms', 'ERV-CMN.db'); -- Malay (Chinese)
INSERT INTO DefaultVersion VALUES ('nb', 'ERV-ENG.db'); -- Norwegian bokmal (English)
INSERT INTO DefaultVersion VALUES ('ne', 'ERV-NEP.db'); -- Nepali
INSERT INTO DefaultVersion VALUES ('nl', 'ERV-ENG.db'); -- Dutch (English)
INSERT INTO DefaultVersion VALUES ('or', 'ERV-ORI.db'); -- Oriya
INSERT INTO DefaultVersion VALUES ('pa', 'ERV-PAN.db'); -- Punjabi
INSERT INTO DefaultVersion VALUES ('pl', 'ERV-RUS.db'); -- Polish (Russian)
INSERT INTO DefaultVersion VALUES ('pt', 'ERV-POR.db'); -- Portuguese
INSERT INTO DefaultVersion VALUES ('ro', 'ERV-ENG.db'); -- Romainian (English)
INSERT INTO DefaultVersion VALUES ('ru', 'ERV-RUS.db'); -- Russia
INSERT INTO DefaultVersion VALUES ('sk', 'ERV-HUN.db'); -- Slovak (Hungarian)
INSERT INTO DefaultVersion VALUES ('sr', 'ERV-SRP.db'); -- Serbia
INSERT INTO DefaultVersion VALUES ('sv', 'ERV-ENG.db'); -- Swedish (English)
INSERT INTO DefaultVersion VALUES ('ta', 'ERV-TAM.db'); -- Tamil
INSERT INTO DefaultVersion VALUES ('th', 'ERV-THA.db'); -- Thai
INSERT INTO DefaultVersion VALUES ('tr', 'ERV-ARB.db'); -- Turkish (Arabic)
INSERT INTO DefaultVersion VALUES ('uk', 'ERV-UKR.db'); -- Ukraine
INSERT INTO DefaultVersion VALUES ('ur', 'ERV-URD.db'); -- Urdu
INSERT INTO DefaultVersion VALUES ('vi', 'ERV-VIE.db'); -- Vietnamese
INSERT INTO DefaultVersion VALUES ('zh', 'ERV-CMN.db'); -- Chinese


CREATE TABLE InstalledVersion (
versionCode NOT NULL PRIMARY KEY REFERENCES Version(versionCode),
startDate NOT NULL,
endDate NULL
);
INSERT INTO InstalledVersion VALUES ('ERV-ARB', '2016-11-11', null);
-- INSERT INTO InstalledVersion VALUES ('ARBVDPD', '2016-06-01', null);
INSERT INTO InstalledVersion VALUES ('ERV-ENG', '2016-10-14', null);
-- INSERT INTO InstalledVersion VALUES ('ERV-SPA', '2016-10-08', null);
-- INSERT INTO InstalledVersion VALUES ('KJVPD', '2016-05-16', null);
INSERT INTO InstalledVersion VALUES ('NMV', '2016-06-27', null);
-- INSERT INTO InstalledVersion VALUES ('WEB', '2016-05-16', null);
-- INSERT INTO InstalledVersion VALUES ('ERV-PAN', '2016-10-28', null);
-- INSERT INTO InstalledVersion VALUES ('ERV-ORI', '2016-10-28', null);



CREATE TABLE Translation (
source TEXT NOT NULL,
target TEXT NOT NULL,
translated TEXT NOT NULL,
PRIMARY KEY(target, source) -- select where target=? is primary query
);

INSERT INTO Translation VALUES ('WORLD', 'ar', 'العالم');
INSERT INTO Translation VALUES ('WORLD', 'ca', 'món');
INSERT INTO Translation VALUES ('WORLD', 'hr', 'Svijet');
INSERT INTO Translation VALUES ('WORLD', 'cs', 'Svět');
INSERT INTO Translation VALUES ('WORLD', 'da', 'Verden');
INSERT INTO Translation VALUES ('WORLD', 'nl', 'Wereld');
INSERT INTO Translation VALUES ('WORLD', 'en', 'World');
INSERT INTO Translation VALUES ('WORLD', 'fi', 'Maailman');
INSERT INTO Translation VALUES ('WORLD', 'fr', 'monde');
INSERT INTO Translation VALUES ('WORLD', 'de', 'Welt');
INSERT INTO Translation VALUES ('WORLD', 'el', 'Κόσμος');
INSERT INTO Translation VALUES ('WORLD', 'he', 'עוֹלָם');
INSERT INTO Translation VALUES ('WORLD', 'hi', 'विश्व');
INSERT INTO Translation VALUES ('WORLD', 'hu', 'Világ');
INSERT INTO Translation VALUES ('WORLD', 'id', 'Dunia');
INSERT INTO Translation VALUES ('WORLD', 'it', 'Mondo');
INSERT INTO Translation VALUES ('WORLD', 'ja', '世界');
INSERT INTO Translation VALUES ('WORLD', 'ko', '세계');
INSERT INTO Translation VALUES ('WORLD', 'ms', 'dunia');
INSERT INTO Translation VALUES ('WORLD', 'nb', 'Verden');
INSERT INTO Translation VALUES ('WORLD', 'pl', 'Świat');
INSERT INTO Translation VALUES ('WORLD', 'pt', 'Mundo');
INSERT INTO Translation VALUES ('WORLD', 'ro', 'Lume');
INSERT INTO Translation VALUES ('WORLD', 'ru', 'Мир');
INSERT INTO Translation VALUES ('WORLD', 'zh', '世界');
INSERT INTO Translation VALUES ('WORLD', 'sk', 'svet');
INSERT INTO Translation VALUES ('WORLD', 'es', 'Mundo');
INSERT INTO Translation VALUES ('WORLD', 'sv', 'världen');
INSERT INTO Translation VALUES ('WORLD', 'th', 'โลก');
INSERT INTO Translation VALUES ('WORLD', 'tr', 'Dünya');
INSERT INTO Translation VALUES ('WORLD', 'uk', 'світ');
INSERT INTO Translation VALUES ('WORLD', 'vi', 'thế giới');

-- INSERT INTO Translation VALUES ('US', 'en', 'United States');
-- INSERT INTO Translation VALUES ('US', 'es', 'Estados Unidos');
-- INSERT INTO Translation VALUES ('US', 'zh', '美国');
-- INSERT INTO Translation VALUES ('US', 'ar', 'الولايات المتحدة');
-- INSERT INTO Translation VALUES ('US', 'fa', 'ایالات متحده');

-- INSERT INTO Translation VALUES ('MX', 'en', 'Mexico');
-- INSERT INTO Translation VALUES ('MX', 'es', 'Méjico');
-- INSERT INTO Translation VALUES ('MX', 'zh', '墨西哥');
-- INSERT INTO Translation VALUES ('MX', 'ar', 'المكسيك');
-- INSERT INTO Translation VALUES ('MX', 'fa', 'مکزیک');
-- ar -- Arabic
INSERT INTO Translation VALUES ('ar', 'ar', 'العربية');
INSERT INTO Translation VALUES ('ar', 'ca', 'àrab');
INSERT INTO Translation VALUES ('ar', 'zh', '阿拉伯');
INSERT INTO Translation VALUES ('ar', 'hr', 'arapski');
INSERT INTO Translation VALUES ('ar', 'cs', 'arabština');
INSERT INTO Translation VALUES ('ar', 'da', 'Arabic');
INSERT INTO Translation VALUES ('ar', 'nl', 'Arabisch');
INSERT INTO Translation VALUES ('ar', 'en', 'Arabic');
INSERT INTO Translation VALUES ('ar', 'fi', 'arabialainen');
INSERT INTO Translation VALUES ('ar', 'fr', 'Arabe');
INSERT INTO Translation VALUES ('ar', 'de', 'Arabisch');
INSERT INTO Translation VALUES ('ar', 'el', 'αραβικός');
INSERT INTO Translation VALUES ('ar', 'he', 'עֲרָבִית');
INSERT INTO Translation VALUES ('ar', 'hi', 'अरबी');
INSERT INTO Translation VALUES ('ar', 'hu', 'arab');
INSERT INTO Translation VALUES ('ar', 'id', 'Arab');
INSERT INTO Translation VALUES ('ar', 'it', 'Arabo');
INSERT INTO Translation VALUES ('ar', 'ja', 'アラビア語');
INSERT INTO Translation VALUES ('ar', 'ko', '아라비아 말');
INSERT INTO Translation VALUES ('ar', 'ms', 'Bahasa Arab');
INSERT INTO Translation VALUES ('ar', 'nb', 'Arabisk');
INSERT INTO Translation VALUES ('ar', 'pl', 'arabski');
INSERT INTO Translation VALUES ('ar', 'pt', 'árabe');
INSERT INTO Translation VALUES ('ar', 'ro', 'arabic');
INSERT INTO Translation VALUES ('ar', 'ru', 'арабский');
INSERT INTO Translation VALUES ('ar', 'sk', 'arabčina');
INSERT INTO Translation VALUES ('ar', 'es', 'Arábica');
INSERT INTO Translation VALUES ('ar', 'sv', 'arabiska');
INSERT INTO Translation VALUES ('ar', 'th', 'ภาษาอาหรับ');
INSERT INTO Translation VALUES ('ar', 'tr', 'Arapça');
INSERT INTO Translation VALUES ('ar', 'uk', 'арабська');
INSERT INTO Translation VALUES ('ar', 'vi', 'tiếng Ả Rập');

-- bg -- Bulgarian
INSERT INTO Translation VALUES ('bg', 'ar', 'البلغارية');
INSERT INTO Translation VALUES ('bg', 'ca', 'búlgar');
INSERT INTO Translation VALUES ('bg', 'zh', '保加利亚语');
INSERT INTO Translation VALUES ('bg', 'hr', 'bugarski');
INSERT INTO Translation VALUES ('bg', 'cs', 'bulharský');
INSERT INTO Translation VALUES ('bg', 'da', 'bulgarsk');
INSERT INTO Translation VALUES ('bg', 'nl', 'Bulgarian');
INSERT INTO Translation VALUES ('bg', 'en', 'Bulgarian');
INSERT INTO Translation VALUES ('bg', 'fi', 'bulgarialainen');
INSERT INTO Translation VALUES ('bg', 'fr', 'bulgare');
INSERT INTO Translation VALUES ('bg', 'de', 'bulgarisch');
INSERT INTO Translation VALUES ('bg', 'el', 'Βούλγαρος');
INSERT INTO Translation VALUES ('bg', 'he', 'בולגרי');
INSERT INTO Translation VALUES ('bg', 'hi', 'बल्गेरियाई');
INSERT INTO Translation VALUES ('bg', 'hu', 'bolgár');
INSERT INTO Translation VALUES ('bg', 'id', 'Bulgaria');
INSERT INTO Translation VALUES ('bg', 'it', 'bulgaro');
INSERT INTO Translation VALUES ('bg', 'ja', 'ブルガリア語');
INSERT INTO Translation VALUES ('bg', 'ko', '불가리아 사람');
INSERT INTO Translation VALUES ('bg', 'ms', 'Bulgaria');
INSERT INTO Translation VALUES ('bg', 'nb', 'bulgarian');
INSERT INTO Translation VALUES ('bg', 'pl', 'bułgarski');
INSERT INTO Translation VALUES ('bg', 'pt', 'búlgaro');
INSERT INTO Translation VALUES ('bg', 'ro', 'bulgară');
INSERT INTO Translation VALUES ('bg', 'ru', 'болгарский');
INSERT INTO Translation VALUES ('bg', 'sk', 'bulharský');
INSERT INTO Translation VALUES ('bg', 'es', 'búlgaro');
INSERT INTO Translation VALUES ('bg', 'sv', 'bulgarisk');
INSERT INTO Translation VALUES ('bg', 'th', 'บัลแกเรีย');
INSERT INTO Translation VALUES ('bg', 'tr', 'Bulgar');
INSERT INTO Translation VALUES ('bg', 'uk', 'болгарська');
INSERT INTO Translation VALUES ('bg', 'vi', 'Bulgaria');

-- bn -- Bengali
INSERT INTO Translation VALUES ('bn', 'ar', 'البنغالي');
INSERT INTO Translation VALUES ('bn', 'ca', 'bengalí');
INSERT INTO Translation VALUES ('bn', 'zh', '孟加拉');
INSERT INTO Translation VALUES ('bn', 'hr', 'bengalski');
INSERT INTO Translation VALUES ('bn', 'cs', 'bengálský');
INSERT INTO Translation VALUES ('bn', 'da', 'Bengali');
INSERT INTO Translation VALUES ('bn', 'nl', 'Bengalees');
INSERT INTO Translation VALUES ('bn', 'en', 'Bengali');
INSERT INTO Translation VALUES ('bn', 'fi', 'Bengali');
INSERT INTO Translation VALUES ('bn', 'fr', 'bengali');
INSERT INTO Translation VALUES ('bn', 'de', 'Bengali');
INSERT INTO Translation VALUES ('bn', 'el', 'Μπενγκάλι');
INSERT INTO Translation VALUES ('bn', 'he', 'בנגלית');
INSERT INTO Translation VALUES ('bn', 'hi', 'बंगाली');
INSERT INTO Translation VALUES ('bn', 'hu', 'bengáli');
INSERT INTO Translation VALUES ('bn', 'id', 'Benggala');
INSERT INTO Translation VALUES ('bn', 'it', 'bengalese');
INSERT INTO Translation VALUES ('bn', 'ja', 'ベンガル語');
INSERT INTO Translation VALUES ('bn', 'ko', '벵골 사람');
INSERT INTO Translation VALUES ('bn', 'ms', 'Bengali');
INSERT INTO Translation VALUES ('bn', 'nb', 'bengali');
INSERT INTO Translation VALUES ('bn', 'pl', 'bengalski');
INSERT INTO Translation VALUES ('bn', 'pt', 'bengali');
INSERT INTO Translation VALUES ('bn', 'ro', 'bengaleză');
INSERT INTO Translation VALUES ('bn', 'ru', 'бенгальский');
INSERT INTO Translation VALUES ('bn', 'sk', 'bengálčina');
INSERT INTO Translation VALUES ('bn', 'es', 'bengalí');
INSERT INTO Translation VALUES ('bn', 'sv', 'bengali');
INSERT INTO Translation VALUES ('bn', 'th', 'ประเทศบังคลาเทศ');
INSERT INTO Translation VALUES ('bn', 'tr', 'Bengal');
INSERT INTO Translation VALUES ('bn', 'uk', 'бенгальський');
INSERT INTO Translation VALUES ('bn', 'vi', 'Bengali');

-- zh -- Chinese
INSERT INTO Translation VALUES ('zh', 'ar', 'الصينية');
INSERT INTO Translation VALUES ('zh', 'ca', 'xinès');
INSERT INTO Translation VALUES ('zh', 'zh', '中文');
INSERT INTO Translation VALUES ('zh', 'hr', 'kineski');
INSERT INTO Translation VALUES ('zh', 'cs', 'čínština');
INSERT INTO Translation VALUES ('zh', 'da', 'kinesisk');
INSERT INTO Translation VALUES ('zh', 'nl', 'Chinese');
INSERT INTO Translation VALUES ('zh', 'en', 'Chinese');
INSERT INTO Translation VALUES ('zh', 'fi', 'Kiinan kieli');
INSERT INTO Translation VALUES ('zh', 'fr', 'chinois');
INSERT INTO Translation VALUES ('zh', 'de', 'Chinesisch');
INSERT INTO Translation VALUES ('zh', 'el', 'κινέζικο');
INSERT INTO Translation VALUES ('zh', 'he', 'סִינִית');
INSERT INTO Translation VALUES ('zh', 'hi', 'चीनी');
INSERT INTO Translation VALUES ('zh', 'hu', 'kínai');
INSERT INTO Translation VALUES ('zh', 'id', 'Cina');
INSERT INTO Translation VALUES ('zh', 'it', 'Cinese');
INSERT INTO Translation VALUES ('zh', 'ja', '中国語');
INSERT INTO Translation VALUES ('zh', 'ko', '중국말');
INSERT INTO Translation VALUES ('zh', 'ms', 'Cina');
INSERT INTO Translation VALUES ('zh', 'nb', 'kinesisk');
INSERT INTO Translation VALUES ('zh', 'pl', 'chiński');
INSERT INTO Translation VALUES ('zh', 'pt', 'chinês');
INSERT INTO Translation VALUES ('zh', 'ro', 'chinez');
INSERT INTO Translation VALUES ('zh', 'ru', 'Китайский');
INSERT INTO Translation VALUES ('zh', 'sk', 'čínsky');
INSERT INTO Translation VALUES ('zh', 'es', 'chino');
INSERT INTO Translation VALUES ('zh', 'sv', 'kinesisk');
INSERT INTO Translation VALUES ('zh', 'th', 'ชาวจีน');
INSERT INTO Translation VALUES ('zh', 'tr', 'Çince');
INSERT INTO Translation VALUES ('zh', 'uk', 'китайський');
INSERT INTO Translation VALUES ('zh', 'vi', 'Trung Quốc');

-- hr -- Croatian
INSERT INTO Translation VALUES ('hr', 'ar', 'الكرواتية');
INSERT INTO Translation VALUES ('hr', 'ca', 'croat');
INSERT INTO Translation VALUES ('hr', 'zh', '克罗地亚');
INSERT INTO Translation VALUES ('hr', 'hr', 'hrvatski');
INSERT INTO Translation VALUES ('hr', 'cs', 'chorvatský');
INSERT INTO Translation VALUES ('hr', 'da', 'Kroatisk');
INSERT INTO Translation VALUES ('hr', 'nl', 'Kroatisch');
INSERT INTO Translation VALUES ('hr', 'en', 'Croatian');
INSERT INTO Translation VALUES ('hr', 'fi', 'kroaatti');
INSERT INTO Translation VALUES ('hr', 'fr', 'croate');
INSERT INTO Translation VALUES ('hr', 'de', 'kroatisch');
INSERT INTO Translation VALUES ('hr', 'el', 'Κροατία');
INSERT INTO Translation VALUES ('hr', 'he', 'קרואטי');
INSERT INTO Translation VALUES ('hr', 'hi', 'क्रोएशियाई');
INSERT INTO Translation VALUES ('hr', 'hu', 'horvát');
INSERT INTO Translation VALUES ('hr', 'id', 'Kroasia');
INSERT INTO Translation VALUES ('hr', 'it', 'croato');
INSERT INTO Translation VALUES ('hr', 'ja', 'クロアチア語');
INSERT INTO Translation VALUES ('hr', 'ko', '크로아티아의');
INSERT INTO Translation VALUES ('hr', 'ms', 'Croatian');
-- INSERT INTO Translation VALUES ('hr', 'nb', 'kroa~~POS=TRUNC');
INSERT INTO Translation VALUES ('hr', 'pl', 'chorwacki');
INSERT INTO Translation VALUES ('hr', 'pt', 'croata');
INSERT INTO Translation VALUES ('hr', 'ro', 'croat');
INSERT INTO Translation VALUES ('hr', 'ru', 'хорватский');
INSERT INTO Translation VALUES ('hr', 'sk', 'chorvátsky');
INSERT INTO Translation VALUES ('hr', 'es', 'croata');
INSERT INTO Translation VALUES ('hr', 'sv', 'Kroatisk');
INSERT INTO Translation VALUES ('hr', 'th', 'โครเอเชีย');
INSERT INTO Translation VALUES ('hr', 'tr', 'Hırvat');
INSERT INTO Translation VALUES ('hr', 'uk', 'хорватський');
INSERT INTO Translation VALUES ('hr', 'vi', 'Croatia');

-- en -- English
INSERT INTO Translation VALUES ('en', 'ar', 'الإنجليزية');
INSERT INTO Translation VALUES ('en', 'ca', 'Anglès');
INSERT INTO Translation VALUES ('en', 'zh', '英语');
INSERT INTO Translation VALUES ('en', 'hr', 'Engleski');
INSERT INTO Translation VALUES ('en', 'cs', 'angličtina');
INSERT INTO Translation VALUES ('en', 'da', 'engelsk');
INSERT INTO Translation VALUES ('en', 'nl', 'Engels');
INSERT INTO Translation VALUES ('en', 'en', 'English');
INSERT INTO Translation VALUES ('en', 'fi', 'englanti');
INSERT INTO Translation VALUES ('en', 'fr', 'Anglais');
INSERT INTO Translation VALUES ('en', 'de', 'Englisch');
INSERT INTO Translation VALUES ('en', 'el', 'Αγγλικά');
INSERT INTO Translation VALUES ('en', 'he', 'אנגלית');
INSERT INTO Translation VALUES ('en', 'hi', 'अंग्रेज़ी');
INSERT INTO Translation VALUES ('en', 'hu', 'angol');
INSERT INTO Translation VALUES ('en', 'id', 'Inggris');
INSERT INTO Translation VALUES ('en', 'it', 'Inglese');
INSERT INTO Translation VALUES ('en', 'ja', '英語');
INSERT INTO Translation VALUES ('en', 'ko', '영어');
INSERT INTO Translation VALUES ('en', 'ms', 'English');
INSERT INTO Translation VALUES ('en', 'nb', 'Engelsk');
INSERT INTO Translation VALUES ('en', 'pl', 'język angielski');
INSERT INTO Translation VALUES ('en', 'pt', 'Inglês');
INSERT INTO Translation VALUES ('en', 'ro', 'Engleză');
INSERT INTO Translation VALUES ('en', 'ru', 'английский');
INSERT INTO Translation VALUES ('en', 'sk', 'Angličtina');
INSERT INTO Translation VALUES ('en', 'es', 'Inglés');
INSERT INTO Translation VALUES ('en', 'sv', 'Engelska');
INSERT INTO Translation VALUES ('en', 'th', 'อังกฤษ');
INSERT INTO Translation VALUES ('en', 'tr', 'İngilizce');
INSERT INTO Translation VALUES ('en', 'uk', 'англійська');
INSERT INTO Translation VALUES ('en', 'vi', 'Anh');

-- fa -- Farsi
INSERT INTO Translation VALUES ('fa', 'ar', 'الفارسية');
INSERT INTO Translation VALUES ('fa', 'ca', 'farsi');
INSERT INTO Translation VALUES ('fa', 'zh', '波斯语');
INSERT INTO Translation VALUES ('fa', 'hr', 'farsi');
INSERT INTO Translation VALUES ('fa', 'cs', 'perština');
INSERT INTO Translation VALUES ('fa', 'da', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'nl', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'en', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'fi', 'Persia');
INSERT INTO Translation VALUES ('fa', 'fr', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'de', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'el', 'Φαρσί');
INSERT INTO Translation VALUES ('fa', 'he', 'פרסי');
INSERT INTO Translation VALUES ('fa', 'hi', 'फारसी');
INSERT INTO Translation VALUES ('fa', 'hu', 'fárszi');
INSERT INTO Translation VALUES ('fa', 'id', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'it', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'ja', 'ペルシア語');
INSERT INTO Translation VALUES ('fa', 'ko', '페르시아어');
INSERT INTO Translation VALUES ('fa', 'ms', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'nb', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'pl', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'pt', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'ro', 'farsi');
INSERT INTO Translation VALUES ('fa', 'ru', 'фарси');
INSERT INTO Translation VALUES ('fa', 'sk', 'perzština');
INSERT INTO Translation VALUES ('fa', 'es', 'Farsi');
INSERT INTO Translation VALUES ('fa', 'sv', 'Persiska');
INSERT INTO Translation VALUES ('fa', 'th', 'ฟาร์ซิ');
INSERT INTO Translation VALUES ('fa', 'tr', 'Farsça');
INSERT INTO Translation VALUES ('fa', 'uk', 'фарсі');
INSERT INTO Translation VALUES ('fa', 'vi', 'Farsi');

-- hi -- Hindi
INSERT INTO Translation VALUES ('hi', 'ar', 'الهندية');
INSERT INTO Translation VALUES ('hi', 'ca', 'hindi');
INSERT INTO Translation VALUES ('hi', 'zh', '印地语');
INSERT INTO Translation VALUES ('hi', 'hr', 'hindski');
INSERT INTO Translation VALUES ('hi', 'cs', 'hindština');
INSERT INTO Translation VALUES ('hi', 'da', 'Hindi');
INSERT INTO Translation VALUES ('hi', 'nl', 'Hindi');
INSERT INTO Translation VALUES ('hi', 'en', 'Hindi');
INSERT INTO Translation VALUES ('hi', 'fi', 'hindi');
INSERT INTO Translation VALUES ('hi', 'fr', 'hindi');
INSERT INTO Translation VALUES ('hi', 'de', 'Hindi');
INSERT INTO Translation VALUES ('hi', 'el', 'Χίντι');
INSERT INTO Translation VALUES ('hi', 'he', 'הינדי');
INSERT INTO Translation VALUES ('hi', 'hi', 'हिंदी');
INSERT INTO Translation VALUES ('hi', 'hu', 'hindi');
INSERT INTO Translation VALUES ('hi', 'id', 'Hindi');
INSERT INTO Translation VALUES ('hi', 'it', 'hindi');
INSERT INTO Translation VALUES ('hi', 'ja', 'ヒンディー語');
INSERT INTO Translation VALUES ('hi', 'ko', '힌디 어');
INSERT INTO Translation VALUES ('hi', 'ms', 'Hindi');
INSERT INTO Translation VALUES ('hi', 'nb', 'Hindi');
INSERT INTO Translation VALUES ('hi', 'pl', 'hinduski');
INSERT INTO Translation VALUES ('hi', 'pt', 'hindi');
INSERT INTO Translation VALUES ('hi', 'ro', 'hindi');
INSERT INTO Translation VALUES ('hi', 'ru', 'хинди');
INSERT INTO Translation VALUES ('hi', 'sk', 'hindčina');
INSERT INTO Translation VALUES ('hi', 'es', 'hindi');
INSERT INTO Translation VALUES ('hi', 'sv', 'hindi');
INSERT INTO Translation VALUES ('hi', 'th', 'ภาษาฮินดี');
INSERT INTO Translation VALUES ('hi', 'tr', 'Hintçe');
INSERT INTO Translation VALUES ('hi', 'uk', 'хінді');
INSERT INTO Translation VALUES ('hi', 'vi', 'Tiếng Hin-ddi');

-- hu -- Hungarian
INSERT INTO Translation VALUES ('hu', 'ar', 'الهنغارية');
INSERT INTO Translation VALUES ('hu', 'ca', 'hongarès');
INSERT INTO Translation VALUES ('hu', 'zh', '匈牙利');
INSERT INTO Translation VALUES ('hu', 'hr', 'madžarski');
INSERT INTO Translation VALUES ('hu', 'cs', 'maďarský');
INSERT INTO Translation VALUES ('hu', 'da', 'ungarsk');
INSERT INTO Translation VALUES ('hu', 'nl', 'Hongaars');
INSERT INTO Translation VALUES ('hu', 'en', 'Hungarian');
INSERT INTO Translation VALUES ('hu', 'fi', 'Unkarin kieli');
INSERT INTO Translation VALUES ('hu', 'fr', 'hongrois');
INSERT INTO Translation VALUES ('hu', 'de', 'ungarisch');
INSERT INTO Translation VALUES ('hu', 'el', 'ουγγρικός');
INSERT INTO Translation VALUES ('hu', 'he', 'הוּנגָרִי');
INSERT INTO Translation VALUES ('hu', 'hi', 'हंगरी');
INSERT INTO Translation VALUES ('hu', 'hu', 'Magyar');
INSERT INTO Translation VALUES ('hu', 'id', 'Hongaria');
INSERT INTO Translation VALUES ('hu', 'it', 'ungherese');
INSERT INTO Translation VALUES ('hu', 'ja', 'ハンガリー語');
INSERT INTO Translation VALUES ('hu', 'ko', '헝가리 인');
INSERT INTO Translation VALUES ('hu', 'ms', 'Hungary');
INSERT INTO Translation VALUES ('hu', 'nb', 'ungarsk');
INSERT INTO Translation VALUES ('hu', 'pl', 'język węgierski');
INSERT INTO Translation VALUES ('hu', 'pt', 'húngaro');
INSERT INTO Translation VALUES ('hu', 'ro', 'maghiar');
INSERT INTO Translation VALUES ('hu', 'ru', 'Венгерский');
INSERT INTO Translation VALUES ('hu', 'sk', 'maďarský');
INSERT INTO Translation VALUES ('hu', 'es', 'húngaro');
INSERT INTO Translation VALUES ('hu', 'sv', 'ungerska');
INSERT INTO Translation VALUES ('hu', 'th', 'ฮังการี');
INSERT INTO Translation VALUES ('hu', 'tr', 'Macarca');
INSERT INTO Translation VALUES ('hu', 'uk', 'угорський');
INSERT INTO Translation VALUES ('hu', 'vi', 'Hungary');

-- id -- Indonesian
INSERT INTO Translation VALUES ('id', 'ar', 'الأندونيسية');
INSERT INTO Translation VALUES ('id', 'ca', 'indonesi');
INSERT INTO Translation VALUES ('id', 'zh', '印度尼西亚');
INSERT INTO Translation VALUES ('id', 'hr', 'indonezijski');
INSERT INTO Translation VALUES ('id', 'cs', 'indonéština');
INSERT INTO Translation VALUES ('id', 'da', 'Indonesisk');
INSERT INTO Translation VALUES ('id', 'nl', 'Indonesisch');
INSERT INTO Translation VALUES ('id', 'en', 'Indonesian');
INSERT INTO Translation VALUES ('id', 'fi', 'indonesialainen');
INSERT INTO Translation VALUES ('id', 'fr', 'indonésien');
INSERT INTO Translation VALUES ('id', 'de', 'Indonesier');
INSERT INTO Translation VALUES ('id', 'el', 'Ινδονησίας');
INSERT INTO Translation VALUES ('id', 'he', 'אינדונזי');
INSERT INTO Translation VALUES ('id', 'hi', 'इन्डोनेशियाई');
INSERT INTO Translation VALUES ('id', 'hu', 'indonéz');
INSERT INTO Translation VALUES ('id', 'id', 'bahasa Indonesia');
INSERT INTO Translation VALUES ('id', 'it', 'indonesiano');
INSERT INTO Translation VALUES ('id', 'ja', 'インドネシア語');
INSERT INTO Translation VALUES ('id', 'ko', '인도네시아 인');
INSERT INTO Translation VALUES ('id', 'ms', 'Indonesia');
INSERT INTO Translation VALUES ('id', 'nb', 'Indonesisk');
INSERT INTO Translation VALUES ('id', 'pl', 'indonezyjski');
INSERT INTO Translation VALUES ('id', 'pt', 'indonésio');
INSERT INTO Translation VALUES ('id', 'ro', 'indoneziană');
INSERT INTO Translation VALUES ('id', 'ru', 'индонезийский');
INSERT INTO Translation VALUES ('id', 'sk', 'indonézsky');
INSERT INTO Translation VALUES ('id', 'es', 'indonesio');
INSERT INTO Translation VALUES ('id', 'sv', 'indonesisk');
INSERT INTO Translation VALUES ('id', 'th', 'ชาวอินโดนีเซีย');
INSERT INTO Translation VALUES ('id', 'tr', 'Endonezya');
INSERT INTO Translation VALUES ('id', 'uk', 'індонезійська');
INSERT INTO Translation VALUES ('id', 'vi', 'Indonesia');

-- kn -- Kannada
INSERT INTO Translation VALUES ('kn', 'ar', 'الكانادا');
INSERT INTO Translation VALUES ('kn', 'ca', 'kannada');
INSERT INTO Translation VALUES ('kn', 'zh', '卡纳达语');
INSERT INTO Translation VALUES ('kn', 'hr', 'kannada');
INSERT INTO Translation VALUES ('kn', 'cs', 'Kanadský');
INSERT INTO Translation VALUES ('kn', 'da', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'nl', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'en', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'fi', 'kannada');
INSERT INTO Translation VALUES ('kn', 'fr', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'de', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'el', 'Κανάντα');
INSERT INTO Translation VALUES ('kn', 'he', 'קנאדה');
INSERT INTO Translation VALUES ('kn', 'hi', 'कन्नड़');
INSERT INTO Translation VALUES ('kn', 'hu', 'kannada');
INSERT INTO Translation VALUES ('kn', 'id', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'it', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'ja', 'カンナダ語');
INSERT INTO Translation VALUES ('kn', 'ko', '칸나다어');
INSERT INTO Translation VALUES ('kn', 'ms', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'nb', 'kannada');
INSERT INTO Translation VALUES ('kn', 'pl', 'kannada');
INSERT INTO Translation VALUES ('kn', 'pt', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'ro', 'kannada');
INSERT INTO Translation VALUES ('kn', 'ru', 'каннады');
INSERT INTO Translation VALUES ('kn', 'sk', 'Kanadský');
INSERT INTO Translation VALUES ('kn', 'es', 'kannada');
INSERT INTO Translation VALUES ('kn', 'sv', 'kannada');
INSERT INTO Translation VALUES ('kn', 'th', 'ดา');
INSERT INTO Translation VALUES ('kn', 'tr', 'Kannada');
INSERT INTO Translation VALUES ('kn', 'uk', 'каннада');
INSERT INTO Translation VALUES ('kn', 'vi', 'kannada');

-- mr -- Marathi
INSERT INTO Translation VALUES ('mr', 'ar', 'المهاراتية');
INSERT INTO Translation VALUES ('mr', 'ca', 'marathi');
INSERT INTO Translation VALUES ('mr', 'zh', '马拉');
INSERT INTO Translation VALUES ('mr', 'hr', 'marathi');
INSERT INTO Translation VALUES ('mr', 'cs', 'maráthština');
INSERT INTO Translation VALUES ('mr', 'da', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'nl', 'marathi');
INSERT INTO Translation VALUES ('mr', 'en', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'fi', 'marathi');
INSERT INTO Translation VALUES ('mr', 'fr', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'de', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'el', 'Μαράθι');
INSERT INTO Translation VALUES ('mr', 'he', 'מרתי');
INSERT INTO Translation VALUES ('mr', 'hi', 'मराठी');
INSERT INTO Translation VALUES ('mr', 'hu', 'marathi');
INSERT INTO Translation VALUES ('mr', 'id', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'it', 'marathi');
INSERT INTO Translation VALUES ('mr', 'ja', 'マラーティー語');
INSERT INTO Translation VALUES ('mr', 'ko', '마라타어');
INSERT INTO Translation VALUES ('mr', 'ms', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'nb', 'marathi');
INSERT INTO Translation VALUES ('mr', 'pl', 'marathi');
INSERT INTO Translation VALUES ('mr', 'pt', 'marata');
INSERT INTO Translation VALUES ('mr', 'ro', 'marathi');
INSERT INTO Translation VALUES ('mr', 'ru', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'sk', 'maráthčina');
INSERT INTO Translation VALUES ('mr', 'es', 'marathi');
INSERT INTO Translation VALUES ('mr', 'sv', 'marathi');
INSERT INTO Translation VALUES ('mr', 'th', 'ฐี');
INSERT INTO Translation VALUES ('mr', 'tr', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'uk', 'Marathi');
INSERT INTO Translation VALUES ('mr', 'vi', 'Marathi');

-- ne -- Nepali
INSERT INTO Translation VALUES ('ne', 'ar', 'النيبالية');
INSERT INTO Translation VALUES ('ne', 'ca', 'nepalès');
INSERT INTO Translation VALUES ('ne', 'zh', '尼泊尔');
INSERT INTO Translation VALUES ('ne', 'hr', 'nepalski');
INSERT INTO Translation VALUES ('ne', 'cs', 'nepálský');
INSERT INTO Translation VALUES ('ne', 'da', 'nepalesisk');
INSERT INTO Translation VALUES ('ne', 'nl', 'nepali');
INSERT INTO Translation VALUES ('ne', 'en', 'Nepali');
INSERT INTO Translation VALUES ('ne', 'fi', 'nepali');
INSERT INTO Translation VALUES ('ne', 'fr', 'népalais');
INSERT INTO Translation VALUES ('ne', 'de', 'Nepali');
INSERT INTO Translation VALUES ('ne', 'el', 'Νεπάλ');
INSERT INTO Translation VALUES ('ne', 'he', 'נפאלית');
INSERT INTO Translation VALUES ('ne', 'hi', 'नेपाली');
INSERT INTO Translation VALUES ('ne', 'hu', 'nepáli');
INSERT INTO Translation VALUES ('ne', 'id', 'Nepal');
INSERT INTO Translation VALUES ('ne', 'it', 'Nepali');
INSERT INTO Translation VALUES ('ne', 'ja', 'ネパール語');
INSERT INTO Translation VALUES ('ne', 'ko', '네팔어');
INSERT INTO Translation VALUES ('ne', 'ms', 'Nepal');
INSERT INTO Translation VALUES ('ne', 'nb', 'Nepali');
INSERT INTO Translation VALUES ('ne', 'pl', 'nepalski');
INSERT INTO Translation VALUES ('ne', 'pt', 'Nepali');
INSERT INTO Translation VALUES ('ne', 'ro', 'nepaleză');
INSERT INTO Translation VALUES ('ne', 'ru', 'непальский');
INSERT INTO Translation VALUES ('ne', 'sk', 'nepálsky');
INSERT INTO Translation VALUES ('ne', 'es', 'nepalí');
INSERT INTO Translation VALUES ('ne', 'sv', 'nepali');
INSERT INTO Translation VALUES ('ne', 'th', 'เนปาล');
INSERT INTO Translation VALUES ('ne', 'tr', 'Nepali');
INSERT INTO Translation VALUES ('ne', 'uk', 'непальська');
INSERT INTO Translation VALUES ('ne', 'vi', 'Nê-pan');

-- or -- Oriya
INSERT INTO Translation VALUES ('or', 'ar', 'الأوريا');
INSERT INTO Translation VALUES ('or', 'ca', 'oriya');
INSERT INTO Translation VALUES ('or', 'zh', '奥里亚语');
INSERT INTO Translation VALUES ('or', 'hr', 'orijsko');
INSERT INTO Translation VALUES ('or', 'cs', 'urijština');
INSERT INTO Translation VALUES ('or', 'da', 'Oriya');
INSERT INTO Translation VALUES ('or', 'nl', 'Oriya');
INSERT INTO Translation VALUES ('or', 'en', 'Oriya');
INSERT INTO Translation VALUES ('or', 'fi', 'Oriya');
INSERT INTO Translation VALUES ('or', 'fr', 'Oriya');
INSERT INTO Translation VALUES ('or', 'de', 'Oriya');
INSERT INTO Translation VALUES ('or', 'el', 'Ορίγια');
INSERT INTO Translation VALUES ('or', 'he', 'אוריה');
INSERT INTO Translation VALUES ('or', 'hi', 'ओरिया');
INSERT INTO Translation VALUES ('or', 'hu', 'oriya');
INSERT INTO Translation VALUES ('or', 'id', 'Oriya');
INSERT INTO Translation VALUES ('or', 'it', 'Oriya');
INSERT INTO Translation VALUES ('or', 'ja', 'オリヤー語');
INSERT INTO Translation VALUES ('or', 'ko', '오리야어');
INSERT INTO Translation VALUES ('or', 'ms', 'Oriya');
INSERT INTO Translation VALUES ('or', 'nb', 'Oriya');
INSERT INTO Translation VALUES ('or', 'pl', 'orija');
INSERT INTO Translation VALUES ('or', 'pt', 'Oriya');
INSERT INTO Translation VALUES ('or', 'ro', 'oriya');
INSERT INTO Translation VALUES ('or', 'ru', 'Ория');
INSERT INTO Translation VALUES ('or', 'sk', 'Urijština');
INSERT INTO Translation VALUES ('or', 'es', 'Oriya');
INSERT INTO Translation VALUES ('or', 'sv', 'oriya');
INSERT INTO Translation VALUES ('or', 'th', 'โอริยา');
INSERT INTO Translation VALUES ('or', 'tr', 'Oriya');
INSERT INTO Translation VALUES ('or', 'uk', 'орія');
INSERT INTO Translation VALUES ('or', 'vi', 'Oriya');

-- pa -- Punjabi
INSERT INTO Translation VALUES ('pa', 'ar', 'البنجابية');
INSERT INTO Translation VALUES ('pa', 'ca', 'punjabi');
INSERT INTO Translation VALUES ('pa', 'zh', '旁遮普');
INSERT INTO Translation VALUES ('pa', 'hr', 'Pendžabljanin');
INSERT INTO Translation VALUES ('pa', 'cs', 'pandžábský');
INSERT INTO Translation VALUES ('pa', 'da', 'punjabi');
INSERT INTO Translation VALUES ('pa', 'nl', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'en', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'fi', 'punjabi');
INSERT INTO Translation VALUES ('pa', 'fr', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'de', 'Panjabi');
INSERT INTO Translation VALUES ('pa', 'el', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'he', 'פונג''בית'); -- 2nd apostrophe added
INSERT INTO Translation VALUES ('pa', 'hi', 'पंजाबी');
INSERT INTO Translation VALUES ('pa', 'hu', 'pandzsábi');
INSERT INTO Translation VALUES ('pa', 'id', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'it', 'punjabi');
INSERT INTO Translation VALUES ('pa', 'ja', 'パンジャブ語');
INSERT INTO Translation VALUES ('pa', 'ko', '펀 자브');
INSERT INTO Translation VALUES ('pa', 'ms', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'nb', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'pl', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'pt', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'ro', 'Punjabi');
INSERT INTO Translation VALUES ('pa', 'ru', 'панджаби');
INSERT INTO Translation VALUES ('pa', 'sk', 'pandžábský');
INSERT INTO Translation VALUES ('pa', 'es', 'punjabi');
INSERT INTO Translation VALUES ('pa', 'sv', 'punjabi');
INSERT INTO Translation VALUES ('pa', 'th', 'ปัญจาบ');
INSERT INTO Translation VALUES ('pa', 'tr', 'Pencap');
INSERT INTO Translation VALUES ('pa', 'uk', 'панджабі');
INSERT INTO Translation VALUES ('pa', 'vi', 'Punjabi');

-- pt -- Portuguese
INSERT INTO Translation VALUES ('pt', 'ar', 'البرتغالية');
INSERT INTO Translation VALUES ('pt', 'ca', 'portuguès');
INSERT INTO Translation VALUES ('pt', 'zh', '葡萄牙语');
INSERT INTO Translation VALUES ('pt', 'hr', 'Portugalski');
INSERT INTO Translation VALUES ('pt', 'cs', 'portugalština');
INSERT INTO Translation VALUES ('pt', 'da', 'portugisisk');
INSERT INTO Translation VALUES ('pt', 'nl', 'Portugees');
INSERT INTO Translation VALUES ('pt', 'en', 'Portuguese');
INSERT INTO Translation VALUES ('pt', 'fi', 'Portugalin kieli');
INSERT INTO Translation VALUES ('pt', 'fr', 'Portugais');
INSERT INTO Translation VALUES ('pt', 'de', 'Portugiesisch');
INSERT INTO Translation VALUES ('pt', 'el', 'Πορτογάλος');
INSERT INTO Translation VALUES ('pt', 'he', 'פורטוגזי');
INSERT INTO Translation VALUES ('pt', 'hi', 'पुर्तगाली');
INSERT INTO Translation VALUES ('pt', 'hu', 'portugál');
INSERT INTO Translation VALUES ('pt', 'id', 'Portugis');
INSERT INTO Translation VALUES ('pt', 'it', 'portoghese');
INSERT INTO Translation VALUES ('pt', 'ja', 'ポルトガル語');
INSERT INTO Translation VALUES ('pt', 'ko', '포르투갈 인');
INSERT INTO Translation VALUES ('pt', 'ms', 'Portugis');
INSERT INTO Translation VALUES ('pt', 'nb', 'portugisisk');
INSERT INTO Translation VALUES ('pt', 'pl', 'portugalski');
INSERT INTO Translation VALUES ('pt', 'pt', 'português');
INSERT INTO Translation VALUES ('pt', 'ro', 'portugheză');
INSERT INTO Translation VALUES ('pt', 'ru', 'португальский');
INSERT INTO Translation VALUES ('pt', 'sk', 'portugalský');
INSERT INTO Translation VALUES ('pt', 'es', 'portugués');
INSERT INTO Translation VALUES ('pt', 'sv', 'portugisiska');
INSERT INTO Translation VALUES ('pt', 'th', 'ชาวโปรตุเกส');
INSERT INTO Translation VALUES ('pt', 'tr', 'Portekizce');
INSERT INTO Translation VALUES ('pt', 'uk', 'португальська');
INSERT INTO Translation VALUES ('pt', 'vi', 'Bồ Đào Nha');

-- ru -- Russian
INSERT INTO Translation VALUES ('ru', 'ar', 'الروسية');
INSERT INTO Translation VALUES ('ru', 'ca', 'rus');
INSERT INTO Translation VALUES ('ru', 'zh', '俄语');
INSERT INTO Translation VALUES ('ru', 'hr', 'ruski');
INSERT INTO Translation VALUES ('ru', 'cs', 'ruština');
INSERT INTO Translation VALUES ('ru', 'da', 'Russisk');
INSERT INTO Translation VALUES ('ru', 'nl', 'Russisch');
INSERT INTO Translation VALUES ('ru', 'en', 'Russian');
INSERT INTO Translation VALUES ('ru', 'fi', 'Venäjän kieli');
INSERT INTO Translation VALUES ('ru', 'fr', 'russe');
INSERT INTO Translation VALUES ('ru', 'de', 'Russisch');
INSERT INTO Translation VALUES ('ru', 'el', 'ρωσικός');
INSERT INTO Translation VALUES ('ru', 'he', 'רוּסִי');
INSERT INTO Translation VALUES ('ru', 'hi', 'रूसी');
INSERT INTO Translation VALUES ('ru', 'hu', 'orosz');
INSERT INTO Translation VALUES ('ru', 'id', 'Rusia');
INSERT INTO Translation VALUES ('ru', 'it', 'russo');
INSERT INTO Translation VALUES ('ru', 'ja', 'ロシア');
INSERT INTO Translation VALUES ('ru', 'ko', '러시아인');
INSERT INTO Translation VALUES ('ru', 'ms', 'Russian');
INSERT INTO Translation VALUES ('ru', 'nb', 'russisk');
INSERT INTO Translation VALUES ('ru', 'pl', 'Rosyjski');
INSERT INTO Translation VALUES ('ru', 'pt', 'russo');
INSERT INTO Translation VALUES ('ru', 'ro', 'Rusă');
INSERT INTO Translation VALUES ('ru', 'ru', 'русский');
INSERT INTO Translation VALUES ('ru', 'sk', 'ruský');
INSERT INTO Translation VALUES ('ru', 'es', 'ruso');
INSERT INTO Translation VALUES ('ru', 'sv', 'ryska');
INSERT INTO Translation VALUES ('ru', 'th', 'รัสเซีย');
INSERT INTO Translation VALUES ('ru', 'tr', 'Rusça');
INSERT INTO Translation VALUES ('ru', 'uk', 'російський');
INSERT INTO Translation VALUES ('ru', 'vi', 'người Nga');

-- sr -- Serbian
INSERT INTO Translation VALUES ('sr', 'ar', 'صربي');
INSERT INTO Translation VALUES ('sr', 'ca', 'serbi');
INSERT INTO Translation VALUES ('sr', 'zh', '塞尔维亚');
INSERT INTO Translation VALUES ('sr', 'hr', 'srpski');
INSERT INTO Translation VALUES ('sr', 'cs', 'srbština');
INSERT INTO Translation VALUES ('sr', 'da', 'serbisk');
INSERT INTO Translation VALUES ('sr', 'nl', 'Servisch');
INSERT INTO Translation VALUES ('sr', 'en', 'Serbian');
INSERT INTO Translation VALUES ('sr', 'fi', 'serbialainen');
INSERT INTO Translation VALUES ('sr', 'fr', 'serbe');
INSERT INTO Translation VALUES ('sr', 'de', 'serbisch');
INSERT INTO Translation VALUES ('sr', 'el', 'Σέρβος');
INSERT INTO Translation VALUES ('sr', 'he', 'סרבי');
INSERT INTO Translation VALUES ('sr', 'hi', 'सर्बियाई');
INSERT INTO Translation VALUES ('sr', 'hu', 'szerb');
INSERT INTO Translation VALUES ('sr', 'id', 'Serbia');
INSERT INTO Translation VALUES ('sr', 'it', 'serbo');
INSERT INTO Translation VALUES ('sr', 'ja', 'セルビア語');
INSERT INTO Translation VALUES ('sr', 'ko', '세르비아 사람');
INSERT INTO Translation VALUES ('sr', 'ms', 'Serbia');
INSERT INTO Translation VALUES ('sr', 'nb', 'serbisk');
INSERT INTO Translation VALUES ('sr', 'pl', 'serbski');
INSERT INTO Translation VALUES ('sr', 'pt', 'sérvio');
INSERT INTO Translation VALUES ('sr', 'ro', 'sârb');
INSERT INTO Translation VALUES ('sr', 'ru', 'сербский');
INSERT INTO Translation VALUES ('sr', 'sk', 'srbský');
INSERT INTO Translation VALUES ('sr', 'es', 'serbio');
INSERT INTO Translation VALUES ('sr', 'sv', 'serb');
INSERT INTO Translation VALUES ('sr', 'th', 'เซอร์เบีย');
INSERT INTO Translation VALUES ('sr', 'tr', 'Sırpça');
INSERT INTO Translation VALUES ('sr', 'uk', 'сербський');
INSERT INTO Translation VALUES ('sr', 'vi', 'Serbia');

-- es -- Spanish
INSERT INTO Translation VALUES ('es', 'ar', 'الأسبانية');
INSERT INTO Translation VALUES ('es', 'ca', 'espanyol');
INSERT INTO Translation VALUES ('es', 'zh', '西班牙语');
INSERT INTO Translation VALUES ('es', 'hr', 'španjolski');
INSERT INTO Translation VALUES ('es', 'cs', 'španělština');
INSERT INTO Translation VALUES ('es', 'da', 'spansk');
INSERT INTO Translation VALUES ('es', 'nl', 'Spaans');
INSERT INTO Translation VALUES ('es', 'en', 'Spanish');
INSERT INTO Translation VALUES ('es', 'fi', 'espanjalainen');
INSERT INTO Translation VALUES ('es', 'fr', 'Espanol');
INSERT INTO Translation VALUES ('es', 'de', 'Spanisch');
INSERT INTO Translation VALUES ('es', 'el', 'ισπανικά');
INSERT INTO Translation VALUES ('es', 'he', 'ספרדית');
INSERT INTO Translation VALUES ('es', 'hi', 'स्पेनिश');
INSERT INTO Translation VALUES ('es', 'hu', 'spanyol');
INSERT INTO Translation VALUES ('es', 'id', 'Spanyol');
INSERT INTO Translation VALUES ('es', 'it', 'spagnolo');
INSERT INTO Translation VALUES ('es', 'ja', 'スペイン語');
INSERT INTO Translation VALUES ('es', 'ko', '스페인 사람');
INSERT INTO Translation VALUES ('es', 'ms', 'Sepanyol');
INSERT INTO Translation VALUES ('es', 'nb', 'spansk');
INSERT INTO Translation VALUES ('es', 'pl', 'język hiszpański');
INSERT INTO Translation VALUES ('es', 'pt', 'espanhol');
INSERT INTO Translation VALUES ('es', 'ro', 'Spaniolă');
INSERT INTO Translation VALUES ('es', 'ru', 'испанский');
INSERT INTO Translation VALUES ('es', 'sk', 'španielsky');
INSERT INTO Translation VALUES ('es', 'es', 'Español');
INSERT INTO Translation VALUES ('es', 'sv', 'spansk');
INSERT INTO Translation VALUES ('es', 'th', 'สเปน');
INSERT INTO Translation VALUES ('es', 'tr', 'İspanyol');
INSERT INTO Translation VALUES ('es', 'uk', 'іспанська');
INSERT INTO Translation VALUES ('es', 'vi', 'người Tây Ban Nha');

-- ta -- Tamil
INSERT INTO Translation VALUES ('ta', 'ar', 'التاميل');
INSERT INTO Translation VALUES ('ta', 'ca', 'tamil');
INSERT INTO Translation VALUES ('ta', 'zh', '泰米尔人');
INSERT INTO Translation VALUES ('ta', 'hr', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'cs', 'tamil');
INSERT INTO Translation VALUES ('ta', 'da', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'nl', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'en', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'fi', 'tamil');
INSERT INTO Translation VALUES ('ta', 'fr', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'de', 'Tamilisch');
INSERT INTO Translation VALUES ('ta', 'el', 'Ταμίλ');
INSERT INTO Translation VALUES ('ta', 'he', 'טמילית');
INSERT INTO Translation VALUES ('ta', 'hi', 'तामिल');
INSERT INTO Translation VALUES ('ta', 'hu', 'tamil');
INSERT INTO Translation VALUES ('ta', 'id', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'it', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'ja', 'タミル語');
INSERT INTO Translation VALUES ('ta', 'ko', '타밀 사람');
INSERT INTO Translation VALUES ('ta', 'ms', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'nb', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'pl', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'pt', 'tâmil');
INSERT INTO Translation VALUES ('ta', 'ro', 'tamil');
INSERT INTO Translation VALUES ('ta', 'ru', 'тамильский');
INSERT INTO Translation VALUES ('ta', 'sk', 'tamil');
INSERT INTO Translation VALUES ('ta', 'es', 'Tamil');
INSERT INTO Translation VALUES ('ta', 'sv', 'tamil');
INSERT INTO Translation VALUES ('ta', 'th', 'มิลักขะ');
INSERT INTO Translation VALUES ('ta', 'tr', 'Tamilce');
INSERT INTO Translation VALUES ('ta', 'uk', 'тамільська');
INSERT INTO Translation VALUES ('ta', 'vi', 'Tamil');

-- th -- Thai
INSERT INTO Translation VALUES ('th', 'ar', 'التايلاندية');
INSERT INTO Translation VALUES ('th', 'ca', 'tailandès');
INSERT INTO Translation VALUES ('th', 'zh', '泰国');
INSERT INTO Translation VALUES ('th', 'hr', 'thai');
INSERT INTO Translation VALUES ('th', 'cs', 'Thai');
INSERT INTO Translation VALUES ('th', 'da', 'Thai');
INSERT INTO Translation VALUES ('th', 'nl', 'Thais');
INSERT INTO Translation VALUES ('th', 'en', 'Thai');
INSERT INTO Translation VALUES ('th', 'fi', 'thaimaalainen');
INSERT INTO Translation VALUES ('th', 'fr', 'thaïlandais');
INSERT INTO Translation VALUES ('th', 'de', 'thailändisch');
INSERT INTO Translation VALUES ('th', 'el', 'Ταϊλάνδης');
INSERT INTO Translation VALUES ('th', 'he', 'תאילנדי');
INSERT INTO Translation VALUES ('th', 'hi', 'थाई');
INSERT INTO Translation VALUES ('th', 'hu', 'thai');
INSERT INTO Translation VALUES ('th', 'id', 'Thai');
INSERT INTO Translation VALUES ('th', 'it', 'Thai');
INSERT INTO Translation VALUES ('th', 'ja', 'タイの');
INSERT INTO Translation VALUES ('th', 'ko', '타이어');
INSERT INTO Translation VALUES ('th', 'ms', 'Thai');
INSERT INTO Translation VALUES ('th', 'nb', 'Thai');
INSERT INTO Translation VALUES ('th', 'pl', 'tajski');
INSERT INTO Translation VALUES ('th', 'pt', 'tailandês');
INSERT INTO Translation VALUES ('th', 'ro', 'tailandez');
INSERT INTO Translation VALUES ('th', 'ru', 'тайский');
INSERT INTO Translation VALUES ('th', 'sk', 'thai');
INSERT INTO Translation VALUES ('th', 'es', 'tailandés');
INSERT INTO Translation VALUES ('th', 'sv', 'Thai');
INSERT INTO Translation VALUES ('th', 'th', 'ไทย');
INSERT INTO Translation VALUES ('th', 'tr', 'Tayland');
INSERT INTO Translation VALUES ('th', 'uk', 'тайський');
INSERT INTO Translation VALUES ('th', 'vi', 'Thái');

-- uk -- Ukrainian
INSERT INTO Translation VALUES ('uk', 'ar', 'الأوكراني');
INSERT INTO Translation VALUES ('uk', 'ca', 'ucraïnès');
INSERT INTO Translation VALUES ('uk', 'zh', '乌克兰');
INSERT INTO Translation VALUES ('uk', 'hr', 'ukrajinski');
INSERT INTO Translation VALUES ('uk', 'cs', 'ukrajinština');
INSERT INTO Translation VALUES ('uk', 'da', 'ukrainsk');
INSERT INTO Translation VALUES ('uk', 'nl', 'Oekraïens');
INSERT INTO Translation VALUES ('uk', 'en', 'Ukrainian');
INSERT INTO Translation VALUES ('uk', 'fi', 'ukrainalainen');
INSERT INTO Translation VALUES ('uk', 'fr', 'ukrainien');
INSERT INTO Translation VALUES ('uk', 'de', 'ukrainisch');
INSERT INTO Translation VALUES ('uk', 'el', 'Ουκρανός');
INSERT INTO Translation VALUES ('uk', 'he', 'אוקראיני');
INSERT INTO Translation VALUES ('uk', 'hi', 'यूक्रेनी');
INSERT INTO Translation VALUES ('uk', 'hu', 'ukrán');
INSERT INTO Translation VALUES ('uk', 'id', 'Ukraina');
INSERT INTO Translation VALUES ('uk', 'it', 'ucraino');
INSERT INTO Translation VALUES ('uk', 'ja', 'ウクライナ語');
INSERT INTO Translation VALUES ('uk', 'ko', '우크라이나 말');
INSERT INTO Translation VALUES ('uk', 'ms', 'Ukraine');
INSERT INTO Translation VALUES ('uk', 'nb', 'ukrainsk');
INSERT INTO Translation VALUES ('uk', 'pl', 'ukraiński');
INSERT INTO Translation VALUES ('uk', 'pt', 'ucraniano');
INSERT INTO Translation VALUES ('uk', 'ro', 'ucrainean');
INSERT INTO Translation VALUES ('uk', 'ru', 'украинец');
INSERT INTO Translation VALUES ('uk', 'sk', 'ukrajinský');
INSERT INTO Translation VALUES ('uk', 'es', 'ucranio');
INSERT INTO Translation VALUES ('uk', 'sv', 'ukrainare');
INSERT INTO Translation VALUES ('uk', 'th', 'ยูเครน');
INSERT INTO Translation VALUES ('uk', 'tr', 'Ukrayna');
INSERT INTO Translation VALUES ('uk', 'uk', 'український');
INSERT INTO Translation VALUES ('uk', 'vi', 'Ukraina');

-- ur -- Urdu
INSERT INTO Translation VALUES ('ur', 'ar', 'الأردية');
INSERT INTO Translation VALUES ('ur', 'ca', 'urdu');
INSERT INTO Translation VALUES ('ur', 'zh', '乌尔都语');
INSERT INTO Translation VALUES ('ur', 'hr', 'urdu');
INSERT INTO Translation VALUES ('ur', 'cs', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'da', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'nl', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'en', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'fi', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'fr', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'de', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'el', 'Ουρντού');
INSERT INTO Translation VALUES ('ur', 'he', 'אורדו');
INSERT INTO Translation VALUES ('ur', 'hi', 'उर्दू');
INSERT INTO Translation VALUES ('ur', 'hu', 'urdu');
INSERT INTO Translation VALUES ('ur', 'id', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'it', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'ja', 'ウルドゥー語');
INSERT INTO Translation VALUES ('ur', 'ko', '우르두어');
INSERT INTO Translation VALUES ('ur', 'ms', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'nb', 'urdu');
INSERT INTO Translation VALUES ('ur', 'pl', 'urdu');
INSERT INTO Translation VALUES ('ur', 'pt', 'urdu');
INSERT INTO Translation VALUES ('ur', 'ro', 'urdu');
INSERT INTO Translation VALUES ('ur', 'ru', 'урду');
INSERT INTO Translation VALUES ('ur', 'sk', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'es', 'Urdu');
INSERT INTO Translation VALUES ('ur', 'sv', 'urdu');
INSERT INTO Translation VALUES ('ur', 'th', 'ภาษาอูรดู');
INSERT INTO Translation VALUES ('ur', 'tr', 'Urduca');
INSERT INTO Translation VALUES ('ur', 'uk', 'урду');
INSERT INTO Translation VALUES ('ur', 'vi', 'Urdu');

-- vi -- Vietnamese
INSERT INTO Translation VALUES ('vi', 'ar', 'الفيتنامية');
INSERT INTO Translation VALUES ('vi', 'ca', 'vietnamita');
INSERT INTO Translation VALUES ('vi', 'zh', '越南');
INSERT INTO Translation VALUES ('vi', 'hr', 'vijetnamski');
INSERT INTO Translation VALUES ('vi', 'cs', 'vietnamština');
INSERT INTO Translation VALUES ('vi', 'da', 'Vietnamesisk');
INSERT INTO Translation VALUES ('vi', 'nl', 'Vietnamees');
INSERT INTO Translation VALUES ('vi', 'en', 'Vietnamese');
INSERT INTO Translation VALUES ('vi', 'fi', 'vietnam');
INSERT INTO Translation VALUES ('vi', 'fr', 'vietnamien');
INSERT INTO Translation VALUES ('vi', 'de', 'Vietnamesisch');
INSERT INTO Translation VALUES ('vi', 'el', 'Βιετνάμ');
INSERT INTO Translation VALUES ('vi', 'he', 'ויאטנמית');
INSERT INTO Translation VALUES ('vi', 'hi', 'वियतनामी');
INSERT INTO Translation VALUES ('vi', 'hu', 'vietnami');
INSERT INTO Translation VALUES ('vi', 'id', 'Vietnam');
INSERT INTO Translation VALUES ('vi', 'it', 'vietnamita');
INSERT INTO Translation VALUES ('vi', 'ja', 'ベトナム語');
INSERT INTO Translation VALUES ('vi', 'ko', '베트남 사람');
INSERT INTO Translation VALUES ('vi', 'ms', 'Vietnam');
INSERT INTO Translation VALUES ('vi', 'nb', 'Vietnamesisk');
INSERT INTO Translation VALUES ('vi', 'pl', 'wietnamski');
INSERT INTO Translation VALUES ('vi', 'pt', 'vietnamita');
INSERT INTO Translation VALUES ('vi', 'ro', 'Vietnameză');
INSERT INTO Translation VALUES ('vi', 'ru', 'вьетнамский');
INSERT INTO Translation VALUES ('vi', 'sk', 'Vietnamec');
INSERT INTO Translation VALUES ('vi', 'es', 'vietnamita');
INSERT INTO Translation VALUES ('vi', 'sv', 'vietnames');
INSERT INTO Translation VALUES ('vi', 'th', 'เวียตนาม');
INSERT INTO Translation VALUES ('vi', 'tr', 'Vietnam');
INSERT INTO Translation VALUES ('vi', 'uk', 'в''єтнамський'); -- 2nd apostrophe added
INSERT INTO Translation VALUES ('vi', 'vi', 'Tiếng Việt');