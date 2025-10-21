from __future__ import annotations

from typing import cast

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .models_core import users as users_table
from .models_orm import User


def get_all_users(s: Session) -> list[User]:
    stmt = select(User).order_by(User.id)
    return list(s.scalars(stmt))


def get_user_by_username(s: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return cast(User | None, s.scalars(stmt).first())


def create_user(
    s: Session,
    *,
    username: str,
    email: str,
    full_name: str,
    password_hash: str,
    is_active: bool = True,
) -> User:
    u = User(
        username=username,
        email=email,
        full_name=full_name,
        password_hash=password_hash,
        is_active=is_active,
    )
    s.add(u)
    try:
        s.commit()
        s.refresh(u)
        return u
    except IntegrityError as e:
        s.rollback()
        raise ValueError(f"Duplicate username/email? {e.orig}") from e
    except SQLAlchemyError as e:
        s.rollback()
        raise RuntimeError(f"DB error: {e}") from e


def update_user_fullname_email(
    s: Session,
    user_id: int,
    *,
    full_name: str | None = None,
    email: str | None = None,
) -> int:
    vals: dict[str, object] = {}
    if full_name is not None:
        vals["full_name"] = full_name
    if email is not None:
        vals["email"] = email
    if not vals:
        return 0

    stmt = update(users_table).where(users_table.c.id == user_id).values(**vals)
    try:
        res = s.execute(stmt)
        s.commit()
        return res.rowcount or 0
    except IntegrityError as e:
        s.rollback()
        raise ValueError(f"Constraint violation: {e.orig}") from e
    except SQLAlchemyError as e:
        s.rollback()
        raise RuntimeError(f"DB error: {e}") from e
