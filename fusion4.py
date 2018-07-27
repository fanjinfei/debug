#read config for proxy/host, git_respo's alias
#option:  --fusion fhost --grepo gitrepo_url --type <datasource/querypipeline/indexpipeline/solrconfig>
#command: download collection datasource
#    create collection datasource
#    upload collection datasource
import argparse

from urllib3 import ProxyManager, make_headers
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

from fusionpy.fusion import Fusion
from fusionpy.connectors import FusionRequester, HttpFusionRequester
from fusionpy.fusioncollection import FusionIndexPipeline
from fusionpy import FusionError

'''bash
FUSION_API_COLLECTION_URL=http://admin:topsecret1@localhost:8764/api/apollo/collections/mythings
'''
parser = argparse.ArgumentParser()
#parser.add_argument("x", type=int, help="the base")
parser.add_argument("command", type=str, help="the command")
parser.add_argument("collection", type=str, help="the collection")
parser.add_argument("item_name", type=str, help="the item")
parser.add_argument("-v", "--verbosity", action="count", default=0)
parser.add_argument("-f", "--config",  default='fusion4.conf', required=True)
parser.add_argument("-t", "--type",  choices=['datasource', 'pipe', 'config'], default='datasource')
args = parser.parse_args()
if args.verbosity >= 2:
    print "Running '{}'".format(__file__)
if args.verbosity >= 1:
    print  args

class stc_fusion():
    def __init__(self, fu):
        self.fu = fu

    def get_solr_count(self, collection, datasource):
        '''url = '{0}/solr/{1}_shard1_replica1/select?q=_lw_data_source_s%3A{2}&rows=1&wt=json'.format(self.solr_url, collection, datasource)
        resp = requests.get(url=url)
        data = json.loads(resp.text)'''
        data = self.fu.get_solr_query('{0}/select?q=_lw_data_source_s%3A{1}&rows=1&wt=json'.format(collection, datasource))
        return data['response']['numFound']

    def test(self): #test new APIs
        print self.fu.get_datasource('uten_otherse', '').get_config()['properties']['startLinks']

    def export_index_stage(self, name, seq, stage):
        fname = '/tmp/'+ name + '-' + '{0:02d}'.format(seq) + '-' + stage['label'] + '.json'
        with open(fname, 'wb') as f:
            if stage.get('script', None):
                js = stage.pop('script')
                stage['script'] = '...'
                fname2 = fname[:-5] + '-' + stage['label'] + '.js'
                with open(fname2, 'wb') as f2:
                    f2.write(js.encode('utf-8'))
            f.write(json.dumps(stage))

    def del_index_pipeline(self):
	pl = self.fu.get_index_pipeline('clsconnsolr_dup')
        config = {}
        config['id'] = 'clsconnsolr_dup'
        pl.delete_config(config)

    def dup_index_pipeline(self):
	pl = self.fu.get_index_pipeline('clsconnsolr') #do not know yet
        config =  pl.get_config()
        config['id']  = 'cannabisconn'
        new_pipeline = FusionIndexPipeline(self.fu, config['id'])
        new_pipeline.create_config(config)

    def get_index_pipeline_list(self):
	pl = self.fu.get_index_pipeline('') #do not know yet
	#print pl.get_list()
        plist = pl.get_list()
        for pipe in plist:
            if pipe['id'] == 'conn_solr_cansim':
            #if pipe['id'] == 'clsconnsolr':
                ip_count = 0
                for stage in pipe['stages']:
                    self.export_index_stage(pipe['id'], ip_count, stage)
                    ip_count += 1
        return

        for pipe in plist:
            if pipe['id'] == 'conn_solr':
                stage = pipe['stages'][12] #13 rules
                print stage['type']
                print stage['script']
        print [p['id'] for p in plist]

    def get_query_pipeline(self, name):
	pl = self.fu.get_query_pipeline(name) #do not know yet
        config =  pl.get_config()
        print json.dumps(config,indent=4)

    def ds_hosts(self):
	for ds_name in daily_cron:
            ds = self.fu.get_datasource(ds_name)
            try:
                config = ds.get_config()
            except FusionError:
                print ds_name, 'Not Found'
                continue
            links = config['properties']['startLinks']
            hosts = {}
            for link in links:
                hosts[urlparse(link).hostname] = True
            print ds_name, [k for k,v in hosts.iteritems()]
    def hist(self):
        rows = []
        for k, dss in fdata.iteritems():
            for ds_name in dss:
                ds = self.fu.get_datasource(ds_name, k)
                hists = ds.history()[-3:] #better merge same day first
                if len(hists) <=1 or hists[-1]['crawl_started'][:4] == u'2016': continue
                print (k, ds_name)
                row = [k, ds_name]
                for h in hists:
                    row.append(h['crawl_started'][:10])
                    counter = 'failed'
                    if h['crawl_state'] =='FINISHED':
                      try:
                        counter = h['pipeline']['stats']['stages'][-1]['counters']['processed']
                        print( h['crawl_started'], h['crawl_stopped'], h['crawl_state'], counter)
                      except KeyError: # implicit error
                        print ( h['crawl_started'], h['crawl_stopped'], h['crawl_state'],
                            h['pipeline']['stats']['stages'][-1])
                    else: #explicit error
                         print( h['crawl_started'], h['crawl_stopped'], h['crawl_state'])
                         #sys.exit(-1)
                    row[-1] = row[-1] + ' ' + str(counter)
                count = self.get_solr_count(k, ds_name)
                row.append('') #pre_date count
                row.append(count)
                rows.append(row)
                
        rows.sort(key=lambda x: x[0]+x[1])

        now = datetime.now()
        day_of_week = now.isocalendar()[2]
        pre_day = (now - timedelta(days=3)) if day_of_week == 1 else (now - timedelta(days=1))
        pre_date = pre_day.strftime("%Y-%m-%d")
        todate = now.strftime("%Y-%m-%d")#datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows.insert(0, ['collection', 'datasource', 'job1 date counter', 'job2 date2 counter', 'latest job', pre_date, todate])
        try:
            content = read_csv('/tmp/fusion-{0}.csv'.format(pre_date))
        except:
            content = None
        if content: #update the pre_date
            ds_dict = {}
            assert(content[0][6] == pre_date)
            for row in content[1:]:
                ds_dict[row[1]] = row[6]
            for row in rows[1:]:
                row[5] = ds_dict.get(row[1], '')
        write_csv('/tmp/fusion-{0}.csv'.format(todate), rows) 

