import spacy
from spacy import displacy
from nltk import Tree
import sys
try:
    nlp = spacy.load("en_core_web_lg")
    #nlp = spacy.load("en_core_web_md")
    #nlp = spacy.load("en_core_web_sm")
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
