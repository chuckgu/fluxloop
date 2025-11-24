"""Document ingestion scaffolding for Fluxloop MCP."""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .store import ChunkRecord, IndexStore

logger = logging.getLogger(__name__)

DEFAULT_SOURCES = [
    "docs/**/*.md",
    "packages/website/docs-cli/**/*.md",
    "packages/website/docs-sdk/**/*.md",
    "packages/sdk/**/*.md",
    "samples/**/*.md",
]


@dataclass
class IngestOptions:
    sources: List[str]
    output_dir: Path
    chunk_size: int = 512
    base_dir: Optional[Path] = None


def expand_sources(patterns: Iterable[str]) -> List[Path]:
    root = Path.cwd()
    results: List[Path] = []
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        results.extend([p for p in matches if p.is_file()])
    return results


def chunk_markdown(text: str, chunk_size: int) -> List[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    current: List[str] = []
    token_count = 0

    for line in text.splitlines():
        # Simple reset on heading boundaries.
        if line.startswith("#") and token_count > 0:
            chunks.append("\n".join(current))
            current = []
            token_count = 0

        current.append(line)
        token_count += max(len(line), 1)

        if token_count >= chunk_size:
            chunks.append("\n".join(current))
            current = []
            token_count = 0

    if current:
        chunks.append("\n".join(current))

    return chunks


def ingest(options: IngestOptions) -> Path:
    store = IndexStore(options.output_dir)
    files = expand_sources(options.sources)
    base_dir = options.base_dir or Path.cwd()

    logger.info("Ingesting %s files into %s", len(files), options.output_dir)

    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning("Skipping non-UTF8 document %s", path)
            continue

        try:
            relative = path.relative_to(base_dir)
        except ValueError:
            relative = path

        for idx, chunk in enumerate(chunk_markdown(text, options.chunk_size)):
            if not chunk.strip():
                continue
            metadata = {
                "source": str(relative),
                "chunk_index": idx,
                "total_chunks": None,
            }
            record = ChunkRecord.from_content(chunk, metadata)
            store.add_chunk(record)

    store.flush()
    return store.output_dir


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fluxloop MCP ingestion scaffolding")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.home() / ".fluxloop" / "mcp" / "index" / "dev",
        help="Directory where the JSONL store will be written.",
    )
    parser.add_argument(
        "--source",
        action="append",
        dest="sources",
        default=[],
        help="Glob pattern to include. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Approximate number of characters per chunk.",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=None,
        help="Base directory used to compute relative sources (defaults to current working directory).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    sources = args.sources or DEFAULT_SOURCES
    options = IngestOptions(
        sources=sources,
        output_dir=args.output,
        chunk_size=args.chunk_size,
        base_dir=args.base_dir,
    )
    ingest(options)


if __name__ == "__main__":
    main()

