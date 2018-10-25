import sys
import multiprocessing
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
handler = RotatingFileHandler('/home/esadmin/peval.log', maxBytes=200000, backupCount=10)
logger.addHandler(handler)


def get_web_html(url):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    a = int(time.time())
    res = requests.get(url=url, verify=False, timeout=100)  
    p = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    b = int(time.time())
    if res.status_code == requests.codes.ok:
      s  =' '.join(['succeed', str(b-a), n, 'to', p, '--', url ]) 
    else:
      s = ' '.join(['fail',str(b-a),  n, 'to', p, '--', url ])
    logger.debug(s)

while True:
    now = int(time.time())
    if now %3600 != 0:
       time.sleep(0.5)
       continue
    url = "https://www150.statcan.gc.ca/n1/en/dsbbcan"
    get_web_html(url)
    url = "https://www150.statcan.gc.ca/n1/en/media01"
    get_web_html(url)
    time.sleep(30)


