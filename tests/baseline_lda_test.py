import os
os.chdir('..')
from citemachine.corpus.dblp import DBLP
from citemachine import topic_model
from citemachine.text_process import CorpusPreprocessor
from citemachine.evaluation import precision, recall
from citemachine.recommender import LDARecommender
from cloud.serialization import cloudpickle
import cPickle


def lda_recommender_setup(num_docs=None, num_topics=100):

    dblp = DBLP('../Data/Watson/DBLP/DBLP.txt', num_docs)
    cp = CorpusPreprocessor(dblp, min_word_count=5, max_word_count=50000)

    recommender = LDARecommender(corpus=dblp, preprocessor=cp, num_topics=num_topics)
    return recommender


def recommendation_ranking_test(recommender):

    doc_ids = recommender.corpus.keys()[:20]
    titles = recommender.corpus.titles
    references = recommender.corpus.references

    for doc_id in doc_ids:

        print 'Matches for: {doc_title}'.format(doc_title=titles[doc_id])

        top_results = recommender.top_scoring_for_doc(doc_id, num_results=50)
        reference_positions = topic_model.locate_references(references[doc_id], top_results)

        if reference_positions:
            print "Actual references found at positions: ", [pos for (doc, pos) in reference_positions]

        i = 0
        for (doc, score) in top_results:
            print "{num}: score: {score} || title: {title}".format(num=i, score=score, title=titles[doc])
            i += 1
        print

def main(recommender_pickle_path=None):

    if recommender_pickle_path:
        with open(recommender_pickle_path, 'rb') as f:
            recommender = cPickle.load(f)
    else:
        recommender = lda_recommender_setup(num_docs=5000, num_topics=50)
    recommendation_ranking_test(recommender)


if __name__ == '__main__':
    main('pickles/LDARecommender_100topics_fulldblp.pickle')
