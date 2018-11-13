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
import httplib

httplib.HTTPConnection.debuglevel = 1

logger = logging.getLogger('peval.log')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/home/esadmin/log/ph.log', maxBytes=200000, backupCount=10)
logger.addHandler(handler)

logger.setLevel(logging.DEBUG)
req_log = logging.getLogger('requests.packages.urllib3')
req_log.setLevel(logging.DEBUG)
req_log.propagate = True
req_log.addHandler(handler)

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

sl = StreamToLogger(logger, logging.INFO)
sys.stdout = sl
sys.stderr = sl


def get_web_html(url):
    n = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    a = int(time.time())
    try:
        res = requests.get(url=url, verify=False, timeout=20)
        #raise Exception('except 1')
    except:
        s = ' '.join(['timeout ', '100' , 'from',  n, '--', url ])
        logger.debug(s)
	return
    p = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    b = int(time.time())
    if res.status_code == requests.codes.ok:
      s  =' '.join(['succeed', str(b-a), n, 'to', p, '--', url ]) 
    else:
      s = ' '.join(['fail',str(b-a),  n, 'to', p, '--', url ])
    logger.debug(s)

def main():
  while True:
    now = int(time.time())
    if now %3600 != 0:
       time.sleep(0.5)
       #continue
    url = "https://www.statcan.gc.ca/fra/concepts/industrie"
    get_web_html(url)
    break
    time.sleep(3)

while True:
    try:
        main()
        break
    except:
        import traceback
        s = traceback.format_exc()
        logger.debug( datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
        logger.debug(s)

