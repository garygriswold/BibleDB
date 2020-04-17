# Config.py
#
# This program reads the configuration file in the HOME directory. 
# The file contains numerous configurations that are each labeled
# with a name in brackets as in [name]
# The intent is that a user might have more than one profile, such as
# dev, test, stage, and prod
#
#

import os
import sys
import re
import configparser

CONFIG_FILENAME = "bibleDB.cfg"

class Config:

	def __init__(self):
		home = os.environ.get('HOME') # unix
		if home == None:
			home = os.environ.get('HOMEPATH') # windows
		if home == None:
			print("ERROR: Environment variable HOME or HOMEPATH must be set to a directory.")
			sys.exit()

		configFile = os.path.join(home, CONFIG_FILENAME)
		if not os.path.exists(configFile):
			print("ERROR: Config file '%s' does not exist." % (configFile))
			sys.exit()

		if len(sys.argv) < 2:
			print("ERROR: config profile, such as 'dev,test,prod' is first required parameter.")
			sys.exit()
		profile = sys.argv[1]

		config = configparser.ConfigParser(interpolation = None)
		config.read(configFile)
		sections = config.sections()
		if profile not in sections:
			print("ERROR: config profile %s is not in %s" % (profile, configFile))
			sys.exit()
		self.hashMap = config[profile]

		if len(self.hashMap) == 0:
			print("ERROR: Config profile %s does not exist in '%s'." % (profileLabel, configFile))
			sys.exit()

		splitPattern = re.compile("\\\\|/") # I have no idea why \\\\ escapes to one \
		programRunning = splitPattern.split(sys.argv[0])[-1]

		self.VERSIONS_DATABASE = self._get("VERSIONS_DATABASE")

		self.S3_DBP_BUCKET = self._get("S3_DBP_BUCKET")
		self.S3_DBP_VIDEO_BUCKET = self._get("S3_DBP_VIDEO_BUCKET")
		self.S3_AWS_DBP_PROFILE = self._get("S3_AWS_DBP_PROFILE")

		self.FILENAME_DBP_LPTS_XML = self._getPath("FILENAME_DBP_LPTS_XML")

		self.DIRECTORY_BUCKET_LIST = self._getPath("DIRECTORY_BUCKET_LIST")

		self.DIRECTORY_ACCEPTED = self._getPath("DIRECTORY_ACCEPTED")
		self.DIRECTORY_QUARANTINE = self._getPath("DIRECTORY_QUARANTINE")
		self.DIRECTORY_DUPLICATE = self._getPath("DIRECTORY_DUPLICATE")
		self.DIRECTORY_INFO_JSON = self._getPath("DIRECTORY_INFO_JSON")

	def _get(self, name):
		value = self.hashMap.get(name)
		if value == None:
			print("ERROR: Config entry '%s' is missing." % (name))
			sys.exit()
		return value

	def _getPath(self, name):
		value = self._get(name)
		path = value.replace("/", os.path.sep)
		if not os.path.exists(path):
			print("ERROR: path %s for %s does not exist" % (path, name))
			sys.exit()
		return path

	def _getInt(self, name):
		return int(self._get(name))

	def _getFloat(self, name):
		return float(self._get(name))


# Unit Test
if (__name__ == '__main__'):
	config = Config()
	print("User", config.database_user)
	print("DB", config.database_db_name)



