"""Index validation scaffolding."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


REQUIRED_CHUNK_FIELDS = {"id", "content", "metadata"}
REQUIRED_METADATA_FIELDS = {"source"}


@dataclass
class ValidationIssue:
    level: str  # "ERROR" | "WARNING"
    message: str

    def __str__(self) -> str:
        return f"{self.level}: {self.message}"


def load_chunks(chunk_file: Path) -> Iterable[dict]:
    with chunk_file.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def validate_chunks(store_dir: Path) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    chunk_file = store_dir / "chunks.jsonl"

    if not chunk_file.exists():
        issues.append(ValidationIssue("ERROR", f"missing chunk file: {chunk_file}"))
        return issues

    seen_ids = set()
    for idx, chunk in enumerate(load_chunks(chunk_file)):
        missing = REQUIRED_CHUNK_FIELDS - set(chunk.keys())
        if missing:
            issues.append(
                ValidationIssue(
                    "ERROR", f"chunk {idx} missing fields: {', '.join(sorted(missing))}"
                )
            )
            continue

        chunk_id = chunk["id"]
        if chunk_id in seen_ids:
            issues.append(ValidationIssue("WARNING", f"duplicate chunk id: {chunk_id}"))
        else:
            seen_ids.add(chunk_id)

        metadata = chunk.get("metadata", {})
        missing_meta = REQUIRED_METADATA_FIELDS - set(metadata.keys())
        if missing_meta:
            issues.append(
                ValidationIssue(
                    "WARNING",
                    f"chunk {chunk_id} missing metadata fields: {', '.join(sorted(missing_meta))}",
                )
            )
        else:
            source = metadata.get("source")
            if not isinstance(source, str) or not source:
                issues.append(
                    ValidationIssue("WARNING", f"chunk {chunk_id} has invalid source: {source!r}")
                )

        content = chunk.get("content", "")
        if not isinstance(content, str) or not content.strip():
            issues.append(
                ValidationIssue("WARNING", f"chunk {chunk_id} has empty content")
            )

    if not seen_ids:
        issues.append(ValidationIssue("ERROR", "no chunks loaded from index"))

    return issues


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Fluxloop MCP index integrity.")
    parser.add_argument(
        "--index-dir",
        type=Path,
        default=Path.home() / ".fluxloop" / "mcp" / "index" / "dev",
        help="Directory containing chunks.jsonl.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status on warnings.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    issues = validate_chunks(args.index_dir)

    if not issues:
        print(f"[fluxloop-mcp] index OK at {args.index_dir}")
        return

    for issue in issues:
        print(issue)

    has_error = any(issue.level == "ERROR" for issue in issues)
    has_warning = any(issue.level == "WARNING" for issue in issues)

    if has_error or (args.strict and has_warning):
        sys.exit(1)


if __name__ == "__main__":
    main()

