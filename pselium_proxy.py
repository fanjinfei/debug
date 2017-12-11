
#copy geckodriver to $PATH

from pandas.io.html import read_html
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options
import zipfile


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from base64 import b64encode
import sys
import time

#sudo apt install xvfb, pip install PyVirtualDisplay
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()

#firefox -p  --create test profile
#firefox -p test -- install proxy (FoxyProxy)

prof = webdriver.FirefoxProfile(sys.argv[1]) #"/home/user/.mozilla/firefox/x95t3pq4.test")
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

url= sys.argv[2] #'http://www120.s.c/'
driver.get(url)
time.sleep(5)

if 'google.' in url: 
	try:
		wait = WebDriverWait(driver, 10)
		element = wait.until(EC.presence_of_element_located((By.ID, "hplogo")))
		print driver.page_source.encode('utf-8')
	#	sbtn = driver.find_element_by_css_selector('button.gbqfba')
	#	sbtn.click()
	except TimeoutException:
		print 'not found'
	except:
		import traceback; traceback.print_exc()
else:
	try:
		table = driver.find_element_by_xpath('//div[@id="tryalso"]/ul/li[1]')
		#table = table.find_element_by_xpath('//ul').find_element_by_xpath('//li')
		table = table.get_attribute('innerHTML')

		print table
		driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'W')
	except:
		import traceback; traceback.print_exc()
		pass
'''
num_of_tabs = ...
for x in range(1, num_of_tabs):
    self.driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'W') #send ^+W to close tab
'''

driver.quit()

display.stop()

def use_phantomjs():
	from selenium import webdriver
	from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
	import base64
	import sys,time

	if len(sys.argv) > 2:
		
		service_args = [
		    '--proxy='+sys.argv[1],
		    '--proxy-type=http',
		    '--proxy-auth={0}'.format(sys.argv[2]),
		]

		authentication_token = "Basic " + base64.b64encode(b'user:passwrd')

		capa = DesiredCapabilities.PHANTOMJS
		#capa['phantomjs.page.customHeaders.Proxy-Authorization'] = authentication_token
		capa['phantomjs.page.customHeaders.Proxy-Authorization'] = authentication_token
		#driver = webdriver.PhantomJS(desired_capabilities=capa, service_args=service_args)
		driver = webdriver.PhantomJS(service_args=service_args)
		print service_args
	else:
		driver = webdriver.PhantomJS() # or add to your PATH
	driver.set_window_size(1024, 768) # optional
	driver.set_page_load_timeout(10)
	driver.get('https://google.ca/')
	#driver.get('https://github.com/')
	#driver.get('http://localhost/')
	time.sleep(3)
	driver.save_screenshot('screen.png') # save a screenshot to disk

	try:
		sbtn = driver.find_element_by_css_selector('button.gbqfba')
		sbtn.click()
	except:
		print 'not found'
		pass

	driver.quit()
#install 
#sudo apt-get install build-essential chrpath libssl-dev libxft-dev libfreetype6-dev libfreetype6 libfontconfig1-dev libfontconfig1 -y
#sudo wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
#sudo tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share/
#sudo ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/

def use_chrome():

	manifest_json = """
	{
	    "version": "1.0.0",
	    "manifest_version": 2,
	    "name": "Chrome Proxy",
	    "permissions": [
		"proxy",
		"tabs",
		"unlimitedStorage",
		"storage",
		"<all_urls>",
		"webRequest",
		"webRequestBlocking"
	    ],
	    "background": {
		"scripts": ["background.js"]
	    },
	    "minimum_chrome_version":"22.0.0"
	}
	"""

	background_js = """
	var config = {
		mode: "fixed_servers",
		rules: {
		  singleProxy: {
		    scheme: "http",
		    host: "hostname",
		    port: parseInt(port)
		  },
		  bypassList: ["foobar.com"]
		}
	      };

	chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

	function callbackFn(details) {
	    return {
		authCredentials: {
		    username: "user",
		    password: "passwrdd"
		}
	    };
	}

	chrome.webRequest.onAuthRequired.addListener(
		    callbackFn,
		    {urls: ["<all_urls>"]},
		    ['blocking']
	);
	"""


	pluginfile = 'proxy_auth_plugin.zip'

	with zipfile.ZipFile(pluginfile, 'w') as zp:
	    zp.writestr("manifest.json", manifest_json)
	    zp.writestr("background.js", background_js)

	co = Options()
	co.add_argument("--start-maximized")
	co.add_extension(pluginfile) #this does not work with co.add_argument("--headless")

	display = Display(visible=0, size=(800, 600))
	display.start()

	driver = webdriver.Chrome("path/to/chromedriver",  chrome_options=co)
	#https://chromedriver.storage.googleapis.com/2.34/chromedriver_linux64.zip

	try:
		driver.get("https://www.google.com")
		print driver.page_source.encode('utf-8')
	except:
		import traceback; traceback.print_exc()

	driver.quit()
	display.stop()


'''
element = driver.wait.until(
    EC.presence_of_element_located(
    EC.element_to_be_clickable(
    EC.visibility_of_element_located(
        (By.NAME, "name")
        (By.ID, "id")
        (By.LINK_TEXT, "link text")
        (By.PARTIAL_LINK_TEXT, "partial link text")
        (By.TAG_NAME, "tag name")
        (By.CLASS_NAME, "class name")
        (By.CSS_SELECTOR, "css selector")
        (By.XPATH, "xpath")
    )
)
 
 
# CATCH EXCEPTIONS
from selenium.common.exceptions import
    TimeoutException
    ElementNotVisibleException
'''
'''
driver.get('http://www1.nyse.com/about/listed/IPO_Index.html')

table = driver.find_element_by_xpath('//div[@class="sp5"]/table//table/..')

df = read_html(table_html)[0]
print df

driver.close()
'''

