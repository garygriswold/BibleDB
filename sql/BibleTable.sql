-- CREATE TABLE Versions (
--  bibleId TEXT NOT NULL PRIMARY KEY,
--  iso3 TEXT NOT NULL, -- I think iso3 and version code are how I associate items in a set
--  abbreviation TEXT NOT NULL, -- (e.g. KJV)
--  script TEXT NULL,
--  numerals TEXT NULL,  
--  name TEXT NOT NULL, -- from info.json
--  nameLocal TEXT NOT NULL, -- from info.json
--  nameTranslated TEXT NULL, -- from google translate
--  priority INT NOT NULL DEFAULT 0, -- affects position in version list, manually set

-- Bibles Table
--  filesetId TEXT NOT NULL PRIMARY KEY, -- use fileset_id for now or GUID
--  bibleId TEXT NOT NULL,
--  mediaType TEXT NOT NULL CHECK (mediaType IN ('audio', 'drama', 'video', 'text', 'sqlite')),
--  scope TEXT NOT NULL, -- NT,OT, NTOT, NTP, etc.
--  bucket TEXT NOT NULL,
--  bitrate INT NULL CHECK (bitrate IN (16, 32, 64, 128)),
--  agency TEXT NULL, -- should be NOT NULL, but source unknown
--  copyrightYear INT NULL, -- should be NOT NULL, but source unknown
--  filenameTemplate TEXT NULL, -- should be NOT NULL, but not yet available

-- currently ERV-ARB
INSERT INTO Bibles VALUES('ERV-ARB.db', 'ARBWTC', 'sqlite', 'ERV', 'arb', 1, 'بِعَهْدَيْهِ القَدِيمِ وَالجَدِيد الكِتَابُ المُقَدَّسُ',
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/ARBERV/ARBERV', 
'%I_%O_%B_%C.html', 'dbp-prod', 'audio/ARBWTC/ARBWTCO1DA', 'audio/ARBWTC/ARBWTCN1DA', 
null, null, null);

-- currently ARBVDPD
INSERT INTO Bibles VALUES('ARBVDPD.db', 'ARBVDV', 'sqlite', 'VDV', 'arb', 1, 'الكتاب المقدس ترجمة فان دايك',
'Van Dyck Holy Bible', null, 'text-%R-shortsands', 'text/ARBVDV/ARBVDV', 
'%I_%O_%B_%C.html', 'dbp-prod', 'audio/ARBVDV/ARZVDVO2DA', 'audio/ARBVDV/ARZVDVN2DA', 
null, null, null);

-- currently ERV-AWA (NO FCBH content)
-- INSERT INTO Bibles VALUES('ERV-AWA.db', 'ERV', 'awa', 1, 'पवित्तर बाइबिल',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/AWAERV/AWAERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/AWAWTC/AWAWTCN2DA', 
-- null, null, null);

-- currently ERV-BEN
INSERT INTO Bibles VALUES('ERV-BEN.db', 'BENWTC', 'sqlite', 'ERV', 'ben', 1, 'পবিত্র বাইবেল',
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/BENERV/BENERV', 
'%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/BENWTC/BNGWTCN2DA', 
null, null, null);

-- currently ERV-BUL (NO FCBH content)
-- INSERT INTO Bibles VALUES('ERV-BUL.db', 'ERV', 'bul', 1, 'Новият завет, съвременен превод',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/BULERV/BULERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/BULPRB/BLGAMBN1DA', 
-- null, null, null); -- audio is different version

-- -- currently ERV-CMN (NO FCBH content)
-- INSERT INTO Bibles VALUES('ERV-CMN.db', 'ERV', 'cmn', 1, '圣经–普通话本',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/CMNERV/CMNERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', 'audio/CMNUNV/CHNUNVO2DA', 'audio/CMNUNV/CHNUNVN2DA', 
-- null, null, null); -- audio is different version

-- -- currently ERV-ENG (NO FCBH content)
-- INSERT INTO Bibles VALUES('ERV-ENG.db', 'ERV', 'eng', 2, 'Easy-to-Read Holy Bible',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/ENGERU/ENGERU', 
-- '%I_%O_%B_%C.html', 'dbp-prod', 'audio/ENGESV/ENGESVO2DA', 'audio/ENGESV/ENGESVN2DA', 
-- null, null, null); -- audio is different version

-- currently KJVPD
-- INSERT INTO Bibles VALUES('KJVPD.db', 'KJV', 'eng', 3, 'King James Holy Bible',
-- 'King James Holy Bible', null, 'text-%R-shortsands', 'text/ENGKJV/ENGKJV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', 'audio/ENGKJV/ENGKJVO2DA', 'audio/ENGKJV/ENGKJVN2DA', 
-- null, null, null);

-- currently WEB
INSERT INTO Bibles VALUES('WEB.db', 'ENGWWH', 'sqlite', 'WEB', 'eng', 4, 'World English Holy Bible',
'World English Holy Bible', null, 'text-%R-shortsands', 'text/ENGWEB/ENGWEB', 
'%I_%O_%B_%C.html', 'dbp-prod', 'audio/ENGWEB/ENGWEBO2DA', 'audio/ENGWEB/ENGWEBN2DA', 
null, null, null);

-- currently ERV-HIN
INSERT INTO Bibles VALUES('ERV-HIN.db', 'HINWTC', 'sqlite', 'ERV', 'hin', 1, 'पवित्र बाइबल',
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/HINERV/HINERV', 
'%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/HINWTC/HNDWTCN2DA', 
null, null, null);

-- -- currently ERV-HRV
-- INSERT INTO Bibles VALUES('ERV-HRV.db', 'ERV', 'hrv', 1, 'Novi zavjet, Suvremeni prijevod',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/HRVERV/HRVERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, null, 
-- null, null, null);

-- -- currently ERV-HUN
-- INSERT INTO Bibles VALUES('ERV-HUN.db', 'ERV', 'hun', 1, 'Biblia Egyszerű fordítás',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/HUNERV/HUNERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/HUNHBS/HUNHBSN1DA', 
-- null, null, null); -- audio is different version

-- currently ERV-IND
-- INSERT INTO Bibles VALUES('ERV-IND.db', 'ERV', 'ind', 1, 'Perjanjian Baru: Versi Mudah Dibaca',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/INDERV/INDERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/INDSHL/INZSHLN2DA', 
-- null, null, null); -- audio is different version

-- currently ERV-KAN
INSERT INTO Bibles VALUES('ERV-KAN.db', 'KANWTC', 'sqlite', 'ERV', 'kan', 1, null,
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/KANERV/KANERV', 
'%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/KANWTC/ERVWTCN2DA', 
null, null, null);

-- currently ERV-MAR
INSERT INTO Bibles VALUES('ERV-MAR.db', 'MARWTC', 'sqlite', 'ERV', 'mar', 1, null,
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/MARERV/MARERV', 
'%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/MARWTC/MARWTCN2DA', 
null, null, null);

-- currently ERV-NEP
-- INSERT INTO Bibles VALUES('ERV-NEP.db', 'ERV', 'nep', 1, null,
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/NEPERV/NEPERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, null, 
-- null, null, null);

-- -- currently ERV-ORI
-- INSERT INTO Bibles VALUES('ERV-ORI.db', 'ERV', 'ori', 1, 'ପବିତ୍ର ବାଇବଲ',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/ORIERV/ORIERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/ORYWTC/ORYWTCN2DA', 
-- null, null, null);

-- -- currently ERV-PAN
-- INSERT INTO Bibles VALUES('ERV-PAN.db', 'ERV', 'pan', 1, null,
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/PANERV/PANERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, null, 
-- null, null, null);

-- currently NMV
INSERT INTO Bibles VALUES('NMV.db', 'PESNMV', 'sqlite', 'NMV', 'pes', 1, 'ترجمۀ هزارۀ نو',
'New Millennium Holy Bible', null, 'text-%R-shortsands', 'text/PESNMV/PESEMV', 
'%I_%O_%B_%C.html', 'dbp-prod', null, null, 
null, null, null);

-- currently ERV-POR
-- INSERT INTO Bibles VALUES('ERV-POR.db', 'ERV', 'por', 1, 'Novo Testamento: Versão Fácil de Ler',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/PORERV/PORERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/PORBAR/PORARAN2DA', 
-- null, null, null); -- audio is a different version

-- currently ERV-RUS
INSERT INTO Bibles VALUES('ERV-RUS.db', 'RUSWTC', 'sqlite', 'ERV', 'rus', 1, 'Святая Библия Современный перевод',
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/RUSWTC/RUSWTC', 
'%I_%O_%B_%C.html', 'dbp-prod', 'audio/RUSS76/RUSS76O2DA', 'audio/RUSS76/RUSS76N2DA', 
null, null, null); -- audio is a different version

-- currently ERV-SPA
INSERT INTO Bibles VALUES('ERV-SPA.db', 'SPNWTC', 'sqlite', 'ERV', 'spa', 1, 'La Biblia: La Palabra de Dios para todos',
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/SPAWTC/SPNWTC', 
'%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/SPAWTC/SPNWTCN2DA', 
null, null, null);

-- currently ERV-SRP
-- INSERT INTO Bibles VALUES('ERV-SRP.db', 'ERV', 'srp', 1, 'Библија Савремени српски превод',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/SRPERV/SRPERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, null, 
-- null, null, null);

-- currently ERV-TAM
INSERT INTO Bibles VALUES('ERV-TAM.db', 'TAMWTC', 'sqlite', 'ERV', 'tam', 1, 'பரிசுத்த பைபிள்',
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/TAMERV/TAMERV', 
'%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/TAMWTC/TCVWTCN1DA', 
null, null, null);

-- currently ERV-THA
-- INSERT INTO Bibles VALUES('ERV-THA.db', 'ERV', 'tha', 1, 'พระ​คริสต​ธรรม​คัมภีร์ ฉบับ​อ่าน​เข้า​ใจ​ง่าย',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/THAERV/THAERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, null, 
-- null, null, null);

-- currently ERV-UKR
-- INSERT INTO Bibles VALUES('ERV-UKR.db', 'ERV', 'ukr', 1, 'Новий Заповіт Сучасною Мовою',
-- 'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/UKRBLI/UKRERV', 
-- '%I_%O_%B_%C.html', 'dbp-prod', null, 'audio/UKRN39/UKRO95N2DA', 
-- null, null, null); -- audio is a different version

-- currently ERV-URD
INSERT INTO Bibles VALUES('ERV-URD.db', 'URDWTC', 'sqlite', 'ERV', 'urd', 1, null,
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/URDWTC/URDWTC', 
'%I_%O_%B_%C.html', 'dbp-prod',  null, 'audio/URDWTC/URDWTCN2DA', 
null, null, null);

-- currently ERV-VIE
INSERT INTO Bibles VALUES('ERV-VIE.db', 'VIEWTC', 'sqlite', 'ERV', 'vie', 1, 'Thánh Kinh: Bản Phổ thông',
'Easy-to-Read Holy Bible', null, 'text-%R-shortsands', 'text/VIEWTC/VIEWTC', 
'%I_%O_%B_%C.html', 'dbp-prod', null, null, 
null, null, null);

-- new ENGESV
INSERT INTO Bibles VALUES('ENGESV.db', 'ENGESV', 'sqlite', 'ESV', 'eng', 1, 'English Standard Bible',
'English Standard Bible', null, 'dbp-prod', 'text/ENGESV/ENGESV', 
'%I_%O_%B_%C.html', 'dbp-prod', 'audio/ENGESV/ENGESVO2DA', 'audio/ENGESV/ENGESVN2DA', 
null, null, null);

