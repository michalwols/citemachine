from collections import Counter, defaultdict
from nltk import word_tokenize
from citemachine.util import stem_all, BiDirMap, filter_dict
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords


class CorpusPreprocessor(object):
    """Class used to preprocess textual data from the provided corpus

    The preprocessor generates the following attributes:

      words: dict from doc id to list of preprocessed words of the document
      number_encodings: dict from doc id to number encoded word vector,
                        which is a list of tuples of the form
                        (word_id, word_count)
      id_to_word_map: map from word_id to word, which is only public because
                        it is used by the LDA.
                        *For normal id to word lookup use the 'to_word' method
    """

    def __init__(self, corpus, tokenize=None, stemmer=None,
                 excluded_words=None, is_valid_word=None, min_word_count=5,
                 max_word_count=500):
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
            min_word_count / max_word_count: words with counts outside of that
                    range are discarded
        """
        self._corpus = corpus
        self._word_counts = defaultdict(int)

        self._initialize_preprocessing_tools(tokenize, stemmer, excluded_words,
                                             is_valid_word)
        self._preprocess_documents(min_word_count, max_word_count)
        self._generate_number_encodings()

    @property
    def id_to_word_map(self):
        """Dictionary from word id to word"""
        return self._word_to_id_map.val_to_key

    def preprocess_text(self, text):
        """Turns a string of text into a representation that is consistent
        with the representation used for the original corpus
        """
        words = self._split_text(text)
        valid_words = self._filter_words(words)

        return valid_words

    def number_encode(self, words):
        """Turns a list of preprocessed words into a number encoded word
        vector"""
        words_as_numbers = (self.to_id(word) for word in words)
        return Counter(words_as_numbers).most_common()

    def text_to_number_encoding(self, text):
        """Turns a string of text into a number encoded word vector"""
        words = self.preprocess_text(text)
        return self.number_encode(words)

    def to_id(self, word):
        """Returns the unique identifier of the word"""
        return self._word_to_id_map[word]

    def to_word(self, word_id):
        """Returns the word that corresponds to the unique identifier"""
        return self._word_to_id_map.get_key(word_id)

    def _initialize_preprocessing_tools(self, tokenize, stemmer,
                                        excluded_words, is_valid_word):
        if stemmer:
            self.stemmer = stemmer
        else:
            self.stemmer = LancasterStemmer()

        if excluded_words:
            self.excluded_words = set(stem_all(excluded_words, self.stemmer))
        else:
            self.excluded_words = set(stem_all(stopwords.words('english'),
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

    def _preprocess_documents(self, min_word_count, max_word_count):
        word_to_id_map = BiDirMap()
        words = {}
        word_counts = self._word_counts
        cur_word_id = 0
        texts = self._corpus.texts
        split_text = self._split_text
        filter_words = self._filter_words

        for doc_id in texts.keys():
            ws = split_text(texts[doc_id])

            for word in ws:
                word_counts[word] += 1
                if word not in word_to_id_map:
                    word_to_id_map.add(word, cur_word_id)
                    cur_word_id += 1

            words[doc_id] = ws

        # need to remove rare and popular words
        is_valid = self.is_valid_word
        for word in word_counts.keys():
            if (not (min_word_count <= word_counts[word] <= max_word_count)) or (not is_valid(word)):
                word_counts.pop(word, 0)

        # words that remain in word counts become the dictionary of the preprocessor
        # all other words will be ignored
        self._valid_words = set(word_counts.keys())
        del word_counts

        for doc_id in words.keys():
            words[doc_id] = filter_words(words[doc_id])

        self._word_to_id_map = word_to_id_map
        self.words = words

    def _split_text(self, text):
        words = self.tokenize(text)
        words = [word.rstrip('.') for word in words]
        words = stem_all(words, self.stemmer)
        return words

    def _filter_words(self, words):
        valid_words = self._valid_words
        return [w for w in words if w in valid_words]

    def _generate_number_encodings(self):
        self.number_encodings = {doc: self.number_encode(self.words[doc])
                                      for doc in self.words}
