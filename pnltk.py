import nltk
from nltk.corpus import gutenberg
from nltk.corpus import webtext
from nltk.corpus import nps_chat
from nltk.corpus import brown
from nltk.corpus import reuters
from nltk.corpus import inaugural

from nltk.corpus import stopwords

# a silly implementation
#nltk.chat.chatbots()

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


