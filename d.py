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

csv.field_size_limit(sys.maxsize)

def read_csv(filename):
    content=[]
    with open(filename) as f:
        f.read(3)
        reader = csv.reader(f, delimiter='\t')
        for x in reader:
            if x:
                content.append(x)
    return content

def read_json():
    url = 'http://f7wcmstestb2.statcan.ca:9601/json/?q=*+lang%3Aen&start={0}&num=100&sort='
    res = []
    for i in range(0, 6):
        r = requests.get(url.format(i*100))
        r = json.loads(r.text)
        r = r['response'].get('result', None)
        if not r: break
        for item in r:
           res.append(item)
    return res
def main():
    data = read_csv(sys.argv[1])
    print 'total', len(data)
    src = {}
    for line in data:
       for cell in line:
          if len(cell) > 40960: print 'data', len(cell), line[0]
          src[line[0]] = 1
    ss = {}
    res = read_json()
    for line in res:
        ss[line['url']] = 1
    print len(src), len(ss)

    for url, v in src.items():
        if url not in ss:
            print 'not indexed', url
   

main()
