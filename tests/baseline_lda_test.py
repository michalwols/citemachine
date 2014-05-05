from __future__ import division

import os
os.chdir('..')
from citemachine.corpus.dblp import DBLP
from citemachine import topic_model
from citemachine.text_process import CorpusPreprocessor
from citemachine.evaluation import precision, recall
from citemachine.recommender import LDARecommender
from cloud.serialization import cloudpickle
import cPickle


def lda_recommender_setup(num_docs=None, num_topics=100, max_word_count=50000):

    dblp = DBLP('../Data/Watson/DBLP/DBLP.txt', num_docs)
    cp = CorpusPreprocessor(dblp, min_word_count=5, max_word_count=max_word_count)

    recommender = LDARecommender(corpus=dblp, corpus_preprocessor=cp, num_topics=num_topics)
    return recommender


def recommendation_ranking_test(recommender, docs_range=(0,10), num_results=10):

    doc_ids = recommender.corpus.keys()[docs_range[0]:docs_range[1]]
    titles = recommender.corpus.titles
    references = recommender.corpus.references
    precisions = []
    recalls = []

    for doc_id in doc_ids:

        num_references = len(references[doc_id])
        if num_references == 0:
            continue

        print 'Matches for: {doc_title}'.format(doc_title=titles[doc_id])

        top_results = recommender.top_scoring_for_doc(doc_id, num_results=num_results)
        reference_positions = topic_model.locate_references(references[doc_id], top_results)

        num_retrieved = len(top_results) - 1
        num_found = len(reference_positions)

        prec = precision(num_found, num_retrieved)
        rec = recall(num_found, num_references)
        precisions.append(prec)
        recalls.append(rec)

        print "Number of references: {refs}".format(refs=num_references)
        if reference_positions:
            print "Actual references found at positions: ", [pos for (doc, pos) in reference_positions]
        
        print "Precision: {p} | Recall: {r}".format(p=prec, r=rec)

        i = 0
        for (doc, score) in top_results:
            print "{num}: score: {score} || title: {title}".format(num=i, score=score, title=titles[doc])
            i += 1
        print

    print "Mean Precision: {p} | Mean Recall: {r}".format(p=sum(precisions)/len(precisions), r=sum(recalls)/len(precisions))


def main(recommender_pickle_path=None):

    if recommender_pickle_path:
        with open(recommender_pickle_path, 'rb') as f:
            recommender = cPickle.load(f)
    else:
        recommender = lda_recommender_setup(num_docs=5000, num_topics=50)
    recommendation_ranking_test(recommender)


if __name__ == '__main__':
    main('pickles/LDARecommender_100topics_fulldblp.pickle')
