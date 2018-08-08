from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
from urlparse import urlparse
from HTMLParser import HTMLParser
from PyPDF2 import PdfFileReader
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

def download_file(url):
    local_filename = '/tmp/tmpparser.pdf'
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

def getPdfContent(url):
    try:
        filename = download_file(url)
        with open(filename, 'rb') as f:
            reader = PdfFileReader(f)
            number_of_pages = reader.getNumPages()
            contents = []
            for page in range(0,number_of_pages):
                cs = reader.getPage(page).extractText().split('\n')
                for c in cs:
                    contents.append(c.strip())
            return ' '.join(contents)
    except:
        return ''

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



def putPdfLink(b, lan): #set pdfurl
#   value['attr_strpdflink'] =  b
    if not b: return ''
    linkval = b
    if 'n1' in linkval or 'alternative' in linkval: 
         return  b

    disppdfurl = "http://www.statcan.gc.ca/access_acces/alternative_alternatif.action?lang={0}&loc=" + linkval 
    return disppdfurl.format('eng' if 'en' in lan else 'fra') 


def putUrlPdfLink( b, lan): #set pdf to url
    linkval = b
    if 'n1' in linkval or 'alternative' in linkval: 
         return b
    disppdfurl = "http://www.statcan.gc.ca/access_acces/alternative_alternatif.action?lang={0}&loc=" + linkval 
    return disppdfurl.format('eng' if 'en' in lan else 'fra')

