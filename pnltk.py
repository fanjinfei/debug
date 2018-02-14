# -*- coding: utf-8 -*-

from random import randint
import nltk, sys
import re
import pprint
from nltk import word_tokenize
from nltk.corpus import wordnet as wn #wordnet
from nltk.corpus import gutenberg, nps_chat
from nltk.corpus import brown
from nltk.corpus import conll2000
#from urllib import request
import requests
import networkx as nx
import matplotlib
# from __future__ import print_function

# a silly implementation
#nltk.chat.chatbots()

#chapter 02
print 'example motocar car.n.01'
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
print 'tree part meronyms', wn.synset('tree.n.01').part_meronyms()
print 'tree substance meronyms', wn.synset('tree.n.01').substance_meronyms()
print 'tree member holonyms', wn.synset('tree.n.01').member_holonyms()

for synset in wn.synsets('mint', wn.NOUN):
    print(synset.name() + ':', synset.definition())
print 'mint part holonyms', wn.synset('mint.n.04').part_holonyms()
print 'mint substance holonyms',wn.synset('mint.n.04').substance_holonyms()

print '\n-------- verb entails ----------'
print 'walk', wn.synset('walk.v.01').entailments()
print 'eat', wn.synset('eat.v.01').entailments()

print '\n------------- antonym ------------'
print 'supply antonym', wn.lemma('supply.n.02.supply').antonyms()
print 'rush antonym', wn.lemma('rush.v.01.rush').antonyms()

#semantic similarity
print '\n------------- semantic similarity ------------'
right = wn.synset('right_whale.n.01')
orca = wn.synset('orca.n.01')
minke = wn.synset('minke_whale.n.01')
tortoise = wn.synset('tortoise.n.01')
novel = wn.synset('novel.n.01')
print 'right_whale lowest common hypernym with mink_whale', right.lowest_common_hypernyms(minke)
print right.lowest_common_hypernyms(orca)
print right.lowest_common_hypernyms(tortoise)
print right.lowest_common_hypernyms(novel)

print right.min_depth()
print wn.synset('baleen_whale.n.01').min_depth()
print wn.synset('whale.n.02').min_depth()
print wn.synset('vertebrate.n.01').min_depth()
print wn.synset('entity.n.01').min_depth()

#process raw text, chapter 03
print '\n--- chap 03 -regex raw word pattern/text ---'
def stem(word):
    regexp = r'^(.*?)(ing|ly|ed|ious|ies|ive|es|s|ment)?$'
    stem, suffix = re.findall(regexp, word)[0]
    return stem

raw = """DENNIS: Listen, strange women lying in ponds distributing swords
is no basis for a system of government.  Supreme executive power derives from
a mandate from the masses, not from some farcical aquatic ceremony."""
tokens = word_tokenize(raw)
print [stem(t) for t in tokens]

moby = nltk.Text(gutenberg.words('melville-moby_dick.txt'))
print moby.findall(r"<a> (<.*>) <man>")
print moby.findall(r"<a> <.*> <man>")

print '\n--- word stemming ----------'
porter = nltk.PorterStemmer()
lancaster = nltk.LancasterStemmer()
wnl = nltk.WordNetLemmatizer()
print 'Porter stemmer:', [porter.stem(t) for t in tokens]
print 'Lancaster stemmer:', [lancaster.stem(t) for t in tokens]
print 'WN lemmatizer:', [wnl.lemmatize(t) for t in tokens]

print '\n------ sentence segmentation -----'
text = nltk.corpus.gutenberg.raw('chesterton-thursday.txt')
sents = nltk.sent_tokenize(text)
pprint.pprint(sents[79:89])

print'\n---- word segmentation ---' #like speech
def segment(text, segs):
    words = []
    last = 0
    for i in range(len(segs)):
        if segs[i] == '1':
            words.append(text[last:i+1])
            last = i+1
    words.append(text[last:])
    return words
