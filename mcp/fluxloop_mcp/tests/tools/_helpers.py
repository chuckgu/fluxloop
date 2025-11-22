"""Shared test helpers for Fluxloop MCP tool tests."""

from __future__ import annotations

import json
from pathlib import Path

from fluxloop_mcp.index import ChunkRecord, IndexStore


def create_express_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "express-app"
    (repo_root / "src").mkdir(parents=True)

    (repo_root / "src" / "server.ts").write_text(
        "import express from 'express';\n"
        "const app = express();\n"
        "app.get('/', (_req, res) => res.send('ok'));\n"
        "app.listen(3000);\n",
        encoding="utf-8",
    )

    (repo_root / "package.json").write_text(
        json.dumps(
            {
                "name": "express-app",
                "version": "0.1.0",
                "dependencies": {"express": "^4.18.0"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return repo_root


def seed_index(tmp_path: Path) -> Path:
    index_dir = tmp_path / "index"
    store = IndexStore(index_dir)
    store.add_chunk(
        ChunkRecord.from_content(
            "FluxLoop integration guide: install @fluxloop/sdk and add middleware hooks.",
            {"source": "docs/express.md", "chunk_index": 0},
        )
    )
    store.flush()
    return index_dir


def seed_mode_assets(repo_root: Path) -> None:
    inputs_dir = repo_root / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    (inputs_dir / "generated.yaml").write_text(
        "items:\n  - prompt: hello world\n    intent: greeting\n",
        encoding="utf-8",
    )

    experiments_dir = repo_root / "experiments" / "exp_1"
    experiments_dir.mkdir(parents=True, exist_ok=True)
    (experiments_dir / "summary.json").write_text(
        json.dumps(
            {
                "config": {"name": "exp_1", "runner": {"type": "local"}},
                "results": {"total_runs": 2, "successful": 1, "duration_seconds": 12.5},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (repo_root / "setting.yaml").write_text(
        "service: express-app\nentrypoint: src/server.ts\n",
        encoding="utf-8",
    )

