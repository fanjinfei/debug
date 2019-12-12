import spacy
from spacy import displacy
from nltk import Tree
import sys
try:
    nlp = spacy.load("en_core_web_lg")
    #nlp = spacy.load("en_core_web_md")
    #nlp = spacy.load("en_core_web_sm")
    print(nlp.meta["labels"]["parser"]) #token.dep_ (amod, nsubj, etc)
    print(nlp.meta["labels"]["tagger"]) #token.pos_ (VERB, NOUN, ADP, etc)
except:
    print('python -m spacy download en_core_web_sm')
    sys.exit(0)

#vocab, word vector
print(nlp.vocab['man'].vector)
tokens = nlp(u'man vehicle school jfido')

for token in tokens:
    print(token.text, token.has_vector, token.vector_norm, token.is_oov)
for token1 in tokens:
    for token2 in tokens:
        print(token1.text, token2.text, token1.similarity(token2))
target = nlp("Cats are beautiful animals.")
 
doc1 = nlp("Dogs are awesome.")
doc2 = nlp("Some gorgeous creatures are felines.")
doc3 = nlp("Dolphins are swimming mammals.")
 
print(target.similarity(doc1))
print(target.similarity(doc2))
print(target.similarity(doc3))
                
#token
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)
for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
    
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

#chunking
doc = nlp(u"First American Financial exposed 16 years worth of mortgage paperwork including bank accounts.")
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)

#named entity
doc = nlp(u"I am planning to go to London in the morning at 10am, I have to buy a HP laptop and 2 speakers for less than 1000 dollars. I hope America and China tradewar won't affect prices.")
for ent in doc.ents:
  print(ent.text, ent.label_, ent.start_char, ent.end_char)
#displacy.render(doc, style='ent', jupyter=True)
displacy.render(doc, style='ent')

train_data = [
    ("Who is Chaka Khan?", [(7, 17, "PERSON")]),
    ("I like London and Berlin.", [(7, 13, "LOC"), (18, 24, "LOC")]),
]

doc = Doc(nlp.vocab, ["rats", "make", "good", "pets"])
gold = GoldParse(doc, entities=["U-ANIMAL", "O", "O", "O"])


'''
>>> print(en.meta["labels"]["parser"])
['ROOT', 'acl', 'acomp', 'advcl', 'advmod', 'agent', 'amod', 'appos', 'attr', 'aux', 'auxpass', 'case', 'cc', 'ccomp', 'compound', 'conj', 'csubj', 'csubjpass', 'dative', 'dep', 'det', 'dobj', 'expl', 'intj', 'mark', 'meta', 'neg', 'nmod', 'npadvmod', 'nsubj', 'nsubjpass', 'nummod', 'oprd', 'parataxis', 'pcomp', 'pobj', 'poss', 'preconj', 'predet', 'prep', 'prt', 'punct', 'quantmod', 'relcl', 'xcomp']
>>> print(en.meta["labels"]["tagger"])
['$', "''", ',', '-LRB-', '-RRB-', '.', ':', 'ADD', 'AFX', 'CC', 'CD', 'DT', 'EX', 'FW', 'HYPH', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NFP', 'NN', 'NNP', 'NNPS', 'NNS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', 'XX', '_SP', '``']
'''

