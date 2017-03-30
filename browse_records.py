#!/usr/bin/env python

import ckanapi
import ckan
from ckanapi.errors import CKANAPIError, NotFound
import argparse
import os
import sys
import logging

class Records():
    def __init__(self, portal_site, reg_site, verbose):
        self.portal_site = portal_site
        self.reg_site = reg_site
        self.verbose = verbose

    def get_records(self, site, q):
        # get records from solr
        # if there are indexing errors, the records are not synced 
        #   with postgres database.
        count =0
        start = 0
        rows = 500
        pids = []
        while True:
            # a list with a hard upper limit 1000, need to loop 
            p_records = site.action.package_search(q=q, fl=['id', 'extras_digital_object_identifier'], 
                    use_default_schema=True, start=start, rows=rows)
            if count == 0:
                count =  p_records['count']
            for v in p_records['results']:
                #pids.append(v['id'])
                if v.get('digital_object_identifier'):
                    pids.append(v)
                #pids.append(v)
            start += len( p_records['results'] )
            if start >= count:
                break
        return count, pids

    def removeRecords(self, site, ids):
        for id in ids:
            try:
                site.action.package_delete(id=id)
            except ckan.logic.NotAuthorized as e:
                raise Exception('API key error')
            except:
                print ( id, 'delete failed')
            else:
                print ( id, 'deleted')
    def update_record(self, site, id):
        return
        try:
            data_dict = site.action.package_show(id=id)
            assert( "'en': u''" in data_dict['digital_object_identifier'] or "'fr': u''" in data_dict['digital_object_identifier'] )
            data_dict.pop('digital_object_identifier')
            site.action.package_update(**data_dict)
        except ckan.logic.NotAuthorized as e:
            raise Exception('API key error')
        except NotFound:
            print ( id, 'not here', site.address)
        except:
            print ( id, 'update failed')
        else:
            print ( id, 'updated')
        
    def filter_records(self):
        q = "collection:{0:s}".format('fgp')
        #q = "collection:{0:s}".format('primary')
        #q='id:0ff23cb3-cb3d-5617-ab8f-9948ede95ad9 and extras_digital_object_identifier:[* TO *]'
        q='extras_digital_object_identifier:[* TO *]'
        q='extras_digital_object_identifier:"doi http://dx.doi.org/10.4095/296356"'
        q='extras_digital_object_identifier:"{u\'en\': u\'\'}"'
        
        count, p_records = self.get_records(self.portal_site, q)
        print ('total record count: ', count)
        for v in p_records:
            print(v)
            self.update_record(self.portal_site, v['id'])
            if self.reg_site:
                self.update_record(self.reg_site, v['id'])
        
def main():
    parser = argparse.ArgumentParser(description='Search portal records with solr conditions.\
    Update records on both portal and registry(if exists) \
    For example: compare_protal2registry.py  --portal http://open.canada.ca/data --registry http://registry.open.canada.ca --quiet')
    parser.add_argument("--url", dest="url", required=True, 
            help="site url")
    parser.add_argument("--apikey", dest="apikey", 
            help="site api key, required if change is needed")
    parser.add_argument("--reg", dest="reg",
            help="reg site url")
    parser.add_argument("--regkey", dest="regkey", 
            help="reg site api key, required if change is needed")
    parser.add_argument("--quiet", dest="verbose",
            action='store_false', default=True, 
            help="print record IDs")

    options = parser.parse_args()

    user_agent = None
    # Instantiate remote ckanapi
    portal_site = ckanapi.RemoteCKAN(
        options.url,
        apikey=options.apikey,
        user_agent=user_agent)
    reg_site = None if not options.reg else ckanapi.RemoteCKAN(
        options.reg,
        apikey=options.regkey,
        user_agent=user_agent)

    # Instantiate remote ckanapi
    site = Records(portal_site, reg_site, options.verbose)
    site.filter_records()

if __name__ == '__main__':
    main()
    sys.exit(0)
