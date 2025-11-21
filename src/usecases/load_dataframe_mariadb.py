from __future__ import annotations

from collections.abc import Callable

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.sql_models import Author, ScientificArticle


def _insert_row_into_mariadb(row: pd.Series, session: Session) -> tuple[int, int]:
    author = Author(
        full_name=str(row["author_full_name"]),
        title=str(row["author_title"]) if row["author_title"] is not None else None,
    )

    article = ScientificArticle(
        title=str(row["title"]),
        summary=str(row["summary"]),
        file_path=str(row["file_path"]),
        arxiv_id=str(row["arxiv_id"]),
        author=author,
    )

    session.add_all([author, article])
    try:
        session.commit()
        session.refresh(author)
        session.refresh(article)
        return article.id, author.id
    except IntegrityError:
        session.rollback()

        existing_article: ScientificArticle = (
            session.query(ScientificArticle).filter_by(arxiv_id=str(row["arxiv_id"])).one()
        )
        existing_author: Author = existing_article.author
        return existing_article.id, existing_author.id


def load_dataframe_into_mariadb(
    df: pd.DataFrame,
    session_factory: Callable[[], Session],
) -> pd.DataFrame:
    df = df.drop_duplicates(subset="arxiv_id").reset_index(drop=True)

    session = session_factory()

    try:

        def _apply(row: pd.Series) -> tuple[int, int]:
            return _insert_row_into_mariadb(row, session)

        results: list[tuple[int, int]] = list(df.apply(_apply, axis=1))

        ids_df = pd.DataFrame(results, columns=["article_id", "author_id"], index=df.index)
        ids_df = ids_df.astype("string")

        df["article_id"] = ids_df["article_id"]
        df["author_id"] = ids_df["author_id"]
    finally:
        session.close()

    return df