# map {ori_url, optional(pdf_link, html_link), calculated_olc_link} ==> url, pdf_link, olc_link
#
def filter_olc(value, lan='en'):

    if value.get('releasedate')[:10] not in [ '2018-08-03', '2018-08-02'] :
        return False

    if value.get('discontinued'): return False

    if value.get('producttypecode') == '10':
       return False

    if '/imdb/' in value.get('url'):
       return False

    title = value.get('title')
    if not title:
        return False

    # filtering out the daily records; 
    display_pid = value.get('display_pid', '')
    if re.search("11-001-X[0-9]", display_pid):
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

    orig_url_str = value.get('url', '').lstrip()
    if len(orig_url_str) >= 8:
        value['attr_strurl'] = orig_url_str

    if value.get('description'):
        desc = value.get('description', '')
        desc = re.sub(r'&nbsp;', r' ', desc)
        desc = re.sub(r'\s+', r' ', desc)
        desc = re.sub(r'<.{1,9}>', r'', desc)
        desc = desc.strip()

        if len(desc) > 200:
            desc = desc + ' '
            desc = re.sub(r"(^.{200}[^\s,.\n?]*)(.*$)", r"\1 ...", desc)

        value['attr_flddesc'] = desc
        value['attr_txtdesc'] = desc

    # 26 with issues, filter out, 2018-01-16 discuss with Kay and Michele in Kay's office
    if value.get('producttypecode'):
        pkeys = value.get('producttypecode').keys()
        if '26' in value.get('producttypecode').keys():
            if value.get('documenttype') == 'issue':
                # make an exception for the issue of SDDS
                if value.get('productid') == '13-608-X2017001':
                    pass
                else:
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

    if value.get('conttype'):
     if not value.get('conttype').keys():
       cont2val =  value.get('conttype')
     else :
       cont2val =  value.get('conttype').values()
       cont2key =  value.get('conttype').keys()
       value['conttypeval_ss'] =  cont2val 
       value['attr_fldconttypeval'] =  cont2val 
       value['conttypekey_ss'] =  cont2key 
       ## Kay in the meeting, contenttype should be searchable, and null records delete, except conf service;    
    else :
       if not 'confer' in value.get('documenttype') and not 'service' in value.get('documenttype'):
          return False

    orig_title = value.get('title')
    pdf_title = orig_title + " (PDF)"
    if value.get('productid'):
        orig_title = value.get('title') + " (" + value.get('productid') + ")"
        if isTable == "1":
            cansimval = value.get('display_pid', value.get('productid'))
            if cansimval:
                orig_title = value.get('title') + " (" + cansimval + ")"
        value['attr_fldtitle'] = orig_title
        value['attr_txttitle'] = orig_title
        strtitle = orig_title.strip()
        strtitle = re.sub(r'(")', r'', strtitle)
        strtitle = re.sub(r'(&laquo;)', r'', strtitle)
        strtitle = strtitle.lstrip()
        value['attr_strtitle'] = strtitle

    origdate = value.get('releasedate')
    if origdate:
        value['date'] = origdate
        stripdate = re.sub(r'(.{10,12})(T.*)', r'\1', origdate)
        value['attr_strdate'] = stripdate
        value['release_date_s'] = stripdate

    if value.get('productid'):
        value['productid_s'] = value.get('productid')

    if value.get('frc'):
        value['attr_fldfrc'] = value.get('frc')

    if value.get('producttypecode'):
        value['producttypecode_s'] = value.get('producttypecode')
    if value.get('documenttype'):
        value['documenttype_s'] = value.get('documenttype')
    if isTable == "1":
        value['ds'] = "tableview"
        # inject the words for searches to match
        value['attr_txtmeta'] =  "table tables tableau tableaux"
    if value.get('producttypecode'):
        if '27' in value.get('producttypecode').keys():
            value['ds'] = "summaryview"

    if value.get('subject'):
        value['attr_fldsubject'] = [x for x in value.get('subject').values()]

    if value.get('subject_codes_desc'):
        value['attr_fldsubjectcodesdesc'] = [x for x in value.get('subject_codes_desc').values()]

    if value.get('subject_levels'):
        value['attr_fldsubjectlevels'] = [x for x in value.get('subject_levels').values()]
        value['subjectlevels_ss'] = [x for x in value.get('subject_levels').values()]

    if value.get('keywords_terms'):
        value['keywords'] = [x for x in value.get('keywords_terms')]

    if 'variable' in value:
        value['attr_txtvariable'] = value.get('variable')
        del value['variable']
    if value.get('cansim'):
        value['cansim_s'] = value.get('cansim')
        # inject the word cansim
        value['attr_fldcansim'] =  "cansim; " + value.get('cansim')
        tmpcansim = value.get('cansim')
        value['attr_fldaltercansim'] = tmpcansim
        if re.search('-', tmpcansim):
            tmpcansim = re.sub(r'-', r'', tmpcansim)
            value['attr_fldaltercansim'] = tmpcansim
        value['attr_strcansim'] = value.get('cansim')
        value['cansim'] = ""
    if value.get('geoname'):
        geo_names = [x for x in value.get('geoname').values()]
        if geo_names[0]:
            value['geoname_s'] = geo_names[0]
            value['attr_fldgeoname'] = geo_names[0]

    # fields added for the client admin verification purposes, jira 1000
    if value.get('geoname'):
        value['attr_fldgeonameval'] = [x for x in value.get('geoname').values()]
        value['attr_fldgeonamekey'] = [x for x in value.get('geoname').keys()]

    if value.get('subject'):
        value['attr_fldsubjectval'] = [x for x in value.get('subject').values()]
        value['attr_fldsubjectkey'] = [x for x in value.get('subject').keys()]

    if value.get('archived'):
        value['archivedval_ss'] = [x for x in value.get('archived').values()]
        value['archivedkey_ss'] = [x for x in value.get('archived').keys()]

    if value.get('discontinued_formats'):
        value['discontinued_formatsval_ss'] = [x for x in value.get('discontinued_formats').values()]
        value['discontinued_formatskey_ss'] = [x for x in value.get('discontinued_formats').keys()]

    domain = "https://www150.statcan.gc.ca/n1/" + lan + "/catalogue/"
    #pdfdomain = "https://stc-ndm-prod-pc.statcan.gc.ca/n1/" + lan 
    pdfdomain = "https://www150.statcan.gc.ca/n1/" + lan 

    olc_link = ""
    if value.get('productid'):
        if isTable == "1":
            value['ds'] = "tableview"
            value['attr_strolclink'] = ""
            olc_link = ""
        else:
            value['attr_strolclink'] = domain + value.get('productid')
            value['ds'] = "olc"
            olc_link = domain + value.get('productid')
        pid = value.get('productid')
    else:
        pid = ""
        value['ds'] = "nolc"
        value['attr_strolclink'] = ""
        return False

    origurl = value.get('url').strip()
    value['ori_url'] = origurl
    if value.get('other_urls'):
        pdf_link = value.get('other_urls', {}).get('8', '')
        html_link = value.get('other_urls', {}).get('17', '')
        '''
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
'''
        if html_link:
            if html_link in orig_url_str or html_link in olc_link:
                html_link = ""

        if pdf_link:
            value['attr_strpdflink'] = putPdfLink(pdf_link, lan)

        if "/catalo" in orig_url_str:
            if pdf_link and html_link:
                value['url'] = html_link
                value['attr_strurl'] = html_link
                value['attr_txturl'] = html_link
                value['attr_strpdflink'] = putPdfLink(pdf_link, lan)

            elif html_link and not pdf_link:
                value['url'] = html_link
                value['attr_strurl'] = html_link
                value['attr_txturl'] = html_link

            elif pdf_link and not html_link:
                value['url'] = pdf_link
                value['attr_strurl'] = putUrlPdfLink(pdf_link, lan)
                value['attr_txturl'] = pdf_link

                value['attr_strpdf_link'] = ""
                value['attr_fldtitle'] = pdf_title
                value['attr_txttitle'] = pdf_title
        else:
            if pdf_link and html_link:
                value['url'] = html_link
                value['attr_strpdflink'] = putPdfLink(pdf_link, lan)
            elif pdf_link:
                value['attr_strpdflink'] = putPdfLink(pdf_link, lan)


    if "/catalo" in value.get('url') and "/catalo" in olc_link:
       value['attr_strolclink'] =  ""

    if value.get('url') in olc_link:
       value['attr_strolclink'] =  ""

    if '.pdf' in value.get('url'):
        value['attr_strpdf_link'] = ""
        value['attr_fldtitle'] = pdf_title
        value['attr_txttitle'] = pdf_title

    if value.get('id'):
        value['ndmid_s'] = value.get('id')
        # value['id'] = value.get('url')
        value['id'] = 'olc' + value.get('productid')
       
    return True