def main():
    url = sys.argv[1] # above api_url
    if len(sys.argv) >=3:
        proxy_user_passwd=sys.argv[2] # 'user:pwd' --- proxy_auth
        proxy_url = sys.argv[3] # http://host:port/
        default_headers = make_headers(proxy_basic_auth=proxy_user_passwd) 
        proxy = ProxyManager(proxy_url, maxsize=10, proxy_headers=default_headers)
        fu_requester = HttpFusionRequester(fusion_url = url, urllib3_pool_manager = proxy)
    else:
        fu_requester = HttpFusionRequester(fusion_url = url)

    #solr_url = sys.argv[4] #http://www:7773/solr/classEN_shard1_replica1/select?q=ds%3A105napcs2017&wt=json&indent=true
    #query fusion: http://*.ca:8764/api/apollo/query-pipelines/src01EN-default/collections/src01EN/select?fl=*,score&echoParams=all&wt=json&json.nl=arrarr&sort&start=0&q=*:*&debug=true&rows=10
    #fusion public query port 9292: view-source:http://.ca:9292/api/apollo/query-pipelines/src01EN-default/collections/src01EN/srs?fl=*,score&echoParams=all&wt=json&json.nl=arrarr&sort&start=0&q=consumer&debug=true&rows=10&hl=on
    #old_csv = sys.argv[4]


    fu = Fusion(requester = fu_requester)
    sf = stc_fusion(fu)

    #sf.hist()
    #sf.ds_hosts()
    #sf.get_index_pipeline_list()
    #sf.test()
    #sf.dup_index_pipeline()
    #sf.del_index_pipeline()
    sf.get_query_pipeline('ult01FR-default')

if __name__ == '__main__':
	main()

'''
collection = fu.get_collection()
ds = fu.get_datasource('mden_custe', 'mod01EN')

print collection.get_features()

print fu.get_collections()

print collection.get_config()

hist = ds.history()[-3:]
for h in hist:
	print( h['crawl_started'], h['crawl_stopped'], h['crawl_state'])
	pprint.pprint( h['pipeline']['stats']['stages'][-1]['counters']['processed'] )

#Additional connectors APIs
http://host:8764/api/apollo/connectors/datasources?collection=src01EN
/api/apollo/connectors/history/sr_sinewrel_en
'''

