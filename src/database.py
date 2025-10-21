from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from .config import settings

ENGINE = create_engine(
    settings.url(),
    poolclass=QueuePool,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_pre_ping=True,
    pool_recycle=settings.pool_recycle,
    future=True,
)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)
