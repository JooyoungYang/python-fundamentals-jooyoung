from __future__ import annotations

from .crud import (
    create_user,
    get_all_users,
    get_user_by_username,
    update_user_fullname_email,
)
from .database import ENGINE, SessionLocal
from .models_orm import Base, User


def init_db() -> None:
    Base.metadata.create_all(bind=ENGINE)


def demo() -> None:
    init_db()
    with SessionLocal() as s:
        print("All users:")
        for user in get_all_users(s):
            print(
                user.id,
                user.username,
                user.email,
                user.full_name,
                user.is_active,
            )

        found: User | None = get_user_by_username(s, "alice")
        print("\nFind 'alice':", found.username if found else "Not found")

        try:
            nu = create_user(
                s,
                username="dave",
                email="dave@example.com",
                full_name="Dave Grohl",
                password_hash="hash",
            )
            print("\nInserted:", nu.id, nu.username)
        except Exception as e:
            print("\nInsert error:", e)

        if found:
            rows = update_user_fullname_email(
                s,
                found.id,
                email="alice+new@example.com",
            )
            print("Rows updated:", rows)


if __name__ == "__main__":
    demo()
