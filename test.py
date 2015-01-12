import json
import urllib2

def url_valid(x):
	try:
		urllib2.urlopen(x)
		return True
	except Exception:
		return False

def main():
	j = open('directory.json').read()
	obj = json.loads(j)
	
	for x in obj:
		url = obj[x]
		if not url_valid(url):
			print "%s is invalid" %url

if __name__ == '__main__':
	main()