import os

import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found.")

genai.configure(api_key=api_key)

EMBEDDING_MODEL = "text-embedding-004"


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


if __name__ == "__main__":
    phrases = ["My cat is sleeping on the sofa.", "I want to do nothing at home.", "I miss you."]

    embeddings = []
    for text in phrases:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="SEMANTIC_SIMILARITY",
        )
        emb = np.array(result["embedding"], dtype=np.float32)
        embeddings.append(emb)

    base = embeddings[0]
    print("Base phrase:", phrases[0])
    print()

    for i in range(1, len(phrases)):
        sim = cosine_similarity(base, embeddings[i])
        print(f"Similarity('{phrases[0]}', '{phrases[i]}) = {sim:.4f}")

    print("\n Embedding test finished successfully")
