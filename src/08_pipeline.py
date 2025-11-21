from __future__ import annotations

from .database import SessionLocal
from .storage.mongodb import init_mongo
from .usecases.arxiv_client import fetch_arxiv_to_dataframe
from .usecases.html_content import add_html_content, add_text_from_html
from .usecases.load_dataframe_mariadb import load_dataframe_into_mariadb
from .usecases.load_dataframe_mongodb import load_dataframe_into_mongodb
from .usecases.mongo_search import search_by_text


def run_pipeline() -> None:
    df = fetch_arxiv_to_dataframe("cat:astro-ph.CO", max_results=10)
    df = add_html_content(df)
    df = add_text_from_html(df)

    df = df.drop_duplicates(subset="arxiv_id").reset_index(drop=True)

    df = load_dataframe_into_mariadb(df, SessionLocal)

    collection = init_mongo()
    load_dataframe_into_mongodb(df, collection)

    results = search_by_text(collection, "inflation")
    print(results)


if __name__ == "__main__":
    run_pipeline()
