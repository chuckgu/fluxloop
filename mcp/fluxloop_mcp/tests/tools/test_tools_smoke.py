from pathlib import Path
from typing import Dict

import pytest

from fluxloop_mcp.tools.analyze_repository import AnalyzeRepositoryTool
from fluxloop_mcp.tools.detect_frameworks import DetectFrameworksTool
from fluxloop_mcp.tools.generate_integration_steps import GenerateIntegrationStepsTool
from fluxloop_mcp.tools.profile import CollectRepoProfileTool
from fluxloop_mcp.tools.propose_edit_plan import ProposeEditPlanTool
from fluxloop_mcp.tools.run_integration_workflow import RunIntegrationWorkflowTool
from fluxloop_mcp.tools.agent_orchestrator import IntegrationContextTool
from fluxloop_mcp.tools.validate_edit_plan import ValidateEditPlanTool
from fluxloop_mcp.tools.mode_context import (
    BaseInputContextTool,
    ExperimentContextTool,
    InsightContextTool,
)

from fluxloop_mcp.tests.tools._helpers import create_express_repo, seed_index, seed_mode_assets


def test_analyze_repository_success(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    tool = AnalyzeRepositoryTool()

    result = tool.analyze({"root": str(repo_root)})

    assert result["root"] == str(repo_root.resolve())
    assert "typescript" in result["languages"]
    assert "npm" in result["packageManagers"]
    assert result["entryPoints"] == ["src/server.ts"]
    assert "express" in result["frameworkCandidates"]
    assert result["stats"]["files"] >= 1


def test_analyze_repository_missing_root(tmp_path: Path) -> None:
    tool = AnalyzeRepositoryTool()
    missing_root = tmp_path / "missing"

    result = tool.analyze({"root": str(missing_root)})

    assert "error" in result
    assert "does not exist" in result["error"]


def test_detect_frameworks_uses_profile(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    profile = AnalyzeRepositoryTool().analyze({"root": str(repo_root)})

    result = DetectFrameworksTool().detect({"repository_profile": profile})

    frameworks = {entry["name"] for entry in result["frameworks"]}
    assert "express" in frameworks
    assert result["recommended_patterns"]


def test_detect_frameworks_without_profile_returns_empty() -> None:
    result = DetectFrameworksTool().detect({})
    assert result["frameworks"] == []
    assert result["recommended_patterns"] == []


def test_generate_integration_steps_for_express(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    profile = AnalyzeRepositoryTool().analyze({"root": str(repo_root)})

    result = GenerateIntegrationStepsTool().generate(
        {"framework": "express", "repository_profile": profile}
    )

    assert result["framework"] == "express"
    assert result["steps"]
    install_step = result["steps"][0]
    assert install_step["id"] == "install_sdk"
    assert install_step["details"] == "npm install @fluxloop/sdk"
    assert not result["warnings"]


def test_generate_integration_steps_requires_framework() -> None:
    result = GenerateIntegrationStepsTool().generate({})
    assert result == {"error": "framework is required"}


def test_propose_edit_plan_for_express(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    profile = AnalyzeRepositoryTool().analyze({"root": str(repo_root)})

    result = ProposeEditPlanTool().propose(
        {"framework": "express", "repository_profile": profile, "root": str(repo_root)}
    )

    assert result["summary"].startswith("Add Fluxloop integration for express")
    assert result["edits"]
    assert result["edits"][0]["filepath"].endswith("server.ts")
    assert result["warnings"] == []


def test_propose_edit_plan_requires_framework() -> None:
    result = ProposeEditPlanTool().propose({})
    assert result == {"error": "framework is required"}


def test_validate_edit_plan_success(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    profile = AnalyzeRepositoryTool().analyze({"root": str(repo_root)})
    plan = ProposeEditPlanTool().propose(
        {"framework": "express", "repository_profile": profile, "root": str(repo_root)}
    )

    result = ValidateEditPlanTool().validate({"plan": plan, "root": str(repo_root)})

    assert result["valid"] is True
    assert result["issues"] == []


def test_validate_edit_plan_requires_structure() -> None:
    result = ValidateEditPlanTool().validate({"plan": {}})

    assert result["valid"] is False
    assert "Missing fields" in result["issues"][0]


def test_run_integration_workflow_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = create_express_repo(tmp_path)
    index_dir = seed_index(tmp_path)
    monkeypatch.setenv("FLUXLOOP_MCP_INDEX_DIR", str(index_dir))

    result = RunIntegrationWorkflowTool().run(
        {
            "root": str(repo_root),
            "question": "How do I add FluxLoop to this repo?",
            "context": {
                "scope": "files",
                "targets": [str(repo_root / "src" / "server.ts")],
                "selectionSnippet": "const app = express()",
            },
        }
    )

    assert set(result.keys()) == {
        "profile",
        "detection",
        "integration_steps",
        "edit_plan",
        "validation",
        "repo_profile",
        "integration_context",
        "llm_inputs",
        "question",
    }
    assert result["validation"]["valid"] is True
    frameworks = {entry["name"] for entry in result["detection"]["frameworks"]}
    assert "express" in frameworks
    assert result["repo_profile"]["framework_signals"]
    assert result["integration_context"]["files"]
    assert result["llm_inputs"]["structure_context"]["framework_candidates"]
    assert result["llm_inputs"]["rag_topics"]
    assert result["llm_inputs"]["rag_documents"]


def test_run_integration_workflow_missing_root(tmp_path: Path) -> None:
    missing_root = tmp_path / "not-real"

    result = RunIntegrationWorkflowTool().run(
        {
            "root": str(missing_root),
            "question": "Why can't FluxLoop run here?",
        }
    )

    assert result == {"error": f"root path does not exist: {missing_root.resolve()}"}


def test_run_integration_workflow_no_framework(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = create_express_repo(tmp_path)
    index_dir = seed_index(tmp_path)
    monkeypatch.setenv("FLUXLOOP_MCP_INDEX_DIR", str(index_dir))

    class NoFrameworkTool(DetectFrameworksTool):
        def detect(self, payload: Dict) -> Dict:  # type: ignore[override]
            return {"frameworks": [], "recommended_patterns": []}

    tool = RunIntegrationWorkflowTool()
    tool.detect_tool = NoFrameworkTool()

    result = tool.run(
        {
            "root": str(repo_root),
            "question": "What frameworks are available?",
            "context": {
                "scope": "folder",
                "targets": [str(repo_root / "src")],
            },
        }
    )

    assert "warnings" in result
    assert "repo_profile" in result
    assert "llm_inputs" in result
    assert "integration_context" in result
    assert "rag_documents" in result["llm_inputs"]


def test_integration_context_tool_returns_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = create_express_repo(tmp_path)
    index_dir = seed_index(tmp_path)
    monkeypatch.setenv("FLUXLOOP_MCP_INDEX_DIR", str(index_dir))

    tool = IntegrationContextTool()
    result = tool.fetch({"root": str(repo_root)})

    assert "workflow" in result
    assert "structure_context" in result
    assert "rag_topics" in result
    assert isinstance(result["workflow"], dict)
    assert "integration_steps" in result["workflow"]


def test_base_input_context_tool_reads_inputs(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    seed_mode_assets(repo_root)

    tool = BaseInputContextTool()
    result = tool.fetch({"root": str(repo_root)})

    assert "repo_profile" in result
    assert result["input_samples"]
    assert result["rag_topics"]
    assert not result.get("error")


def test_experiment_context_tool_summarizes_runs(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    seed_mode_assets(repo_root)

    tool = ExperimentContextTool()
    result = tool.fetch({"root": str(repo_root)})

    assert result["recent_experiments"]
    assert "simulation_templates" in result
    assert result["rag_topics"]


def test_insight_context_tool_aggregates_metrics(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    seed_mode_assets(repo_root)

    tool = InsightContextTool()
    result = tool.fetch({"root": str(repo_root)})

    assert result["reports"]
    metrics = result["aggregated_metrics"]
    assert metrics["total_runs"] == 2
    assert metrics["successful"] == 1


def test_collect_repo_profile_returns_signals(tmp_path: Path) -> None:
    repo_root = create_express_repo(tmp_path)
    tool = CollectRepoProfileTool()

    result = tool.collect({"root": str(repo_root)})

    assert result["workspaceRoot"] == str(repo_root.resolve())
    assert result["framework_signals"]
    assert result["framework_signals"][0]["name"] == "express"
    assert isinstance(result["agent_signals"], list)
    assert isinstance(result["runner_configs"], list)
    assert isinstance(result["errors"], list)


def test_collect_repo_profile_missing_root(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing"
    tool = CollectRepoProfileTool()

    result = tool.collect({"root": str(missing_root)})

    assert "error" in result

