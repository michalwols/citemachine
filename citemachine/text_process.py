from collections import Counter
from nltk import word_tokenize
from citemachine.util import stem_all, BiDirMap
import nltk
import gensim


def num_encode(words_dict, word_num_map):
    """Encodes the documents using the numbers assigned to each word

    Args:
        words_dict: dictionary mapping from document ids to list of words
                    from the document
        word_num_map: dictionary mapping from each word in the corpus to a
                    unique integer
    Returns:
        documents: A list of encoded documents, with each document represented
                   as a list of tuple of the form (word_num, word_count)
    """
    documents = []
    for doc_id in words_dict:

        words = words_dict[doc_id]
        num_encoded = (word_num_map[word] for word in words)
        documents.append(Counter(num_encoded).most_common())

    return documents


def preprocess_documents(text_dict, stemmer=None, excluded_words=None,
                         word_check_func=None):
    """Batch preprocesses the text in each document

    Args:
        text_dict: dictionary from document id to document text
        stemmer: stemming object, which provides a method called stem
        excluded_words: list of words to be excluded from the final
                    representation
        word_check_func: boolean function to further validate each word
    Returns:
        words_dict: dictionary mapping from document id to list of preprocessed
                    words
        word_num_map: bidirectional map from word to unique number and unique
                    number to word
    """
    if not stemmer:
        stemmer = nltk.stem.lancaster.LancasterStemmer()
    if not excluded_words:
        excluded_words = set(stem_all(nltk.corpus.stopwords.words('english'),
                             stemmer))
    else:
        excluded_words = set(stem_all(excluded_words, stemmer))
    if not word_check_func:
        word_check_func = lambda word: (len(word) > 2) and \
                                       (word not in excluded_words)

    word_num_map = BiDirMap()
    words_dict = {}
    cur_word_id = 0

    for doc_id, text in text_dict.items():

        words = word_tokenize(text)
        words = [word.rstrip('.') for word in words]
        words = stem_all(words, stemmer)
        words = filter(word_check_func, words)

        for word in words:
            if word not in word_num_map:
                word_num_map.add(word, cur_word_id)
                cur_word_id += 1

        words_dict[doc_id] = words

    return words_dict, word_num_map
