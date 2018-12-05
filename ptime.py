import sys
import multiprocessing
import subprocess
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
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('peval.log')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/home/esadmin/peval-im.log', maxBytes=200000, backupCount=10)
logger.addHandler(handler)


urls = [ 'https://www150.statcan.gc.ca/n1/en/dsbbcan',
    'https://www150.statcan.gc.ca/n1/en/media01',
    'https://www.statcan.gc.ca/eng/concepts/definitions/guide-symbol',
    'https://www.statcan.gc.ca/eng/subjects/standard/otherclass-subject',
    'https://www.statcan.gc.ca/eng/concepts/definitions/index',
    'https://www.statcan.gc.ca/fra/concepts/industrie'
     ]

def get_web_html(url):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    a = int(time.time())
    try:
        res = requests.get(url=url, verify=False, timeout=100)
        #raise Exception('except 1')
    except:
        s = ' '.join(['timeout ', '100' , 'from',  n, '--', url ])
        logger.debug(s)
        if 'industri' in url:
            subprocess.call(["/opt/es/demo/py2venv/bin/python", "/opt/es/demo/census-ui/ph.py"])
        return
    p = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    b = int(time.time())
    if res.status_code == requests.codes.ok:
      s  =' '.join(['succeed', str(b-a), n, 'to', p, '--', url ]) 
    else:
      s = ' '.join(['fail',str(b-a),  n, 'to', p, '--', url ])
    logger.debug(s)

def main():
  global urls
  while True:
    now = int(time.time())
    if now %3600 != 0:
       time.sleep(0.5)
       continue
    for url in urls:
        get_web_html(url)
    #raise Exception('except 2')
    time.sleep(30)

while True:
    try:
        main()
    except:
        import traceback
        s = traceback.format_exc()
        logger.debug( datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
        logger.debug(s)

