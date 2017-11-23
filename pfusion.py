from urllib3 import ProxyManager, make_headers
import sys

from fusionpy.fusion import Fusion
from fusionpy.connectors import FusionRequester, HttpFusionRequester

'''bash
FUSION_API_COLLECTION_URL=http://admin:topsecret1@localhost:8764/api/apollo/collections/mythings
'''

url = sys.argv[1] # above api_url
proxy_user_passwd=sys.argv[2] # 'user:pwd' --- proxy_auth
proxy_url = sys.argv[3] # http://host:port/

default_headers = make_headers(proxy_basic_auth=proxy_user_passwd) 
proxy = ProxyManager(proxy_url, maxsize=10, proxy_headers=default_headers)

fu_requester = HttpFusionRequester(fusion_url = url, urllib3_pool_manager = proxy)
fu = Fusion(requester = fu_requester)
collection = fu.get_collection()

print collection.get_features()

print fu.get_collections()

print collection.get_config()

#Additional connectors APIs
'''
http://host:8764/api/apollo/connectors/datasources?collection=src01EN
/api/apollo/connectors/history/sr_sinewrel_en
'''

