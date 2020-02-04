from nltk.corpus import wordnet as wn
from graphviz import Digraph
import pandas as pd
from grapheekdb.backends.data.localmem import LocalMemoryGraph
'''>>> import nltk
  >>> nltk.download('wordnet')
  build quick graph
  relations:
    synset: hypernyms(), hyponyms(), member_holonyms(), root_hypernyms(), lowest_common_hypernyms(syn_arg)
    lemma: antonyms(), pertainyms(), derivationally_related_forms()
    
  
'''

def test():
    print(wn.synsets('internet'))
    print(wn.synsets('dog')) #sets, lemma
    sn = wn.synset('dog.n.01')
    print(sn, sn.definition(), sn.examples())
    print('\t', sn.lemmas(), [str(lemma.name()) for lemma in sn.lemmas()] )
    lemma = wn.lemma('dog.n.01.dog')
    print('\t', lemma.synset(), lemma.name(), lemma.synset().lemma_names())
    count = 0
    for ss in wn.all_synsets():
        print (ss, ss.lemma_names(),' ||| ', ss.definition() )
        count += 1
        if count > 10: break
    words = [ i for i in wn.words() ]
    print (words[1000:1050])

def test2():
    print(wn.synsets('tell'))
    print(wn.synsets('know'))

    sn = wn.synset('tell.v.01')
    print(sn, sn.definition(), sn.examples())
    print('\t', sn.lemmas(), [str(lemma.name()) for lemma in sn.lemmas()] )
    paths = sn.hypernym_paths()
    print (sn.hypernyms(), sn.root_hypernyms())
    print (paths)
    print (wn.synset('express.v.02').hypernyms())
    print('')
    sn1 = sn

    sn = wn.synset('know.v.01')
    print(sn, sn.definition(), sn.examples())
    print('\t', sn.lemmas(), [str(lemma.name()) for lemma in sn.lemmas()] )
    paths = sn.hypernym_paths()
    print (sn.hypernyms(), sn.root_hypernyms())
    print (paths)
    print (sn1.lowest_common_hypernyms(sn))
    print('')

def test3():
    print('show verb top roots (root hypernyms)')
    roots = {}
    count = 0
    for sn in wn.all_synsets(pos='v'):
        ks = [str(rsn)[8:-2] for rsn in sn.root_hypernyms()][0]
        print(sn,  ks)
        roots[ks] = True
        count += 1
    print(len(roots), count)
    res = []
    for k,v in roots.items():
        res.append(k)
    print(res)

def build_verb_graph():
    g = LocalMemoryGraph()
    g.add_node_index('name') # can be combined/filter like add('name', 'kind', thema='a') g.remove_node_index('my_id')
    g.add_node_index('name', 'kind', thema='a')
    print (g.get_node_indexes())
    #g.add_edge_index('dep') g.remove_edge_index
    for sn in wn.all_synsets(pos='v'):
        rs = [str(rsn)[8:-2] for rsn in sn.root_hypernyms()][0]
        ks = str(sn)[8:-2]
        if g.V(name=rs).count() ==0:
            n1 = g.add_node(kind='verb_root', name=str(rs))
        else:
            n1 = list(g.V(name=rs))[0]
        n2 = g.add_node(kind='verb', name=str(ks))
        g.add_edge(n1, n2, dep='root_hypernym')
    return g

def gv_graph(g, src_attr='attr', dst_attr='attr', edge_attr='attr'):
    # This may raise an exception
    # let's it raise to warn user that
    # networkx should be installed for this method to be used
    from graphviz import Digraph
    G = Digraph('G')
    node_ids = set()
    edge_ids = set()
    for node in g.V(kind='verb_root').limit(10):
        node_id = node.get_id()
        node_attr = node.data().get(src_attr, '_None') + str(node_id) + ' ' + node.kind
        if not node_id in node_ids:
            G.node(node_attr)
            node_ids.add(node_id)
        count = 0
        for out_edge, out_node in zip(node.outE(), node.outV()):
            out_edge_id = out_edge.get_id()
            out_node_id = out_node.get_id()
            out_node_attr = out_node.data().get(dst_attr, '_None') + str(out_node_id) + ' ' +out_node.kind
            out_edge_attr = out_edge.data().get(edge_attr, '_None')
            if not out_node_id in node_ids:
                G.node(out_node_attr)
                node_ids.add(out_node_id)
            if not out_edge_id in edge_ids:
                G.edge(node_attr, out_node_attr, label=out_edge_attr)
                edge_ids.add(out_edge_id)
            count += 1
            if count > 10: break
    return G   
        
if __name__ == '__main__':
    #test3()
    g = build_verb_graph()
    gv = gv_graph(g, 'name', 'name', 'dep')
    gv.view()
    
'''
>>> good = wn.synset('good.a.01')
>>> good.antonyms()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Synset' object has no attribute 'antonyms'
>>> good.lemmas()[0].antonyms()
[Lemma('bad.a.01.bad')]
'''
