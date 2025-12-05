from __future__ import annotations

import os
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "adminpassword")
MONGO_DB = os.getenv("MONGO_DB", "dataeng")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "articles")


def init_mongo() -> Collection[Any]:
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
    client: MongoClient = MongoClient(uri)
    db: Database = client[MONGO_DB]
    collection: Collection[Any] = db[MONGO_COLLECTION]
    return collection
