from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
from urlparse import urlparse
from HTMLParser import HTMLParser
import sys
import re
import requests
import logging
import yaml, json

import csv
import unicodecsv
import codecs
import traceback

import time
from datetime import datetime

from crawler_base import write_csv, read_csv, read_jsonfile


def clean_rec2(b,lan):
    b = re.sub(r"\\\t", " ", b)
    b = re.sub(r"\\\n", " ", b)
    # b = re.sub(r"\\\"", " ", b)
    ## b = re.sub(r"\\\"", ' &quot; ', b)
    b = re.sub(r"\t", " ", b)
    b = re.sub(r"\n", " ", b)
    # b = re.sub(r"\[pubURLRoot\]", "www.statcan.gc.ca", b)
    # b = b.encode('utf-8')
    if b:
        line = b
        line = re.sub(r'<.{1,12}>', r'', line)
        line = re.sub(r'("attr_strtitle": ")\\u00ab ', r'\1', line)
        line = re.sub(r'\\\/', r'/', line)
        #line = re.sub(r"'", r'&#8217;', line)
        line = re.sub(r'\\u003C.{1,10}\\u003E', r'', line)
        line = re.sub(r'"([a-zA-Z\-\_]+)":(["\[])', r'"\1_s":\2', line)
        b = line
    #b = re.sub(r"http\:\/\/\[pubURLRoot\]", "https://[pubURLRoot]", b)
    #b = re.sub(r"https\:\/\/\[pubURLRoot\]", pdfdomain, b)
    # repdomain = "https://stc-ndm-prod-pc.statcan.gc.ca/n1/" + lan
    repdomain = "https://www150.statcan.gc.ca/n1/" + lan
    b = re.sub(r"http\:\/\/\[pubURLRoot\]", "https://[pubURLRoot]", b)
    b = re.sub(r"https\:\/\/\[pubURLRoot\]", repdomain, b)

    # repdomain = "https://stc-ndm-prod-pc.statcan.gc.ca/n1/" + lan
    repdomain = "https://www150.statcan.gc.ca/n1/" + lan
    b = re.sub(r"http\:\/\/\[navURLSummaryRoot\]", "https://[navURLSummaryRoot]", b)
    b = re.sub(r"https\:\/\/\[navURLRsummaryRoot\]", repdomain, b)

    # repdomain = "https://stc-ndm-prod-pc.statcan.gc.ca/n1/" + lan
    repdomain = "https://www150.statcan.gc.ca/n1/" + lan
    b = re.sub(r"http\:\/\/\[dailyURLRoot\]", "https://[dailyURLRoot]", b)
    b = re.sub(r"https\:\/\/\[dailyURLRoot\]", repdomain, b)

    # repdomain = "https://stc-ndm-prod-pc.statcan.gc.ca/t1/" + lan
    repdomain = "https://www150.statcan.gc.ca/t1/" + lan
    b = re.sub(r"http\:\/\/\[tableviewURLRoot\]", "https://[tableviewURLRoot]", b)
    b = re.sub(r"https\:\/\/\[tableviewURLRoot\]", repdomain, b)

    #repdomain = "https://stc-ndm-prod-pc.statcan.gc.ca/t1/" + lan + "/catalogue/"
    repdomain = "https://www150.statcan.gc.ca/t1/" + lan + "/catalogue/"
    b = re.sub(r"http\:\/\/\[catalogueURLRoot_EN\]", "https://[catalogueURLRoot_EN]", b)
    b = re.sub(r"https\:\/\/\[catalogueURLRoot_EN\]", repdomain, b)
    b = re.sub(r"http\:\/\/\[catalogueURLRoot_FR\]", "https://[catalogueURLRoot_FR]", b)
    b = re.sub(r"https\:\/\/\[catalogueURLRoot_FR\]", repdomain, b)

    return b

def clean_rec(b):
    b = re.sub(r"\\\t", " ", b)
    b = re.sub(r"\\\n", " ", b)
    return b



def putpdflink(b, lan): #set pdfurl
#   value['attr_strpdflink'] =  b
    if not b: return ''
    linkval = b
    if 'n1' in linkval or 'alternative' in linkval: 
         return  b

    disppdfurl = "http://www.statcan.gc.ca/access_acces/alternative_alternatif.action?lang={0}&loc=" + linkval 
    return disppdfurl.format('eng' if 'en' in lan else 'fra') 


def puturlpdflink(value, b, lan): #set pdf to url
    if not b: return 1
    linkval = b

    value['url'] =  b
    if 'n1' in linkval or 'alternative' in linkval: 
         value['attr_strurl'] =  b
         return 1
    else : 
        disppdfurl = "http://www.statcan.gc.ca/access_acces/alternative_alternatif.action?lang={0}&loc=" + linkval 
        value['attr_strurl'] =  disppdfurl.format('eng' if 'en' in lan else 'fra')
        #fixed by me:
        value['url'] =  value['attr_strurl']
        return 0

