from __future__ import annotations

import os
import uuid

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

EMBEDDING_MODEL = "text-embedding-004"
QDRANT_COLLECTION = "article_chunks"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

EMBEDDING_DIM = 768

DATA_PARQUET = "data/article_chunks_with_embeddings.parquet"


class ChunkMetadata(BaseModel):
    point_id: str
    article_id: int | str
    chunk_index: int
    chunk_text: str
    title: str | None = None


def get_gemini_client() -> None:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key is None:
        raise ValueError("GOOGLE_API_KEY not found.")
    genai.configure(api_key=api_key)


def get_qdrant_client() -> QdrantClient:
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return client


def ensure_collection(client: QdrantClient) -> None:
    if client.collection_exists(collection_name=QDRANT_COLLECTION):
        return

    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=qmodels.VectorParams(
            size=EMBEDDING_DIM,
            distance=qmodels.Distance.COSINE,
        ),
    )


def embed_text(text: str) -> list[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="SEMANTIC_SIMILARITY",
    )
    embedding = result["embedding"]
    return list(float(x) for x in embedding)


def make_point_id(article_id: int | str, chunk_index: int) -> str:
    raw = f"{article_id}_{chunk_index}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, raw))


def chunk_exists(
    client: QdrantClient,
    point_id: str,
) -> bool:
    records = client.retrieve(
        collection_name=QDRANT_COLLECTION,
        ids=[point_id],
        with_vectors=False,
        with_payload=False,
    )
    return len(records) > 0


def upsert_chunk(
    client: QdrantClient,
    metadata: ChunkMetadata,
    embedding: list[float],
) -> None:
    point = qmodels.PointStruct(
        id=metadata.point_id,
        vector=embedding,
        payload=metadata.model_dump(),
    )

    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[point],
    )


def sync_chunks_to_qdrant() -> None:
    get_gemini_client()
    client = get_qdrant_client()
    ensure_collection(client)

    if not os.path.exists(DATA_PARQUET):
        raise FileNotFoundError(f"{DATA_PARQUET} not found. Make parquent first.")

    df = pd.read_parquet(DATA_PARQUET)

    expected_cols = {"article_id", "chunk_index", "chunk_text"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(
            f"Do not exist for Parquet file. Need: {expected_cols}, Now: {set(df.columns)}"
        )

    df["point_id"] = df.apply(
        lambda row: make_point_id(row["article_id"], int(row["chunk_index"])),
        axis=1,
    )

    all_ids = df["point_id"].tolist()
    existing_records = client.retrieve(
        collection_name=QDRANT_COLLECTION,
        ids=all_ids,
        with_vectors=False,
        with_payload=False,
    )
    existic_ids = {rec.id for rec in existing_records}

    missing_df = df[~df["point_id"].isin(existic_ids)].copy()
    print(f"Of the Total {len(df)} chunks, {len(missing_df)} chunks need to be newly added")

    has_embedding_col = "embedding" in missing_df.columns

    points: list[qmodels.PointStruct] = []

    for _, row in missing_df.iterrows():
        point_id = row["point_id"]
        chunk_text: str = str(row["chunk_text"])
        article_id = row["article_id"]
        chunk_index = int(row["chunk_index"])
        title = row["title"] if "title" in row and pd.notna(row["title"]) else None

        metadata = ChunkMetadata(
            point_id=point_id,
            article_id=article_id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            title=title,
        )

        if has_embedding_col:
            emb_list = row["embedding"]
            embedding = list(float(x) for x in emb_list)
        else:
            embedding = embed_text(chunk_text)

        points.append(
            qmodels.PointStruct(
                id=metadata.point_id,
                vector=embedding,
                payload=metadata.model_dump(),
            )
        )

    if points:
        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points,
        )
        print(f"{len(points)} chunks successfully upserted into Qdrant.")
    else:
        print("No new chunks to store.")


def search_chunks(query: str, top_k: int = 5) -> list[qmodels.ScoredPoint]:
    get_gemini_client()
    client = get_qdrant_client()

    query_emb = embed_text(query)

    results = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_emb,
        limit=top_k,
        with_payload=True,
    )

    points = results.points or []
    return list(points)


if __name__ == "__main__":
    sync_chunks_to_qdrant()

    hits = search_chunks("How do gravitational wave events help constrain the Hubble parameter?")
    for hit in hits:
        meta = hit.payload or {}
        print("-----")
        print("score:", hit.score)
        print("article_id:", meta.get("article_id"))
        print("chunk_index:", meta.get("chunk_index"))
        print("text snippet:", str(meta.get("chunk_text", ""))[:120], "...")
