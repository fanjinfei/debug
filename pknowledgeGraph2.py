import re
import bs4
import requests
import spacy
from spacy import displacy
from spacy.matcher import Matcher 
from spacy.tokens import Span 

import networkx as nx
from graphviz import Digraph
import pandas as pd
from grapheekdb.backends.data.localmem import LocalMemoryGraph

import matplotlib.pyplot as plt
from tqdm import tqdm

#Spacy == 2.2.3 version

nlp = spacy.load('en_core_web_sm')
pd.set_option('display.max_colwidth', 200)
# %matplotlib inline

def learn_spacy():
    doc = nlp("The 22-year-old recently won ATP Challenger tournament.")

    for tok in doc:
      print(tok.text, "...", tok.dep_)
    doc = nlp("Nagal won the first set.")

    for tok in doc:
      print(tok.text, "...", tok.dep_)

def create_subgraph(root, g, parent=None):
    if parent == None:
        parent = g.add_node(kind="st") #sentence root
    print(str(root))
    node = g.add_node(kind=root.pos_, name=str(root))
    g.add_edge(parent, node, dep=str(root.dep_))
    for child in root.children:
        create_subgraph(child, g, node)
    if parent.kind == 'st':
        return parent

def reduce_subgraph_set(parent, g): #the 'st' node
    # reduce and conj for noun, adj and verb, create a SET node
    def get_parallel(node, res):
        e1 = list(node.inE())[0]
        p = list(node.in_())[0]
        nres = list(p.out_(dep=e1.dep))
        if len(nres)>0:
            for r in nres:
                if r != node: res.append(r)
    def get_conj(node, res):
        nres = list(node.out_(dep='conj'))
        if len(nres)>0:
            for r in nres: res.append(r) 
            for r in nres:
                get_conj(r, res)
    def get_cc(node):
        ccs = list(node.out_(dep='cc'))
        if len(ccs) >0:
            return ccs[0]
        else:
            for i in list(node.out_(dep='conj')):
                res = get_cc(i)
                if res:
                    return res
        return None
            
    conj_nodes = []
    get_conj(parent, conj_nodes)
    cc = get_cc(parent)
    s_node = None
    def rebuild():
        #import pdb; pdb.set_trace()
        #replace the conj_nodes[0] with 'set' node, 'name'=cc.name, and edges 'contain' to all the nodes, 
        s_node = g.add_node(kind='_set', name='__'+cc.name)
        up_node = list(parent.in_())[0]
        data = list(parent.inE())[0].data()
        g.add_edge(up_node, s_node, **data)
        
        #remove current node's inE
        e = list(parent.inE())[0]
        e.remove()
        g.add_edge(s_node, parent, dep="contain")
        
        #remove the conj edge
        for i in conj_nodes:
            e = list(i.inE())[0]
            e.remove()
            g.add_edge(s_node, i, dep="contain")
        
        #remove cc node
        cc.remove()
        
        #ambiguity -->? <sometimes not needed here, depends on the context and meaning(!)
        #move parent's out_() to s_node
        if parent.kind not in ['AUX', 'VERB']: #these sub_nodes are directly related to parent
            for i in parent.out_():
                e = list(i.inE())[0]
                data = e.data()
                g.add_edge(s_node, i, **data)
                e.remove()
        return s_node
    if len(conj_nodes):  #conj_nodes[0] != parent
        s_node = rebuild()
    #other cc nodes, such as 'nsubj', no 'conj' for parent
    elif cc:
         get_parallel(parent, conj_nodes)
         if len(conj_nodes):
             s_node = rebuild()
             #import pdb; pdb.set_trace()
             pass
    if s_node:
        reduce_subgraph_set(s_node, g)
    #if parent.outE().count():
    for node in list(parent.out_()): # late eval, will miss the remvoed child
#    for node in parent.out_(): #get early evaluated first, removed child will be itered
        reduce_subgraph_set(node, g)

