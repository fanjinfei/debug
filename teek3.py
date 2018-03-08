from grapheekdb.backends.data.localmem import LocalMemoryGraph
from grapheekdb.backends.data.symaslmdb import LmdbGraph
import sys
import shutil

#g = LocalMemoryGraph()
shutil.rmtree('/tmp/a.db')
g = LmdbGraph('/tmp/a.db')

book1 = g.add_node(kind='book', name='python tutorial', author='tim aaaa', thema='programming')
book2 = g.add_node(kind='book', name='cooking for dummies', author='tom bbbb', thema='cooking')
book3 = g.add_node(kind='book', name='grapheekdb', author='raf cccc', thema='programming')
book4 = g.add_node(kind='book', name='python secrets', author='tim aaaa', thema='programming')
book5 = g.add_node(kind='book', name='cooking a python', author='tom bbbb', thema='cooking')
book6 = g.add_node(kind='book', name='rst the hard way', author='raf cccc', thema='documentation')

for n in g.V():
    print (n.data())
print('-----------------------------')
person1 = g.add_node(kind='person', name='sam xxxx')
person2 = g.add_node(kind='person', name='tim xxxx')
person3 = g.add_node(kind='person', name='lue xxxx')
person4 = g.add_node(kind='person', name='joe xxxx')

d1 = {'kind':'car', 'name':'ford'}
d2 = {'kind':'car', 'name':'honda'}
g.bulk_add_node([d1,d2])
d1=list(g.V(kind='car', name='ford').limit(1))[0]
data = d1.data()
data.update({u'lang':u'fn'})
d1.update(**data)
#d1.update(lang=u'en', cn=u'CA')

g.add_edge(person1, book1, action='bought')
g.add_edge(person1, book3, action='bought')
g.add_edge(person1, book4, action='bought')
g.add_edge(person2, book2, action='bought')
g.add_edge(person2, book5, action='bought')
g.add_edge(person3, book1, action='bought')
g.add_edge(person3, book3, action='bought')
g.add_edge(person3, book5, action='bought')
g.add_edge(person3, book6, action='bought')

g.add_edge(person4, book1, action='saw')

for n in g.V():
    #print (n.data())
    print (n.kind, n.name, n.data())
print('------------------------')

foo = g.add_node(foo=1)
foo.remove()

for n in g.V(kind='book'):
    #print (n.data())
    print (n.name, '\tAuthor:', n.data()['author'])
print('------------------------')

for n in g.V(kind='book', thema="programming"):
    #print (n.data())
    print (n.name, '\tthema:', n.data()['thema'])
print('------------------------')

for n in g.V(name__contains='python'):
    print (n.name)
print('------------------------')

for e in g.E(action='saw'):
    print (e.data())
print('------------------------')


