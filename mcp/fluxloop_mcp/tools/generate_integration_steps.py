"""Generate integration steps tool scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from fluxloop_mcp.recipes.registry import DEFAULT_REGISTRY, Recipe


@dataclass
class Step:
    id: str
    title: str
    details: str


class GenerateIntegrationStepsTool:
    """Produces integration checklists based on simple recipes."""

    def __init__(self) -> None:
        self.registry = DEFAULT_REGISTRY

    def generate(self, payload: Dict) -> Dict:
        framework = payload.get("framework")
        if not framework:
            return {"error": "framework is required"}

        recipe = self.registry.get(framework)
        if not recipe:
            return {"error": f"no recipe available for framework '{framework}'"}

        repo_profile = payload.get("repository_profile") or {}
        package_manager = self._resolve_package_manager(payload, repo_profile)
        entrypoints = repo_profile.get("entryPoints", [])

        warnings: List[str] = []
        if not entrypoints:
            warnings.append("No entry points detected; verify runner target manually.")

        steps = [
            {
                "id": step["id"],
                "title": step["title"],
                "details": self._hydrate_details(step, package_manager),
                "doc_ref": recipe.doc_url,
            }
            for step in recipe.steps
        ]

        return {
            "framework": recipe.framework,
            "runner_pattern": recipe.runner_pattern,
            "steps": steps,
            "estimated_time": "10 minutes",
            "package_manager": package_manager,
            "warnings": warnings,
        }

    def _resolve_package_manager(self, payload: Dict, profile: Dict) -> str:
        explicit = payload.get("package_manager")
        if isinstance(explicit, str) and explicit:
            return explicit

        managers = profile.get("packageManagers") or []
        priority = ["pnpm", "yarn", "bun", "npm", "pip"]
        for candidate in priority:
            if candidate in [m.lower() for m in managers]:
                return candidate
        return "npm" if "javascript" in (profile.get("languages") or []) else "pip"

    def _hydrate_details(self, step: Dict[str, str], package_manager: str) -> str:
        details = step["details"]
        if step["id"] == "install_sdk":
            details = self._format_install_command(package_manager)
        return details

    def _format_install_command(self, package_manager: str) -> str:
        if package_manager == "pnpm":
            return "pnpm add @fluxloop/sdk"
        if package_manager == "yarn":
            return "yarn add @fluxloop/sdk"
        if package_manager == "bun":
            return "bun add @fluxloop/sdk"
        if package_manager == "pip":
            return "pip install fluxloop"
        # default npm
        return "npm install @fluxloop/sdk"

