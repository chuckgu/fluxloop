"""Regression tests covering multi-mode context flows."""

from __future__ import annotations

from pathlib import Path

import pytest

from fluxloop_mcp.tools.agent_orchestrator import IntegrationContextTool
from fluxloop_mcp.tools.mode_context import (
    BaseInputContextTool,
    ExperimentContextTool,
    InsightContextTool,
)

from fluxloop_mcp.tests.tools._helpers import create_express_repo, seed_index, seed_mode_assets


def test_multi_mode_contexts_regression(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = create_express_repo(tmp_path)
    seed_mode_assets(repo_root)
    index_dir = seed_index(tmp_path)
    monkeypatch.setenv("FLUXLOOP_MCP_INDEX_DIR", str(index_dir))

    integration = IntegrationContextTool().fetch({"root": str(repo_root), "context": {"scope": "workspace"}})
    assert "workflow" in integration
    assert integration["workflow"].get("integration_steps")
    assert integration["structure_context"]
    assert integration["rag_topics"]

    base_context = BaseInputContextTool().fetch({"root": str(repo_root), "limit": 5})
    assert base_context["input_samples"]
    assert base_context["service_settings"]
    assert base_context["rag_topics"]

    experiment_context = ExperimentContextTool().fetch({"root": str(repo_root), "limit": 5})
    assert experiment_context["recent_experiments"]
    assert experiment_context["rag_topics"]

    insight_context = InsightContextTool().fetch({"root": str(repo_root), "limit": 5})
    assert insight_context["reports"]
    aggregated = insight_context["aggregated_metrics"]
    assert aggregated["total_runs"] >= 0
    assert aggregated["successful"] >= 0

