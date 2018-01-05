from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
import sys
import re
import requests
import logging
import yaml

import csv
import unicodecsv
import codecs
import traceback

import time
from datetime import datetime


#import eventlet
#eventlet.monkey_patch()

#with eventlet.Timeout(10):
#    requests.get("http://ipv4.download.thinkbroadband.com/1GB.zip", verify=False)

'''
import httplib
def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial
    return inner

httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)
'''

def get_web_html(url):
    '''url = '{0}/solr/{1}_shard1_replica1/select?q=_lw_data_source_s%3A{2}&rows=1&wt=json'.format(self.solr_url, collection, datasource)
        resp = requests.get(url=url)
        data = json.loads(resp.text)'''
    user_agent = {'User-agent': 'statcan dev crawler; abuse report'}
    proxies = {'http': 'http://u:p@ip:port/',
               'https': 'http://u:p@ip:port/'}
#    with eventlet.Timeout(10):
#    res = requests.get(url=url, headers=user_agent, proxies=proxies, timeout=10)
    res = requests.get(url=url, timeout=10)
    return res.text

def write_csv(filename, rows, header=None):
    outf=open(filename, 'wb')
    outf.write(codecs.BOM_UTF8)
    writer = unicodecsv.writer(outf, delimiter='\t')

    if header:
        writer.writerow(header)
    for row in rows:
        writer.writerow(row)

def filter_stopindex(content):
    stop = '<!--stopindex-->'
    start = '<!--startindex-->'
    tokens = [stop, start]
    state = 0 #keep, 1:skip
    pos = 0
    res = [ ]
    def find_next( ):
        if state == 0: return (content.find(stop, pos), 1)
        return (content.find(start, pos), 0)
    while True:
        npos, nstate = find_next()
        if npos >= 0:
            if state == 0:
                res.append(content[pos:npos])
            pos, state = npos, nstate
        else:
            if pos == 0: return content
            if state == 0:
                res.append(content[pos:])
            break
    return ''.join(res)


def tag_visible(element, dts):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    if element.parent in dts:
        return False
#       import pdb; pdb.set_trace()
    return True

def get_text(m, dts):
    texts = m.findAll(text=True)
    #visible_texts = filter(tag_visible, texts)  
    visible_texts =[]
    for ele in texts:
        if tag_visible(ele, dts):
            visible_texts.append(ele)
    return u" ".join(t.strip() for t in visible_texts)

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def link_filter(url):
    m = re.compile('^http://www\.statcan\.gc\.ca/eng/survey/.*', re.I)
    return True if m.match(url) else False

def links(s):
    for link in s.find_all('a', href=True):
        url = link['href']
        if url[:4] != 'http': url = 'http://www.statcan.gc.ca' + url
        if link_filter(url):
            print url

class Doc():
    def __init__(self, url, content, lang='en'): #to get default host url
        self.s = mparser(filter_stopindex(content), "lxml")
        self.url = url
        self.last_modified = None
        self.title = None
        self.content = None
        self.last_crawled = str(int(time.time()))
        self.author = None
        self.format = 'html' #filetype
        self.language = lang #fr
        self.content_length = 0
        self.encoding = 'utf-8'

    def process(self):
	dt = self.s.find(id="wb-dtmd")
        dts = []
        if dt: #last_modified":"2017-11-27T18:29:13.000Z", this is UTC, will display it -5 for US/Canada east
            self.last_modified = dt.find(name='time').text[:10] + 'T00:00:01.000Z'
            dts = dt.findChildren() 
        for p in self.s.find(name='div',
                             attrs={'class':'pane-bean-report-problem-button'}).findChildren():
            dts.append(p)

#        self.content = get_text(self.s, dts).strip().replace(',', ' ')
#        self.title = self.s.find(name='title').text.replace(',', ' ')
        self.content = get_text(self.s, dts).strip()
        self.title = self.s.find(name='title').text

        self.links = []
        for link in self.s.find_all('a', href=True):
            url = link['href']
            if url[:4] != 'http': url = 'http://www.statcan.gc.ca' + url.strip()
            self.links.append(url.strip())

    def link(self):
        return self.links

    def header(self):
        return['url', 'title', 'content', 'lastmodified', 'format', 'lang', 'timestamp', 'encoding']

    def export(self):
        return [self.url, self.title, self.content, self.last_modified, 
                self.format, self.language, self.last_crawled, self.encoding]

    def debug(self):
        print '\n'.join(self.export())

class Crawler():
    def __init__(self, data):
        self.start_links = data['start_links']
        self.depth = data['depth']
        self.lang = data['lang']
        self.incls = data['include_patterns']
        self.excls = data['exclude_patterns']
        self.csv_file = data['output_file']
        self.handled_urls = {}

        self.ims = [re.compile(p, re.I) for p in self.incls]
        self.ems = [re.compile(p, re.I) for p in self.excls]

    def link_filter(self, url):
        for m in self.ems:
            if m.match(url): return False
        for m in self.ims:
            if m.match(url): return True
        return False
        
    def process(self):
        urls = {}
        failed_urls = []
        for url in self.start_links:
            urls[url] = 0
        data = []
        while urls:
            for url,depth in urls.iteritems():
                break
            self.handled_urls[url] = True
            urls.pop(url)

            print url, len(urls), len(self.handled_urls)
#            if depth == self.depth: continue

            count = 5
            while count > 0:
                try:
                    c = get_web_html(url)
                    break
                except Exception:
                    c = None
                    count = count - 1
                    print "error:", url
                    print (traceback.format_exc())
                    time.sleep(5)
            if not c:
                failed_urls.append(url)
                continue
            c = filter_stopindex(c)
            doc = Doc(url, c, self.lang)
            doc.process()
            links = doc.link()
            data.append(doc.export())

            time.sleep(2)

            if depth == self.depth: continue
            for link in links:
                if link in self.handled_urls: continue
                if link in urls: continue
                if self.link_filter(link):
                    urls[link] = depth + 1

        write_csv(self.csv_file, data)
        print "failed urls:", failed_urls

def read_config(filename):
    with open(filename) as f:
    # use safe_load instead load
        return yaml.safe_load(f)

def main():
    logging.basicConfig(format='%(asctime)s %(message)s',
                         filename='/tmp/myapp.log', level=logging.DEBUG) #INFO

    confs = read_config(sys.argv[1])
    for conf in confs:
        for short_name, data in conf.iteritems():
            craw = Crawler(data)
            craw.process()

    return
    
def test():
    url = 'http://www.statcan.gc.ca/fra/enquete/entreprise/5220'
    c = get_web_html(url)
    c = filter_stopindex(c)
    doc = Doc(url, c)
    doc.process()
    doc.debug()

    data = []
    #data.append(doc.header())
    data.append(doc.export())
    write_csv('/tmp/isp.csv', data)
    logging.info('doc last modified: '+ doc.last_modified)
    return

main()

'''
directories=/opt/es/demo/raw_data/module_isp
fileEncoding=UTF-8
separatorCharacter=\t

url=cell1
title=cell2
content=cell3
cache=cell3
digest=cell3
anchor=
content_length=cell3.length()
last_modified=cell4
timestamp=cell4
filetype=cell5
lang=cell6
'''
