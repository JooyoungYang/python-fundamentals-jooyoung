from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from pymongo import MongoClient
from pymongo.results import InsertOneResult

MONGO_URI = "mongodb://admin:adminpassword@localhost:27017/dataeng?authSource=admin"

client = MongoClient(MONGO_URI)
db = client["dataeng"]
users = db["users"]


def create_user(
    username: str,
    email: str,
    first_name: str | None = None,
    last_name: str | None = None,
    age: int | None = None,
) -> str:
    doc: dict = {
        "username": username,
        "email": email,
        "created_at": datetime.now(UTC),
    }

    profile: dict[str, Any] = {}
    if first_name:
        profile["first_name"] = first_name
    if last_name:
        profile["last_name"] = last_name
    if age is not None:
        profile["age"] = age

    if profile:
        doc["profile"] = profile

    result: InsertOneResult = users.insert_one(doc)
    return str(result.inserted_id)


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    raw_doc = users.find_one({"_id": ObjectId(user_id)})
    if raw_doc is None:
        return None

    doc: dict[str, Any] = dict(raw_doc)
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


def get_user_by_username(username: str) -> dict[str, Any] | None:
    raw_doc = users.find_one({"username": username})
    if raw_doc is None:
        return None

    doc: dict[str, Any] = dict(raw_doc)
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


def update_user_email(user_id: str, new_email: str) -> bool:
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"email": new_email}},
    )
    modified: int = result.modified_count or 0
    return modified > 0


def increment_user_age(user_id: str, amount: int = 1) -> bool:
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"profile.age": amount}},
    )
    modified: int = result.modified_count or 0
    return modified > 0


if __name__ == "__main__":
    new_id = create_user(
        "david",
        "david@example.com",
        first_name="David",
        age=35,
    )
    print("inserted:", new_id)
    print(get_user_by_id(new_id))
