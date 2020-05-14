# APIBibleReader.py

# This class reads the APIBible API of DBL.

import io
import json
from urllib.request import Request, urlopen
from Config import *
from SqliteUtility import *

class APIBibleReader:

	def __init__(self, config):
		self.config = config


	def getBibles(self):
		bibles = self.getResponse("bibles")
		for bible in bibles:
			print("id: %s, dblld: %s, language: %s, abbreviation: %s, abbreviationLocal: %s, name: %s, nameLocal: %s, script: %s" % 
				(bible["id"], bible["dblId"], bible["language"]["id"], bible["abbreviation"], bible["abbreviationLocal"],
				bible["name"], bible["nameLocal"], bible["language"]["script"]))
		return bibles


	def getResponse(self, urlPath):
		request = Request("https://api.scripture.api.bible/v1/" + urlPath)
		request.add_header('api-key', self.config.DBL_MY_API_BIBLE)
		response = urlopen(request)
		content = response.read()
		result = None
		try:
			result = json.loads(content)
		except Exception as err:
			print("ERROR: Json Error in %s" % (urlPath), err)
			return None
		return result.get("data")


if __name__ == "__main__":
	config = Config()
	reader = APIBibleReader(config)
	content = reader.getBibles()


