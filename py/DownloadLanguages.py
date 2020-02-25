import urllib2

response = urllib2.urlopen("https://api.dbp4.org/languages?key=afcb0adb-5247-4327-832d-abeb316358f9&v=4&format=json&pretty=true")
print(response.read())