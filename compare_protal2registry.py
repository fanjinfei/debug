#!/usr/bin/env python

import ckanapi
import ckan
from ckanapi.errors import CKANAPIError
import argparse
import os
import sys
import logging

class CompareRecord():
    def __init__(self, portal_site, reg_site, verbose):
        self.portal_site = portal_site
        self.registry_site = reg_site
        self.verbose = verbose

    def getRecordIds(self, site, q):
        # get records from solr
        # if there are indexing errors, the records are not synced 
        #   with postgres database.
        count =0
        start = 0
        rows = 500
        pids = []
        while True:
            # a list with a hard upper limit 1000, need to loop 
            p_records = site.action.package_search(q=q, fl='id', 
                    use_default_schema=True, start=start, rows=rows)
            if count == 0:
                count =  p_records['count']
            for v in p_records['results']:
                pids.append(v['id'])
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
    def compareFgp(self, delete_fgp_registry=False):
        q = "collection:{0:s}".format('fgp')
        count, p_records = self.getRecordIds(self.portal_site, q)
        print ('total FGP record count in portal: ', count, p_records if self.verbose else '')
        
        
        count,r_records = self.getRecordIds(self.registry_site, q) # a list
        print ('total FGP record count in registry: ', count, r_records if self.verbose else '')

        ldiff = list (set(p_records) - set(r_records))
        print ('In portal but not in registry: ', len(ldiff), ldiff if self.verbose else '')

        rdiff = list ( set(r_records) -set(p_records) )
        print ('In registry but not in portal: ', len(rdiff), rdiff if self.verbose else '')
        
        common = list( set(r_records).intersection( p_records) )
        print( 'In registry and in portal: ', len(common), common if self.verbose else '')
        
        if delete_fgp_registry:
            self.removeRecords(self.registry_site, common)

def main():
    parser = argparse.ArgumentParser(description='Compare portal records with registry records.\
    For example: compare_protal2registry.py  --portal http://open.canada.ca/data --registry http://registry.open.canada.ca --quiet')
    parser.add_argument("--portal", dest="portal_url", required=True, 
            help="portal url")
    parser.add_argument("--registry", dest="registry_url", required=True, 
            help="registry url")
    #parser.add_argument("--portal_apikey", dest="portal_apikey", help="portal api key")
    parser.add_argument("--registry_apikey", dest="registry_apikey", 
            help="registry api key, required if delete_fgp_registry is set")
    parser.add_argument("--delete_fgp_registry", dest="delete_fgp_registry",
            action='store_true', default=False, 
            help="delete FGP records which are in registry and also in portal")
    parser.add_argument("--quiet", dest="verbose",
            action='store_false', default=True, 
            help="print record IDs")

    options = parser.parse_args()
    if options.delete_fgp_registry and not options.registry_apikey:
        parser.error("need registry api key")
        sys.exit(-1)

    user_agent = None
    portal_apikey = None
    # Instantiate remote ckanapi
    portal_site = ckanapi.RemoteCKAN(
        options.portal_url,
        apikey=portal_apikey,
        user_agent=user_agent)

    # Instantiate remote ckanapi
    reg_site = ckanapi.RemoteCKAN(
        options.registry_url,
        apikey=options.registry_apikey,
        user_agent=user_agent)
    comparePortalReg = CompareRecord(portal_site, reg_site, options.verbose)
    comparePortalReg.compareFgp(options.delete_fgp_registry)

if __name__ == '__main__':
    main()
    sys.exit(0)
