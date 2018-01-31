from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
from urlparse import urlparse
from HTMLParser import HTMLParser
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

#export PYTHONWARNINGS="ignore:Unverified HTTPS request"
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_web_html(s, url):
    user_agent = {'User-agent': 'statcan dev crawler; abuse report jinfei.fan@canada.ca'}
    if not s:
        res = requests.get(url=url, headers=user_agent, verify=False, timeout=10)
    else:
        res = s.get(url=url, headers=user_agent, verify=False, timeout=10)
    if res.status_code == requests.codes.ok:
        rtext = []
        if res.encoding is None:
            res.encoding = 'utf-8'
        #for line in res.iter_lines(decode_unicode=True):
        for line in res.iter_lines():
            # filter out keep-alive new lines
            if line:
                decoded_line = line.decode('utf-8', errors='ignore')
                rtext.append(decoded_line)
        return u'\n'.join(rtext)
    else:
        return None

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

def get_inc_text(m, dts):
    visible_texts =[]
    for section in dts:
        for name, attrs in section.items():
            break
        info = m.find(name=name, attrs=attrs)
        if not info: continue
        texts = info.findAll(text=True)
        for ele in texts:
            visible_texts.append(ele)
    return u" ".join(t.strip() for t in visible_texts)

class Doc():
    def __init__(self, url, content, excl_htmls, incl_htmls, lang='en'): #to get default host url
        #self.s = mparser(filter_stopindex(content), "lxml")
        self.s = mparser(filter_stopindex(content), "html.parser")
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
        self.excl_htmls = excl_htmls
        self.incl_htmls = incl_htmls
        self.prefix = urlparse(url).hostname
        if url[:5] == 'https':
            self.prefix = 'https://' + self.prefix
        else:
            self.prefix = 'http://' + self.prefix

    def html_item(self, nodes, name, attrs, all=True):
        info = self.s.find(name=name, attrs=attrs)
        if info:
            nodes.append(info)
            if all:
                for p in info.findChildren():
                    nodes.append(p)
       
    def html_sections(self, nodes, sections, exclude = True):
        if exclude:
            self.html_item(nodes, 'div', {'class':'pane-bean-report-problem-button'})
            self.html_item(nodes, 'a', {'href':'https://www.canada.ca/en/report-problem.html'}, False)
            self.html_item(nodes, 'a', {'href':'#wb-cont'}, False)
            self.html_item(nodes, 'a', {'href':'#wb-info'}, False)

        for section in sections or []:
            node = self.s.find(name=section)
            if node:
               for child in node.findChildren():
                   nodes.append(child)
        return nodes

    def verify_date(self, s): #some hack
        try:
            r = s.replace('*', '0').replace(' ', '-')
            datetime.strptime(r, "%Y-%m-%dT%H:%M:%S.%fZ")
            return r
        except:
            return None

    def process(self):
	dt = self.s.find(id="wb-dtmd")
        if not dt:
            dt = self.s.find(id="gcwu-date-mod")

        dts = []
        if dt: #last_modified":"2017-11-27T18:29:13.000Z", this is UTC, will display it -5 for US/Canada east
            dtext = dt.find(name='time').text.strip()
            self.last_modified = dt.find(name='time').text.strip()[:10] + 'T00:00:01.000Z'
            self.last_modified = self.verify_date(self.last_modified)
            if not self.last_modified:
                try:
                    y,m,d = [ int(i) for i in dtext.split('-')[:3]]
                    self.last_modified = "{0}-{1:02d}-{2:02d}".format(y,m,d) + 'T00:00:01.000Z'
                except:
                    print 'error last modified', self.url
                    print (traceback.format_exc())
                    self.last_modified = '2015-12-17T00:00:01.000Z'
            dts = dt.findChildren()

        dts = self.html_sections(dts, self.excl_htmls)

        if not self.incl_htmls:
            self.content = get_text(self.s, dts).strip()
        else:
            self.content = get_inc_text(self.s, self.incl_htmls).strip()
        title = self.s.find(name='title')
        self.title = title.text if title else None
        self.title = self.title.replace('\n', ' ') 
        self.title = self.title.replace('\t', ' ') 
        self.content = self.content.replace('\n', ' ')
        self.content = self.content.replace('\t', ' ')
        self.content = self.content.replace('\r', ' ')

        self.links = []
        for link in self.s.find_all('a', href=True):
            url = link['href']
            if url[0] == '#': continue
            if url[:4] != 'http': url = self.prefix  + url.strip()
            id_same = url.rfind('#')
            if id_same != -1: #chop it
                url = url[:id_same]
            self.links.append(url.strip())

    def link(self):
        return self.links

    def header(self):
        return['url', 'title', 'content', 'lastmodified', 'format', 'lang', 'timestamp', 'encoding']

    def export(self):
        hp = HTMLParser()
        res = [self.url, hp.unescape(self.title), hp.unescape(self.content),
                self.last_modified, 
                self.format, self.language, self.last_crawled, self.encoding]
        return [ item.replace('\t', ' ').replace('\r', ' ').replace('\d', ' ') for item in res]

    def debug(self):
        print '\n'.join(self.export())

