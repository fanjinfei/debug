# -*- coding: utf-8 -*-
#YATL; yet another try language (understanding)
from __future__ import division, print_function
from random import randint
import nltk, sys
import re
import pprint
from nltk import word_tokenize
from nltk import load_parser

from nltk.corpus import wordnet as wn #wordnet
from nltk.corpus import gutenberg, nps_chat
from nltk.corpus import brown
from nltk.corpus import conll2000
from nltk.corpus import treebank
#from urllib import request
import requests
import networkx as nx

from sympy import *
from sympy import symbols
from sympy import expand, factor
import math
import numpy



'''
system architecture
Principle: No hard-code rules of parsing; no strict/consistent logic in sentence meaning
1. building blocks
  word -> lemma, lexicon relation
  grammar -> syntax, tense, singluar/plural
  word -> grammar
  phrase -> grammar
  sentence -> grammar( FOL, quantifier)
  Discourse(multi-sentence) -> space/time serials (Temporal Reasoning in Natural Language Processing)
    anaphoric antecedent --> discourse referents: 
    Cataphora (included in the broad sense of anaphora, species of endophora)
       a. Because he was very cold, David put on his coat
    Sarcasm

2. training building blocks
  tagged samples -> rules (regex/function, dictionary)?

3. build context
  samples -> word -> phrase ->sentence -> predicate -> (lambda + entities net)
  Sympy.lambdify or lamby or self built FOL(first order logic) processor
  How to handle time related context? (past, present, future, date, etc)

4. output
  apply strategy (dialogue/essay/summary) -> set of (lamda/entities) -> reduction -> formating (NLG-generation)

'''
