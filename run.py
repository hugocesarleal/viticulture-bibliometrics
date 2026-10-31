"""Bibliometric analysis of a Scopus export: documents per year and type,
thematic axes and keyword co-occurrence network."""

import argparse
from pathlib import Path

import pandas as pd

from bibliometrics import plots
from bibliometrics.analysis import cooccurrence_network, theme_counts
from bibliometrics.scopus import document_texts, load_export
from bibliometrics.themes import CHART_LABELS, THEMES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="CSV file exported from Scopus")
    parser.add_argument("--out", type=Path, default=Path("results"), help="output folder")
    parser.add_argument("--top", type=int, default=10, help="keywords in the network")
    parser.add_argument("--min-cooccurrence", type=int, default=2,
                        help="minimum number of co-occurrences of an edge")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    records = load_export(args.export)
    print(f"{len(records)} documents")

    by_year = records["Year"].value_counts().sort_index().rename_axis("year").rename("documents")
    by_type = records["Document Type"].value_counts().rename_axis("type").rename("documents")
    by_year.to_csv(args.out / "documents_by_year.csv")
    by_type.to_csv(args.out / "documents_by_type.csv")
    print(by_type.to_string(header=False))

    counts = theme_counts(document_texts(records), THEMES)
    pd.DataFrame({"theme": list(counts), "terms": ["; ".join(t) for t in THEMES.values()],
                  "documents": list(counts.values())}).to_csv(args.out / "themes.csv", index=False)
    for name, n in counts.items():
        print(f"{name:30s} {n:4d}")

    graph = cooccurrence_network(records, args.top, args.min_cooccurrence)
    nodes = pd.DataFrame([{"keyword": n, **graph.nodes[n]} for n in sorted(graph.nodes)])
    edges = pd.DataFrame([{"keyword_a": u, "keyword_b": v, "cooccurrences": w}
                          for u, v, w in sorted(graph.edges(data="weight"))])
    nodes.to_csv(args.out / "network_nodes.csv", index=False)
    edges.to_csv(args.out / "network_edges.csv", index=False)
    print(f"network: {graph.number_of_nodes()} keywords, {graph.number_of_edges()} edges")

    plots.radar(counts, CHART_LABELS, args.out / "themes_radar")
    plots.network(graph, args.out / "keyword_network")


if __name__ == "__main__":
    main()
