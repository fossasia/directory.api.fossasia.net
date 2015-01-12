import sys
import json
import urllib2

def url_valid(x):
	try:
		urllib2.urlopen(x)
		return True
	except Exception:
		return False

def main():
	j = open('./directory.json').read()
	obj = json.loads(j)
	invalid_urls = []
	for x in obj:
		url = obj[x]
		if not url_valid(url):
			invalid_urls.append(url)

	if len(invalid_urls) > 0:
		print '\n'.join(invalid_urls) + " are invalid urls"
		sys.exit(1)
	else:
		sys.exit(0)

if __name__ == '__main__':
	main()