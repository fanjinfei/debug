from pandas.io.html import read_html
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import *

from base64 import b64encode
import sys
import time

#firefox -p  --create test profile
#firefox -p test -- install proxy (FoxyProxy)

prof = webdriver.FirefoxProfile("/home/user/.mozilla/firefox/x95t3pq4.test")
'''
prof.set_preference('signon.autologin.proxy', 'true')
prof.set_preference('network.proxy.share_proxy_settings', 'false')
prof.set_preference('network.automatic-ntlm-auth.allow-proxies', 'false')
prof.set_preference('network.auth.use-sspi', 'false')

proxy_data = {'address': 'ax.cd.ca',
              'port': 80,
              'username': sys.argv[1],
              'password': sys.argv[2]}

proxy_dict = {'proxyType': ProxyType.MANUAL,
              'httpProxy': proxy_data['address'],
              'ftpProxy': proxy_data['address'],
              'sslProxy': proxy_data['address'],
              'noProxy': 'localhost, 127.0.0.1',
              'socksUsername': proxy_data['username'],
              'socksPassword': proxy_data['password']}

proxy_config = Proxy(proxy_dict)

binary = FirefoxBinary('/usr/bin/firefox')
'''
#driver = webdriver.Firefox(firefox_binary=binary)
#driver = webdriver.Firefox(proxy=proxy_config, firefox_profile=prof)
driver = webdriver.Firefox(firefox_profile=prof)

url= 'http://www120.s.c/'
driver.get(url)
time.sleep(5)

table = driver.find_element_by_xpath('//div[@id="tryalso"]/ul/li[1]')
#table = table.find_element_by_xpath('//ul').find_element_by_xpath('//li')
table = table.get_attribute('innerHTML')

print table

driver.close()

'''
driver.get('http://www1.nyse.com/about/listed/IPO_Index.html')

table = driver.find_element_by_xpath('//div[@class="sp5"]/table//table/..')

df = read_html(table_html)[0]
print df

driver.close()
'''