def filter_olc(value, lan='en'): 
    if value.get('discontinued'): return False

    if value.get('producttypecode') == '10':
       return False

    if '/imdb/' in value.get('url'):
       return False

    if not value.get('title'):
       return False

    # filtering out the daily records; 
    display_pid = value.get('display_pid', '')
    if re.search("11-001-X[0-9]", display_pid):
        return False

    title = value.get('title')
    if not title:
        return False

    if not value.get('archived'):
       value['stclac'] =  "1;2"
    elif '2' in value.get('archived').keys():
       value['stclac'] =  "1;2"
    elif '3' in value.get('archived').keys():
       value['stclac'] =  "1;3"
    elif '4' in value.get('archived').keys():
       return False
    elif value.get('archived'):
       value['stclac'] =  "1;3"

    orighiopid = ""
    if value.get('hierarchy'):
       orighiopid = value.get('hierarchy')
    if value.get('producttypecode'):
       if '26' in value.get('producttypecode').keys() :
          if value.get('documenttype') == 'issue':
              if not value.get('productid') == orighiopid : 
              #if not value.get('productid') in orighiopid : 
                 return False


    isTable = ""
    if value.get('producttypecode'):
       value['producttypecodeval_ss'] =  value.get('producttypecode').values()
       value['producttypecodekey_ss'] =  value.get('producttypecode').keys()
       if '11' in value['producttypecodekey_ss']:
           isTable = "1" #ds:tableview
           return False
       elif '27' in value['producttypecodekey_ss']:
           isSummary = True #ds:summary   --- not found yet
           #print 'ds:summaryview', value.get('url')
           return False
       if '10' in value['producttypecodekey_ss']:
           return False

    domain = "https://www150.statcan.gc.ca/n1/" + lan + "/catalogue/"
    #pdfdomain = "https://stc-ndm-prod-pc.statcan.gc.ca/n1/" + lan 
    pdfdomain = "https://www150.statcan.gc.ca/n1/" + lan 

    #domain = "https://stc-ndm-qa-pc.statcan.gc.ca/n1/en/catalogue/"
    olclink = ""
    pid = ""
    if value.get('productid'):
       value['attr_strolclink'] =  domain + value.get('productid')
       # if tablevstr in value.get('url') or 'Tables' in value.get('conttype'):
       # if 'Tables' in value.get('conttype'):
       if isTable == "1" :
          value['ds'] =  "tableview"
          value['attr_strolclink'] =  ""
          olclink = ""
       else:
          value['ds'] =  "olc"
          olclink = domain + value.get('productid')
       pid = value.get('productid')
    else:
       value['ds'] =  "nolc"
       value['attr_strolclink'] =  ""
       return False

    pdflink = ""
    origurl = value.get('url').strip()
    value['ori_url'] = origurl
    if value.get('other_urls'):
        #urls =  value.get('other_urls')
        #if 'stageb' in machine:
        urls =  value.get('other_urls').values()

        pdflink =  ""
        htmlink =  ""
        if urls[0] :
           if ".pdf" in urls[0] :
               pdflink = urls[0]
           else:
               htmlink = urls[0]

        if len(urls)>1 and urls[1] :
            if ".pdf" in urls[1] :
               pdflink = urls[1]
            else:
               htmlink = urls[1]

        if len(urls)>2 and urls[2] :
            if ".pdf" in urls[2] :
               pdflink = urls[2]
            else:
               htmlink = urls[2]


        if htmlink and htmlink in origurl :
           htmlink = ""

        if htmlink and htmlink in olclink :
           htmlink = ""

        if pdflink :
           value['attr_strpdflink'] = putpdflink(pdflink, lan)
           #value['attr_strpdflink'] =  pdflink
           if pdflink :
	       tmppdflink = pdflink


        if "/catalo" in origurl :
		if pdflink and htmlink :
                   value['url'] =  htmlink
	           value['attr_strurl'] =  htmlink
	           value['attr_txturl'] =  htmlink

                   value['attr_strpdflink'] =  putpdflink(pdflink, lan)
                   #value['attr_strpdflink'] =  pdflink
		elif htmlink and not pdflink :
                   value['url'] =  htmlink
	           value['attr_strurl'] =  htmlink
	           value['attr_txturl'] =  htmlink

		elif pdflink and not htmlink :
                   donothing = puturlpdflink(value, pdflink, lan)
                   #value['url'] =  pdflink
	           #value['attr_strurl'] =  pdflink
	           value['attr_txturl'] =  pdflink

                   value['attr_strpdflink'] =  ""
        else:
		if pdflink and htmlink :
                   value['url'] =  htmlink
                   value['attr_strpdflink'] = putpdflink(pdflink, lan)
		elif pdflink :
                   value['attr_strpdflink'] = putpdflink(pdflink, lan)


    if "/catalo" in value.get('url') and "/catalo" in olclink:
       value['attr_strolclink'] =  ""

    if value.get('url') in olclink:
       value['attr_strolclink'] =  ""

    if '.pdf' in value.get('url'):
       value['attr_strpdflink'] =  ""
       value['attr_strpdflink'] =  ""
       
    return True

