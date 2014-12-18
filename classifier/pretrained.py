"""
Train a naive Bayes classifier from the IMDb reviews data set
"""
from __future__ import division
from math import log, exp
from functools import partial
import re
import os
import random
import itertools
import pickle
import json
import pylab

handle = open("countdata.pickle", "rb")
positive, negative, sums = pickle.load(handle)

def tokenize(text):
    return re.findall("\w+", text)

def negate_sequence(text):
    """
    Detects negations and transforms negated words into "not_" form.
    """
    negation = False
    delims = "?.,!:;"
    result = []
    words = text.split()
    for word in words:
        stripped = word.strip(delims).lower()
        result.append("not_" + stripped if negation else stripped)

        if any(neg in word for neg in frozenset(["not", "n't", "no"])):
            negation = not negation

        if any(c in word for c in delims):
            negation = False
    return result

def get_positive_prob(word):
    return 1.0 * (positive[word] + 1) / (2 * sums['pos'])

def get_negative_prob(word):
    return 1.0 * (negative[word] + 1) / (2 * sums['neg'])

def classify(text, preprocessor=negate_sequence):
    words = preprocessor(text)
    pscore, nscore = 0, 0

    for word in words:
        pscore += log(get_positive_prob(word))
        nscore += log(get_negative_prob(word))

    return pscore > nscore

def classify_demo(text):
    features = set(positive.keys() + negative.keys())
    words = reduce_features_with_bigrams(features, text)
    pscore, nscore = 0, 0

    for word in words:
        pdelta = log(get_positive_prob(word))
        ndelta = log(get_negative_prob(word))
        pscore += pdelta
        nscore += ndelta

    return pscore > nscore, pscore, nscore

def test():
    strings = [
        "This book was quite good.",
        "I think this product is horrible."
    ]
    print map(classify, strings)

def mutual_info(word):
    """
    Finds the mutual information of a word with the training set.
    """
    cnt_p, cnt_n = sums['pos'], sums['neg']
    total = cnt_n + cnt_p
    cnt_x = positive[word] + negative[word]
    if (cnt_x == 0):
        return 0
    cnt_x_p, cnt_x_n = positive[word], negative[word]
    I = [[0]*2]*2
    I[0][0] = (cnt_n - cnt_x_n) * log ((cnt_n - cnt_x_n) * total / cnt_x / cnt_n) / total
    I[0][1] = cnt_x_n * log ((cnt_x_n) * total / (cnt_x * cnt_n)) / total if cnt_x_n > 0 else 0
    I[1][0] = (cnt_p - cnt_x_p) * log ((cnt_p - cnt_x_p) * total / cnt_x / cnt_p) / total
    I[1][1] = cnt_x_p * log ((cnt_x_p) * total / (cnt_x * cnt_p)) / total if cnt_x_p > 0 else 0

    return sum(map(sum, I))

def reduce_features(features, stream):
    return [word for word in negate_sequence(stream) if word in features]

def reduce_features_with_bigrams(features, stream):
    words = []
    word_set = negate_sequence(stream)
    words += [word for word in word_set if word in features]
    for w1, w2 in itertools.izip(word_set, word_set[1:]):
        if w1+' '+w2 in features:
            words.append(w1+' '+w2)
    return words

def feature_selection_experiment(test_set):
    """
    Select top k features. Vary k from 1000 to 50000 and plot data
    """
    keys = positive.keys() + negative.keys()
    sorted_keys = sorted(keys, cmp=lambda x, y: mutual_info(x) > mutual_info(y)) # Sort descending by mutual info
    features = set()
    num_features, accuracy = [], []

    for k in xrange(0, 500000, 5000):
        features |= set(sorted_keys[k:k+5000])
        preprocessor = partial(reduce_features, features)
        # preprocessor = partial(reduce_features_with_bigrams, features)
        correct = 0
        tested = 0
        for filename in test_set:
            with open("../testdata/" + filename) as test_file:
                test_data = json.load(test_file)

            for yak in test_data['yaks']:
                if yak['sentiment'] == 'positive':
                    tested += 1
                    correct += classify(yak['message'], preprocessor) == True
                elif yak['sentiment'] == 'neutral':
                    tested += 1
                    correct += classify(yak['message'], preprocessor) == False

        num_features.append(k+5000)
        accuracy.append(correct / tested)

    pylab.plot(num_features, accuracy)
    pylab.show()

def get_paths():
    """
    Returns supervised paths annotated with their actual labels.
    """
    testfiles = [("../testdata/" + f) for f in os.listdir("../testdata/")]
    return testfiles


def generate_statistics():
    """
    Writes the stats of all of the json files in test data to statistics.txt
    """

    stats_file = open("statistics.txt","w")

    for filename in os.listdir("../universityYaks"):
        with open("../universityYaks/" + filename) as test_file:
            test_data = json.load(test_file)

        positive = 0
        negative = 0

        for yak in test_data['yacks']:
            if classify(yak['message']):
                positive += 1
            else:
                negative += 1

        stats_file.write(filename[:-5] + '\t\t' + 'percent positive: ' + str(float(positive)/len(test_data['yacks'])) + '\tpercent negative: ' + str(float(negative)/len(test_data['yacks'])) + '\n')


if __name__ == '__main__':
    while True:
        commandline = raw_input("Input Sentence: ")
        commandline = commandline.strip()

        (b, _, _) = classify_demo(commandline)
        if b :
            print "Positive"
        else:
            print "Negitive"