def olcData(val):
    data = {
        'url': val['attr_strurl'],
        'title': val['attr_fldtitle'],
        'desc': val['attr_flddesc'],
        'pdfurl': val.get('attr_strpdflink', ''),
        'olcurl': val.get('attr_strolclink', ''),
        'pdf_content':'',
        'last_modified': val.get('releasedate', ''),
        }
    if '.pdf' in data['url']:
        slink = data['url']
    elif '.pdf' in data['pdfurl']:
        slink = data['pdfurl']
    else:
        slink = ''
    if slink:
        data['pdf_content'] = getPdfContent(slink)
    return data
    
solr_pdf_url = {
    'en': 'http://f7searchprodz1.stcpaz.statcan.gc.ca:10219/solr/ndmpdfEN/',
    'fr':  'http://f7searchprodz1.stcpaz.statcan.gc.ca:10219/solr/ndmpdfFR/',
    }
def get_solr_pdf_links(lang):
    pdf_ids = []
    _solr_response = requests.get(
        solr_pdf_url[lang] + 'select?q=*&rows=3000000&fl=id,url&wt=json', proxies=proxies)
    for solr_doc in _solr_response.json()['response']['docs']:
        if solr_doc.get('id'):
            if 'ndmpdf' in solr_doc.get('id'):
                b = solr_doc.get('id')
                b = re.sub(r"^.*ndmpdf[^/]*/", "", b)
                pdf_ids.append(b.strip())
    return set(pdf_ids)

def get_pdf_content(lang):
    _pdf_content = {}
    _solr_response = requests.get(
        solr_pdf_url[lang] + 'select?q=*:*&rows=3000000&fl=id,content&wt=json',
        proxies=proxies)
    for solr_doc in _solr_response.json()['response']['docs']:
        if solr_doc.get('id'):
            url = re.sub(r'^.*ndmpdf[^/]*/', '', solr_doc.get('id'))
            _pdf_content[url] = solr_doc.get('content')
    return _pdf_content

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
            #if not filter_olc(item):
            #    pass #continue
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

link_filters = {
}

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

    def get_start_links(self, urls, urls_modified):
        total, res = read_json_url(self.start_links[0])
        for item in res:
            if not filter_olc(item): #do some filtering here
                continue
            url = item.get('attr_strurl', None) #the main key
            if not url:
                #print json.dumps(i, indent=4)
                sys.exit(-1)
            d = olcData(item)
          
            urls[url] = d
            #last_modified = item['releasedate']
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
        for k, d in urls.iteritems():
            url = k
            pdf_url = d['pdfurl']
            olc_url = d['olcurl']
            title = d['title']
            content = d['desc']
            pdf_content = d['pdf_content']

            language = self.lang
            filetype = 'html'
            encoding = 'utf-8'
            last_modified = d['last_modified'] or datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            sformat = filetype
            last_crawled = str(int(time.time()))
            res = [url, title, content, last_modified, 
                sformat, language, last_crawled, encoding, 'md5sum', pdf_content, pdf_url, olc_url]
            d = [ item.replace('\t', ' ').replace('\r', ' ').replace('\d', ' ') if item else '' for item in res]
            data.append(d)
        write_csv(self.csv_file, data)
        print "total OLCs:", len(data)

