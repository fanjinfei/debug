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
            content_en = v[0]
            content_fr =v[1]
            short_names_en = v[2]
            short_names_fr = v[3]
            details = v[4]
            language = ''
            filetype = ''
            encoding = 'utf-8'
            last_modified = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            sformat = filetype
            last_crawled = str(int(time.time()))
            res = [url, content_en, content_fr, short_names_en, short_names_fr, details, last_modified, 
                sformat, language, last_crawled, encoding]
            d = [ item.replace('\t', ' ').replace('\r', ' ').replace('\d', ' ') if item else '' for item in res]
            d = [ item.replace('\n', ' ') if item else '' for item in d]
            data.append(d)
        write_csv(fn, data)

    def get_all(self):
        urls = {}
        for f in self.files:
            fn = self.path+f
            abstract, rs = self.get_xml_sitemap(fn)
            urls[f] = [ abstract['en'], abstract['fr'] ]
            des_en = []
            des_fr = []            
            for k, v in rs.iteritems():
                des_en.append(v[1].get('en', ''))
                des_fr.append(v[1].get('en', ''))
            urls[f].append( ' '.join(des_en))
            urls[f].append( ' '.join(des_fr))
            urls[f].append(json.dumps(rs))
        print len(urls)
        self.urls = urls
        return urls
            
    def get_xml_sitemap(self, fn):
        parser = etree.XMLParser(recover=True)
        root = etree.parse(fn).getroot()
        ns = "{http://www.isotc211.org/2005/gmd}"
        gco = "{http://www.isotc211.org/2005/gco}"
        urls = {}
        abstract = {}
        for item in root.iter(ns+"abstract"): #abstract
           for le in item.iter(gco+"CharacterString"):
               abstract['en'] = le.text
           for lf in item.iter(ns+"LocalisedCharacterString"):
               abstract['fr'] = lf.text
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
            urls[link] = [[x.replace(':', ' ') for x in protocol][0], name_text, lang]
            #print link, protocol
            #print '          ', name_text, descr
        return abstract, urls

def main():
    files = ['fgp_json_ex.xml', 'fgp_metadata1.xml',  'xml_basemap.xml',  'xml_metadata_get2.xml',  'xml_metadata_get.xml']
    
    fgp = Fgp(sys.argv[1], files)
    fgp.get_all()
    fgp.save(sys.argv[2])
    
if __name__ =='__main__':
    main()
    
    
'''
ID	AWF2pYv_CgIS7QsQ3ZGM
Name	daily
Handler Name	CsvDataStore
Parameter	directories=/raw_data/daily
    fileEncoding=UTF-8
    separatorCharacter=\t

'''
