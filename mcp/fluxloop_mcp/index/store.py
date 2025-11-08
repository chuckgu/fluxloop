"""Lightweight JSONL store scaffolding for document chunks."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class ChunkRecord:
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_content(cls, content: str, metadata: Dict[str, Any]) -> "ChunkRecord":
        return cls(chunk_id=str(uuid.uuid4()), content=content, metadata=metadata)


class IndexStore:
    """Minimal store that writes chunks into JSONL for early experimentation."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.chunks: List[ChunkRecord] = []
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._chunk_file = self.output_dir / "chunks.jsonl"

    def add_chunk(self, record: ChunkRecord) -> None:
        self.chunks.append(record)

    def extend(self, records: Iterable[ChunkRecord]) -> None:
        self.chunks.extend(records)

    def flush(self) -> None:
        with self._chunk_file.open("w", encoding="utf-8") as fp:
            for record in self.chunks:
                json.dump(
                    {
                        "id": record.chunk_id,
                        "content": record.content,
                        "metadata": record.metadata,
                    },
                    fp,
                    ensure_ascii=False,
                )
                fp.write("\n")