def evaluate(text, segs):
    words = segment(text, segs)
    text_size = len(words)
    lexicon_size = sum(len(word) + 1 for word in set(words))
    return text_size + lexicon_size
def flip(segs, pos):
    return segs[:pos] + str(1-int(segs[pos])) + segs[pos+1:]

def flip_n(segs, n):
    for i in range(int(n)):
        segs = flip(segs, randint(0, len(segs)-1))
    return segs

def anneal(text, segs, iterations, cooling_rate):
    temperature = float(len(segs))
    while temperature > 0.5:
        best_segs, best = segs, evaluate(text, segs)
        for i in range(iterations):
            guess = flip_n(segs, round(temperature))
            score = evaluate(text, guess)
            if score < best:
                best, best_segs = score, guess
        score, segs = best, best_segs
        temperature = temperature / cooling_rate
        print(evaluate(text, segs), segment(text, segs))
    print()
    return segs
text = "doyouseethekittyseethedoggydoyoulikethekittylikethedoggy"
seg1 = "0000000000000001000000000010000000000000000100000000000"
print 'Anneal:', 'skipped' #anneal(text, seg1, 5000, 1.2)
print "shoud be: 43 ['doyou', 'see', 'thekitty', 'see', 'thedoggy', 'doyou', 'like', 'thekitty', 'like', 'thedoggy']"

print '\n-----chap 04 --- network X - python programming-----'
def traverse(graph, start, node):
    graph.depth[node.name] = node.shortest_path_distance(start)
    for child in node.hyponyms():
        graph.add_edge(node.name, child.name)
        traverse(graph, start, child)

def hyponym_graph(start):
    G = nx.Graph()
    G.depth = {}
    traverse(G, start, start)
    return G

def graph_draw(graph):
    from networkx.drawing.nx_agraph import graphviz_layout
#sudo apt install libgraphviz-dev
#pip install pygraphviz
    pos = graphviz_layout(graph)
    #nx.draw(graph, pos)
    nx.draw_networkx(graph, 
         node_size = [16 * graph.degree(n) for n in graph],
         node_color = [graph.depth[n] for n in graph],
         with_labels = False)
#
#    nx.drawing.draw_graphviz(graph,
#         node_size = [16 * graph.degree(n) for n in graph],
#         node_color = [graph.depth[n] for n in graph],
#         with_labels = False)
    matplotlib.pyplot.show()

dog = wn.synset('dog.n.01')
graph = hyponym_graph(dog)
print 'draw graph skipped' #graph_draw(graph)

print '\n---- chap 05 categorize/tagging word --------------'
#Concept: part-of-speech tagging, POS-tagging, or simply tagging. 
#Parts of speech are also known as word classes or lexical categories.
text = word_tokenize("And now for something completely different")
print 'Part of speech:', nltk.pos_tag(text)
# CC: coordinating conjunction
# RB: adverbs
# IN: a preposition
# NN: noun
# JJ: an adjective.
#NLTK provides documentation for each tag, which can be queried using the tag, e.g. nltk.help.upenn_tagset('RB'), or a regular expression, e.g. nltk.help.upenn_tagset('NN.*'). Some corpora have README files with tagset documentation, see  nltk.corpus.???.readme(), substituting in the name of the corpus.
#
text = word_tokenize("They refuse to permit us to obtain the refuse permit")
print nltk.pos_tag(text)
text = 'The woman bought over $150,000 worth of clothes.'
print nltk.pos_tag(word_tokenize(text))

# VBP: present tense verb
# VBD: past tense verb
# VBN: past participle
# DT: determiner (the,a, an)
# TO: "to" as preposition or infinitive marker
# NNS: noun plural
# PRP: pronoun, personal

