from nltk.corpus import wordnet as wn
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

if __name__ == '__main__':
    test()
    
'''
>>> good = wn.synset('good.a.01')
>>> good.antonyms()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Synset' object has no attribute 'antonyms'
>>> good.lemmas()[0].antonyms()
[Lemma('bad.a.01.bad')]
'''
