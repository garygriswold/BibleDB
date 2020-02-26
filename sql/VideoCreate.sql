DROP TABLE IF EXISTS Video;

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
	PRIMARY KEY (languageId, mediaId)
);
CREATE INDEX Video_langCode ON Video (langCode);
