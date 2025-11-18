from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from src.models.sql_models import Author, ScientificArticle
from src.storage.mariadb import get_session, init_db


def save_article(line: dict[str, str]) -> ScientificArticle | None:
    from sqlalchemy.orm import Session

    with get_session() as session:
        assert isinstance(session, Session)
        try:
            author = Author(
                full_name=line["author_full_name"],
                title=line["author_title"],
            )
            article = ScientificArticle(
                title=line["title"],
                summary=line["summary"],
                file_path=line["file_path"],
                arxiv_id=line["arxiv_id"],
                author=author,
            )
            session.add(article)
            session.commit()
            print(f"Success: {article.arxiv_id}")
            return article
        except IntegrityError as exc:
            print(f"Failure (duplicate?): {exc}")
            return None


def load_data_from_csv(path: Path) -> list[ScientificArticle]:
    init_db()

    articles: list[ScientificArticle] = []
    with path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for line in reader:
            article = save_article(line)
            if article is not None:
                articles.append(article)

    print(f"Imported {len(articles)} articles from {path}")
    return articles
