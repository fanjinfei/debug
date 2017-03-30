#!/usr/bin/env python3
import lmdb
from random import shuffle
import sys


def copy(file1, file2):
    env = lmdb.open(file1, readonly=True);
    lst_data = [];
    with env.begin() as txn:
        cursor = txn.cursor();
        for key, value in cursor:
            innerlst_data = [key,value]
            lst_data.append(innerlst_data)

    shuffle(lst_data);

    env1 = lmdb.open(file2, map_size=100*1024*1024*1024);
    with env1.begin(write=True) as txn1:
        for k, v in lst_data:
            txn1.put(k,v)
    
    
copy('/tmp/od_linkcheker.db', '/tmp/od_linkcheker2.db')
sys.exit(0)

env = lmdb.open('/tmp/tlmdb.db', map_size=100*1024)
with env.begin(write=True) as txn:
    txn.put('hello'.encode('utf-8'), b'1234')

with env.begin() as txn:
    print (txn.get('hello'.encode('utf-8')).decode('utf-8'))
    print (txn.get('ahello'.encode('utf-8')))

with env.begin(write=True) as txn:
    txn.put('hello'.encode('utf-8'), b'1234asdf')

with env.begin() as txn:
    print (txn.get('hello'.encode('utf-8')).decode('utf-8'))
    print (txn.get('ahello'.encode('utf-8')))

for i in range(0, 10000):
    with env.begin(write=True) as txn:
        txn.put('hello'.encode('utf-8'), b'1234asdf')
    with env.begin() as txn:
        txn.get('hello'.encode('utf-8')).decode('utf-8')
    if i %100 == 0:
        print("iter {0}".format(i))

print('Done')
