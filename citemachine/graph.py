from collections import defaultdict
from operator import itemgetter

import networkx as nx
import community


class CommunityRank(object):

    def __init__(self, directed_graph):
        self.directed_graph = directed_graph

        dendogram = community.generate_dendogram(self.directed_graph.to_undirected())
        partitions = community.partition_at_level(dendogram, len(dendogram)-1)
        communities = self._get_communities(partitions)
        major_communities = self._get_large_communities(communities)

        self.community_graphs = self._build_community_graphs(communities,
                                      valid_communities=major_communities)

        self.community_rankings = self._pagerank_communities(self.community_graphs)

    def _get_communities(self, partitions):
        community_sets = defaultdict(set)
        for node, community in partitions.iteritems():
            community_sets[community].add(node)
        return community_sets

    def _get_large_communities(self, communities, min_size=10):

        valid_communities = set()
        for com, nodes in communities.items():
            if len(nodes) >= min_size:
                valid_communities.add(com)

        return valid_communities

    def _build_community_graphs(self, communities, valid_communities=None):

        if valid_communities is None:
            valid_communities = communities.keys()

        community_graphs = {}
        for com in valid_communities:
            community_graphs[com] = self.directed_graph.subgraph(communities[com])

        return community_graphs

    def _pagerank_communities(self, community_graphs):

        pageranks = {}
        for com in community_graphs:
            pagerank = nx.pagerank(community_graphs[com], max_iter=200)
            pageranks[com] = sorted(pagerank.items(), key=itemgetter(1), reverse=True)
        return pageranks
        

def adj_lists_to_directed_graph(adjacency_lists):
    """Turns a dict of lists of nodes to a directed graph"""
    return nx.from_dict_of_lists(adjacency_lists, create_using=nx.DiGraph())
