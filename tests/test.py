import sys
import json
import urllib2
import threading
import Queue

hdr = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'application/json,text/javascript,application/jsonrequest;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive' }

def read_url(url, queue):
    req = urllib2.Request(url, headers=hdr)
    try:
        res = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        print 'HTTPError %s: %s' % (e.code, url)
        queue.put(url)
    except URLError as e:
        print 'URLError: %s: %s' % (e.reason, url)
        queue.put(url)
    #else:
    #    print 'OK %s: %s' % (code, url)

def fetch_parallel(urls_to_load):
    result = Queue.Queue()
    threads = [threading.Thread(target=read_url, args = (url, result)) for url in urls_to_load]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result

def main():
    j = open('./directory.json').read()
    obj = json.loads(j)
    urls_to_load = []
    invalid_urls = []

    for x in obj:
        urls_to_load.append(obj[x])

    result = fetch_parallel(urls_to_load)

    if result.empty():
        print 'Result: All URLs are valid :-)'
        sys.exit(0)
    else:
        print '\nResult: Invalid URLs found :-('
        sys.exit(1)

if __name__ == '__main__':
    main()