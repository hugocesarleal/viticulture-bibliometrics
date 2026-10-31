"""Reading of Scopus CSV exports."""

import re

import pandas as pd

TEXT_FIELDS = ("Title", "Abstract", "Author Keywords", "Index Keywords")
KEYWORD_FIELDS = ("Author Keywords", "Index Keywords")
CITATIONS_FIELD = "Cited by"

# Short words that occasionally appear as keywords after splitting.
STOPWORDS = {"with", "from", "into", "using", "based"}


def load_export(path):
    records = pd.read_csv(path, encoding="utf-8-sig")
    records[CITATIONS_FIELD] = pd.to_numeric(records[CITATIONS_FIELD], errors="coerce").fillna(0)
    return records


def document_texts(records):
    """Title, abstract and keywords of each document, in lower case."""
    fields = [field for field in TEXT_FIELDS if field in records.columns]
    return records[fields].fillna("").apply(lambda row: " ".join(row).lower(), axis=1).tolist()


def split_keywords(cell):
    """Keywords of one field of one document.

    Scopus separates keywords with semicolons; commas and vertical bars are
    also treated as separators. Terms with three characters or fewer are
    discarded.
    """
    return [part.strip().lower() for part in re.split(r"[;,|]", str(cell)) if len(part.strip()) > 3]


def keyword_cells(records):
    """(row index, keywords) for every non-empty keyword field, author keywords first."""
    for field in KEYWORD_FIELDS:
        for index, cell in records[field].dropna().items():
            yield index, split_keywords(cell)
