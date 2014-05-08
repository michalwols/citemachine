from collections import defaultdict
from operator import itemgetter

import networkx as nx
import community


class CommunityRank(object):

    def __init__(self, graph):
        self.graph = graph

        self.dendogram = community.generate_dendogram(self.graph)
        self.partitions = community.partition_at_level(self.dendogram,
                                                       len(self.dendogram)-1)

        self.communities = self._get_communities(self.partitions)
        self.major_communities = self._get_large_communities(self.communities)

        self.community_graphs = self._build_community_graphs(self.communities,
                                     valid_communities=self.major_communities)
        self.pageranks = self._pagerank_communities(self.community_graphs)

    def _get_communities(self, partitions):
        community_sets = defaultdict(set)
        for node, community in partitions.iteritems():
            community_sets[community].add(node)
        return community_sets

    def _get_large_communities(self, communities, min_size=100):

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
            community_graphs[com] = self.graph.subgraph(communities[com])

        return community_graphs

    def _pagerank_communities(self, community_graphs):

        pageranks = {}
        for com in community_graphs:
            pageranks[com] = nx.pagerank(community_graphs[com])
        return pageranks

    def rankings_for_community(self, community_num):
        pagerankings = self.pageranks[community_num]
        return sorted(pagerankings.items(), key=itemgetter(1), reverse=True)

def adj_lists_to_graph(adjacency_lists):
    """Turns a dict of lists of nodes to a directed graph"""
    return nx.from_dict_of_lists(adjacency_lists)
