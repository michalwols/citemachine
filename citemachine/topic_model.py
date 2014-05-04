from operator import itemgetter


def build_topics_dict(lda, number_encodings_dict):

    topics = {}
    for doc_id in number_encodings_dict:
        topics[doc_id] = lda[number_encodings_dict[doc_id]]

    return topics


def topic_intersection(doc1_topics, doc2_topics):
    """Computes the intersection of the topic vectors"""
    p1 = 0
    p2 = 0

    topic_overlaps = []
    while p1 < len(doc1_topics) and p2 < len(doc2_topics):

        if doc1_topics[p1][0] == doc2_topics[p2][0]:
            topic_num = doc1_topics[p1][0]
            intersection = min(doc1_topics[p1][1], doc2_topics[p2][1])
            topic_overlaps.append((topic_num, intersection))

            p1 += 1
            p2 += 1
        elif doc1_topics[p1][0] < doc2_topics[p2][0]:
            p1 += 1
        else:
            p2 += 1

    return topic_overlaps


def histogram_intersection_kernel(topics1, topics2):
    """Calculates the sum of topic intersections"""
    topic_intersect = topic_intersection(topics1, topics2)
    score = sum((val for (topic, val) in topic_intersect))
    return score


def score_topics(query_topics, topics_dict,
                 similarity_func=histogram_intersection_kernel):
    """Scores the topics in the query against all topics in the topics_dict
       using similarity_func
    """
    scores = []
    for doc_id in topics_dict:
        score = similarity_func(query_topics, topics_dict[doc_id])
        scores.append((doc_id, score))

    scores.sort(key=itemgetter(1), reverse=True)
    return scores

def filter_scores(scores, query_year, citation_counts, years):
    is_feasible = lambda t: (years[t[0]] <= query_year) and \
                            (citation_counts[t[0]] > 0)
    return filter(is_feasible, scores)

def locate_references(references, scores):
    """Finds the positions of the references in the topic scores list"""
    refs = set(references)

    i = 0
    positions = []
    while (i < len(scores)) and (len(positions) < len(references)):
        if scores[i][0] in refs:
            positions.append((scores[i][0], i))
        i += 1

    return positions
