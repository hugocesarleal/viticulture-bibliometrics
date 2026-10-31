"""Thematic axes and keyword co-occurrence network."""

from collections import Counter
from itertools import combinations

import networkx as nx

from .scopus import CITATIONS_FIELD, STOPWORDS, keyword_cells


def theme_counts(texts, themes):
    """Number of documents that mention each thematic axis."""
    return {name: sum(any(term in text for term in terms) for text in texts)
            for name, terms in themes.items()}


def keyword_frequency(records):
    """Occurrences of each keyword, adding author and index keywords."""
    frequency = Counter()
    for _, keywords in keyword_cells(records):
        frequency.update(k for k in keywords if k not in STOPWORDS)
    return frequency


def cooccurrence_network(records, top=10, min_cooccurrence=2):
    """Co-occurrence network of the most frequent keywords.

    Two keywords co-occur when they appear in the same keyword field of a
    document; author and index keywords are counted separately, so a pair
    present in both fields of a document counts twice. Edges observed fewer
    than `min_cooccurrence` times are discarded. Each node stores its
    frequency, the citations accumulated by the documents that contain it
    (once per occurrence) and its degree.
    """
    frequency = keyword_frequency(records)
    selected = [keyword for keyword, _ in frequency.most_common(top)]

    pairs = Counter()
    for _, keywords in keyword_cells(records):
        present = sorted({k for k in keywords if k in selected})
        pairs.update(combinations(present, 2))

    graph = nx.Graph()
    for (a, b), count in pairs.items():
        if count >= min_cooccurrence:
            graph.add_edge(a, b, weight=count)

    citations = dict.fromkeys(graph.nodes, 0.0)
    for index, keywords in keyword_cells(records):
        for keyword in keywords:
            if keyword in citations:
                citations[keyword] += records.at[index, CITATIONS_FIELD]

    for node in graph.nodes:
        graph.nodes[node].update(frequency=frequency[node], citations=int(citations[node]),
                                 degree=graph.degree(node))
    return graph
