from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from mongoengine import (
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
    NotUniqueError,
    StringField,
    ValidationError,
    connect,
)

connect(
    db="dataeng",
    host="mongodb://admin:adminpassword@localhost:27017/dataeng?authSource=admin",
)


class Profile(EmbeddedDocument):
    first_name = StringField()
    last_name = StringField()
    age = IntField(min_value=0, max_value=100)


class User(Document):
    username = StringField(required=True, unique=True, max_length=50)
    email = StringField(required=True)
    profile = EmbeddedDocumentField(Profile)
    created_at = DateTimeField(default=lambda: datetime.now(UTC))

    meta = {"collection": "users"}


def me_create_user(
    username: str,
    email: str,
    first_name: str | None = None,
    last_name: str | None = None,
    age: int | None = None,
) -> str | None:
    if User.objects(username=username).first():
        return None

    profile_doc: Profile | None = None
    if first_name or last_name or age is not None:
        profile_doc = Profile(
            first_name=first_name,
            last_name=last_name,
            age=age,
        )

    user = User(
        username=username,
        email=email,
        profile=profile_doc,
    )

    try:
        user.save()
    except (ValidationError, NotUniqueError):
        return None

    return str(user.id)


def me_get_user_by_id(user_id: str) -> dict[str, Any] | None:
    user = User.objects(id=user_id).first()
    if not user:
        return None

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "profile": user.profile.to_mongo() if user.profile else None,
        "created_at": user.created_at,
    }


def me_get_user_by_username(username: str) -> dict[str, Any] | None:
    user = User.objects(username=username).first()
    if not user:
        return None

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "profile": user.profile.to_mongo() if user.profile else None,
        "created_at": user.created_at,
    }


def me_update_user_email(user_id: str, new_email: str) -> bool:
    user = User.objects(id=user_id).first()
    if not user:
        return False
    user.email = new_email
    user.save()
    return True


def me_update_user_profile(
    user_id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    age: int | None = None,
) -> bool:
    user = User.objects(id=user_id).first()
    if not user:
        return False

    if not user.profile:
        user.profile = Profile()

    if first_name is not None:
        user.profile.first_name = first_name
    if last_name is not None:
        user.profile.last_name = last_name
    if age is not None:
        user.profile.age = age

    user.save()
    return True


def safe_me_create_user(**kwargs: Any) -> str | None:
    try:
        return me_create_user(**kwargs)
    except ValidationError as e:
        print("validation failed:", e)
        return None


if __name__ == "__main__":
    new_id = me_create_user(
        "emma",
        "emma@example.com",
        first_name="Emma",
        age=22,
    )
    print("created:", new_id)
    if new_id:
        print(me_get_user_by_id(new_id))
