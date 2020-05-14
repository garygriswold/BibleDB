DROP TABLE IF EXISTS JesusFilm;
CREATE TABLE JesusFilm (
  country TEXT NOT NULL,
  iso3 TEXT NOT NULL,
  languageId TEXT NOT NULL,
  population INT NOT NULL,
  PRIMARY KEY(country, iso3, languageId));
