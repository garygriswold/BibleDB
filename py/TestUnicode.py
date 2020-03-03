

import io
import sys
import os
import unicodedata

result = set()
for index in range(0x10ffff):
	#print(index)#, unicodedata.name(unichr(char)))
	c = chr(index)
	try:
		name2 = unicodedata.name(c)
		print(index, c, name2)
		result.add(name2.split(" ")[0])
	except:
		a=1
		#print("None")

#for item in result:
#	print(item)