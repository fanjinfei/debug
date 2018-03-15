#!/usr/bin/env python

import json
import os, sys
from lxml import etree
import csv
import unicodecsv
import codecs

import requests
import time
from collections import defaultdict
'''
curl -o portal_datasets.out --request POST 'http://solr.host/core_staging_portal/select/' 
  --data 'q=dataset_type%3Adataset&version=2.2&start=0&rows=118000&indent=on&fl=id'
'''
csv.field_size_limit(sys.maxsize)
def write_csv(filename, rows, header=None):
    outf=open(filename, 'wb')
    outf.write(codecs.BOM_UTF8)
    writer = unicodecsv.writer(outf, delimiter='\t')

    if header:
        writer.writerow(header)
    for row in rows:
        writer.writerow(row)

def read_csv(filename):
    content=[]
    with open(filename) as f:
        f.read(3)
        reader = csv.reader(f, delimiter='\t')
        for x in reader:
            if x:
                content.append(x)
    return content

def daily_archive_filter(urls, latest, current):
    res = {}
    for link, d in urls.items():
        link = link.replace('.ca/daily', '.ca/n1/daily')
        i = link.find('?rid=')
        if i > 0:
            link = link[:i]
        if link and link not in latest and link not in current:
            #if link.find('dq000225b-eng.htm') > 0:
            #    import pdb; pdb.set_trace()
                
            res[link] = 0
    return res

def proc(url):
        url = url.replace('.ca/daily', '.ca/n1/daily')
        if url.find('/n1/daily') < 0: return None, None # vs '/daily-q..'
        i = url.find('?rid=')
        if i < 0: return None, None
        url, rid = url[:i], url[i+5:]
        return url, rid

def daily_filter(urls, latest):
    res = {}
    for url, _ in urls.items():
        link, _ = proc(url)
        if link and link not in latest:
            ds = int(url.split('/')[5])
            if ds < 150616: continue
            res[link] = 0
    return res

def daily_latest_filter(urls):
    rids = defaultdict(list)
    for url, _ in urls.items():
        link, rid = proc(url)
        if link:
            rids[rid].append(link)
    res = {}
    for rid, links in rids.items():
        links.sort()
        url = links[0]
        res[url] = 0
    return res


link_filters = {"a": daily_archive_filter}


def read_xml(filename):
    root = etree.parse(filename).getroot()
    urls = {}
    for element in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        link = None
        for l in element.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            link = l.text
        for l in element.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"):
            urls[link] = l.text
    return urls

def modify_date(filename):
    rs = read_csv(filename)
    for r in rs:
        r[3] = r[3] + 'T00:00:01.000Z'
    write_csv(filename, rs)

#modify_date(sys.argv[1])
#sys.exit(0)
def list2a(la):
    data = []
    for l in la:
        data.append([l])
    return data

urls = read_xml(sys.argv[1])
print 'total', len(urls)

latest = daily_latest_filter(urls)
print 'latest', len(latest)

current = daily_filter(urls, latest)
print 'current', len(current)

archived = daily_archive_filter(urls, latest, current)
print 'archived', len(archived)


write_csv('/tmp/aa.csv', list2a(archived))
write_csv('/tmp/ac.csv', list2a(current))
write_csv('/tmp/al.csv', list2a(latest))
