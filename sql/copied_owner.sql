


DROP TABLE IF EXISTS Owner;
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

