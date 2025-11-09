from pathlib import Path
from typing import Iterable, List

from fluxloop_mcp.index.retriever import Retriever
from fluxloop_mcp.index.store import ChunkRecord, IndexStore


class CountingEmbedder:
    """Very small embedder that captures keyword frequency."""

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            lowered = text.lower()
            vectors.append(
                [
                    lowered.count("fluxloop"),
                    lowered.count("faq") + 1,  # ensure non-zero norm
                ]
            )
        return vectors


def _write_chunks(store_dir: Path, contents: List[str]) -> None:
    store = IndexStore(store_dir)
    for idx, content in enumerate(contents):
        metadata = {"source": f"docs/doc-{idx}.md", "chunk_index": idx}
        store.add_chunk(ChunkRecord.from_content(content, metadata))
    store.flush()


def test_retriever_returns_relevant_chunks(tmp_path: Path) -> None:
    store_dir = tmp_path / "index"
    contents = [
        "Fluxloop collects observability data for your agents.",
        "Instrumentation FAQ covers troubleshooting steps.",
    ]
    _write_chunks(store_dir, contents)

    retriever = Retriever(store_dir, CountingEmbedder())
    results = retriever.top_k("How do I integrate fluxloop?", k=1)

    assert results
    top_chunk, score = results[0]
    assert "Fluxloop collects" in top_chunk["content"]
    assert score > 0


def test_retriever_handles_empty_index(tmp_path: Path) -> None:
    store_dir = tmp_path / "empty"
    store_dir.mkdir()

    retriever = Retriever(store_dir, CountingEmbedder())

    assert retriever.top_k("any query", k=3) == []

