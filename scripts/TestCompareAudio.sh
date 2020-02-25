#!/bin/sh

##
## Test compare Audio files
##

sqlite orig_Versions.db <<END_SQL1

.output $HOME/Desktop/AudioVersion_orig.txt
SELECT versionCode, dbpLanguageCode, dbpVersionCode 
FROM AudioVersion 
ORDER BY versionCode, dbpLanguageCode;

.output $HOME/Desktop/Audio_orig.txt
SELECT damId, dbpLanguageCode, dbpVersionCode, collectionCode, mediaType, volumeName
FROM Audio
ORDER BY damId;

.output $HOME/Desktop/AudioBook_orig.txt
SELECT damId, bookId, bookOrder, numberOfChapters
FROM AudioBook
ORDER BY damId, bookId;

.output $HOME/Desktop/AudioChapter_orig.txt
SELECT damId, bookId, chapter, versePositions
FROM AudioChapter
ORDER BY damId, bookId, chapter;

END_SQL1

sqlite Versions.db <<END_SQL2

.output $HOME/Desktop/AudioVersion_new.txt
SELECT versionCode, dbpLanguageCode, dbpVersionCode 
FROM AudioVersion 
ORDER BY versionCode, dbpLanguageCode;

.output $HOME/Desktop/Audio_new.txt
SELECT damId, dbpLanguageCode, dbpVersionCode, collectionCode, mediaType, volumeName
FROM Audio
ORDER BY damId;

.output $HOME/Desktop/AudioBook_new.txt
SELECT damId, bookId, bookOrder, numberOfChapters
FROM AudioBook
ORDER BY damId, bookId;

.output $HOME/Desktop/AudioChapter_new.txt
SELECT damId, bookId, chapter, versePositions
FROM AudioChapter
ORDER BY damId, bookId, chapter;

END_SQL2


diff $HOME/Desktop/AudioVersion_orig.txt $HOME/Desktop/AudioVersion_new.txt > $HOME/Desktop/AudioVersion.diff
diff $HOME/Desktop/Audio_orig.txt $HOME/Desktop/Audio_new.txt > $HOME/Desktop/Audio.diff
diff $HOME/Desktop/AudioBook_orig.txt $HOME/Desktop/AudioBook_new.txt > $HOME/Desktop/AudioBook.diff
diff $HOME/Desktop/AudioChapter_orig.txt $HOME/Desktop/AudioChapter_new.txt > $HOME/Desktop/AudioChapter.diff

