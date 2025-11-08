"""Minimal FAQ tool used to validate MCP server wiring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import textwrap
from typing import Iterable, List, Optional, Sequence, Set

from fluxloop_mcp.index.embedder import StubEmbedder
from fluxloop_mcp.index.retriever import Retriever


@dataclass
class FAQEntry:
    question: str
    answer: str
    keywords: List[str]
    citations: List[str]


class FAQTool:
    """Knowledge lookup backed by the ingested index."""

    def __init__(self, index_dir: Optional[Path] = None) -> None:
        index_root = index_dir or Path.home() / ".fluxloop" / "mcp" / "index" / "dev"
        self.retriever = Retriever(index_root, StubEmbedder())
        self._fallback_entries = [
            FAQEntry(
                question="Where can I find FastAPI integration steps?",
                answer=(
                    "Refer to the FastAPI runner documentation. Define the runner target as a "
                    "callable in your FastAPI app and install the `fluxloop` Python package."
                ),
                keywords=["fastapi", "python"],
                citations=["packages/website/docs-cli/configuration/runners/python-function.md"],
            )
        ]

    def query(self, prompt: str) -> dict:
        """Return the best matching FAQ answer."""

        results = self.retriever.top_k(prompt, k=3)
        if results:
            primary_chunk, score = results[0]
            citations = _collect_citations(chunk for chunk, _ in results)
            answer = _summarize_text(primary_chunk["content"])

            related_sections: List[str] = []
            seen_sources: Set[str] = set()
            primary_source = _normalize_source(primary_chunk["metadata"].get("source"))
            if primary_source:
                seen_sources.add(primary_source)

            for chunk, _ in results[1:]:
                source = _normalize_source(chunk["metadata"].get("source"))
                if not source or source in seen_sources:
                    continue
                seen_sources.add(source)
                snippet = _summarize_text(chunk["content"], max_lines=3, max_chars=220)
                if snippet:
                    related_sections.append(_format_related_entry(source, snippet))

            if related_sections:
                answer = f"{answer}\n\n### Related\n" + "\n".join(related_sections)

            return {
                "answer": answer,
                "citations": sorted(_normalize_source(path) for path in citations if path),
                "score": score,
            }

        # Fallback to static stub if the index is empty or missing.
        normalized = prompt.lower()
        for entry in self._fallback_entries:
            if any(kw in normalized for kw in entry.keywords):
                return {
                    "question": entry.question,
                    "answer": entry.answer,
                    "citations": entry.citations,
                }

        return {"answer": "No relevant information available.", "citations": []}


def _collect_citations(chunks: Iterable[dict]) -> Set[str]:
    citations: Set[str] = set()
    for chunk in chunks:
        source = chunk["metadata"].get("source")
        if isinstance(source, str):
            citations.add(source)
    return citations


def _summarize_text(text: str, max_lines: int = 6, max_chars: int = 600) -> str:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return ""

    summary: List[str] = []
    total_chars = 0

    for line in lines:
        summary.append(line)
        total_chars += len(line)
        if len(summary) >= max_lines or total_chars >= max_chars:
            break

    return "\n".join(summary)


def _normalize_source(source: Optional[str]) -> Optional[str]:
    if not source:
        return None

    try:
        path = Path(source)
        if path.is_absolute():
            repo_root = _repo_root()
            if repo_root and repo_root in path.parents:
                path = path.relative_to(repo_root)
        return str(path).lstrip("./")
    except Exception:
        return source


def _repo_root() -> Optional[Path]:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "packages").exists():
            return parent
    return None


def _format_related_entry(source: str, snippet: str) -> str:
    bullet = f"- **{source}**\n"
    snippet_lines = textwrap.indent(snippet, "  ")
    return f"{bullet}{snippet_lines}"

