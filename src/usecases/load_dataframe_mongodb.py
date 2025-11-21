from __future__ import annotations

from typing import Any

import pandas as pd
from pymongo.collection import Collection


def _row_to_document(row: pd.Series) -> dict[str, Any]:
    return {
        "article_id": str(row.get("article_id", "")),
        "author_id": str(row.get("author_id", "")),
        "title": str(row.get("title", "")),
        "summary": str(row.get("summary", "")),
        "arxiv_id": str(row.get("arxiv_id", "")),
        "author_full_name": str(row.get("author_full_name", "")),
        "author_title": str(row.get("author_title", "")),
        "file_path": str(row.get("file_path", "")),
        "text": str(row.get("text_content", "")),
    }


def load_dataframe_into_mongodb(df: pd.DataFrame, collection: Collection) -> None:
    documents = df.apply(_row_to_document, axis=1).to_list()
    if not documents:
        return
    collection.insert_many(documents)
