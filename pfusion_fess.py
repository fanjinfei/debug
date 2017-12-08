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
from fusionpy import FusionError

'''bash
FUSION_API_COLLECTION_URL=http://admin:topsecret1@localhost:8764/api/apollo/collections/mythings
'''
#collections:
mod01EN = ['mden_custe', 'mden_dailye', 'mden_ispe', 'nmden_newrele']
mod01FR = ['mdfr_custf', 'mdfr_dailyf', 'mdfr_ispf', 'nmdfr_newrelf']
ult01EN = ['nuten_newrele', 'uten_addtoindexe', 'uten_cansime', 'uten_canstate', 'uten_censuse', 'uten_censusfoge',
           'uten_censusprofe', 'uten_censustbte', 'uten_dailyarce', 'uten_dailye', 'uten_dailyle', 'uten_imdbe',
           'uten_ispe', 'uten_nhse', 'uten_olce', 'uten_olcrele', 'uten_otherse', 'uten_pandsarce', 'uten_pandse',
           'uten_sdge', 'uten_t1fogf']
ult01FR = ['nutfr_newrelf', 'utfr_addtoindexf', 'utfr_cansimf', 'utfr_canstatf', 'utfr_censusf', 'utfr_censusfogf',
           'utfr_censusproff', 'utfr_censustbtf', 'utfr_dailyarcf', 'utfr_dailyf', 'utfr_dailylf', 'utfr_imdbf',
           'utfr_ispf', 'utfr_nhsf', 'utfr_olcf', 'utfr_olcrelf', 'utfr_othersf', 'utfr_petsarcf', 'utfr_petsf',
           'utfr_sdgf', 'utfr_t1fogf']
classEN = ['clen_101naics2012', 'clen_101naics2017', 'clen_102noc2011', 'clen_102noc2016', 'clen_103sgc2011', 
           'clen_103sgc2016', 'clen_104cip2011', 'clen_104cip2016', 'clen_105napcs2012', 'clen_105napcs2017' ]
classFR = ['clfr_101scian2012', 'clfr_101scian2017', 'clfr_102cnp2011', 'clfr_102cnp2016', 'clfr_103cgt2011', 
           'clfr_103cgt2016', 'clfr_104cpe2011', 'clfr_104cpe2016', 'clfr_105scpan2012', 'clfr_105scpan2017' ]
            
fdata = { 'mod01EN':mod01EN,
    'mod01FR':mod01FR,
    'ult01EN':ult01EN,
    'ult01FR':ult01FR,
    'classEN':classEN,
    'classFR':classFR }

#these jobs are running daily, plus NET OLC olcnetbfull.sh, filternav2.sh, sr_olc_etc?
daily_cron = ['sr_navigation_en', 'sr_navigation_fr',
              'uten_dailye',  'utfr_dailyf',
              'uten_olce', 'utfr_olcf',
              'uten_cansime', 'utfr_cansimf',
              'uten_dailyle', 'utfr_dailylf',
              'uten_otherse', 'utfr_othersf',
              'uten_ispe', 'utfr_ispf',
              'nuten_newrele', 'nutfr_newrelf',
              'nmden_newrele', 'nmdfr_newrelf',
              'sr_sinewrel_en', 'sr_sinewrel_fr',
              'uten_canstate', 'utfr_canstatf',
#              'sr_olc_etc',
              'mden_dailye', 'mdfr_dailyf',
              'mden_custe', 'mdfr_custf',
              'mden_ispe', 'mdfr_ispf',
              'sr_others_en', 'sr_others_fr',
              'uten_imdbe', 'utfr_imdbf',
             ]


def read_csv(filename):
    content=[]
    with open(filename) as f:
        reader = csv.reader(f)
        for x in reader:
            if x:
                content.append(x)
    return content

def write_csv(filename, rows, header=None):
    outf=open(filename, 'wb')
    outf.write(codecs.BOM_UTF8)
    writer = unicodecsv.writer(outf)

    if header:
        writer.writerow(header)
    for row in rows:
        writer.writerow(row)

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

    def get_index_pipeline_list(self):
	pl = self.fu.get_index_pipeline('') #do not know yet
	#print pl.get_list()
        plist = pl.get_list()
        for pipe in plist:
            if pipe['id'] == 'conn_solr':
                stage = pipe['stages'][12] #13 rules
                print stage['type']
                print stage['script']
        print [p['id'] for p in plist]

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
    #old_csv = sys.argv[4]


    fu = Fusion(requester = fu_requester)
    sf = stc_fusion(fu)

    #sf.hist()
    #sf.ds_hosts()
    sf.get_index_pipeline_list()
    #sf.test()

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

