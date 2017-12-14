#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import json
from datetime import datetime, timedelta
import csv
import unicodecsv
import codecs
import requests
from urlparse import urlparse
import pprint

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError as EsNotFound
from elasticsearch.exceptions import RequestError as EsRequestError
class M_Eserver():
    def __init__(self, host, port):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    def list_index(self):
        pass
    def search(self, **kv): #value not anaylzed for prefix/term/wildcard, can call 
        # curl -XPOST 'localhost:9200/_analyze?analyzer=standard' -d'I love Bears and Fish.'
        # 'text' can be used with 'analyzer':'lowercase_keyword' 
        print kv
        try:
            return self.es.search(**kv)
        except EsNotFound:
            return None
        except EsRequestError as e:
            print e
            return None

    def test(self):
        es = self.es
        es.index(index='test-index', doc_type='test', id=1, body={"name": "Luke Skywalker", 'test': 'test'})
        #es.delete(index='test-index', doc_type='test', id=1)
        es.index(index='sw', doc_type='people', id=1, body={
            "name": "Luke Skywalker",
            "height": "172",
            "mass": "77",
            "hair_color": "blond",
            "birth_year": "19BBY",
            "gender": "male",
            })
        try:
            print es.get(index='sw', doc_type='people', id=1)
            es.get(index='sw', doc_type='people', id=65)
        except EsNotFound:
            print 'not found'
        print self.search(index="sw", body={"query": {"prefix" : { "name" : "Darth Vader" }}})
        print self.search(index="sw", body={"query": {"prefix" : { "name" : "Lu" }}})

        #index: _all/empty, comma sepparated list of string
        kv = {'index':'_all', 'body':{"query": {"prefix" : { "name" : "lu" }}} }
        print self.search(**kv)
        print self.search(index="sw", body={"query": {"match_all" : {  }}})

        q = self.search(index="sw", body={"query": {"fuzzy_like_this_field" : { "name" : {"like_text": "jaba", "max_query_terms":5}}}})
        print q
    
def main(host='localhost', port=9200):
    mes = M_Eserver(host, port)
    mes.test()

if __name__ =='__main__':
    main()
