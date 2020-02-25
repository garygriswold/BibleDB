#!/bin/sh -v

# This is a development / test script that compares two Versions.db databases
# one is expected in ShortSands/BibleApp/Versions and the other in Desktop


sqlite Versions.db <<END_SQL1

.output $HOME/Desktop/Versions_orig.txt
select languageId, mediaId, silCode, langCode, title, lengthMS, longDescription
from Video
order by languageId, mediaId;

END_SQL1

sqlite $HOME/Desktop/Versions.db <<END_SQL2

.output $HOME/Desktop/Versions_new.txt
select languageId, mediaId, silCode, langCode, title, lengthMS, longDescription 
from Video 
order by languageId, mediaId;

END_SQL2


diff $HOME/Desktop/Versions_orig.txt $HOME/Desktop/Versions_new.txt > $HOME/Desktop/Versions.diff