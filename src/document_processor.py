from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class Document(BaseModel):
    id: int
    title: str
    published: bool
    tags: list[str] | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(default=None)
    ratings: list[int] | None = Field(default=None)

    def mean_rating(self) -> float | None:
        if not self.ratings:
            return None
        return sum(self.ratings) / len(self.ratings)


def load_documents(path: str | Path) -> list[Document]:
    """Load JSON and validate records with Pydantic."""
    import json

    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"JSON file not found: {p}")

    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Root of JSON must be a list of documents.")

    docs: list[Document] = []
    for i, obj in enumerate(raw):
        try:
            doc = Document.model_validate(obj)  # Pydantic v2
        except ValidationError as e:
            raise ValueError(f"Invalid document at index {i}: {e}") from e
        docs.append(doc)
    return docs


def display_documents(docs: Iterable[Document]) -> str:
    """Pretty-print core info, handling missing optionals."""
    lines: list[str] = []
    for d in docs:
        tags = ", ".join(d.tags) if d.tags else "(no tags)"
        if d.metadata and "author" in d.metadata:
            author = str(d.metadata["author"])
        else:
            author = "Unknown"
        mean = d.mean_rating()
        mean_str = f"{mean:.2f}" if mean is not None else "N/A"
        lines.append(
            f"- #{d.id} | {d.title!r} | published={d.published} | "
            f"tags=[{tags}] | author={author} | mean_rating={mean_str}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    json_path = Path(__file__).resolve().parent.parent / "data" / "documents.json"
    ds = load_documents(json_path)
    print(display_documents(ds))
