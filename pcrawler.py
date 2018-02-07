# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
from urlparse import urlparse
from HTMLParser import HTMLParser
from lxml import etree
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
import dateparser

#export PYTHONWARNINGS="ignore:Unverified HTTPS request"
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from url_filters import daily_filter, daily_archive_filter, daily_latest_filter

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
    def __init__(self, url, content, excl_htmls, incl_htmls, lang='en', last_modified=True): #to get default host url
        self.s = mparser(filter_stopindex(content), "lxml")
        #self.s = mparser(filter_stopindex(content), "html.parser")
        self.url = url
        self.last_modified = None
        self.title = None
        self.content = None
        self.last_crawled = str(int(time.time()))
        self.try_last_modified = last_modified
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
        pathp = url.rfind('/')
        if pathp < 9: self.upath = self.prefix+'/'
        else: self.upath = url[:pathp+1]

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

    def get_meta_date(self, s):
        #dt = s.find(lambda tag: tag.name.lower()=='meta', name=lambda x: x and x.lower()=='date')
	#meta name="dcterms.modifed" scheme="W3CDTF" content="2011-12-21" />
        ms = s.findAll(name='meta')
        for item in ms:
            iname = item.get('name', None)
            if not iname: continue
            iname = iname.lower()
            if iname in ['date', 'dcterms.modifed', 'dcterms.issued']:
                return item['content']
        return None

    def get_title_date(self, title):
        if not self.try_last_modified: return None
        if not title: return None
        try:
            dstr = title[title.find(',')+1:]
            sep = dstr.find('.')
            if  sep!= -1:
                dstr=dstr[:sep]
            return str(dateparser.parse(dstr.strip()).date()) + 'T00:00:01.000Z'
        except:
            return None

    def get_link_date(self, url):
        #http://www.statcan.gc.ca/daily-quotidien/990513/dq990513e-eng.htm -> 1999-05-13
        a = url.find('daily-quotidien/')
        if not a: return None
        s = url[a+len('daily-quotidien/'):]
        if s[6] != '/': return None
        s = s[:6]
        if not isdigit(s): return None
        return '19'+s[:2] +'-' + s[2:4] + '-' + s[4:]

    def get_content_date(self, content):
        #import pdb; pdb.set_trace()
	start = content.find(u"modifi\xe9 le\xa0:")
        if start <0:
            start = content.find("date de modification")
        if start <0:
            start = content.find("date modified:")
        if start>0:
            s = content[start:]
            s = s[s.find(':')+1:]
            dt =filter(lambda x: x.strip(), s.split(' '))
            if dt and len(dt[0])>=8 : return dt[0]

        def get_ldate(content, start):
            s = content[start:].split()
            if len(s) >=5:
                s = s[2:5]
                return '-'.join(s)
            return None

        start = content.find(u"modifi\xe9 le\xa0")
        if start <0:
            start = content.find(u"modifi\xe9 le")
        if start <0:
            start = content.find("last modified")
        if start <0:
            start = content.find("date published:")

        if start>0:
            dt = get_ldate(content, start)
            if dt: return dt

        start = content.find(u"publi\xe9 le :")
        if start>0:
            start += 7
            dt = get_ldate(content, start)
            if dt: return dt

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
        if not self.last_modified:
            lm = self.get_meta_date(self.s)
            if lm:
                self.last_modified = lm + 'T00:00:01.000Z'
        if not self.last_modified:
                self.last_modified = self.get_link_date(self.url)               

        dts = self.html_sections(dts, self.excl_htmls)

        if not self.incl_htmls:
            self.content = get_text(self.s, dts).strip()
        else:
            self.content = get_inc_text(self.s, self.incl_htmls).strip()
        title = self.s.find(name='title')
        self.title = title.text if title else None
        self.title = self.title.replace('\n', ' ')  if self.title else ''
        self.title = self.title.replace('\t', ' ') 
        if not self.last_modified:
            self.last_modified = self.get_title_date(self.title)
        
        hp = HTMLParser()
        self.content = hp.unescape(self.content)
        self.content = self.content.replace('\n', ' ') if self.content else ''
        self.content = self.content.replace('\t', ' ')
        self.content = self.content.replace('\r', ' ')
        if (not self.last_modified) and self.try_last_modified:
            rawContent = ' '.join(get_text(self.s, []).split())
            self.last_modified = self.get_content_date(rawContent.lower())

        self.links = []
        for link in self.s.find_all('a', href=True):
            url = link['href'].strip()
            if not url: continue
            if url[0] == '#': continue
            if url[:7].lower() == 'mailto:': continue
            if url[:3] == '../': continue
            if url[:4] != 'http':
                if url[0]=='/':
                    url = self.prefix  + url.strip()
                else:
                    url = self.upath + url.strip()
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
        res = [self.url, hp.unescape(self.title), self.content,
                self.last_modified, 
                self.format, self.language, self.last_crawled, self.encoding]
        return [ item.replace('\t', ' ').replace('\r', ' ').replace('\d', ' ') if item else '' for item in res]

    def debug(self):
        print '\n'.join(self.export())