'''
Lexical categories like "noun" and part-of-speech tags like NN seem to have their uses, but the details will be obscure to many readers. You might wonder what justification there is for introducing this extra level of information. Many of these categories arise from superficial analysis the distribution of words in text. Consider the following analysis involving woman (a noun), bought (a verb), over (a preposition), and the (a determiner). The text.similar() method takes a word w, finds all contexts w1w w2, then finds all words w' that appear in the same context, i.e. w1w'w2.
'''
# universal tagset is different from pos_tag ???
print nltk.corpus.brown.tagged_words(tagset='universal')[:10]
'''
Universal Part-of-Speech Tagset

Tag	Meaning	English Examples
ADJ	adjective	new, good, high, special, big, local
ADP	adposition	on, of, at, with, by, into, under
ADV	adverb	really, already, still, early, now
CONJ	conjunction	and, or, but, if, while, although
DET	determiner, article	the, a, some, most, every, no, which
NOUN	noun	year, home, costs, time, Africa
NUM	numeral	twenty-four, fourth, 1991, 14:24
PRT	particle	at, on, out, over per, that, up, with
PRON	pronoun	he, their, her, its, my, I, us
VERB	verb	is, say, told, given, playing, would
.	punctuation marks	. , ; !
X	other	ersatz, esprit, dunno, gr8, univeristy
'''
brown_news_tagged = brown.tagged_words(categories='news', tagset='universal')
tag_fd = nltk.FreqDist(tag for (word, tag) in brown_news_tagged)
print 'tagged news:', tag_fd.most_common()

wsj = nltk.corpus.treebank.tagged_words(tagset='universal')
wsj = nltk.corpus.treebank.tagged_words()
cfd1 = nltk.ConditionalFreqDist(wsj)
print [w for w in cfd1.conditions() if 'VBD' in cfd1[w] and 'VBN' in cfd1[w]][:10]
idx1 = wsj.index(('kicked', 'VBD'))
idx2 = wsj.index(('kicked', 'VBN'))
print wsj[idx1-4:idx1+1]
print wsj[idx2-4:idx2+1]

'''
English has several categories of closed class words in addition to prepositions, such as articles (also often called determiners) (e.g., the, a), modals (e.g., should, may), and personal pronouns (e.g., she, they). Each dictionary and grammar classifies these words differently.
'''

print '\n--- tagger --- (regex, lookup) ----'
patterns = [
    (r'.*ing$', 'VBG'),               # gerunds
    (r'.*ed$', 'VBD'),                # simple past
    (r'.*es$', 'VBZ'),                # 3rd singular present
    (r'.*ould$', 'MD'),               # modals
    (r'.*\'s$', 'NN$'),               # possessive nouns
    (r'.*s$', 'NNS'),                 # plural nouns
    (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal numbers
    (r'.*', 'NN')                     # nouns (default)
]
regexp_tagger = nltk.RegexpTagger(patterns)
brown_sents = brown.sents(categories='news')
brown_tagged_sents = brown.tagged_sents(categories='news')
print regexp_tagger.tag(brown_sents[3])
print regexp_tagger.evaluate(brown_tagged_sents)

#nltk.tag.brill.demo() # sequence if-then-else
#nltk.tbl.demo.demo() #re-organized nltk demo, Accuracy 0.8551
print '\n -- training Brill tagger: skipped --'
print 'linguists use morphological, syntactic, and semantic clues to determine the category of a word'
print '''Some morphosyntactic distinctions in the Brown tagset

Form	Category	Tag
go	base	VB
goes	3rd singular present	VBZ
gone	past participle	VBN
going	gerund	VBG
went	simple past	VBD'''

print '\n---- chap 06 text classification ---un*/supervised------'
print '#feature extraction'
print '#document classification: positve/negative review -- NaiveBayesian ----'
print '\t more: nltk.NaiveBayesClassifier.train(train_set) nltk.DecisionTreeClassifier.train()'
print '\t More:--  Sequence Classification (greedy?) Seq-Score?'

print '\n -- Sentence segementation --, diaglogue act type'
print '\t 15 dialogue act types, such as "Statement," "Emotion," "ynQuestion", and "Continuer."'
print '''\t performative statements such as "I forgive you" or "I bet you can't climb that hill." But greetings, questions, answers, assertions, and clarifications can all be thought of as types of speech-based actions.'''

print '\n ------ Recognizing textual entailment (RTE) is the task of determining whether a given piece of text T entails another text called the "hypothesis" (as already discussed in 5). To date, there have been four RTE Challenges'

print '\n ------ chap 07 Extracting Information from Text --- STRUCTUREd here (chap 10, general)-----'
print '''1. How can we build a system that extracts structured data, such as tables, from unstructured text?
2. What are some robust methods for identifying the entities and relationships described in a text?
3. Which corpora are appropriate for this work, and how do we use them for training and evaluating our models?'''
print '\n -- 07.02 chunking -- \n\t Noun-Phrase(NP) -- simple regex chunker grammar \n\t tag pattern'

#these POS tag are not easy to decide !!
sentence = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"),
            ("dog", "NN"), ("barked", "VBD"), ("at", "IN"),  ("the", "DT"), ("cat", "NN")]
