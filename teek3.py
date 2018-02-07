from grapheekdb.backends.data.localmem import LocalMemoryGraph
g = LocalMemoryGraph()
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
    print (n.kind, n.name)
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