link_filters = {
    "daily_archive_filter": daily_archive_filter,
    "daily_filter": daily_filter,
    "daily_latest_filter": daily_latest_filter,
}
class Crawler():
    def __init__(self, data):
        self.start_links = data['start_links']
        self.depth = data['depth'] if data['depth'] != -1 else 1000000
        self.lang = data['lang']
        self.excl_htmls = data.get('exclude_html_sections', None)
        self.incl_htmls = data.get('include_html_sections', None)
        self.incls = data['include_patterns']
        self.excls = data.get('exclude_patterns', [])
        self.follow_only = data.get('follow_link_not_index', [])
        self.csv_file = data['output_file']
        self.default_last_modified = data.get('default_last_modified', None)
        self.try_last_modified = data.get('try_last_modified', True)
        self.link_filter_func = link_filters.get(data.get('link_filter_function', None), None)
        if not self.try_last_modified: #no field in html
            if not self.default_last_modified:
                self.default_last_modified = datetime.now().isoformat()+'Z'
        self.handled_urls = {}

        self.ims = dict( (p,re.compile(p, re.I)) for p in self.incls)
        self.ems = dict((p,re.compile(p, re.I)) for p in self.excls)

        skip_index_urls = [ '_dot_file', '-dot-', 'dotpage', 'Dot_', 'DOT']
        self.skip_index_patterns = [re.compile(p, re.I) for p in skip_index_urls]
        for p in self.follow_only:
            self.skip_index_patterns.append(re.compile(p, re.I))
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

    def get_xml_sitemap(self, url, urls, urls_modified):
        #c = get_web_html(None, url)
        #root = etree.parse(filename).getroot()
        #root = etree.fromstring(c.decode('utf-8')).getroot()
        root = etree.parse(url).getroot()
        for element in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            link = None
            for l in element.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                    urls[l.text] = 0
                    link = l.text
            for l in element.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"):
                    urls_modified[link] = l.text
        return urls

    def get_start_links(self, urls, urls_modified):
        for url in self.start_links:
            if url[-4:] == '.xml':
                self.get_xml_sitemap(url, urls, urls_modified)
            else:
                urls[url] = 0
        return urls

    def process(self):
        urls = {}
        urls_last_modified = {}
        failed_urls = []
        error_urls = []
        urls = self.get_start_links(urls, urls_last_modified)
        if self.link_filter_func:
            urls = self.link_filter_func(urls)
        import pdb; pdb.set_trace()
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
            doc = Doc(url, c, self.excl_htmls, self.incl_htmls, self.lang, self.try_last_modified)
            doc.process()
            lastmod = urls_last_modified.get(url, None)
            if lastmod:
                doc.last_modified = lastmod # priority
            if not doc.last_modified:
                if self.default_last_modified:
                     doc.last_modified = self.default_last_modified
                else:
                    print "error last modified"
                    error_urls.append(url)
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
        print "error parsing urls:", error_urls

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
            print '"'+short_name+'"'
            if not data.get('enabled', True):
                continue
            #if short_name[:10] != 'statcan_en': continue
            #if short_name[:8] != 'phone_en': continue

            if short_name.strip() != 'ndm_daily_archive_en': continue
            #if short_name.strip() != 'daily_archive_en': continue
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
    url = 'http://www.statcan.gc.ca/daily-quotidien/020423/dq020423a-eng.htm'
    url = 'http://www.statcan.gc.ca/daily-quotidien/990830/dq990830c-eng.htm'
    url = 'http://www.statcan.gc.ca/daily-quotidien/990830/dq990830c-fra.htm'
    url = 'http://www44.statcan.ca/2015/02/s0500-eng.htm'

    url = 'http://www44.statcan.ca/2003/12/s0101_1_f.htm' # date modified
    url = 'http://www44.statcan.ca/2003/12/s0101_1_e.htm'
    url = 'http://www44.statcan.ca/2003/06/s0400_e.htm'
    url = 'http://www44.statcan.ca/2006/09/s0700_f.htm'
    url = 'http://www44.statcan.ca/2000/11/s0700_f.htm'
    url = 'http://www44.statcan.ca/2007/07/s0101b_e.htm'
    url = 'http://www44.statcan.ca/2002/11/0201_e.htm'
    if len(sys.argv) >=2:
         f = open(sys.argv[1])
         c = f.read()
    else:
        c = get_web_html(None, url).encode('utf-8')
    #print (c)
    c = filter_stopindex(c)
    #doc = Doc(url, c, ['header', 'footer'], [{'h1': { "id": "wb-cont", "class": "page-header" }}] )
    doc = Doc(url, c, ['header', 'footer'], None )
    doc.process()
    
    print doc.get_meta_date(doc.s)
    print doc.get_title_date(doc.title)
    print doc.last_modified
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