def read_json_url(url):
#    url = 'https://www150.statcan.gc.ca/n1/en/metadata.json?count={count}&type=products&offset={offset}'
    res = []
    total = 0
    for i in range(0, 1000):
        r = requests.get(url.format(count=500, offset=i*500))
        r = json.loads(r.text)
        if total == 0:
            total = r.get('found', 0)
        r = r.get('result', None)
        if not r: break
        for item in r:
            if item.get('variable'): # not used
                item.pop('variable')
            if not filter_olc(item):
                pass #continue
            res.append(item)
    return total, res

def read_jsonl(url):
    res = []
    with open(url) as f:
        for line in f:
            try:
              r = json.loads(line.rstrip())
            except:
              import pdb; pdb.set_trace()
            res.append(r)
    return res


class OLC_Crawler():
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

    def get_start_links(self, urls, urls_modified):
        total, res = read_json(self.start_links[0])
        for item in res:
            url = item['url'] #three link, but we will only use one
            other_urls = item.get('other_urls', {})
            pdf_url = other_urls.get('8')
            olc_url = other_url.get('17') # the same as url ??? (CAT link)
            if cat_url and item.get('productid', ''): # display_pid
                cat_url = 'https://www150.statcan.gc.ca/n1/en/catalogue' + item.get('productid', '')
            short_description = item['description']
            doc_type = item['documenttype']
            archived = item['archived'] #{"2":"current"} is a dict
            title = item['title']
            subject = item['subject']
            last_modified = item['releasedate']
            '''
{u'author': [u'Brule, Shawn'], u'hierarchy': u'82-625-X2017001', u'subject_levels': {u'13': u'Health', u'1306': u'Health/Lifestyle and social conditions', u'130699': u'Health/Lifestyle and social conditions/Other content related to Lifestyle and social conditions'}, u'author_initials': [u'B'], u'id': u'52fb31cd7676cf32', u'featureweight': u'0', u'producttypecode': {u'28': u'Grow Pub publications (pubs with issues & articles)'}, u'subject': {u'130699': u'Health/Lifestyle and social conditions/Other content related to Lifestyle and social conditions'}, u'frc': u'82300', u'archived': {u'2': u'Current'}, u'title': u'Life Satisfaction, 2016', u'other_urls': {u'8': u'https://www150.statcan.gc.ca/n1/pub/82-625-x/2017001/article/54862-eng.pdf', u'17': u'https://www150.statcan.gc.ca/n1/pub/82-625-x/2017001/article/54862-eng.htm'}, u'display_pid': u'82-625-X201700154862', u'conttype': {u'2016': u'Analysis/Stats in brief'}, u'source': [u'Canadian Community Health Survey - Annual Component'], u'score': 1.5014778, u'documenttype': u'article', u'description': u'<p>This is a Health fact sheet about life satisfaction among Canadians. Life satisfaction is a personal subjective assessment of global well-being. The results shown are based on data from the Canadian Community Health Survey.</p>', u'pubyear': u'2017', u'sourcecode': [u'3226'], u'article_id': u'54862', u'productid': u'82-625-X201700154862', u'archive_date': u'2020-01-11T05:00:00Z', u'url': u'https://www150.statcan.gc.ca/n1/pub/82-625-x/2017001/article/54862-eng.htm', u'issueno': u'2017001', u'releasedate': u'2017-09-27T04:00:00Z'}
'''
        return urls

    def process(self):
        urls = {}
        urls_last_modified = {}
        failed_urls = []
        error_urls = []
        urls = self.get_start_links(urls, urls_last_modified)
        if self.link_filter_func:
            urls = self.link_filter_func(urls)
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

def main():
    pass

def test():
    if sys.argv[1]=='download':
        url = 'https://www150.statcan.gc.ca/n1/en/metadata.json?count={count}&type=products&offset={offset}'
        t, r = read_json_url(url)
        for i in r:
            print json.dumps(i)
        return

    #handle downloaded files
    src, dst = set(), set()
    dedup = {}
    dup = {}
    r = read_jsonl(sys.argv[1]) #above download file
    for i in r:
        if not filter_olc(item): #do some filtering here
            pass #continue
        url = i['url']
        if dedup.get(url, None):
            #print i
            #print dedup[url]
            #print '\n'
            dup[url] = True
            dedup[url].append(i)
        else:
            dedup[url] = [i]
        src.add(i['url'])
    for i in r[:3]:
        continue
    #print json.dumps(i)

    #http://f7searchprodz1.stcpaz.statcan.gc.ca:7773/solr/src01EN_shard1_replica1/select?q=ds%3Aolc&rows=12000&fl=id+attr_strurl&wt=json&indent=true
    olc = read_jsonfile(sys.argv[2]) #from solr
    olc = olc['response']['docs']
    for i in olc:
        dst.add(i['attr_strurl'])

    print len(r), len(olc)
    diffs = list( src.difference(dst))
    diffs.sort()
    for url in diffs:
        print url

    print '###################'
    diffs2 = list( dst.difference(src))
    diffs2.sort()
    for url in diffs2:
        print url

    print len(diffs), len(diffs2)
    print len(src), len(dst)

    print '********************'
    dl= dup.keys()
    dl.sort()
    for l in dl:
        print l, len(dedup[l])
    sys.exit(0)

if __name__ =='__main__':
    #main()
    test()