def clause_coref():
    doc = nlp('He and she tell me about people, bird and animals in konoha who have wind style chakra and are red and above jonin level')
    #doc = nlp('tell me about people, bird and animals in konoha who have wind style chakra and are red and above jonin level')
    #doc =nlp('I give him the book and tell him what to do next.')  #TODO
    #doc = nlp('people in konoha have wind style chakra and we are above jonin level')
    for tok in doc:
      print(tok.text, "...", tok.dep_)
    [printree(sent.root) for sent in doc.sents]
    g = LocalMemoryGraph()
    g_sts = [create_subgraph(sent.root, g) for sent in doc.sents] #graph sentences
    [ reduce_subgraph_set(p, g) for p in g_sts]
    gv = gv_graph(g, 'name', 'name', 'dep')
    gv.view()
    
    displacy.serve(doc, style='dep') #style='ent', replace it with a lmdb 

def build_kgraph():
    sts = pd.read_csv("wiki_sentences_v2.csv")
    print(sts.shape) #rows x cloumns
    g = LocalMemoryGraph()
    entity_pairs = []
    for i in tqdm(sts["sentence"][:1000]):
        entity_pairs.append(get_entities(i))
    relations = [get_relation(i) for i in tqdm(sts['sentence'][:1000])]
    print(pd.Series(relations).value_counts()[:50])

    # extract subject
    source = [i[0] for i in entity_pairs]
    # extract object
    target = [i[1] for i in entity_pairs]
    kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':relations})
    for index, row in kg_df.iterrows():
        edge = row['edge']
        src = g.add_node(attr = row['source']) #src.update(m=1, n=2) or **args
        target = g.add_node(attr = row['target'])
        g.add_edge(src, target, attr = edge)
        if index>10: break
    #  filter is always available (kind='person', name__contains='m')
    #print( list(g.V(attr='connie'))[:10])
    #print( list(g.E())[:10])
    print( list (g.V().limit(10)) )
    print( list(g.E().limit(10)) )

    print( list (g.V().inV().limit(10)) ) #outV, bothV, outE inE bothE, in_ out_ both_
    # out_ = outE().outV(), in_ = inE().inV(); both_ = out_ + in_
    print( list(g.E().limit(10)) )
    
    gv = gv_graph(g, 'attr', 'attr', 'attr')
    gv.view()
    #import pdb; pdb.set_trace()

def gv_graph(g, src_attr='attr', dst_attr='attr', edge_attr='attr'):
    # This may raise an exception
    # let's it raise to warn user that
    # networkx should be installed for this method to be used
    from graphviz import Digraph
    G = Digraph('G')
    node_ids = set()
    edge_ids = set()
    for node in g.V():
        node_id = node.get_id()
        node_attr = node.data().get(src_attr, '_None') + str(node_id) + ' ' + node.kind
        if not node_id in node_ids:
            G.node(node_attr)
            node_ids.add(node_id)
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
    return G   
def printree(root, islast=False):
    total = sum(1 for _ in root.children)
    if  total==0:
        print('"'+str(root)+'(' + str(root.pos_)+', ' + str(root.dep_)+')"', end=' ' if islast else ', ')
        return
    print('"'+str(root)+'('+ str(root.pos_)+', '+str(root.dep_)+')"', end=', [ ')
    count = 0
    for child in root.children:
        count += 1
        printree(child, count==total)
    print('', end= ' ] ' if islast else ' ], ')
     
