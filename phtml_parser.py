from bs4 import BeautifulSoup as mparser
import sys

f = open(sys.argv[1])
c = f.read()

s = mparser(c, "lxml")

print s.find(name="h2", attrs={'style':'text-align: justify; font-weight:700;',
		'class':"h5 mrgn-tp-0 text-info control-label"}).text
