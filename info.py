from __future__ import division
from math import log, exp
from operator import mul
from collections import Counter
import json
import os
import pylab
import cPickle


class MyDict(dict):
    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return 0

pos = MyDict()
neg = MyDict()
features = set()
totals = [0, 0]
delchars = ''.join(c for c in map(chr, range(128)) if not c.isalnum())

CDATA_FILE = "countdata.pickle"
FDATA_FILE = "reduceddata.pickle"

training_data=open('training_data')
data = json.load(json_data)
training_data.close()

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
    global pos, neg, totals
    retrain = False

    # Load counts if they already exist.
    if not retrain and os.path.isfile(CDATA_FILE):
        pos, neg, totals = cPickle.load(open(CDATA_FILE))
        return

    for school in data:
        for yak in data[school]['yaks']:
            for word in yak['message']:
                if yak['sentiment'] == 'positive':
                    pos[word] += 1
                    neg['not_' + word] += 1
                elif yak['sentiment'] == 'negative':
                    neg[word] += 1
                    pos['not_' + word] += 1
                else:
                    neutral[word] += 1


    prune_features()

    totals[0] = sum(pos.values())
    totals[1] = sum(neutral.values())
    totals[2] = sum(neg.values())

    countdata = (pos, neg, totals)
    cPickle.dump(countdata, open(CDATA_FILE, 'w'))

def classify(text):
    words = set(word for word in negate_sequence(text) if word in features)
    if (len(words) == 0): return True
    # Probability that word occurs in pos documents
    pos_prob = sum(log((pos[word] + 1) / (2 * totals[0])) for word in words)
    neutral_prob = sum(log((neutral[word] + 1) / (2 * totals[1])) for word in words)
    neg_prob = sum(log((neg[word] + 1) / (2 * totals[2])) for word in words)
    return pos_prob > neg_prob

def classify2(text):
    """
    For classification from pretrained data
    """
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0): return True
    # Probability that word occurs in pos documents
    pos_prob = sum(log((pos[word] + 1) / (2 * totals[0])) for word in words)
    neutral_prob = sum(log((neutral[word] + 1) / (2 * totals[1])) for word in words)
    neg_prob = sum(log((neg[word] + 1) / (2 * totals[2])) for word in words)
    return pos_prob > neg_prob

def classify_demo(text):
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0):
        print "No features to compare on"
        return True

    pprob, nprob = 0, 0
    for word in words:
        posp = log((pos[word] + 1) / (2 * totals[0]))
        neutp = log((neutral[word] + 1) / (2 * totals[1]))
        negp = log((neg[word] + 1) / (2 * totals[2]))
        print "%15s %.9f %.9f" % (word, exp(posp), exp(negp))
        pprob += posp
        neutprob += neutp
        nprob += negp

    cls = max(pprob, neutprob, nprob)
    if cls == pprob:
        print "Positive", "prob = %.9f" % pprob
    elif cls == neutprob:
        print "Neutral", "prob = %.9f" % pprob
    else:
        print "Negative", "prob = %.9f" % pprob

def MI(word):
    """
    Compute the weighted mutual information of a term.
    """
    T = totals[0] + totals[1] + totals[2]
    W = pos[word] + neutral[word] + neg[word]
    I = 0
    if W==0:
        return 0
    if neg[word] > 0:
        # doesn't occur in -ve
        I += (totals[2] - neg[word]) / T * log ((totals[2] - neg[word]) * T / (T - W) / totals[2])
        # occurs in -ve
        I += neg[word] / T * log (neg[word] * T / W / totals[2])
    if neutral[word] > 0:
        # doesn't occur in +ve
        I += (totals[1] - neutral[word]) / T * log ((totals[1] - neutral[word]) * T / (T - W) / totals[1])
        # occurs in +ve
        I += neutal[word] / T * log (neutral[word] * T / W / totals[1])
    if pos[word] > 0:
        # doesn't occur in +ve
        I += (totals[0] - pos[word]) / T * log ((totals[0] - pos[word]) * T / (T - W) / totals[0])
        # occurs in +ve
        I += pos[word] / T * log (pos[word] * T / W / totals[0])
    return I

def get_relevant_features():
    pos_dump = MyDict({k: pos[k] for k in pos if k in features})
    neutral_dump = MyDict({k: neutral[k] for k in neutral if k in features})
    neg_dump = MyDict({k: neg[k] for k in neg if k in features})
    totals_dump = [sum(pos_dump.values()), sum(neg_dump.values())]
    return (pos_dump, neutral_dump, neg_dump, totals_dump)

def prune_features():
    """
    Remove features that appear only once.
    """
    global pos, neg, neutral
    for k in pos.keys():
        if pos[k] <= 1 and neg[k] <= 1 and neutral[k] <= 1:
            del pos[k]

    for k in neutral.keys():
        if pos[k] <= 1 and neg[k] <= 1 and neutral[k] <= 1:
            del neutral[k]

    for k in neg.keys():
        if pos[k] <= 1 and neg[k] <= 1 and neutral[k] <= 1:
            del neg[k]

def feature_selection_trials():
    """
    Select top k features. Vary k and plot data
    """
    global pos, neg, totals, features
    retrain = True

    if not retrain and os.path.isfile(FDATA_FILE):
        pos, neg, totals = cPickle.load(open(FDATA_FILE))
        return

    words = list(set(pos.keys() + neg.keys()))
    print "Total no of features:", len(words)
    words.sort(key=lambda w: -MI(w))
    num_features, accuracy = [], []
    bestk = 0
    limit = 500
    path = "./aclImdb/test/"
    step = 500
    start = 20000
    best_accuracy = 0.0
    for w in words[:start]:
        features.add(w)
    for k in xrange(start, 40000, step):
        for w in words[k:k+step]:
            features.add(w)
        correct = 0
        size = 0

        for file in os.listdir(path + "pos")[:limit]:
            correct += classify(open(path + "pos/" + file).read()) == True
            size += 1

        for file in os.listdir(path + "neg")[:limit]:
            correct += classify(open(path + "neg/" + file).read()) == False
            size += 1

        num_features.append(k+step)
        accuracy.append(correct / size)
        if (correct / size) > best_accuracy:
            bestk = k
        print k+step, correct / size

    features = set(words[:bestk])
    cPickle.dump(get_relevant_features(), open(FDATA_FILE, 'w'))

    pylab.plot(num_features, accuracy)
    pylab.show()

def test_pang_lee():
    """
    Tests the Pang Lee dataset
    """
    total, correct = 0, 0
    for fname in os.listdir("txt_sentoken/pos"):
        correct += int(classify2(open("txt_sentoken/pos/" + fname).read()) == True)
        total += 1
    for fname in os.listdir("txt_sentoken/neg"):
        correct += int(classify2(open("txt_sentoken/neg/" + fname).read()) == False)
        total += 1
    print "accuracy: %f" % (correct / total)

if __name__ == '__main__':
    train()
    feature_selection_trials()
    # test_pang_lee()
    # classify_demo(open("pos_example").read())
    # classify_demo(open("neg_example").read())
