#!/usr/bin/env python3

import argparse
import os
import time
import sys
import logging
import tempfile
import gzip
import json
from collections import defaultdict

import lmdb

import requests
import asyncio
from functools import partial
from requests.models import Response
import urllib
from urllib.request import urlopen
import traceback
import unicodecsv
import codecs

proxy= os.environ['http_proxy']


def test_ftp(url):
    res = Response()
    try:
        req = urllib.request.Request(url)
        if proxy:
            req.set_proxy(proxy, 'http')
        response = urlopen(req, timeout=30)
        chunk = response.read(16)
        if len(chunk) == 16:
            res.status_code = 200
        else:
            res.status_code = 404
    except:
        res.status_code = 404
    print(url, res.status_code)
    return res

USER_AGENT="open.canada.ca dataset link checker; abuse report open-ouvert@tbs-sct.gc.ca"


def get_a_byte(response, *args, **kwargs):
    if response.status_code == requests.codes.ok:
        count = 0
        for line in response.iter_content():
            count += (len(line))
            if count > 0:
                print(response.url, count)
                response.close()
                break


@asyncio.coroutine
def test_urls(urls, results):
    loop = asyncio.get_event_loop()
    futures =[]
    for url in urls:
        if url[:6].lower() =='ftp://':
            future = loop.run_in_executor(None, test_ftp,url)
        else:
            future = loop.run_in_executor(None, partial(requests.get, headers={"user-agent":USER_AGENT},
                                          hooks={'response': get_a_byte}, verify=False,
                                          timeout=30, stream=True), url)
        futures.append(future)
    for future in futures:
        try:
            res = yield from future
        except requests.exceptions.ReadTimeout:
            print('timeout', urls[ futures.index(future)])
            res = Exception()
        except (requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL):
            print('invalidURL', urls[ futures.index(future)])
            res = Response()
            res.status_code = 404
        except:
            import traceback
            traceback.print_exc()
            res = Exception()
        results.append(res)


