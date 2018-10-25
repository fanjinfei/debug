
#copy geckodriver to $PATH
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from base64 import b64encode
import sys, os
import time

binary = FirefoxBinary('../firefox/firefox/firefox')

os.environ['MOZ_HEADLESS'] = '1'

proxy = "127.0.0.1"
port = 8014

fp = webdriver.FirefoxProfile()
fp.set_preference('network.proxy.ssl_port', int(port))
fp.set_preference('network.proxy.ssl', proxy)
fp.set_preference('network.proxy.http_port', int(port))
fp.set_preference('network.proxy.http', proxy)
fp.set_preference('network.proxy.ftp', proxy)
fp.set_preference('network.proxy.ftp_port', int(port))
fp.set_preference('network.proxy.socks', proxy)
fp.set_preference('network.proxy.socks_port', int(port))

fp.set_preference('network.proxy.type', 1)


driver = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp)

url= "https://google.ca/" #sys.argv[2] #'http://www120.s.c/'
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

def dump_dom_tree(driver):
	from StringIO import StringIO
	import lxml.etree

	parser = lxml.etree.HTMLParser()

	driver.get("http://google.com")

	# We get this element only for the sake of illustration, for the tests later.
	input_from_find = driver.find_element_by_id("lst-ib")
	input_from_find.send_keys("foo")

	html = driver.execute_script("return document.documentElement.outerHTML")
	tree = lxml.etree.parse(StringIO(html), parser)

	# Find our element in the tree.
	field = tree.find("//*[@id='lst-ib']")
	# Get the XPath that will uniquely select it.
	path = tree.getpath(field)

	# Use the XPath to get the element from the browser.
	input_from_xpath = driver.find_element_by_xpath(path)

	print "Equal?", input_from_xpath == input_from_find
	# In JavaScript we would not call ``getAttribute`` but Selenium treats
	# a query on the ``value`` attribute as special, so this works.
	print "Value:", input_from_xpath.get_attribute("value")


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

