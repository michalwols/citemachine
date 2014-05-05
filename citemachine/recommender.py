from datetime import date
import cPickle

from gensim.models.ldamodel import LdaModel

from citemachine import topic_model
from citemachine.text_process import CorpusPreprocessor


class LDARecommender(object):

    def __init__(self, corpus, corpus_preprocessor=None, num_topics=100,
                 train_at_init=False):
        """
        Args:
            corpus: an instance of a citation corpus class
            corpus_preprocessor:
            num_topics: number of topics to train the LDA with
            train_at_init: if True, trains a new LDA model at initialization,
                    otherwise need to call '_train' method to train the model
        """
        self.corpus = corpus
        if corpus_preprocessor:
            self.preprocessor = corpus_preprocessor
        else:
            self.preprocessor = CorpusPreprocessor(self.corpus)

        self.num_topics = num_topics

        if train_at_init:
            self._train(num_topics)
        else:
            self.LDA = None
            self.topics = None

    @classmethod
    def init_from_pickle(cls, pickle_path):
        """Used to instantiante new class by loading a pretrained model from
        an old pickled instance, which might not provide newly implemented
        methods"""
        with open(pickle_path, 'rb') as pkl:
            lda_recom = cPickle.load(pkl)

        self = cls(corpus=lda_recom.corpus,
                   corpus_preprocessor=lda_recom.preprocessor, 
                   num_topics=lda_recom.num_topics)
        self.LDA = lda_recom.LDA
        self.topics = lda_recom.topics

        return self

    def _train(self, num_topics=None):
        if num_topics:
            self.num_topics = num_topics

        self.LDA = LdaModel(self.preprocessor.number_encodings.values(),
                            num_topics=self.num_topics,
                            id2word=self.preprocessor.id_to_word_map)

        self.topics = topic_model.build_topics_dict(self.LDA,
                            self.preprocessor.number_encodings)

    def top_scoring_for_topics(self, topic_vector,
                               publication_year=None,
                               num_results=None):

        if publication_year is None:
            publication_year = date.today().year

        scores = topic_model.score_topics(topic_vector, self.topics)
        valid_scores = topic_model.filter_scores(scores,
                                                 publication_year,
                                                 self.corpus.citation_counts,
                                                 self.corpus.years)
        if num_results is None:
            return valid_scores
        else:
            return valid_scores[0:num_results]

    def top_scoring_for_doc(self, doc_id, num_results=None):

        topic_vector = self.topics[doc_id]
        publication_year = self.corpus.years[doc_id]
        return self.top_scoring_for_topics(topic_vector,
                                           publication_year,
                                           num_results)

    def top_scoring_for_text(self, text, publication_year=None,
                             num_results=None):

        topic_vector = self.text_to_topic_vector(text)
        return self.top_scoring_for_topics(topic_vector,
                                           publication_year,
                                           num_results)

    def text_to_topic_vector(self, text):
        num_encoded_text = self.preprocessor.text_to_number_encoding(text)
        topic_vector = self.LDA[num_encoded_text]
        return topic_vector