sent1 = [ ('another', 'DT'), ('sharp', 'JJ'), ('dive', 'NN'),
	('trade','NN'), ('figures','NNS'),
	('any','DT'), ('new','JJ'), ('policy','NN'), ('measures','NNS'),
	('earlier','JJR'),  ('stages','NNS'),
	('Panamanian','JJ'), ('dictator','NN'), ('Manuel','NNP'), ('Noriega','NNP') ]
grammar = "NP: {<DT>?<JJ>*<NN>}"
cp = nltk.RegexpParser(grammar)
print cp.parse(sentence)
cp1 = nltk.RegexpParser("NP: {<DT>?<JJ.*>*<NN.*>+}")
print cp1.parse(sent1)

#more grammar regex
grammar = r"""
  NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
      {<NNP>+}                # chunk sequences of proper nouns
"""
cp = nltk.RegexpParser(grammar)
sentence = [("Rapunzel", "NNP"), ("let", "VBD"), ("down", "RP"),
                 ("her", "PP$"), ("long", "JJ"), ("golden", "JJ"), ("hair", "NN")]
print cp.parse(sentence)

grammar = r"""
  NP:
    {<.*>+}          # Chunk everything
    }<VBD|IN>+{      # Chink sequences of VBD and IN
  """
sentence = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"),
       ("dog", "NN"), ("barked", "VBD"), ("at", "IN"),  ("the", "DT"), ("cat", "NN")]
cp = nltk.RegexpParser(grammar)
print(cp.parse(sentence))

text = '''
he PRP B-NP
accepted VBD B-VP
the DT B-NP
position NN I-NP
of IN B-PP
vice NN B-NP
chairman NN I-NP
of IN B-PP
Carlyle NNP B-NP
Group NNP I-NP
, , O
a DT B-NP
merchant NN I-NP
banking NN I-NP
concern NN I-NP
. . O
'''
#nltk.chunk.conllstr2tree(text, chunk_types=['NP']).draw()
print 'draw sentence tree: skipped'
print('training text:', conll2000.chunked_sents('train.txt')[99])

#recursive grammar, vs full parsing
grammar = r"""
  NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
  PP: {<IN><NP>}               # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}           # Chunk NP, VP
  """
cp = nltk.RegexpParser(grammar)
sentence = [("Mary", "NN"), ("saw", "VBD"), ("the", "DT"), ("cat", "NN"),
    ("sit", "VB"), ("on", "IN"), ("the", "DT"), ("mat", "NN")]
print(cp.parse(sentence))

sentence = [("John", "NNP"), ("thinks", "VBZ"), ("Mary", "NN"),
    ("saw", "VBD"), ("the", "DT"), ("cat", "NN"), ("sit", "VB"),
    ("on", "IN"), ("the", "DT"), ("mat", "NN")]
print(cp.parse(sentence))
cp = nltk.RegexpParser(grammar, loop=2)
print(cp.parse(sentence))

