"""Placeholder embedding backend."""

from __future__ import annotations

import hashlib
from typing import Iterable, List


class StubEmbedder:
    """Deterministic hashing-based embedder used for scaffolding."""

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            # Slice into chunks to produce a float vector.
            vector = [int.from_bytes(digest[i : i + 4], "big") / 1_000_000_000 for i in range(0, 32, 4)]
            vectors.append(vector)
        return vectors

