"""RAG service scaffold using the local MCP index."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List

from ..index import Retriever, StubEmbedder


class RagService:
    """Retrieves citation-ready snippets for given topics."""

    def __init__(self, index_dir: Path | None = None) -> None:
        env_dir = os.environ.get("FLUXLOOP_MCP_INDEX_DIR")
        resolved = Path(index_dir or env_dir or Path.home() / ".fluxloop" / "mcp" / "index" / "dev")
        self.index_dir = resolved

    def retrieve(self, topics: Iterable[Dict], per_topic: int = 2, max_documents: int = 10) -> List[Dict]:
        if not self.index_dir.exists():
            return []

        retriever = Retriever(self.index_dir, StubEmbedder())
        documents: List[Dict] = []
        seen = set()

        for topic in topics:
            query = topic.get("query")
            topic_id = topic.get("id") or "topic"
            if not isinstance(query, str) or not query.strip():
                continue

            for chunk, score in retriever.top_k(query, per_topic):
                metadata = chunk.get("metadata", {})
                source = metadata.get("source", "unknown")
                citation_id = f"ref:{source.replace('/', '_')}"
                doc_id = f"{topic_id}-{metadata.get('chunk_index', 0)}"
                if doc_id in seen:
                    continue
                seen.add(doc_id)

                documents.append(
                    {
                        "id": doc_id,
                        "topic": topic_id,
                        "title": source,
                        "path": source,
                        "excerpt": chunk.get("content", "")[:600],
                        "citation": citation_id,
                        "score": score,
                    }
                )

                if len(documents) >= max_documents:
                    return documents

        return documents