def test():

  # import wikipedia sentences
  #https://s3-ap-south-1.amazonaws.com/av-blog-media/wp-content/uploads/2019/10/wiki_sentences_v2.csv
  # Other data source https://dumps.wikimedia.org/wikidatawiki/entities/ latest-all.json.bz2
  #   https://dumps.wikimedia.org/enwiki/latest/  enwiki-latest-pages-articles-multistream.xml.bz2
  candidate_sentences = pd.read_csv("wiki_sentences_v2.csv")
  candidate_sentences.shape

  doc = nlp("the drawdown process is governed by astm standard d823")
  for tok in doc:
    print(tok.text, "...", tok.dep_)

  get_entities("the film had 200 patents")
  entity_pairs = []

  for i in tqdm(candidate_sentences["sentence"][:1000]):
    entity_pairs.append(get_entities(i))
  get_relation("John completed the task")
  relations = [get_relation(i) for i in tqdm(candidate_sentences['sentence'][:1000])]
  pd.Series(relations).value_counts()[:50]
  
  # extract subject
  source = [i[0] for i in entity_pairs]

  # extract object
  target = [i[1] for i in entity_pairs]

  kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':relations})
  
  if False: #full graph
  # create a directed-graph from a dataframe
    G=nx.from_pandas_edgelist(kg_df, "source", "target", 
                          edge_attr=True, create_using=nx.MultiDiGraph())
    plt.figure(figsize=(12,12))
    G=nx.from_pandas_edgelist(kg_df[kg_df['edge']=="composed by"], "source", "target", 
                          edge_attr=True, create_using=nx.MultiDiGraph())

    plt.figure(figsize=(12,12))
    pos = nx.spring_layout(G, k = 0.5) # k regulates the distance between nodes
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()

    pos = nx.spring_layout(G)
    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()
  else : #partial graph  
    G=nx.from_pandas_edgelist(kg_df[kg_df['edge']=="composed by"], "source", "target", 
                          edge_attr=True, create_using=nx.MultiDiGraph())

    plt.figure(figsize=(12,12))
    pos = nx.spring_layout(G, k = 0.5) # k regulates the distance between nodes
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()
    
  if False: #only 'written by' OR 'released in' relations
    G=nx.from_pandas_edgelist(kg_df[kg_df['edge']=="written by"], "source", "target", 
                              edge_attr=True, create_using=nx.MultiDiGraph())

    plt.figure(figsize=(12,12))
    pos = nx.spring_layout(G, k = 0.5)
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()
    
def get_relation(sent):

  doc = nlp(sent)

  # Matcher class object 
  matcher = Matcher(nlp.vocab)

  #define the pattern 
  pattern = [{'DEP':'ROOT'}, 
            {'DEP':'prep','OP':"?"},
            {'DEP':'agent','OP':"?"},  
            {'POS':'ADJ','OP':"?"}] 

  matcher.add("matching_1", None, pattern) 

  matches = matcher(doc)
  k = len(matches) - 1

  span = doc[matches[k][1]:matches[k][2]] 

  return(span.text)
    
def get_entities(sent):
  ## chunk 1
  ent1 = ""
  ent2 = ""

  prv_tok_dep = ""    # dependency tag of previous token in the sentence
  prv_tok_text = ""   # previous token in the sentence

  prefix = ""
  modifier = ""

  #############################################################
  
  for tok in nlp(sent):
    ## chunk 2
    # if token is a punctuation mark then move on to the next token
    if tok.dep_ != "punct":
      # check: token is a compound word or not
      if tok.dep_ == "compound":
        prefix = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          prefix = prv_tok_text + " "+ tok.text
      
      # check: token is a modifier or not
      if tok.dep_.endswith("mod") == True:
        modifier = tok.text
        # if the previous word was also a 'compound' then add the current word to it
        if prv_tok_dep == "compound":
          modifier = prv_tok_text + " "+ tok.text
      
      ## chunk 3
      if tok.dep_.find("subj") == True:
        ent1 = modifier +" "+ prefix + " "+ tok.text
        prefix = ""
        modifier = ""
        prv_tok_dep = ""
        prv_tok_text = ""      

      ## chunk 4
      if tok.dep_.find("obj") == True:
        ent2 = modifier +" "+ prefix +" "+ tok.text
        
      ## chunk 5  
      # update variables
      prv_tok_dep = tok.dep_
      prv_tok_text = tok.text
  #############################################################

  return [ent1.strip(), ent2.strip()]
  
def main():
    #test()
    #build_kgraph()
    clause_coref()
    
if __name__ == '__main__':
    main()
