# Viticulture Bibliometrics

Bibliometric analysis of the literature on computer vision and deep learning
applied to viticulture, based on a Scopus export. The code produces the number
of documents per year and type, the number of documents in each thematic axis
(radar chart) and the co-occurrence network of the most frequent keywords.

## Search

The search was run in Scopus in May 2026 over titles, abstracts and keywords
with the expression below, and the results were limited to journal articles
and conference papers in English published from 2020 to 2026.

```
TITLE-ABS-KEY(
  (
    grape OR grapes OR grapevine OR grapevines OR vineyard OR vineyards
    OR viticulture OR viticultural OR "Vitis vinifera"
    OR "wine grape" OR "wine grapes" OR "table grape" OR "table grapes"
  )
  AND
  (
    "computer vision" OR "machine vision" OR "image processing" OR "image analysis"
    OR "deep learning" OR "machine learning" OR "artificial intelligence"
    OR "convolutional neural network" OR "convolutional neural networks"
    OR CNN OR YOLO OR "you only look once"
    OR "object detection" OR segmentation
    OR "semantic segmentation" OR "instance segmentation"
  )
)
```

The search returned 262 documents. The Scopus export itself is not included,
because its abstracts are subject to the Scopus terms of use;
`data/records.csv` lists the 262 documents by Scopus EID and DOI. To reproduce
the analysis, export the same records from Scopus as CSV, including titles,
abstracts, author and index keywords and citation counts, and save the file as
`data/scopus.csv`. Citation counts change over time, so a
new export may give slightly different node sizes in the network.

## Usage

Python 3.10 or later.

```bash
pip install -r requirements.txt
python run.py data/scopus.csv --out results
```

`--top` sets the number of keywords in the network (default 10) and
`--min-cooccurrence` the minimum number of co-occurrences of an edge
(default 2).

## Method

**Thematic axes.** The terms of the controlled vocabulary in
`bibliometrics/themes.py` are searched, case-insensitively and by substring, in
the title, abstract, author keywords and index keywords of each document. A
document is counted in an axis when it contains at least one of its terms, so
it may be counted in more than one axis. The axis names are in Portuguese, the
language of the study.

**Keyword network.** Author and index keywords are split at semicolons (commas
and vertical bars are also treated as separators), converted to lower case,
and terms of up to three characters are discarded. The network keeps the
`--top` most frequent keywords, adding both fields. Two keywords co-occur when
they appear in the same keyword field of a document; author and index keywords
are counted separately. Edge width and opacity grow with the number of
co-occurrences, and node area grows with the citations accumulated by the
documents that contain the keyword. The layout is a spring layout with a fixed
seed followed by the removal of node overlaps.

## Outputs

| File | Content |
|---|---|
| `documents_by_year.csv`, `documents_by_type.csv` | Number of documents per year and per document type |
| `themes.csv` | Terms and number of documents of each thematic axis |
| `network_nodes.csv` | Keyword, frequency, accumulated citations and degree in the network |
| `network_edges.csv` | Pairs of keywords and number of co-occurrences |
| `themes_radar.pdf`, `.png` | Radar chart of the thematic axes |
| `keyword_network.pdf`, `.png` | Keyword co-occurrence network |

The `results` folder contains the outputs obtained from the export used in the
study.

## License

The code is released under the MIT License.

## Related repositories

- [Grape Frame Extractor](https://doi.org/10.5281/zenodo.20874000): extraction of frames from the vineyard videos.
- [Grape Dataset Deduplication](https://doi.org/10.5281/zenodo.20874787): removal of redundant images by perceptual hashing.
- [Grape Segmentation Training](https://doi.org/10.5281/zenodo.23842354): training and evaluation of the YOLO segmentation models.
