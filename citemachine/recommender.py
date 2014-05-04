from gensim.models.ldamodel import LdaModel
from citemachine import topic_model
from citemachine.text_process import CorpusPreprocessor


class LDARecommender(object):

    def __init__(self, corpus, corpus_preprocessor=None, num_topics=200):
        self.corpus = corpus
        if corpus_preprocessor:
            self.preprocessor = corpus_preprocessor
        else:
            self.preprocessor = CorpusPreprocessor(self.corpus)

        self.num_topics = num_topics
        self.LDA = LdaModel(self.preprocessor.number_encodings.values(),
                            num_topics=self.num_topics,
                            id2word=self.preprocessor.id_to_word_map)
        self.topics = topic_model.build_topics_dict(self.LDA,
                            self.preprocessor.number_encodings)

    def top_scoring_for_doc(self, doc_id, num_results=None):

        scores = topic_model.score_topics(self.topics[doc_id], self.topics)

        publication_year = self.corpus.years[doc_id]
        scores = topic_model.filter_scores(scores, publication_year,
                                           self.corpus.citation_counts,
                                           self.corpus.years)
        if num_results is None:
            return scores
        else:
            return scores[0:num_results]
