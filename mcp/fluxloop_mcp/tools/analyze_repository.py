"""Analyze repository tool implementation."""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


LANGUAGE_EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".rb": "ruby",
    ".java": "java",
    ".cs": "csharp",
}

CODE_EXTENSIONS: Set[str] = set(LANGUAGE_EXTENSIONS.keys())
DEFAULT_EXCLUDES = {".git", "node_modules", ".venv", "venv", "__pycache__", ".idea", ".pytest_cache"}

ENTRYPOINT_RULES: Tuple[Tuple[str, str], ...] = (
    ("src/server.ts", "express"),
    ("app/main.py", "fastapi"),
    ("main.py", ""),
    ("manage.py", "django"),
    ("src/index.ts", ""),
    ("src/main.ts", ""),
)

PY_PACKAGE_MARKERS = (
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
)

JS_PACKAGE_MARKERS = (
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
)


@dataclass
class RepositoryStats:
    files: int
    loc: int


class AnalyzeRepositoryTool:
    """Scans a repository directory to produce profile metadata."""

    def analyze(self, payload: Dict) -> Dict:
        root_path = Path(payload.get("root", ".")).expanduser().resolve()
        if not root_path.exists():
            return {"error": f"root path does not exist: {root_path}"}

        globs = payload.get("globs")  # Currently unused; placeholder for future filtering

        languages_counter: Counter[str] = Counter()
        package_managers: Set[str] = set()
        entrypoints: Set[str] = set()
        framework_candidates: Set[str] = set()
        file_count = 0
        loc_count = 0

        requirement_paths: List[Path] = []
        package_json_paths: List[Path] = []

        for dirpath, dirnames, filenames in os.walk(root_path):
            self._filter_excluded(dirpath, dirnames)
            rel_dir = Path(dirpath).relative_to(root_path)

            for filename in filenames:
                file_path = Path(dirpath) / filename
                rel_path = file_path.relative_to(root_path)
                suffix = file_path.suffix.lower()

                # Track package manager hints
                if filename in PY_PACKAGE_MARKERS:
                    package_managers.add("pip")
                    requirement_paths.append(file_path)
                if filename in JS_PACKAGE_MARKERS:
                    package_managers.add("npm")
                    if filename == "package.json":
                        package_json_paths.append(file_path)

                if suffix in CODE_EXTENSIONS:
                    languages_counter[LANGUAGE_EXTENSIONS[suffix]] += 1
                    file_count += 1
                    loc_count += self._count_loc(file_path)

                entrypoint_match = self._match_entrypoint(rel_path)
                if entrypoint_match:
                    entrypoints.add(entrypoint_match[0])
                    if entrypoint_match[1]:
                        framework_candidates.add(entrypoint_match[1])

        # Parse dependency files for additional framework hints
        framework_candidates.update(self._frameworks_from_requirements(requirement_paths))
        package_frameworks = self._frameworks_from_package_json(package_json_paths)
        framework_candidates.update(package_frameworks)

        languages = [lang for lang, _ in languages_counter.most_common()]
        entrypoint_list = sorted(entrypoints)
        framework_list = sorted(framework_candidates)
        risk_flags = self._compute_risk_flags(entrypoint_list)

        stats = RepositoryStats(files=file_count, loc=loc_count)

        return {
            "root": str(root_path),
            "languages": languages,
            "packageManagers": sorted(package_managers),
            "entryPoints": entrypoint_list,
            "frameworkCandidates": framework_list,
            "riskFlags": risk_flags,
            "stats": {"files": stats.files, "loc": stats.loc},
        }

    def _filter_excluded(self, dirpath: str, dirnames: List[str]) -> None:
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDES]

    def _match_entrypoint(self, rel_path: Path) -> Optional[Tuple[str, str]]:
        normalized = rel_path.as_posix()
        for rule_path, framework in ENTRYPOINT_RULES:
            if normalized.endswith(rule_path):
                return normalized, framework
        return None

    def _count_loc(self, file_path: Path) -> int:
        try:
            with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
                return sum(1 for _ in handle)
        except (OSError, UnicodeDecodeError):
            return 0

    def _frameworks_from_requirements(self, paths: Iterable[Path]) -> Set[str]:
        frameworks: Set[str] = set()
        keywords = {
            "fastapi": "fastapi",
            "django": "django",
            "flask": "flask",
            "langchain": "langchain",
            "opentelemetry": "opentelemetry",
        }

        for path in paths:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            for needle, framework in keywords.items():
                if needle in text:
                    frameworks.add(framework)
        return frameworks

    def _frameworks_from_package_json(self, paths: Iterable[Path]) -> Set[str]:
        frameworks: Set[str] = set()
        keywords = {
            "express": "express",
            "next": "nextjs",
            "nestjs": "nestjs",
            "svelte": "svelte",
        }

        for path in paths:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue

            dependencies = self._collect_package_dependencies(data)
            for needle, framework in keywords.items():
                if needle in dependencies:
                    frameworks.add(framework)
        return frameworks

    def _collect_package_dependencies(self, package_json: Dict) -> Set[str]:
        dependencies: Set[str] = set()
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            section = package_json.get(key) or {}
            if isinstance(section, dict):
                dependencies.update(name.lower() for name in section.keys())
        return dependencies

    def _compute_risk_flags(self, entrypoints: List[str]) -> List[str]:
        flags: List[str] = []
        if len(entrypoints) == 0:
            flags.append("missing_entrypoint")
        elif len(entrypoints) > 1:
            flags.append("multiple_entrypoints")
        return flags

