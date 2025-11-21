from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

import pandas as pd
import requests

ARXIV_API_URL = "http://export.arxiv.org/api/query"


def fetch_arxiv_to_dataframe(query: str, max_results: int = 10) -> pd.DataFrame:
    params: dict[str, str] = {
        "search_query": query,
        "start": "0",
        "max_results": str(max_results),
    }
    resp = requests.get(ARXIV_API_URL, params=params, timeout=10)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    rows: list[dict[str, Any]] = []

    for entry in root.findall("atom:entry", ns):
        arxiv_id = entry.findtext("atom:id", default="", namespaces=ns) or ""
        if "/" in arxiv_id:
            arxiv_id = arxiv_id.rsplit("/", maxsplit=1)[-1]

        title = entry.findtext("atom:title", default="", namespaces=ns) or ""
        summary = entry.findtext("atom:summary", default="", namespaces=ns) or ""

        authors = [
            a.findtext("atom:name", default="", namespaces=ns) or ""
            for a in entry.findall("atom:author", ns)
        ]
        author_full_name = authors[0] if authors else ""

        author_title = "Researcher"

        file_path = f"papers/{arxiv_id}.pdf"

        rows.append(
            {
                "title": title.strip(),
                "summary": summary.strip(),
                "file_path": file_path,
                "arxiv_id": arxiv_id,
                "author_full_name": author_full_name,
                "author_title": author_title,
            },
        )

    df = pd.DataFrame(rows, dtype="string")

    for col in df.columns:
        df[col] = df[col].astype("string")

    return df
