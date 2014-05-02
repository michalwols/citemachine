from collections import Counter
from nltk import word_tokenize
from citemachine.util import stem_all, BiDirMap
import nltk


class CorpusPreprocessor(object):
    """Class used to preprocess textual data from the provided corpus"""

    def __init__(self, corpus, tokenize=None, stemmer=None,
                 excluded_words=None, is_valid_word=None):
        """
        Args:
            corpus: corpus object, which should contain a 'texts' dictionary
                    mapping from document ids to the text of the document
            tokenize: function used to tokenize the text
            stemmer: stemming object, with method 'stem' which takes a word
                    and returns a stemmed version of it
            excluded_words: list of words that should be excluded from the
                    final representation of the documents (stopwords)
            is_valid_word: function used for further filtering,
                    should take in a single word and return True or False
        """
        if stemmer:
            self.stemmer = stemmer
        else:
            self.stemmer = nltk.stem.lancaster.LancasterStemmer()

        if excluded_words:
            self.excluded_words = set(stem_all(excluded_words, self.stemmer))
        else:
            self.excluded_words = set(stem_all(nltk.corpus.stopwords.words('english'),
                                      self.stemmer))

        if is_valid_word is None:
            self.is_valid_word = lambda word: (len(word) > 2) and \
                                              (word not in self.excluded_words)
        else:
            self.is_valid_word = is_valid_word

        if tokenize is None:
            self.tokenize = word_tokenize
        else:
            self.tokenize = tokenize

        self._corpus = corpus
        self._preprocess()

    def _preprocess(self):

        word_num_map = BiDirMap()
        words = {}
        cur_word_id = 0

        # store as local vars to avoid slow attribute lookups in tight loop
        texts = self._corpus.texts
        stemmer = self.stemmer
        tokenize = self.tokenize
        is_valid_word = self.is_valid_word

        for doc_id in texts.keys():

            ws = tokenize(texts[doc_id])
            ws = [word.rstrip('.') for word in ws]
            ws = stem_all(ws, stemmer)
            ws = filter(is_valid_word, ws)

            for word in ws:
                if word not in word_num_map:
                    word_num_map.add(word, cur_word_id)
                    cur_word_id += 1

            words[doc_id] = ws

        self._word_num_map = word_num_map
        self.words = words

    def to_number(self, word):
        """Returns the unique identifier of the word"""
        return self._word_num_map[word]

    def to_word(self, word_number):
        """Returns the word that corresponds to the unique identifier"""
        return self._word_num_map.get_key(word_number)

    def generate_number_encodings(self):
        """Generates a new attribute called 'number_encodings', which is a
        dictionary that maps from doc id to a list of tuples of words
        represented as their ids and their count in the document.

            [(word_id, word_count), ...]
        """
        # store as local vars to avoid slow attribute lookups in tight loop
        number_encodings = {}
        to_number = self.to_number
        words = self.words

        for doc_id in self._corpus.ids():
            words_as_nums = (to_number(word) for word in words[doc_id])
            number_encodings[doc_id] = Counter(words_as_nums).most_common()

        self.number_encodings = number_encodings

    def number_encoded_corpus(self):

        if not hasattr(self, 'number_encodings'):
            self.generate_number_encodings()

        for doc_id in self._corpus.ids():
            yield self.number_encodings[doc_id]
