from __future__ import annotations

from pathlib import Path

from src.usecases.load_csv_to_mariadb import load_data_from_csv
from src.usecases.search_mongo import search_text_index
from src.usecases.transfer_mariadb_to_mongo import export_from_db


def main() -> None:
    new_articles_sqla = load_data_from_csv(Path("data/articles.csv"))
    print("len new articles sqla:", len(new_articles_sqla))

    mongo_articles = export_from_db()
    print("len mongo articles:", len(mongo_articles))

    results = search_text_index(mongo_articles, "Hubble")
    print("len results:", len(results))
    for article in results:
        print(f"{article.arxiv_id}: {article.title}")


if __name__ == "__main__":
    main()
