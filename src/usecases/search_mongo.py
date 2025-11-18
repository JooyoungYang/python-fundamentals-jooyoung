from __future__ import annotations

from src.models.mongo_models import ScientificArticleDocument
from src.storage.mongodb import init_mongo


def search_text(keyword: str) -> list[ScientificArticleDocument]:
    init_mongo()
    query = ScientificArticleDocument.objects(text__icontains=keyword)
    return list(query)


def search_text_index(
    articles: list[ScientificArticleDocument],
    keyword: str,
) -> list[ScientificArticleDocument]:
    init_mongo()
    all_ids = [a.id for a in articles]
    query = ScientificArticleDocument.objects(id__in=all_ids).search_text(keyword)
    return list(query)
