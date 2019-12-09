import spacy
from spacy import displacy
from nltk import Tree
import sys
try:
    nlp = spacy.load("en_core_web_lg")
    #nlp = spacy.load("en_core_web_md")
    #nlp = spacy.load("en_core_web_sm")
    print(en.meta["labels"]["parser"]) #token.dep_ (amod, nsubj, etc)
    print(en.meta["labels"]["tagger"]) #token.pos_ (VERB, NOUN, ADP, etc)
except:
    print('python -m spacy download en_core_web_sm')
    sys.exit(0)
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)

#displacy.serve(doc, style="dep")            
print("\n")

doc = nlp("Autonomous cars shift insurance liability toward manufacturers")
for token in doc:
    print(token.text, token.dep_, token.head.text, token.head.pos_,
            [child for child in token.children])
            
def printree(root):
    if sum(1 for _ in root.children) ==0:
        print(root, end='')
        return
    print(root, end=' [ ')
    for child in root.children:
        printree(child)
    print('', end= ' ], ')

[printree(sent.root) for sent in doc.sents]

'''
>>> print(en.meta["labels"]["parser"])
['ROOT', 'acl', 'acomp', 'advcl', 'advmod', 'agent', 'amod', 'appos', 'attr', 'aux', 'auxpass', 'case', 'cc', 'ccomp', 'compound', 'conj', 'csubj', 'csubjpass', 'dative', 'dep', 'det', 'dobj', 'expl', 'intj', 'mark', 'meta', 'neg', 'nmod', 'npadvmod', 'nsubj', 'nsubjpass', 'nummod', 'oprd', 'parataxis', 'pcomp', 'pobj', 'poss', 'preconj', 'predet', 'prep', 'prt', 'punct', 'quantmod', 'relcl', 'xcomp']
>>> print(en.meta["labels"]["tagger"])
['$', "''", ',', '-LRB-', '-RRB-', '.', ':', 'ADD', 'AFX', 'CC', 'CD', 'DT', 'EX', 'FW', 'HYPH', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NFP', 'NN', 'NNP', 'NNPS', 'NNS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', 'XX', '_SP', '``']
'''