#tree
tree1 = nltk.Tree('NP', ['Alice'])
tree2 = nltk.Tree('NP', ['the', 'rabbit'])
tree3 = nltk.Tree('VP', ['chased', tree2])
tree4 = nltk.Tree('S', [tree1, tree3])
print(tree4)

def traverse(t):
    try:
        t.label()
    except AttributeError:
        print(t+ " ")
    else:
        # Now we know that t.node is defined
        print('(' + t.label()+ " ")
        for child in t:
            traverse(child)
        print(')'+ " ")

#t = nltk.Tree('(S (NP Alice) (VP chased (NP the rabbit)))')
t = tree4
traverse(t)

print '\n ---- identify named entity recognition (NER) ------'
print '\t May and North are likely to be parts of named entities for DATE and LOCATION, respectively, but could both be part of a PERSON; conversely Christian Dior looks like a PERSON but is more likely to be of type ORGANIZATION.'
sent = nltk.corpus.treebank.tagged_sents()[22]
print(' '.join(str(nltk.ne_chunk(sent, binary=True)).split()))
print(' '.join(str(nltk.ne_chunk(sent)).split()))

print '\n ----------  relation extraction -------------'
IN = re.compile(r'.*\bin\b(?!\b.+ing)')
for doc in nltk.corpus.ieer.parsed_docs('NYT_19980315'):
    for rel in nltk.sem.extract_rels('ORG', 'LOC', doc,
                                     corpus='ieer', pattern = IN):
        print(nltk.sem.rtuple(rel))

print '\n ----- chap 08 Analyzing Sentence Structure -------------------'
print '\tHaving read in a text, can a program "understand" it enough to be able to answer simple questions about "what happened" or "who did what to whom"?'
groucho_grammar = nltk.CFG.fromstring("""
S -> NP VP
PP -> P NP
NP -> Det N | Det N PP | 'I'
VP -> V NP | VP PP
Det -> 'an' | 'my'
N -> 'elephant' | 'pajamas'
V -> 'shot'
P -> 'in'
""")
sent = ['I', 'shot', 'an', 'elephant', 'in', 'my', 'pajamas']
parser = nltk.ChartParser(groucho_grammar)
for tree in parser.parse(sent):
    print(tree)

print '\n--- ## use syntax to parse sentence: Content Free Grammar##'
grammar1 = nltk.CFG.fromstring("""
  S -> NP VP
  VP -> V NP | V NP PP
  PP -> P NP
  V -> "saw" | "ate" | "walked"
  NP -> "John" | "Mary" | "Bob" | Det N | Det N PP
  Det -> "a" | "an" | "the" | "my"
  N -> "man" | "dog" | "cat" | "telescope" | "park"
  P -> "in" | "on" | "by" | "with"
  """)
# grammar1 = nltk.data.load('file:mygrammar.cfg') load it from disk file
sent = "Mary saw Bob".split()
rd_parser = nltk.RecursiveDescentParser(grammar1)
for tree in rd_parser.parse(sent):
     print(tree)


grammar2 = nltk.CFG.fromstring("""
  S  -> NP VP
  NP -> Det Nom | PropN
  Nom -> Adj Nom | N
  VP -> V Adj | V NP | V S | V NP PP
  PP -> P NP
  PropN -> 'Buster' | 'Chatterer' | 'Joe'
  Det -> 'the' | 'a'
  N -> 'bear' | 'squirrel' | 'tree' | 'fish' | 'log'
  Adj  -> 'angry' | 'frightened' |  'little' | 'tall'
  V ->  'chased'  | 'saw' | 'said' | 'thought' | 'was' | 'put'
  P -> 'on'
  """)
sent = "the angry bear chased the frightened little squirrel".split()
rd_parser = nltk.RecursiveDescentParser(grammar2)
for tree in rd_parser.parse(sent):
     print(tree)



sys.exit(0) #done following test

''' chaper 01
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