class Crawler():
    def __init__(self, data):
        self.start_links = data['start_links']
        self.depth = data['depth'] if data['depth'] != -1 else 1000000
        self.lang = data['lang']
        self.excl_htmls = data.get('exclude_html_sections', None)
        self.incl_htmls = data.get('include_html_sections', None)
        self.incls = data['include_patterns']
        self.excls = data['exclude_patterns']
        self.csv_file = data['output_file']
        self.handled_urls = {}

        self.ims = dict( (p,re.compile(p, re.I)) for p in self.incls)
        self.ems = dict((p,re.compile(p, re.I)) for p in self.excls)

        skip_index_urls = [ '_dot_file', '-dot-', 'dotpage', 'Dot_', 'DOT']
        self.skip_index_patterns = [re.compile(p, re.I) for p in skip_index_urls]
        self.do_index = re.compile('Cadotte', re.I)

        self.sessions = {}

    def get_session(self, url):
        host = urlparse(url).hostname
        if not self.sessions.get(host, None):
            self.sessions[host] = requests.Session()
        return self.sessions[host]

    def link_filter(self, url):
        for p, m in self.ems.items():
            if m.match(url):
                #print 'exlcude 1:', p, url
                return False
        for p,m in self.ims.items():
            if m.search(url): return True
        #print 'exlcude 2:', url
        return False
        
    def index_filter(self, doc):
        # TODO: follow_link_not_index from yaml
        url = doc.url
        if self.do_index.search(url): return True

        for m in self.skip_index_patterns:
            if m.search(url): return False
        return True

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
                    c = get_web_html(self.get_session(url), url)
                    # todo: handle status
                    break
                except Exception:
                #ChunkedEncodingError, ReadTimeout, ConnectionError
                    c = None
                    count = count - 1
                    print (traceback.format_exc())
                    time.sleep(5)
            if not c:
                failed_urls.append(url)
                print "failed:", url
                continue
            c = filter_stopindex(c)
            doc = Doc(url, c, self.excl_htmls, self.incl_htmls, self.lang)
            doc.process()
            links = doc.link()
            if self.index_filter(doc):
                data.append(doc.export())
            print '\t\t^', doc.title
            #todo: if not content: log warning

            #time.sleep(2)

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
                         filename='/tmp/myapp.log', level=logging.INFO) #INFO, DEBUG

    confs = read_config(sys.argv[1])
    for conf in confs:
        for short_name, data in conf.iteritems():
            if not data.get('enabled', True):
                continue
            #if short_name[:7] != 'ndm_isp': continue
            #if short_name != 'ndm_navigation_en': continue
            craw = Crawler(data)
            craw.process()

    return
    
def test():
    url = 'http://www.statcan.gc.ca/fra/enquete/entreprise/5220'
    url = 'http://www.statcan.gc.ca/daily-quotidien/160603/dq160603f-eng.htm'
    url = 'https://www150.statcan.gc.ca/n1/en/subjects'
    url = 'https://icn-rci.statcan.ca/07/07f/07f1/07f1_000-eng.html'
    url = 'https://icn-rci.statcan.ca/888/888c/888c16/888c16_001-fra.html'
    url = 'https://icn-rci.statcan.ca/24/24e/24e_000-eng.html'
    c = get_web_html(None, url).encode('utf-8')
    #print (c)
    c = filter_stopindex(c)
    #doc = Doc(url, c, ['header', 'footer'], [{'h1': { "id": "wb-cont", "class": "page-header" }}] )
    doc = Doc(url, c, ['header', 'footer'], None )
    doc.process()
    #doc.debug()

    data = []
    #data.append(doc.header())
    data.append(doc.export())
    write_csv('/tmp/isp.csv', data)
    logging.info('doc last modified: '+ str(doc.last_modified))
    return

main()
#test()

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
