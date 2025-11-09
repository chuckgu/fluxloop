import json
from pathlib import Path

import pytest

from fluxloop_mcp.tools.analyze_repository import AnalyzeRepositoryTool
from fluxloop_mcp.tools.detect_frameworks import DetectFrameworksTool
from fluxloop_mcp.tools.generate_integration_steps import GenerateIntegrationStepsTool
from fluxloop_mcp.tools.propose_edit_plan import ProposeEditPlanTool
from fluxloop_mcp.tools.run_integration_workflow import RunIntegrationWorkflowTool
from fluxloop_mcp.tools.validate_edit_plan import ValidateEditPlanTool


def _create_express_repo(tmp_path: Path) -> Path:
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


def test_analyze_repository_success(tmp_path: Path) -> None:
    repo_root = _create_express_repo(tmp_path)
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
    repo_root = _create_express_repo(tmp_path)
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
    repo_root = _create_express_repo(tmp_path)
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
    repo_root = _create_express_repo(tmp_path)
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
    repo_root = _create_express_repo(tmp_path)
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


def test_run_integration_workflow_success(tmp_path: Path) -> None:
    repo_root = _create_express_repo(tmp_path)

    result = RunIntegrationWorkflowTool().run({"root": str(repo_root)})

    assert set(result.keys()) == {
        "profile",
        "detection",
        "integration_steps",
        "edit_plan",
        "validation",
    }
    assert result["validation"]["valid"] is True
    frameworks = {entry["name"] for entry in result["detection"]["frameworks"]}
    assert "express" in frameworks


def test_run_integration_workflow_missing_root(tmp_path: Path) -> None:
    missing_root = tmp_path / "not-real"

    result = RunIntegrationWorkflowTool().run({"root": str(missing_root)})

    assert result == {"error": f"root path does not exist: {missing_root.resolve()}"}

