#!/usr/bin/env python

import sys
import shlex, gzip
from collections import defaultdict
from datetime import datetime, timedelta

'''
    weblog_parser.py [ <2017-12-12T03> | <2017-12-12T03:4>]  log_file1 log_file2 ...
   /software/soopt3/fus211/var/log/connectors/connectors-20.log.gz
'''
level = len('2017-12-12T03:43:11,541 - ')
class WebLog():
    def __init__(self):
        self.start = False
        self.ignore = False
    def reset(self):
        self.start = False
        self.ignore = False
    def read_line(self, line, start_date):
        if not self.start:
            if line[:len(start_date)] == start_date:
                self.start = True
        if not self.start:
            return
        if line.find('scheduled-task-pool-3:SolrMetricLoggingComponent') > 0:
           self.ignore = True
        elif line.find('scheduled-task-pool-0:SolrMetricLoggingComponent') > 0:
           self.ignore = True
        elif line[level:level+4] == 'INFO' and line.find('failure') <0:
            self.ignore = True
            return
        elif line[:len(start_date)] == start_date:
            self.ignore = False

        if self.ignore == True: return
        print line

def main():
    log = WebLog()
    start_date = sys.argv[1]
    for fname in sys.argv[2:]:
        log.reset()
        if fname[-3:] == '.gz':
            f = gzip.open(fname)
        else:
            f = open(fname, 'rb')
        for line in f:
            log.read_line(line.decode('utf-8'), start_date)
    
main()
