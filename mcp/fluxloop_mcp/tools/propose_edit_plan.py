"""Propose edit plan tool scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, cast

from fluxloop_mcp.recipes.registry import DEFAULT_REGISTRY, Recipe


EditDict = Dict[str, Any]
AnchorList = List[Dict[str, str]]
PayloadDict = Dict[str, Any]


@dataclass
class EditPlan:
    summary: str
    edits: List[EditDict]
    post_checks: List[str]
    rollback: Dict[str, str]
    warnings: List[str]


class ProposeEditPlanTool:
    """Generate a lightweight edit plan based on recipe metadata."""

    def __init__(self) -> None:
        self.registry = DEFAULT_REGISTRY

    def propose(self, payload: Dict) -> Dict:
        framework = payload.get("framework")
        if not framework:
            return {"error": "framework is required"}

        recipe = self.registry.get(framework)
        if not recipe:
            return {"error": f"no recipe available for framework '{framework}'"}

        repo_profile = payload.get("repository_profile") or {}
        root_path = Path(payload.get("root", ".")).expanduser().resolve()

        summary = f"Add Fluxloop integration for {recipe.framework} project using {recipe.runner_pattern} runner."
        edits, warnings = self._build_edits(recipe, repo_profile, root_path)
        post_checks = self._build_post_checks(repo_profile)

        plan = EditPlan(
            summary=summary,
            edits=edits,
            post_checks=post_checks,
            rollback={"instruction": "git restore -SW :/"},
            warnings=warnings,
        )

        return {
            "summary": plan.summary,
            "edits": plan.edits,
            "postChecks": plan.post_checks,
            "rollback": plan.rollback,
            "warnings": plan.warnings,
        }

    def _build_post_checks(self, repo_profile: Dict) -> List[str]:
        package_managers = repo_profile.get("packageManagers") or []
        if "npm" in package_managers:
            return ["npm run build"]
        if "pnpm" in package_managers:
            return ["pnpm run build"]
        if "yarn" in package_managers:
            return ["yarn build"]
        if "pip" in package_managers:
            return ["pytest || python -m build"]
        return ["Run project tests or build command to ensure integration is successful."]

    def _build_edits(
        self,
        recipe: Recipe,
        repo_profile: Dict,
        root_path: Path,
    ) -> Tuple[List[EditDict], List[str]]:
        warnings: List[str] = []
        entrypoints = repo_profile.get("entryPoints", [])

        if recipe.framework == "express":
            target_path = self._select_entrypoint(
                entrypoints,
                ["src/server.ts", "src/index.ts", "server.ts", "app.ts"],
            )
            if not target_path:
                warnings.append("Could not identify Express entry point; using src/server.ts.")
                target_path = "src/server.ts"

            express_edit: EditDict = {
                "filepath": target_path,
                "strategy": "insert_middleware",
                "anchors": [
                    {"type": "after_match", "pattern": "const app = express()"},
                ],
                "payload": {
                    "import": "import { fluxloop } from '@fluxloop/sdk';",
                    "code": "app.use(fluxloop({ projectKey: '<PROJECT_KEY>' }));",
                },
            }
            warnings.extend(self._validate_anchor_from_edit(root_path, express_edit))
            return [express_edit], warnings

        if recipe.framework == "fastapi":
            target_path = self._select_entrypoint(
                entrypoints,
                ["app/main.py", "main.py"],
            )
            if not target_path:
                warnings.append("Could not identify FastAPI entry point; using app/main.py.")
                target_path = "app/main.py"

            fastapi_edit: EditDict = {
                "filepath": target_path,
                "strategy": "wrap_router",
                "anchors": [
                    {"type": "after_match", "pattern": "app = FastAPI("},
                ],
                "payload": {
                    "import": "from fluxloop import fluxloop",
                    "code": (
                        "@fluxloop.trace()\n"
                        "async def instrumented_handler(request):\n"
                        "    return await original_handler(request)\n"
                    ),
                },
            }
            warnings.extend(self._validate_anchor_from_edit(root_path, fastapi_edit))
            return [fastapi_edit], warnings

        if recipe.framework == "nextjs":
            target_path = self._select_entrypoint(
                entrypoints,
                ["app/api/fluxloop/route.ts", "pages/api/fluxloop.ts"],
            )
            if not target_path:
                warnings.append("Configure a dedicated API route for Fluxloop ingestion.")
                target_path = "pages/api/fluxloop.ts"

            nextjs_edit: EditDict = {
                "filepath": target_path,
                "strategy": "create_or_replace",
                "anchors": [],
                "payload": {
                    "code": (
                        "import { fluxloop } from '@fluxloop/sdk';\n\n"
                        "export default fluxloop(async function handler(req, res) {\n"
                        "  // TODO: integrate with Fluxloop runner\n"
                        "});\n"
                    ),
                },
            }
            warnings.extend(self._validate_anchor_from_edit(root_path, nextjs_edit))
            return [nextjs_edit], warnings

        if recipe.framework == "nestjs":
            target_path = self._select_entrypoint(
                entrypoints,
                ["src/main.ts"],
            )
            if not target_path:
                warnings.append("Could not identify NestJS bootstrap file; using src/main.ts.")
                target_path = "src/main.ts"

            nestjs_edit: EditDict = {
                "filepath": target_path,
                "strategy": "wrap_bootstrap",
                "anchors": [
                    {"type": "after_match", "pattern": "NestFactory.create"},
                ],
                "payload": {
                    "import": "import { FluxloopInterceptor } from '@fluxloop/sdk/nest';",
                    "code": (
                        "app.useGlobalInterceptors(new FluxloopInterceptor({ projectKey: '<PROJECT_KEY>' }));"
                    ),
                },
            }
            warnings.extend(self._validate_anchor_from_edit(root_path, nestjs_edit))
            return [nestjs_edit], warnings

        # Fallback generic instruction
        fallback_edit: EditDict = {
            "filepath": "README.md",
            "strategy": "add_note",
            "anchors": [],
            "payload": {
                "code": "TODO: Add Fluxloop integration steps here.",
            },
        }
        warnings.extend(self._validate_anchor_from_edit(root_path, fallback_edit))
        return [fallback_edit], warnings

    def _select_entrypoint(self, entrypoints: List[str], candidates: List[str]) -> Optional[str]:
        for candidate in candidates:
            for entry in entrypoints:
                if entry.endswith(candidate):
                    return entry
        return None

    def _validate_anchor_from_edit(self, root_path: Path, edit: EditDict) -> List[str]:
        relative_path = cast(Optional[str], edit.get("filepath"))
        anchors = cast(Optional[Sequence[Mapping[str, str]]], edit.get("anchors"))
        payload = cast(Optional[Mapping[str, Any]], edit.get("payload"))
        return self._validate_anchor(root_path, relative_path, anchors, payload)

    def _validate_anchor(
        self,
        root_path: Path,
        relative_path: Optional[str],
        anchors: Optional[Sequence[Mapping[str, str]]],
        payload: Optional[Mapping[str, Any]],
    ) -> List[str]:
        warnings: List[str] = []
        if not relative_path:
            warnings.append("Edit missing filepath; cannot validate anchors.")
            return warnings
        file_path = root_path / relative_path
        if not file_path.exists():
            warnings.append(f"File {relative_path} does not exist; create it before applying edits.")
            return warnings

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            warnings.append(f"Unable to read {relative_path}; verify permissions.")
            return warnings

        anchor_list = list(anchors or [])
        for anchor in anchor_list:
            pattern = anchor.get("pattern") if isinstance(anchor, Mapping) else None
            if pattern and pattern not in text:
                warnings.append(f"Anchor pattern '{pattern}' not found in {relative_path}.")

        payload_data = dict(payload or {})
        import_snippet = payload_data.get("import")
        if isinstance(import_snippet, str) and import_snippet in text:
            warnings.append(f"Import already present in {relative_path}; avoid duplicates.")

        code_snippet = payload_data.get("code")
        if isinstance(code_snippet, str) and code_snippet in text:
            warnings.append(f"Fluxloop code snippet already exists in {relative_path}.")

        return warnings

