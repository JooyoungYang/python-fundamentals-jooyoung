from __future__ import annotations

import pymupdf4llm
from mongoengine import DoesNotExist
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models.mongo_models import AuthorEmbedded, ScientificArticleDocument
from ..models.sql_models import ScientificArticle
from ..storage.mariadb import get_session
from ..storage.mongodb import init_mongo


def save_article(article: ScientificArticle) -> ScientificArticleDocument | None:
    try:
        m_author = AuthorEmbedded(
            db_id=article.author.id,
            full_name=article.author.full_name,
            title=article.author.title,
        )

        md_text = pymupdf4llm.to_markdown(article.file_path)

        kwargs = dict(
            db_id=article.id,
            title=article.title,
            summary=article.summary,
            file_path=article.file_path,
            created_at=article.created_at,
            arxiv_id=article.arxiv_id,
            author=m_author,
            text=md_text,
        )

        m_article: ScientificArticleDocument

        try:
            m_article = ScientificArticleDocument.objects.get(
                arxiv_id=article.arxiv_id,
            )
            m_article.update(**kwargs)
            m_article.reload()
        except DoesNotExist:
            m_article = ScientificArticleDocument(**kwargs)
            m_article.save()

        print(f"Success (Mongo): {article.arxiv_id}")
        return m_article

    except Exception as exc:
        print(f"Failure (Mongo): {article.arxiv_id} → {exc}")
        return None


def export_from_db() -> list[ScientificArticleDocument]:
    init_mongo()

    new_articles: list[ScientificArticleDocument] = []

    with get_session() as session:
        assert isinstance(session, Session)

        stmt = select(ScientificArticle).options(selectinload(ScientificArticle.author))
        for article in session.scalars(stmt):
            m_article = save_article(article)
            if m_article is not None:
                new_articles.append(m_article)

    print(f"Exported {len(new_articles)} articles to MongoDB")
    return new_articles
