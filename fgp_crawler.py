from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
from urlparse import urlparse
from HTMLParser import HTMLParser
from lxml import etree

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

class Fgp():
    def __init__(self, path, files):
        self.path = path
        self.files = files

    def save(self, fn):
        data = []
        for k, v in self.urls.iteritems():
            url = k
            title = v[1]
            content = ''
            language = v[2]
            filetype = v[0][0]
            encoding = 'utf-8'
            last_modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            sformat = filetype
            last_crawled = str(int(time.time()))
            res = [url, title, content, last_modified, 
                sformat, language, last_crawled, encoding]
            d = [ item.replace('\t', ' ').replace('\r', ' ').replace('\d', ' ') if item else '' for item in res]
            data.append(d)
        write_csv(fn, data)

    def get_all(self):
        urls = {}
        for f in self.files:
            fn = self.path+f
            rs = self.get_xml_sitemap(fn)
            #urls.update(rs) #FIXME: merge values['SERVICE']
            for k, v in rs.iteritems():
                ev = urls.get(k, None)
                if not ev:
                    urls[k] = v
                else:
                    for service in v[0]:
                        if service not in ev[0]:
                            ev[0].append(service)
            print '---', len(rs)
            print '**********************************'
        print len(urls)

#        for l,v in urls.keys():
        for l,v in urls.iteritems():
            pass #print l
            print l,v
        self.urls = urls
        return urls
            
    def get_xml_sitemap(self, fn):
        parser = etree.XMLParser(recover=True)
        root = etree.parse(fn).getroot()
        ns = "{http://www.isotc211.org/2005/gmd}"
        gco = "{http://www.isotc211.org/2005/gco}"
        urls = {}
        for element in root.iter(ns+"CI_OnlineResource"):
            link, protocol, name_text = None, [], {}
            descr = {}
            lang = ''
            for l in element.iter(ns+"URL"): #URL
                    link = l.text

            for pt in element.iter(ns+"protocol"): #multiple service for url
                    for c in pt.iter(gco+"CharacterString"):
                        prot =  c.text
                        if prot:
                            protocol.append(prot)

#                    prot = pt.find(gco+"CharacterString")
#                    if prot is not None: 
#                        protocol =  prot.text
            if not protocol: continue
            name = element.find(ns+"name") #display name
            if name is not None:
                name_c = name.find(gco+"CharacterString")
                if name_c is not None:
                    name_text['en'] = name_c.text
                for name_c in name.iter(ns+"LocalisedCharacterString"):
                    name_text['fr'] = name_c.text

            name = element.find(ns+"description") #determine lang:eng/fra
            if name is not None:
                name_c = name.find(gco+"CharacterString")
                if name_c is not None:
                    descr['en'] = name_c.text
                for name_c in name.iter(ns+"LocalisedCharacterString"):
                    descr['fr'] = name_c.text
                    #print link
                    #print '\t', name_c.text.encode('utf-8')
                if descr['en'].find(';eng') > 0: lang='en'
                elif descr['en'].find(';fra') > 0: lang='fr'
            if lang in ['en', 'fr']:
               title = name_text[lang]
            elif name_text.get('en', None):
                title = name_text['en'] +' '+ name_text['fr']
            else:
                title = ''
            if not title:
                print 'NO TITLE:', link, name_text, descr
                continue
            urls[link] = [[x.replace(':', ' ') for x in protocol], title, lang]
            #print link, protocol
            #print '          ', name_text, descr
        return urls

def main():
    files = ['fgp_json_ex.xml',  'fgp_metadata1.xml',  'xml_basemap.xml',  'xml_metadata_get2.xml',  'xml_metadata_get.xml']
    
    fgp = Fgp(sys.argv[1], files)
    fgp.get_all()
    fgp.save(sys.argv[2])
    
if __name__ =='__main__':
    main()
    
    
'''
ID	AWF2pYv_CgIS7QsQ3ZGM
Name	daily
Handler Name	CsvDataStore
Parameter	directories=/data/jffan/ecn/raw_data/daily
    fileEncoding=UTF-8
    separatorCharacter=\t
Script	url=cell1
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
Boost	1.0
Permissions	{role}guest
Virtual Hosts	
Label	daily
Status	Enabled
Description

Username	jffan
Last Name	Fan
First Name	Jinfei
E-Mail	jinfei.fan@canada.ca
Roles	admin
admin-api
'''
