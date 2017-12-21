from bs4 import BeautifulSoup as mparser
from bs4.element import Comment
import sys

def filter_stopindex(content):
    stop = '<!--stopindex-->'
    start = '<!--startindex-->'
    tokens = [stop, start]
    state = 0 #keep, 1:skip
    pos = 0
    res = [ ]
    def find_next( ):
        if state == 0: return (content.find(stop, pos), 1)
        return (content.find(start, pos), 0)
    while True:
        npos, nstate = find_next()
        if npos >= 0:
            if state == 0:
                res.append(content[pos:npos])
            pos, state = npos, nstate
        else:
            if pos == 0: return content
            if state == 0:
                res.append(content[pos:])
            break
    return ''.join(res)


def tag_visible(element, dts):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    if element.parent in dts:
        return False
#       import pdb; pdb.set_trace()
    return True

def get_text(m, dts):
    texts = m.findAll(text=True)
    #visible_texts = filter(tag_visible, texts)  
    visible_texts =[]
    for ele in texts:
        if tag_visible(ele, dts):
            visible_texts.append(ele)
    return u" ".join(t.strip() for t in visible_texts)

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def main():
     f = open(sys.argv[1])
     c = f.read()
     c = filter_stopindex(c)

     s = mparser(c, "lxml")
     #s = mparser(c, "html.parser")
     dt = s.find(id="wb-dtmd")
     
     #import pdb; pdb.set_trace()
     dts = dt.findChildren() 
     for p in s.find(name='div', attrs={'class':'pane-bean-report-problem-button'}).findChildren():
         dts.append(p)

     print get_text(s, dts)
     print 'dbg', dt.text, dt.contents
     print dt.findChildren()
     return

     print s.find(name="h2", attrs={'style':'text-align: justify; font-weight:700;',
		'class':"h5 mrgn-tp-0 text-info control-label"}).text

main()
