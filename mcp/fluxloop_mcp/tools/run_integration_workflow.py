"""End-to-end integration workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from .analyze_repository import AnalyzeRepositoryTool
from .detect_frameworks import DetectFrameworksTool
from .generate_integration_steps import GenerateIntegrationStepsTool
from .llm_context import LlmContextBuilder
from .profile import CollectRepoProfileTool
from .rag import RagService
from .propose_edit_plan import ProposeEditPlanTool
from .validate_edit_plan import ValidateEditPlanTool


class RunIntegrationWorkflowTool:
    """Runs analyze -> detect -> steps -> plan -> validate pipeline."""

    def __init__(self) -> None:
        self.analyze_tool = AnalyzeRepositoryTool()
        self.detect_tool = DetectFrameworksTool()
        self.steps_tool = GenerateIntegrationStepsTool()
        self.plan_tool = ProposeEditPlanTool()
        self.validate_tool = ValidateEditPlanTool()
        self.profile_tool = CollectRepoProfileTool()
        self.llm_builder = LlmContextBuilder()
        self.rag_service = RagService()

    def run(self, payload: Dict) -> Dict:
        root = payload.get("root", ".")

        # Step 1: Analyze repository
        profile = self.analyze_tool.analyze({"root": root})
        if profile.get("error"):
            return {"error": profile["error"]}

        # Step 2: Detect frameworks
        detection_result = self.detect_tool.detect({"repository_profile": profile})
        frameworks = detection_result.get("frameworks", [])
        context_payload = payload.get("context")

        repo_profile_v2 = self.profile_tool.collect(
            {
                "root": root,
                "profile_cache": profile,
                "detection_cache": detection_result,
            }
        )
        if repo_profile_v2.get("error"):
            return repo_profile_v2

        integration_context = self._collect_context(root, context_payload)

        if not frameworks:
            empty_steps = {"steps": [], "framework": None}
            empty_plan = {"summary": "", "edits": [], "warnings": []}
            empty_validation = {"valid": False, "issues": ["No frameworks detected"], "warnings": []}
            llm_inputs = self.llm_builder.build(
                repo_profile=repo_profile_v2,
                detection=detection_result,
                integration_steps=empty_steps,
                edit_plan=empty_plan,
                validation=empty_validation,
                integration_context=integration_context,
            )
            rag_documents = self.rag_service.retrieve(llm_inputs.get("rag_topics", []))
            llm_inputs["rag_documents"] = rag_documents
            return {
                "profile": profile,
                "detection": detection_result,
                "repo_profile": repo_profile_v2,
                "warnings": ["No supported frameworks detected."],
                "integration_context": integration_context,
                "llm_inputs": llm_inputs,
            }

        primary = frameworks[0]["name"]

        # Step 3: Generate integration steps
        steps_result = self.steps_tool.generate(
            {"framework": primary, "repository_profile": profile}
        )

        # Step 4: Propose edit plan
        plan_result = self.plan_tool.propose(
            {
                "framework": primary,
                "repository_profile": profile,
                "root": root,
            }
        )

        # Step 5: Validate edit plan
        validation_result = self.validate_tool.validate(
            {
                "plan": plan_result,
                "root": root,
            }
        )

        llm_inputs = self.llm_builder.build(
            repo_profile=repo_profile_v2,
            detection=detection_result,
            integration_steps=steps_result,
            edit_plan=plan_result,
            validation=validation_result,
            integration_context=integration_context,
        )
        rag_documents = self.rag_service.retrieve(llm_inputs.get("rag_topics", []))
        llm_inputs["rag_documents"] = rag_documents

        return {
            "profile": profile,
            "detection": detection_result,
            "integration_steps": steps_result,
            "edit_plan": plan_result,
            "validation": validation_result,
            "repo_profile": repo_profile_v2,
            "integration_context": integration_context,
            "llm_inputs": llm_inputs,
        }

    def _collect_context(self, root: str, context_payload: Optional[Dict]) -> Dict:
        root_path = Path(root).expanduser().resolve()
        scope = "workspace"
        selection_snippet: Optional[str] = None
        targets_input: Optional[List[str]] = None

        if isinstance(context_payload, dict):
            scope = context_payload.get("scope") or scope
            selection_snippet = context_payload.get("selectionSnippet")
            targets_input = context_payload.get("targets")

        targets = targets_input or [root_path.as_posix()]
        files: List[Dict] = []
        errors: List[Dict] = []

        for target in targets[:10]:
            target_path = Path(target)
            if not target_path.is_absolute():
                target_path = root_path / target_path
            try:
                target_path = target_path.resolve()
            except OSError:
                errors.append(
                    {
                        "stage": "collect_context",
                        "target": target,
                        "message": "Unable to resolve path",
                    }
                )
                continue

            if not str(target_path).startswith(str(root_path)):
                errors.append(
                    {
                        "stage": "collect_context",
                        "target": target,
                        "message": "Target outside workspace; skipped",
                    }
                )
                continue

            rel_path = target_path.relative_to(root_path).as_posix()
            if target_path.is_dir():
                entries = []
                try:
                    for child in target_path.iterdir():
                        entries.append(child.name)
                        if len(entries) >= 10:
                            break
                except OSError as exc:
                    errors.append(
                        {
                            "stage": "collect_context",
                            "target": rel_path,
                            "message": f"Unable to read directory: {exc}",
                        }
                    )
                    continue

                files.append(
                    {
                        "path": rel_path,
                        "kind": "directory",
                        "entries": entries,
                    }
                )
            elif target_path.is_file():
                try:
                    text = target_path.read_text(encoding="utf-8", errors="ignore")
                except OSError as exc:
                    errors.append(
                        {
                            "stage": "collect_context",
                            "target": rel_path,
                            "message": f"Unable to read file: {exc}",
                        }
                    )
                    continue

                snippet = text[:2000]
                files.append(
                    {
                        "path": rel_path,
                        "kind": "file",
                        "size": target_path.stat().st_size,
                        "snippet": snippet,
                    }
                )
            else:
                errors.append(
                    {
                        "stage": "collect_context",
                        "target": rel_path,
                        "message": "Target is neither file nor directory",
                    }
                )

        if not files and not targets_input:
            files.append(
                {
                    "path": ".",
                    "kind": "directory",
                    "entries": [child.name for child in list(root_path.iterdir())[:10]],
                }
            )

        return {
            "scope": scope,
            "selectionSnippet": selection_snippet,
            "targets": [Path(t).as_posix() for t in targets[:10]],
            "files": files,
            "errors": errors,
        }

