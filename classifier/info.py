from __future__ import division
from pprint import pprint
from math import log, exp
from operator import mul
from collections import Counter
from collections import defaultdict
from nltk.corpus import stopwords
import itertools
import sys
import glob
import errno
import os
import pylab
import csv
import json
import cPickle


class MyDict(dict):
    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return 0

stop = stopwords.words("english")
pos = MyDict()
neg = MyDict()
features = set()
totals = {'pos': 0, 'neg':0}
delchars = ''.join(c for c in map(chr, range(128)) if not c.isalnum())

CDATA_FILE = "countdata.pickle"
FDATA_FILE = "reduceddata.pickle"

POS_PATH = "../trainingdata/pos"
NEG_PATH = "../trainingdata/neg"

def negate_sequence(text):
    """
    Detects negations and transforms negated words into "not_" form.
    """
    negation = False
    delims = "?.,!:;"
    result = []
    words = text.split()
    prev = None
    pprev = None
    for word in words:
        # stripped = word.strip(delchars)
        stripped = word.strip(delims).lower()
        negated = "not_" + stripped if negation else stripped
        result.append(negated)
        if prev:
            bigram = prev + " " + negated
            result.append(bigram)
            if pprev:
                trigram = pprev + " " + bigram
                result.append(trigram)
            pprev = prev
        prev = negated

        if any(neg in word for neg in ["not", "n't", "no"]):
            negation = not negation

        if any(c in word for c in delims):
            negation = False

    return result

def train():
    print "Training Dataset"
    global pos, neg, totals
    retrain = False

    # Load counts if they already exist.
    # if not retrain and os.path.isfile(CDATA_FILE):
    #     pos, neg, totals = cPickle.load(open(CDATA_FILE))
    #     return

    # Cornell Movie Review Data
    # for file in os.listdir(POS_PATH):
    #     for word in set(negate_sequence(open(POS_PATH + '/' + file).read())):
    #         pos[word] += 1
    #         neg['not_' + word] += 1
    # for file in os.listdir(NEG_PATH):
    #     for word in set(negate_sequence(open(NEG_PATH + '/' + file).read())):
    #         neg[word] += 1
    #         pos['not_' + word] += 1

    with open('../trainingdata/twitter_training_data.csv', 'rU') as csvfile:
        tweets = csv.reader(csvfile)
        # numpos = 0
        # numneg = 0
        # limit = 35000
        for row in tweets:
            if row[0] == '4': # positive
                word_set = negate_sequence(row[1])
                unigrams(word_set, True)
                bigrams(word_set, True)
            elif row[0] == '0': # negative
                word_set = negate_sequence(row[1])
                unigrams(word_set, False)
                bigrams(word_set, False)

    # Hand Selected Yaks
    # for yak in training_data['yaks']:
    #     for word in set(negate_sequence(yak['message'])):
    #         # if word.lower() in stop:
    #             # continue
    #         if yak['sentiment'] == 'positive':
    #             pos[word] += 1
    #             neg['not_' + word] += 1
    #         elif yak['sentiment'] == 'negative':
    #             neg[word] += 1
    #             pos['not_' + word] += 1

    prune_features()

    totals['pos'] = sum(pos.values())
    totals['neg'] = sum(neg.values())

    countdata = (pos, neg, totals)
    cPickle.dump(countdata, open(CDATA_FILE, 'w'))

def unigrams(word_set, sentiment):
    for word in word_set:
        if sentiment:
            pos[word] += 1
            neg['not_'+word] += 1
        else:
            neg[word] += 1
            pos['not_'+word] += 1

def bigrams(word_set, sentiment):
    for w1, w2 in itertools.izip(word_set, word_set[1:]):
        if sentiment:
            pos[w1+' '+w2] += 1
        else:
            neg[w1+' '+w2] += 1

def prune_features():
    """
    Remove features that appear only once.
    """
    global pos, neg
    for k in pos.keys():
        if pos[k] <= 1 and neg[k] <= 1:
            del pos[k]

    for k in neg.keys():
        if neg[k] <= 1 and pos[k] <= 1:
            del neg[k]

if __name__ == '__main__':
    train()