def read_config(filename):
    with open(filename) as f:
    # use safe_load instead load
        return yaml.safe_load(f)

def main():
    confs = read_config(sys.argv[1])
    if len(sys.argv) >2:
        for conf in confs:
            data = conf.get(sys.argv[2], None)
            if not data: 
                continue
            craw = OLC_Crawler(data)
            craw.process()
            return
        return

def test():
    if sys.argv[1]=='download':
#        url = 'https://www150.statcan.gc.ca/n1/en/metadata.json?producttypecode=11,20,25,26,27,28&count={count}&type=products&offset={offset}&releasedate={release_date}'
        url = 'https://www150.statcan.gc.ca/n1/en/metadata.json?producttypecode=11,20,25,26,27,28&count={count}&type=products&offset={offset}&releasedate=2018-08-02'
#full_url = "https://www150.statcan.gc.ca/n1/{lan}/metadata.json?producttypecode=11,20,25,26,27,28&count={count}&offset={offset}&releasedate={release_date}"    new release only
        t, r = read_json_url(url)
        for i in r:
            print json.dumps(i)
        return

    #handle downloaded files
    src, dst = [], set()
    dedup = {}
    dup = {}
    r = read_jsonl(sys.argv[1]) #above download file
    for i in r:
        if not filter_olc(i): #do some filtering here
            continue
        url = i.get('attr_strurl', None) #the main key
        if not url:
            print json.dumps(i, indent=4)
            sys.exit(0)
        if dedup.get(url, None):
            #print i
            #print dedup[url]
            #print '\n'
            dup[url] = True
            dedup[url].append(i)
        else:
            dedup[url] = [i]
            src.append(i)
    for i in src:
        d = olcData(i)
        print 'url', d['url']
        print 'tile', d['title']
        print 'desc', d['desc']
        
        # additional fields more than web page
        #attr_body : get from pdf parsing
        print 'pdf', d['pdfurl']
        print 'olc', d['olcurl']
        print 'content', d['pdf_content']
        print '*******************************'
    sys.exit(0)

    #ds:olc && release_date_dt:[2018-08-03T00:00:00Z TO 2018-08-04T00:00:00Z]
    #fl=release_date_dt, url, attr_strurl, ds, attr_str*, attr_body, attr_flddesc, attr_fldtitle
    #sort - release_date_dt desc
    #http://f7searchprodz1.stcpaz.statcan.gc.ca:7773/solr/src01EN_shard1_replica1/select?q=ds%3Aolc&rows=12000&fl=id+attr_strurl&wt=json&indent=true
    
    #OR http://f7searchprodz1.stcpaz.statcan.gc.ca:7773/solr/src01EN_shard1_replica1/select?q=ds%3Aolc+%26%26+release_date_dt%3A%5B2018-08-02T00%3A00%3A00Z+TO+2018-08-03T00%3A00%3A00Z%5D&sort=release_date_dt+desc&rows=50&fl=release_date_dt%2C+url%2C+attr_strurl%2C+ds%2C+attr_str*%2C+attr_body%2C+attr_flddesc%2C+attr_fldtitle&wt=json&indent=true&facet=true&facet.field=ds
    olc = read_jsonfile(sys.argv[2]) #from solr
    olc = olc['response']['docs']
    for i in olc:
        dst.add(i['attr_strurl'])

    print len(r), len(olc)
    diffs = list( src.difference(dst))
    diffs.sort()
    for url in diffs:
        pass #print url.encode('utf-8')

    print '###################'
    diffs2 = list( dst.difference(src))
    diffs2.sort()
    for url in diffs2:
        print url.encode('utf-8')

    print len(diffs), len(diffs2)
    print len(src), len(dst)

    print '********************'
    dl= dup.keys()
    dl.sort()
    for l in dl:
        print l, len(dedup[l])
    sys.exit(0)

if __name__ =='__main__':
    main()
    #test()

