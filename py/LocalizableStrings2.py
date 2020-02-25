#
# This program is used to process .xliff files and do an automated translation
# using Google translate, and insert the result into the <target> element.
# I think the translation process should skip over any element that already has a
# target element.
#
# 1. Select Languages to be localized in the xCode project
# 2. Add any new languages to the Languages array below
# 3. in xCode run Edition -> Export Localization, put into Downloads
# 4. Run this program which will update the .xliff files
# 5. For each Language inport the .xcloc directory
# PS. There are commandline options for generating and importing the language
#
# https://developer.apple.com/videos/play/wwdc2018/404/
#
import httplib
import io
import os
import sys
import json
import xml.dom.minidom

sourceDir = os.environ['HOME'] + "/Downloads/SafeBible/"

# item 0 is Apple code for language
# item 1 is Google code for language
# item 2 is common name for language
languages = {
	'ar': ['ar', 'Arabic'],
	'ca': ['ca', 'Catalan'],
	'zh-Hans': ['zh-CN', 'Chinese Simplified'],
	'zh-Hant': ['zh-TW', 'Chinese Traditional'],
	'hr': ['hr', 'Croatian'],
	'cs': ['cs', 'Czech'],
	'da': ['da', 'Danish'],
	'nl': ['nl', 'Dutch'],
	'fi': ['fi', 'Finnish'],
	'fr': ['fr', 'French'],
	'de': ['de', 'German'],
	'el': ['el', 'Greek'],
	'he': ['he', 'Hebrew'],
	'hi': ['hi', 'Hindi'],
	'hu': ['hu', 'Hungarian'],
	'id': ['id', 'Indonesian'],
	'it': ['it', 'Italian'],
	'ja': ['ja', 'Japanese'],
	'ko': ['ko', 'Korean'],
	'ms': ['ms', 'Malay'],
	'nb': ['no', 'Norwegian Bokmal'], # changed nb to no
	'pl': ['pl', 'Polish'],
	'pt-BR': ['pt', 'Portuguese Brazil'],
	'pt-PT': ['pt', 'Portuguese'],
	'ro': ['ro', 'Romanian'],
	'ru': ['ru', 'Russian'],
	'sk': ['sk', 'Slovak'],
	'es': ['es', 'Spanish'],
	'es-419': ['es', 'Spanish Latin Amer'], # same as Spanish
	'sv': ['sv', 'Swedish'],
	'th': ['th', 'Thai'],
	'tr': ['tr', 'Turkish'],
	'uk': ['uk', 'Ukrainian'],
	'vi': ['vi', 'Vietnamese']
}

# Parse an XLIFF file to extract keys, and comments to be translated
#[ Key, Source, hasTarget]
#def parseXLIFF(langCode):
def parseXLIFF(doc):
	parsedFile = []
	body = doc.getElementsByTagName("body")[1]
	transUnitElems = body.getElementsByTagName("trans-unit")
	for transUnit in transUnitElems:
		key = transUnit.getAttribute("id")
		sourceElems = transUnit.getElementsByTagName("source")
		source = sourceElems[0].firstChild.nodeValue
		parsedFile.append([key, source])
	return parsedFile

# generate a request message
def generateRequest(parsedFile, langCode):
	request = '{ "source":"en", "target":"' + langCode + '"'
	for item in parsedFile:
		request += ', "q":"' + item[1] + '"'
	request += ' }'
	return request

# submit a request to Google for translation
def getTranslation(body):
	conn = httplib.HTTPSConnection("translation.googleapis.com")
	path = "/language/translate/v2?key=AIzaSyAl5-Sk0A8w7Qci93-SIwerWS7lvP_6d_4"
	headers = {"Content-Type": "application/json; charset=utf-8"}
	conn.request("POST", path, body, headers)
	response = conn.getresponse()
	print response.status, response.reason
	obj = json.JSONDecoder().decode(response.read())
	translations = obj["data"]["translations"]
	return translations

# generate result and update the XML Document with translated text
def updateXliff(doc, translations):
	index = -1
	body = doc.getElementsByTagName("body")[1]
	transUnitElems = body.getElementsByTagName("trans-unit")
	for transUnit in transUnitElems:
		index += 1
		translation = translations[index]["translatedText"]
		translation = translation.replace("&quot;", '"')
		translation = translation.replace("&#39;", "'")
		targetElems = transUnit.getElementsByTagName("target")
		if len(targetElems) > 0:
			if len(targetElems[0].childNodes) > 0:
				targetElems[0].firstChild.nodeValue = translation
			else:
				textNode = doc.createTextNode(translation)
				targetElems[0].appendChild(textNode)
		else:
			target = doc.createElement("target")
			textNode = doc.createTextNode(translation)
			target.appendChild(textNode)
			noteElems = transUnit.getElementsByTagName("note")
			transUnit.insertBefore(target, noteElems[0])
			

for langDir in os.listdir(sourceDir):
	if langDir[-6:] == ".xcloc":
		appleLang = langDir[0:-6]
		#print appleLang
		filename = sourceDir + langDir + "/Localized Contents/" + appleLang + ".xliff"
		#print filename
		xmlDoc = xml.dom.minidom.parse(filename)
		#print xmlDoc.toxml("utf-8")
		parsedFile = parseXLIFF(xmlDoc)
		#print parsedFile
		googleLang = languages[appleLang][0]
		#print googleLang
		request = generateRequest(parsedFile, googleLang)
		#print request
		translations = getTranslation(request)
		#print translations
		if len(translations) != len(parsedFile):
			print("num translations not correct", len(translations), len(parsedFile))
			sys.exit()
		updateXliff(xmlDoc, translations)
		print xmlDoc.toxml("utf-8")
		output = io.open(filename + ".out", mode="w", encoding="utf-8")
		output.write(xmlDoc.toxml())
		output.close()

for langDir in os.listdir(sourceDir):
	if langDir[-6:] == ".xcloc":
		appleLang = langDir[0:-6]
		filename = sourceDir + langDir + "/Localized Contents/" + appleLang + ".xliff"
		saveFilename = sourceDir + langDir + "/Notes/" + appleLang + ".xliff"
		print filename
		os.rename(filename, saveFilename)
		os.rename(filename + ".out", filename)
