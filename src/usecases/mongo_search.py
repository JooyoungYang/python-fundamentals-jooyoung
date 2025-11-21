from __future__ import annotations

from typing import Any

from pymongo.collection import Collection


def search_by_text(collection: Collection, keyword: str) -> list[dict[str, Any]]:
    cursor = collection.find({"title": {"$regex": keyword, "$options": "i"}}).limit(10)
    return list(cursor)
