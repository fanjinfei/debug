# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
from bs4 import NavigableString
#from urlparse import urlparse
#from HTMLParser import HTMLParser
from lxml import etree

import sys
import re
import requests

import csv
import unicodecsv
import codecs
import traceback


#export PYTHONWARNINGS="ignore:Unverified HTTPS request"
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#from crawler_base import write_csv, read_csv

def get_web_html(s, url):
    user_agent = {'User-agent': 'statcan dev crawler; abuse report search team'}
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


def get_text(m):
    texts = m.findAll(text=True)
    #visible_texts = filter(tag_visible, texts)  
    visible_texts =[]
    for ele in texts:
            visible_texts.append(ele)
    return u" ".join(t.strip() for t in visible_texts)

class Doc():
    def __init__(self, url, content ): #to get default host url
        self.ori_content = content
        self.s = mparser(content, "lxml")
        #self.s = mparser(filter_stopindex(content), "html.parser")
        self.url = url
        self.title = None
        self.content = None

#    self.html_item(nodes, 'div', {'class':'pane-bean-report-problem-button'})
    def html_item(self, nodes, name, attrs, all=True):
        info = self.s.find(name=name, attrs=attrs)
        if info:
            nodes.append(info)
            if all:
                for p in info.findChildren():
                    nodes.append(p)
       
    def get_links(self):
        self.links = []
        name, attrs = "span", {'class':"list-identifier"}
        for ele in self.s.find_all(name=name, attrs=attrs):
            if isinstance(ele, NavigableString):
                continue
#            if ele.tag=='a' and ele.title=='Abstract':
            for link in ele.find_all('a'):
                if link['title'] == 'Abstract':
                    self.links.append('https://arxiv.org'+link['href'])
                    break
        return self.links
    def process(self):

        self.content = get_text(self.s).strip()

        
        name, attrs = 'blockquote', {'class':"abstract mathjax"}
        info = self.s.find(name=name, attrs=attrs)
        res=[]
        if info:
            texts = info.findAll(text=True)
            for ele in texts[1:]:
                ele = ' '.join(ele.replace('\r', ' ').split('\n'))
                res.append(ele)
        abstract = res[0] if len(res) else ''

        name, attrs = 'h1', {'class':"title mathjax"}
        info = self.s.find(name=name, attrs=attrs)
        res = []
        if info:
            texts = info.findAll(text=True)
            for ele in texts[1:]:
                ele = ' '.join(ele.replace('\r', ' ').split('\n'))
                res.append(ele)
        title = res[0] if len(res) else ''
        #print (title + ' ' + self.url, abstract)
        return title + ' ' + self.url, abstract
def write_csv(filename, rows, header=None):
    outf=open(filename, 'wb')
    outf.write(codecs.BOM_UTF8)
    writer = unicodecsv.writer(outf, delimiter='\t')

    if header:
        writer.writerow(header)
    for row in rows:
        writer.writerow(row)


def main():
    url = 'https://arxiv.org/list/cs.CL/recent'
    c = get_web_html(None, url).encode('utf-8')
    docs = Doc(url, c)
    res = []
    for url in docs.get_links():
        c = get_web_html(None, url).encode('utf-8')
        doc = Doc(url, c)
        title, content = doc.process()
        res.append([title, content])
    write_csv('/tmp/xivg.csv', res)

if __name__ == '__main__':    
    main()


