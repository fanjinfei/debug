import nltk, sys
from nltk.corpus import wordnet as wn #wordnet

# a silly implementation
#nltk.chat.chatbots()

print'example motocar car.n.01'
print 'synsets:', wn.synsets('motorcar')
print 'lemma_names:', wn.synset('car.n.01').lemma_names()
print 'definition:', wn.synset('car.n.01').definition()
print 'examples:', wn.synset('car.n.01').examples()
print 'lemmas:', wn.synset('car.n.01').lemmas()

print '---------'
print wn.lemma('car.n.01.automobile')
print wn.lemma('car.n.01.automobile').synset()
wn.lemma('car.n.01.automobile').name()


print '--- car ---------'
print 'synsets:', wn.synsets('car')
for synset in wn.synsets('car'):
    print('   lemma names:', synset.lemma_names(), ' for -', synset)
print '   -- all lemmas involve "car" ---'
print '    ', wn.lemmas('car')
for lemma in wn.lemmas('car'):
    print '\t', lemma, lemma.name(), lemma.synset()

#  the concepts that are more specific; the (immediate) hyponyms.
print '--- hierarchy - hyponyms--------------'
motorcar = wn.synset('car.n.01')
types_of_motorcar = motorcar.hyponyms()
print 'motocar hyponyms:', types_of_motorcar[:10]

x = sorted(lemma.name() for synset in types_of_motorcar for lemma in synset.lemmas())
print 'all lemmas in motocar hyponyms\' lemmas:', x[:10]

# hypernyms (more generic)
print '\n--- hypernyms ---'
print motorcar.hypernyms()
paths = motorcar.hypernym_paths()
print len(paths), paths
print 'path0 synset name:', [synset.name() for synset in paths[0]]
print 'path1 synset name:', [synset.name() for synset in paths[1]]
print 'root:', motorcar.root_hypernyms()

#from items to their components (meronyms) or to the things they are contained in (holonyms)
print '\n------ meronyms holohyms ---------'


sys.exit(0) #done following test

'''
from nltk.corpus import gutenberg
from nltk.corpus import webtext
from nltk.corpus import nps_chat
from nltk.corpus import brown
from nltk.corpus import reuters
from nltk.corpus import inaugural

from nltk.corpus import stopwords
from nltk.corpus import swadesh #comparative wordlist
from nltk.corpus import toolbox #toolbox lexicon

print gutenberg.fileids()

emma = gutenberg.words('austen-emma.txt')
print len(emma)

for fileid in gutenberg.fileids():
    continue
    num_chars = len(gutenberg.raw(fileid))
    num_words = len(gutenberg.words(fileid))
    num_sents = len(gutenberg.sents(fileid))
    num_vocab = len(set(w.lower() for w in gutenberg.words(fileid)))
    print(round(num_chars/num_words), round(num_words/num_sents), round(num_words/num_vocab), fileid)

macbeth_sentences = gutenberg.sents('shakespeare-macbeth.txt')
longest_len = max(len(s) for s in macbeth_sentences)

print [s for s in macbeth_sentences if len(s) == longest_len], longest_len

for fileid in webtext.fileids():
    print(fileid, webtext.raw(fileid)[:65], '...')

chatroom = nps_chat.posts('10-19-20s_706posts.xml')
print chatroom[123]

bcg = brown.categories()
news_text = brown.words(categories='news')
print bcg, news_text, brown.words(fileids=['cg22']), brown.sents(categories=['news', 'editorial', 'reviews'])

fdist = nltk.FreqDist(w.lower() for w in news_text)
modals = ['can', 'could', 'may', 'might', 'must', 'will']
for m in modals:
    print(m + ':', fdist[m], ' ')

cfd = nltk.ConditionalFreqDist(
          (genre, word)
          for genre in brown.categories()
          for word in brown.words(categories=genre))
genres = ['news', 'religion', 'hobbies', 'science_fiction', 'romance', 'humor']
modals = ['can', 'could', 'may', 'might', 'must', 'will']
cfd.tabulate(conditions=genres, samples=modals)

print reuters.fileids()[:10]
print reuters.categories()[:10]
print reuters.categories('training/9865')
print reuters.fileids('barley')
print reuters.words('training/9865')[:14]
print reuters.words(['training/9865', 'training/9880'])[:10] # multiple args, for fields, categories
print reuters.words(categories='barley')[:10]

print inaugural.fileids()[:10]
print [fileid[:4] for fileid in inaugural.fileids()][:10]
cfd = nltk.ConditionalFreqDist(
          (target, fileid[:4])
          for fileid in inaugural.fileids()
          for w in inaugural.words(fileid)
          for target in ['america', 'citizen']
          if w.lower().startswith(target))
#cfd.plot() a metplot fig

# A lexical entry consists of a headword (also known as a lemma) along with additional information such as the part of speech and the sense definition. Two distinct words having the same spelling are called homonyms.
def unusual_words(text):
    text_vocab = set(w.lower() for w in text if w.isalpha())
    english_vocab = set(w.lower() for w in nltk.corpus.words.words())
    unusual = text_vocab - english_vocab
    return sorted(unusual)
print unusual_words(nltk.corpus.gutenberg.words('austen-sense.txt'))[:10]

#stopwords, that is, high-frequency words like the, to and also that we sometimes want to filter out of a document before further processing. Stopwords usually have little lexical content, and their presence in a text fails to distinguish it from other texts.
print stopwords.words('english')

# pronouncing dictionary, for speech synthesizers
entries = nltk.corpus.cmudict.entries()
for entry in entries[42371:42379]:
    print(entry)

'''
