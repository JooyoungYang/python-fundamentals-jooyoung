from __future__ import annotations

from mongoengine import (
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
    StringField,
)


class AuthorEmbedded(EmbeddedDocument):
    db_id = IntField(required=True)
    full_name = StringField(required=True)
    title = StringField(required=False)


class ScientificArticleDocument(Document):
    meta = {
        "collection": "articles",
        "indexes": [
            "db_id",
            "arxiv_id",
            "$text",
        ],
    }

    db_id = IntField(required=True)
    title = StringField()
    summary = StringField()
    file_path = StringField()
    created_at = DateTimeField()
    arxiv_id = StringField()
    author = EmbeddedDocumentField(AuthorEmbedded)
    text = StringField()