class Records():
    def __init__(self, file, verbose):
        self.file = file
        self.download_file = None
        self.verbose = verbose
        mapsize = 100 * 1024 * 1024 * 1024
        self.env = lmdb.open('/tmp/od_linkcheker2.db', map_size=mapsize, sync=False)
        #self.txn = self.env.begin(write=True)

        #p_records = site.action.current_package_list_with_resources( offset=start, limit=rows)
    def __delete__(self):
        self.env.close()
        if not self.file:
            if self.download_file:
                os.unlink(self.download_file)
                print('temp file deleted', self.download_file)

    def download(self):
        if not self.file:
            # dataset http://open.canada.ca/data/en/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7
            url='http://open.canada.ca/static/od-do-canada.jl.gz'
            r = requests.get(url, stream=True)

            f = tempfile.NamedTemporaryFile(delete=False)
            for chunk in r.iter_content(1024 * 64):
                    f.write(chunk)
            f.close()
            self.download_file = f.name

        records = []
        fname = self.file or f.name
        try:
            with gzip.open(fname, 'rb') as fd:
                for line in fd:
                    records.append(json.loads(line.decode('utf-8')))
                    if len(records) >= 50:
                        yield (records)
                        records = []
            if len(records) >0:
                yield (records)
        except GeneratorExit:
            pass
        except:
            import traceback
            traceback.print_exc()
            print('error reading downloaded file')

    def test_links(self, new_url, urls):
        links = []
        results = []
        for k,v in new_url.items():
            links.append(k)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_urls(links, results))
        with self.env.begin(write=True) as txn:
            now = time.time()
            results = zip(links, results)
            for url, response in results:
                if type(response) is Exception:
                    res={'timestamp': now,
                         'status': -1,
                         'resources': new_url[url]}
                else:
                    res={'timestamp': now,
                         'status':response.status_code}
                    if response.status_code != requests.codes.ok:
                        res['resources'] = new_url[url]
                        res['org'] = urls.get(url, None)
                txn.put(url.encode('utf-8'), json.dumps(res).encode('utf-8'))
        if links:
            time.sleep(5)  # break

    def get_resources(self):
        count = 0
        new_url = defaultdict(list)
        urls = {}
        for records in self.download():
            now = time.time()
            count += len(records)
            with self.env.begin() as txn:
                for record in records:
                    id = record['id']
                    for res in record['resources']:
                        if (not res['url_type']) and res.get('url'):
                            #print(res)
                            url= res['url']
                            details =txn.get(url.encode('utf-8'))
                            if details:
                                details = json.loads(details.decode('utf-8'))
                                #if now - details.get('timestamp', 0) < 34 * 3600 and (details['status']!= -1):
                                #if details['status'] == requests.codes.ok:
                                if details['status'] != -1 or url[:7]!='http://':
                                    continue
                            new_url[url].append('/'.join([id, res['id']]))
                            if record.get('organization'):
                                urls[url]={'name': record['organization']['name'],
                                           'title': record['organization']['title']}
            if len(new_url) >=500:
                self.test_links(new_url, urls)
                new_url = defaultdict(list)
                urls = {}
        if new_url:
            self.test_links(new_url, urls)
        print ('total record count: ', count)

    def dumpBrokenLink(self):
        outf=open('/tmp/brokenlink.csv', 'wb')
        outf.write(codecs.BOM_UTF8)
        out = unicodecsv.writer(outf)
        out.writerow(['organization name', 'status', 'link', 'dataset_id/resource_id'])
        data = defaultdict(list)
        with self.env.begin() as txn:
            for url, value in txn.cursor():
                details = json.loads(value.decode('utf-8'))
                if details['status'] != requests.codes.ok:
                    #print(url.decode('utf-8'), details)
                    org_name = details['org']['name'] if details.get('org') else 'unknown_org'
                    data[org_name].append([url, details['resources'], details['status']])
        count, count2 = 0, 0
        for name, urls in data.items():
            for url, res, status in urls:
                status_str = status if status!= -1 else 'timeout'
                out.writerow([name,  status_str, url.decode('utf-8'), json.dumps(res)])
                count += 1
                if status ==-1:
                    count2 += 1
        outf.close()
        print(self.env.info())
        print(self.env.stat())
        print('total {0} dumped, timeout_count {1}'.format(count, count2))

    def searchUrl(self, url):
        with self.env.begin() as txn:
            details =txn.get(url.encode('utf-8'))
            if details:
                details = json.loads(details.decode('utf-8'))
                print(details)
            else:
                print('Not found')

    def addOrg(self):
        for records in self.download():
            urls = {}
            with self.env.begin() as txn:
                for record in records:
                    for res in record['resources']:
                        if (not res['url_type']) and res.get('url'):
                            url= res['url']
                            try:
                                details =txn.get(url.encode('utf-8'))
                            except:
                                traceback.print_exc()
                                sys.exit(-1)
                            if details:
                                details = json.loads(details.decode('utf-8'))
                                if (not details.get('org')) and record.get('organization'):
                                    try:
                                        details['org']={'name': record['organization']['name'],
                                                        'title': record['organization']['title']}
                                        urls[url] = details
                                    except:
                                        pass
            with self.env.begin(write=True) as txn:
                for url, details in urls.items():
                    txn.put(url.encode('utf-8'), json.dumps(details).encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description='Search portal records broken resource link')
    parser.add_argument("--file", dest="file", help="site file")
    parser.add_argument("--quiet", dest="verbose",default=True)
    parser.add_argument("--dump", dest="dump",action='store_true',default=False)
    parser.add_argument("--search", dest="search")
    parser.add_argument("--org", dest="org", action='store_true',default=False)

    options = parser.parse_args()

    user_agent = None

    site = Records(options.file, options.verbose)
    if options.dump:
        site.dumpBrokenLink()
        return
    elif options.search:
        site.searchUrl(options.search)
        return
    elif options.org:
        site.addOrg()
        return
    site.get_resources()


if __name__ == '__main__':
    main()
    sys.exit(0)
