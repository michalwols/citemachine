import nltk
from collections import defaultdict


def count_words(word_list, counts_dict=None):

    if not counts_dict:
        counts_dict = defaultdict(int)

    for word in word_list:
        counts_dict[word] += 1

    return counts_dict


def filter_dict(func, dictionary):
    """Filter a dictionary *in place* based on filter function

    Args:
        func: func(key, value), returns ture if item should be retained,
            false otherwise
        dictionary: dict to be filtered
    """
    for key in dictionary.keys():
        if not func(key, dictionary[key]):
            dictionary.pop(key, 0)

    return dictionary


def stem_all(words, stemmer):

    return [stemmer.stem(w) for w in words]


class BiDirMap(object):
    """Bidirectional Map, for quick key->value and value->key lookup"""

    def __init__(self):
        self.key_to_val = {}
        self.val_to_key = {}

    def __contains__(self, key):
        return key in self.key_to_val

    def add(self, key, value):
        self.key_to_val[key] = value
        self.val_to_key[value] = key

    def get_key(self, value):
        return self.val_to_key(value)

    def get_value(self, key):
        return self.key_to_val(key)
