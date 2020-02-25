
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
.import sql/Region.txt Region

