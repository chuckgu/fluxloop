"""Simple retriever implementation leveraging the JSONL store."""

from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Dict, Iterable, List, Protocol, Tuple

def _load_chunks(store_dir: Path) -> List[Dict]:
    chunk_file = store_dir / "chunks.jsonl"
    if not chunk_file.exists():
        return []
    with chunk_file.open("r", encoding="utf-8") as fp:
        return [json.loads(line) for line in fp if line.strip()]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sqrt(sum(a * a for a in vec_a))
    norm_b = sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbedderLike(Protocol):
    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        ...


class Retriever:
    def __init__(self, store_dir: Path, embedder: EmbedderLike) -> None:
        self.store_dir = store_dir
        self.embedder = embedder
        self._chunks = _load_chunks(store_dir)
        self._vectors = self.embedder.embed(chunk["content"] for chunk in self._chunks)

    def top_k(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        query_vec = self.embedder.embed([query])[0]
        scored = []
        for chunk, vector in zip(self._chunks, self._vectors):
            score = cosine_similarity(query_vec, vector)
            scored.append((chunk, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:k]

