from __future__ import annotations

from .database import ENGINE
from .models.sql_models import Base


def main() -> None:
    print("Dropping authors & scientific_articles tables...")
    Base.metadata.drop_all(bind=ENGINE)

    print("Recreating tables with new schema...")
    Base.metadata.create_all(bind=ENGINE)

    print("Done.")


if __name__ == "__main__":
    main()
