import spacy
import sys
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print('python -m spacy download en_core_web_sm')
    sys.exit(0)
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)
