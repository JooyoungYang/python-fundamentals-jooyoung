from __future__ import annotations

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    text,
)

metadata = MetaData()

UPDATED_AT_DEFAULT = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(50), nullable=False),
    Column("email", String(255), nullable=False),
    Column("full_name", String(100), nullable=False),
    Column("password_hash", String(255), nullable=False),
    Column("is_active", Boolean, nullable=False, server_default=text("1")),
    Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Column(
        "updated_at",
        TIMESTAMP,
        nullable=False,
        server_default=UPDATED_AT_DEFAULT,
    ),
    UniqueConstraint("username", name="uq_users_username"),
    UniqueConstraint("email", name="uq_users_email"),
    CheckConstraint("CHAR_LENGTH(username) >= 3", name="ck_username_minlen"),
)
