"""Mode-specific context collectors for Flux Agent multi-mode orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .profile import CollectRepoProfileTool


class _ContextHelper:
    """Utility helpers shared across context collectors."""

    _PREVIEW_LIMIT = 2000

    @staticmethod
    def read_text_preview(path: Path, limit: int = _PREVIEW_LIMIT) -> Tuple[Optional[str], Optional[str]]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:  # pragma: no cover - filesystem variance
            return None, f"Unable to read {path}: {exc}"

        if len(text) > limit:
            text = f"{text[:limit]}\n...[truncated]"
        return text, None

    @staticmethod
    def relative(path: Path, root: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)


class BaseInputContextTool:
    """Collects existing input samples and repository notes for Base Input mode."""

    def __init__(self) -> None:
        self.profile_tool = CollectRepoProfileTool()
        self.helper = _ContextHelper()

    def fetch(self, payload: Dict) -> Dict:
        root_path = Path(payload.get("root", ".")).expanduser().resolve()
        limit = int(payload.get("limit") or 5)

        repo_profile = self.profile_tool.collect({"root": str(root_path)})
        if repo_profile.get("error"):
            return repo_profile

        samples, warnings = self._collect_input_samples(root_path, limit)
        settings_preview = self._read_service_settings(root_path)

        rag_topics = self._derive_topics(samples, repo_profile)

        return {
            "repo_profile": repo_profile,
            "input_samples": samples,
            "service_settings": settings_preview,
            "warnings": warnings,
            "rag_topics": rag_topics,
        }

    def _collect_input_samples(self, root_path: Path, limit: int) -> Tuple[List[Dict], List[str]]:
        samples: List[Dict] = []
        warnings: List[str] = []
        inputs_dir = root_path / "inputs"

        if not inputs_dir.exists():
            warnings.append("inputs directory not found; create inputs/ to seed base prompts.")
            return samples, warnings

        for file_path in sorted(inputs_dir.rglob("*")):
            if not file_path.is_file():
                continue
            preview, error = self.helper.read_text_preview(file_path)
            if error:
                warnings.append(error)
                continue
            samples.append(
                {
                    "path": self.helper.relative(file_path, root_path),
                    "size": file_path.stat().st_size,
                    "preview": preview,
                }
            )
            if len(samples) >= limit:
                break

        if not samples:
            warnings.append("No base input samples found under inputs/.")

        return samples, warnings

    def _read_service_settings(self, root_path: Path) -> Optional[Dict]:
        candidates = [
            root_path / "setting.yaml",
            root_path / "settings.yaml",
            root_path / "configs" / "input.yaml",
        ]
        for path in candidates:
            if not path.exists():
                continue
            preview, _ = self.helper.read_text_preview(path, limit=4000)
            if preview:
                return {
                    "path": self.helper.relative(path, root_path),
                    "preview": preview,
                }
        return None

    def _derive_topics(self, samples: List[Dict], repo_profile: Dict) -> List[Dict]:
        topics: List[Dict] = []
        if repo_profile.get("framework_signals"):
            primary = repo_profile["framework_signals"][0]
            topics.append(
                {
                    "id": f"framework-{primary.get('name', 'unknown')}",
                    "query": f"FluxLoop base input examples for {primary.get('name')}",
                    "reasons": primary.get("rationale", []),
                }
            )

        for sample in samples[:3]:
            topics.append(
                {
                    "id": f"input-{sample['path']}",
                    "query": f"Best practices for FluxLoop inputs similar to {sample['path']}",
                    "reasons": [sample["path"]],
                }
            )

        if not topics:
            topics.append({"id": "base-input", "query": "FluxLoop base input templates", "reasons": []})
        return topics


class ExperimentContextTool:
    """Collects simulation templates and experiment history for Experiment mode."""

    def __init__(self) -> None:
        self.profile_tool = CollectRepoProfileTool()
        self.helper = _ContextHelper()

    def fetch(self, payload: Dict) -> Dict:
        root_path = Path(payload.get("root", ".")).expanduser().resolve()
        limit = int(payload.get("limit") or 5)

        repo_profile = self.profile_tool.collect({"root": str(root_path)})
        if repo_profile.get("error"):
            return repo_profile

        experiments, warnings = self._collect_recent_experiments(root_path, limit)
        simulation_templates = self._collect_simulation_templates(root_path)

        rag_topics = self._derive_topics(experiments, repo_profile)

        return {
            "repo_profile": repo_profile,
            "recent_experiments": experiments,
            "simulation_templates": simulation_templates,
            "runner_configs": repo_profile.get("runner_configs", []),
            "warnings": warnings,
            "rag_topics": rag_topics,
        }

    def _collect_recent_experiments(self, root_path: Path, limit: int) -> Tuple[List[Dict], List[str]]:
        experiments_dir = root_path / "experiments"
        warnings: List[str] = []
        items: List[Dict] = []

        if not experiments_dir.exists():
            warnings.append("experiments directory not found; run at least one evaluation.")
            return items, warnings

        children = [child for child in experiments_dir.iterdir() if child.is_dir()]
        children.sort(key=lambda path: path.stat().st_mtime, reverse=True)

        for child in children[:limit]:
            summary_path = child / "summary.json"
            summary = None
            if summary_path.exists():
                preview, error = self.helper.read_text_preview(summary_path, limit=4000)
                if error:
                    warnings.append(error)
                else:
                    try:
                        summary = json.loads(preview.replace("...[truncated]", ""))
                    except json.JSONDecodeError:
                        summary = {"preview": preview}

            traces_path = child / "traces.jsonl"
            items.append(
                {
                    "path": self.helper.relative(child, root_path),
                    "summary": summary,
                    "has_traces": traces_path.exists(),
                }
            )

        if not items:
            warnings.append("No experiment runs detected under experiments/.")

        return items, warnings

    def _collect_simulation_templates(self, root_path: Path) -> List[Dict]:
        templates: List[Dict] = []
        candidates = [
            root_path / "configs" / "simulation.yaml",
            root_path / "simulation.yaml",
        ]
        for path in candidates:
            if not path.exists():
                continue
            preview, _ = self.helper.read_text_preview(path, limit=4000)
            if preview:
                templates.append(
                    {
                        "path": self.helper.relative(path, root_path),
                        "preview": preview,
                    }
                )
        return templates

    def _derive_topics(self, experiments: List[Dict], repo_profile: Dict) -> List[Dict]:
        topics: List[Dict] = []
        for exp in experiments[:3]:
            topics.append(
                {
                    "id": f"experiment-{exp['path']}",
                    "query": f"Lessons learned from FluxLoop experiment {exp['path']}",
                    "reasons": ["recent_experiment"],
                }
            )
        runner_configs = repo_profile.get("runner_configs") or []
        for config in runner_configs[:2]:
            topics.append(
                {
                    "id": f"runner-{config.get('runner_type', 'unknown')}",
                    "query": f"{config.get('runner_type', 'unknown')} runner configuration tips",
                    "reasons": [config.get("path", "")],
                }
            )
        if not topics:
            topics.append({"id": "experiment-general", "query": "FluxLoop experiment authoring guide", "reasons": []})
        return topics


class InsightContextTool:
    """Collects evaluation reports and metrics for Insight mode."""

    def __init__(self) -> None:
        self.helper = _ContextHelper()

    def fetch(self, payload: Dict) -> Dict:
        root_path = Path(payload.get("root", ".")).expanduser().resolve()
        limit = int(payload.get("limit") or 5)

        reports, warnings = self._collect_reports(root_path, limit)
        aggregated = self._aggregate_metrics(reports)

        topics = []
        if reports:
            topics.append(
                {
                    "id": "insight-reports",
                    "query": "FluxLoop evaluation insight techniques",
                    "reasons": [report["path"] for report in reports[:3]],
                }
            )
        else:
            topics.append(
                {"id": "insight-general", "query": "FluxLoop evaluation troubleshooting", "reasons": []}
            )

        return {
            "reports": reports,
            "aggregated_metrics": aggregated,
            "warnings": warnings,
            "rag_topics": topics,
        }

    def _collect_reports(self, root_path: Path, limit: int) -> Tuple[List[Dict], List[str]]:
        experiments_dir = root_path / "experiments"
        warnings: List[str] = []
        reports: List[Dict] = []

        if not experiments_dir.exists():
            warnings.append("experiments directory not found; run evaluations to enable insight mode.")
            return reports, warnings

        children = [child for child in experiments_dir.iterdir() if child.is_dir()]
        children.sort(key=lambda path: path.stat().st_mtime, reverse=True)

        for child in children[:limit]:
            summary_path = child / "summary.json"
            if not summary_path.exists():
                continue
            preview, error = self.helper.read_text_preview(summary_path, limit=4000)
            if error:
                warnings.append(error)
                continue
            try:
                data = json.loads(preview.replace("...[truncated]", ""))
            except json.JSONDecodeError:
                data = {"preview": preview}

            results = data.get("results") or {}
            reports.append(
                {
                    "path": self.helper.relative(child, root_path),
                    "results": results,
                    "config": data.get("config"),
                }
            )

        if not reports:
            warnings.append("No summary.json files detected in experiments/.")

        return reports, warnings

    def _aggregate_metrics(self, reports: List[Dict]) -> Dict:
        total_runs = 0
        total_success = 0
        durations: List[float] = []

        for report in reports:
            results = report.get("results") or {}
            total_runs += int(results.get("total_runs") or 0)
            total_success += int(results.get("successful") or 0)
            duration = results.get("duration_seconds")
            if isinstance(duration, (int, float)):
                durations.append(float(duration))

        success_rate = (total_success / total_runs) if total_runs else None
        avg_duration = (sum(durations) / len(durations)) if durations else None

        return {
            "total_runs": total_runs,
            "successful": total_success,
            "success_rate": success_rate,
            "avg_duration_seconds": avg_duration,
        }


__all__ = [
    "BaseInputContextTool",
    "ExperimentContextTool",
    "InsightContextTool",
]

