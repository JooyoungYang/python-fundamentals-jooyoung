import os
from pathlib import Path
from typing import cast

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from pypdf import PdfReader

EMBEDDING_MODEL = "text-embedding-004"

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found.")

genai.configure(api_key=api_key)


def load_papers_from_pdf(papers_dir: str = "papers") -> pd.DataFrame:
    base = Path(papers_dir)
    rows = []

    for pdf_path in base.glob("*.pdf"):
        reader = PdfReader(str(pdf_path))
        texts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            texts.append(t)
        full_text = "\n".join(texts)

        rows.append(
            {
                "article_id": pdf_path.stem,
                "filename": pdf_path.name,
                "text": full_text,
            }
        )

    return pd.DataFrame(rows)


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[str] = []

    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_words = words[start:end]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break

    return chunks


def make_chunk_df(
    df: pd.DataFrame,
    text_col: str = "text",
    id_col: str = "article_id",
    chunk_size: int = 200,
    overlap: int = 50,
) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        article_id = row[id_col]
        text = str(row[text_col])
        chunks = chunk_text(text, chunk_size, overlap)
        for idx, ch in enumerate(chunks):
            rows.append(
                {
                    "article_id": article_id,
                    "chunk_index": idx,
                    "chunk_text": ch,
                }
            )
    return pd.DataFrame(rows)


def embed_chunk(text: str) -> list[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="SEMANTIC_SIMILARITY",
    )

    embedding = cast(list[float], result["embedding"])
    return embedding


def embed_chunks_df(df_chunks: pd.DataFrame) -> pd.DataFrame:
    embeddings = []
    for t in df_chunks["chunk_text"]:
        emb = embed_chunk(t)
        embeddings.append(emb)

    df_chunks = df_chunks.copy()
    df_chunks["embedding"] = embeddings
    return df_chunks


if __name__ == "__main__":
    df_articles = load_papers_from_pdf("papers")
    print("Loaded articles:", len(df_articles))

    df_chunk = make_chunk_df(df_articles)
    print("Total chunks:", len(df_chunk))

    df_chunk_emb = embed_chunks_df(df_chunk)

    output_path = "data/article_chunks_with_embeddings.parquet"
    df_chunk_emb.to_parquet(output_path, index=False)
    print("Saved embeddings to", output_path)
