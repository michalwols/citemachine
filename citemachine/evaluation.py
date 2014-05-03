from __future__ import division


def precision(num_found, num_retrieved):
    return num_found / num_retrieved


def recall(num_found, total_relevant):
    return num_found / total_relevant


def F1_score(num_found, total_relevant, num_retrieved):
    p = precision(num_found, num_retrieved)
    r = recall(num_found, total_relevant)

    F1 = 2 * p * r / (p + r)
    return F1
