"""Simple in-memory recipe registry used by MCP tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Recipe:
    framework: str
    runner_pattern: str
    doc_url: str
    steps: List[Dict[str, str]]


class RecipeRegistry:
    """Minimal recipe lookup for early experimentation."""

    def __init__(self) -> None:
        self._recipes: Dict[str, Recipe] = {
            "express": Recipe(
                framework="express",
                runner_pattern="http-rest",
                doc_url="packages/website/docs-cli/configuration/runners/http-rest.md",
                steps=[
                    {
                        "id": "install_sdk",
                        "title": "Install Fluxloop SDK",
                        "details": "npm install @fluxloop/sdk",
                    },
                    {
                        "id": "add_middleware",
                        "title": "Register middleware",
                        "details": "Add `app.use(fluxloop())` after Express app initialization.",
                    },
                ],
            ),
            "nextjs": Recipe(
                framework="nextjs",
                runner_pattern="http-rest",
                doc_url="packages/website/docs-cli/configuration/runners/http-rest.md",
                steps=[
                    {
                        "id": "update_api_route",
                        "title": "Wrap Next.js API handler",
                        "details": "Instrument Next.js API route to call Fluxloop runner endpoint.",
                    },
                    {
                        "id": "configure_env",
                        "title": "Set Fluxloop environment variables",
                        "details": "Add FLUXLOOP_PROJECT_KEY to .env.local and expose to API route.",
                    },
                ],
            ),
            "nestjs": Recipe(
                framework="nestjs",
                runner_pattern="http-rest",
                doc_url="packages/website/docs-cli/configuration/runners/http-rest.md",
                steps=[
                    {
                        "id": "install_sdk",
                        "title": "Install Fluxloop SDK",
                        "details": "npm install @fluxloop/sdk",
                    },
                    {
                        "id": "add_guard",
                        "title": "Add Fluxloop guard/interceptor",
                        "details": "Register Fluxloop interceptor in main.ts to capture requests.",
                    },
                ],
            ),
            "fastapi": Recipe(
                framework="fastapi",
                runner_pattern="python-function",
                doc_url="packages/website/docs-cli/configuration/runners/python-function.md",
                steps=[
                    {
                        "id": "install_sdk",
                        "title": "Install Fluxloop SDK",
                        "details": "pip install fluxloop",
                    },
                    {
                        "id": "configure_runner",
                        "title": "Update simulation.yaml runner",
                        "details": "Set `runner.target` to your FastAPI callable.",
                    },
                ],
            ),
        }

    def get(self, framework: str) -> Optional[Recipe]:
        return self._recipes.get(framework.lower())

    def list(self) -> List[Recipe]:
        return list(self._recipes.values())


DEFAULT_REGISTRY = RecipeRegistry()

