#!/usr/bin/python2

import sys
import json
import urllib2
import threading
import Queue
import glob
import os
import jsonschema

hdr = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'application/json,text/javascript,application/jsonrequest;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive' }

ff_api_specs = {} 

def read_url(url, queue):
    req = urllib2.Request(url, headers=hdr)
    try:
        res = urllib2.urlopen(req, None, 10)
        api_content = {}
        api_content = json.loads(res.read())
        if 'jsondraft' in ff_api_specs[api_content['api']]:
            json_draft = ff_api_specs[api_content['api']]['jsondraft']
        else:
            json_draft = 'http://json-schema.org/draft-03/schema#'
        jsonschema.Draft3Validator.check_schema(ff_api_specs[api_content['api']]['schema'])
        v = jsonschema.Draft3Validator(ff_api_specs[api_content['api']]['schema'])
        result = v.iter_errors(api_content)
        has_error = False
        text_result = ''
        for error in sorted(result,key=str):
            if not has_error:
                text_result = 'ValidationError in community file %s:\n' % (api_content['name'])
            has_error = True
            text_result = '%s\t Error in %s: %s\n' % (text_result, '->'.join(str(path) for path in error.path), error.message)

        if has_error:
            text_result = '%s\t Url: %s' %(text_result, url)
            print(text_result)
            queue.put(url)

    except urllib2.HTTPError as e:
        print('HTTPError: %s: %s' % (e.code, url))
        queue.put(url)
    except urllib2.URLError as e:
        print('URLError: %s: %s' % (e.reason, url))
        queue.put(url)
    except ValueError as e:
        print('Value error while paring JSON: %s' % (url))
        queue.put(url)
    except KeyError as e:
        print('Invalid or unknown API version %s: %s' % (api_content['api'], url))
        queue.put(url)
#    else:
#        print 'OK %s: %s' % (api_content['api'], url)

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
    spec_dir = './api.fossasia.net/specs/*.json'
    spec_files = glob.glob(spec_dir)
    for spec_file in spec_files:
        spec_content = open(spec_file).read()
        ff_api_specs[os.path.splitext(os.path.basename(spec_file))[0]] = json.loads(spec_content)

    urls_to_load = []
    invalid_urls = []

    for x in obj:
        urls_to_load.append(obj[x])

    result = fetch_parallel(urls_to_load)

    if result.empty():
        print('Result: All URLs are valid :-)')
        sys.exit(0)
    else:
        print('\nResult: Invalid URLs found :-(')
        sys.exit(1)

if __name__ == '__main__':
    main()
