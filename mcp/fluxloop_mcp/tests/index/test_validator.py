import json
from pathlib import Path

from fluxloop_mcp.index.store import ChunkRecord, IndexStore
from fluxloop_mcp.index.validator import validate_chunks


def _create_store_with_chunk(tmp_path: Path) -> Path:
    store_dir = tmp_path / "store"
    store = IndexStore(store_dir)
    store.add_chunk(
        ChunkRecord.from_content(
            "Fluxloop FAQ entry",
            {"source": "docs/faq.md", "chunk_index": 0},
        )
    )
    store.flush()
    return store_dir


def test_validate_chunks_success(tmp_path: Path) -> None:
    store_dir = _create_store_with_chunk(tmp_path)

    issues = validate_chunks(store_dir)

    assert issues == []


def test_validate_chunks_reports_missing_file(tmp_path: Path) -> None:
    store_dir = tmp_path / "missing"
    store_dir.mkdir()

    issues = validate_chunks(store_dir)

    assert issues
    assert issues[0].level == "ERROR"
    assert "missing chunk file" in issues[0].message


def test_validate_chunks_detects_missing_fields(tmp_path: Path) -> None:
    store_dir = tmp_path / "invalid"
    store_dir.mkdir()
    chunk_file = store_dir / "chunks.jsonl"
    chunk_file.write_text(json.dumps({"id": "abc123"}), encoding="utf-8")

    issues = validate_chunks(store_dir)

    assert issues
    errors = [issue for issue in issues if issue.level == "ERROR"]
    assert errors
    assert "missing fields" in errors[0].message

