"""Collect an enriched repository profile used by Fluxloop integration tools."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:  # Optional dependency; fall back to heuristic parsing if unavailable.
    import yaml  # type: ignore
except Exception:  # pragma: no cover - handled gracefully in runtime
    yaml = None

from .analyze_repository import AnalyzeRepositoryTool
from .detect_frameworks import DetectFrameworksTool


_MAX_AGENT_FILES = 200
_MAX_AGENT_BYTES = 200_000


@dataclass
class FrameworkSignal:
    name: str
    confidence: float
    entrypoints: List[str]
    rationale: List[str]
    hints: List[str]
    status: str


class CollectRepoProfileTool:
    """Aggregates repository signals into the repo_profile_v2 schema."""

    def __init__(self) -> None:
        self.analyzer = AnalyzeRepositoryTool()
        self.detector = DetectFrameworksTool()

    def collect(self, payload: Dict) -> Dict:
        root = payload.get("root", ".")
        root_path = Path(root).expanduser().resolve()

        analyzer_result = payload.get("profile_cache")
        if not isinstance(analyzer_result, dict):
            analyzer_result = self.analyzer.analyze({"root": str(root_path)})
        if analyzer_result.get("error"):
            return analyzer_result

        detection_result = payload.get("detection_cache")
        if not isinstance(detection_result, dict):
            detection_result = self.detector.detect({"repository_profile": analyzer_result})


        framework_signals = self._build_framework_signals(analyzer_result, detection_result)
        agent_signals, agent_errors = self._scan_agent_signals(root_path)
        runner_configs, runner_errors = self._collect_runner_configs(root_path)

        errors = []
        errors.extend(agent_errors)
        errors.extend(runner_errors)

        profile = {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "workspaceRoot": str(root_path),
            "framework_signals": framework_signals,
            "agent_signals": agent_signals,
            "runner_configs": runner_configs,
            "errors": errors,
        }
        return profile

    def _build_framework_signals(self, analyzer: Dict, detection: Dict) -> List[Dict]:
        entrypoints = analyzer.get("entryPoints", [])
        known_candidates = set()

        signals: List[Dict] = []
        for item in detection.get("frameworks", []):
            name = item.get("name")
            if not name:
                continue
            known_candidates.add(name)
            confidence = float(item.get("confidence") or 0.0)
            rationale = item.get("reasons") or []
            hints = []
            anchors = item.get("insertAnchors") or []
            for anchor in anchors:
                filepath = anchor.get("filepath")
                pattern = anchor.get("pattern")
                if filepath and pattern:
                    hints.append(f"anchor:{filepath}:{pattern}")
            status = self._status_from_confidence(confidence)
            signals.append(
                {
                    "name": name,
                    "confidence": confidence,
                    "entrypoints": entrypoints,
                    "rationale": rationale,
                    "hints": hints,
                    "status": status,
                }
            )

        # Include low-confidence candidates surfaced by the analyzer.
        for candidate in analyzer.get("frameworkCandidates", []):
            if candidate in known_candidates:
                continue
            signals.append(
                {
                    "name": candidate,
                    "confidence": 0.35,
                    "entrypoints": entrypoints,
                    "rationale": ["Detected via dependency or file heuristic"],
                    "hints": [],
                    "status": "ambiguous",
                }
            )

        signals.sort(key=lambda item: item["confidence"], reverse=True)
        return signals

    def _scan_agent_signals(self, root_path: Path) -> Tuple[List[Dict], List[Dict]]:
        signals: List[Dict] = []
        errors: List[Dict] = []
        scanned = 0

        for path in root_path.rglob("*.py"):
            if scanned >= _MAX_AGENT_FILES:
                break
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                errors.append(
                    {
                        "stage": "agent_scan",
                        "file": str(path),
                        "message": f"Unable to read file: {exc}",
                    }
                )
                continue

            if len(text) > _MAX_AGENT_BYTES:
                text = text[: _MAX_AGENT_BYTES]

            if "fluxloop" not in text:
                continue

            line_no, snippet = self._find_line(text, "fluxloop")
            agent_type = self._infer_agent_type(path)
            signals.append(
                {
                    "module": str(path.relative_to(root_path)),
                    "agent_type": agent_type,
                    "class_or_function": self._find_declared_symbol(text),
                    "framework_dep": "fluxloop",
                    "evidence": [
                        {
                            "pattern": "fluxloop",
                            "file": str(path.relative_to(root_path)),
                            "line": line_no,
                        }
                    ],
                    "confidence": 0.65,
                    "notes": snippet,
                }
            )

        signals.sort(key=lambda entry: entry["module"])
        return signals, errors

    def _collect_runner_configs(self, root_path: Path) -> Tuple[List[Dict], List[Dict]]:
        configs: List[Dict] = []
        errors: List[Dict] = []

        for rel_path in ("configs/simulation.yaml", "configs/input.yaml"):
            file_path = root_path / rel_path
            if not file_path.exists():
                continue

            data = self._load_yaml(file_path)
            if data is None:
                # Heuristic fallback
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                runner_entry = self._extract_runner_from_text(text)
                if runner_entry:
                    configs.append(
                        {
                            "source": rel_path.split("/")[-1].split(".")[0] + "_yaml",
                            "path": f"{rel_path}#runner",
                            "runner_type": runner_entry.get("type", "unknown"),
                            "target": runner_entry.get("target", ""),
                            "parameters": runner_entry.get("parameters", {}),
                            "linked_frameworks": runner_entry.get("frameworks", []),
                            "confidence": 0.4,
                        }
                    )
                continue

            runner_section = data.get("runner") if isinstance(data, dict) else None
            if isinstance(runner_section, dict):
                configs.append(
                    {
                        "source": rel_path.split("/")[-1].split(".")[0] + "_yaml",
                        "path": f"{rel_path}#runner",
                        "runner_type": runner_section.get("type", "unknown"),
                        "target": runner_section.get("target", ""),
                        "parameters": runner_section.get("parameters", {}),
                        "linked_frameworks": runner_section.get("frameworks", []),
                        "confidence": 0.8,
                    }
                )
            else:
                errors.append(
                    {
                        "stage": "runner_scan",
                        "file": rel_path,
                        "message": "runner section missing or invalid",
                    }
                )

        env_file = root_path / ".env"
        if env_file.exists():
            try:
                env_content = env_file.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                errors.append(
                    {"stage": "runner_scan", "file": ".env", "message": f"Unable to read: {exc}"}
                )
            else:
                target = self._find_env_value(env_content, "FLUXLOOP_RUNNER_TARGET")
                if target:
                    configs.append(
                        {
                            "source": "env",
                            "path": ".env#FLUXLOOP_RUNNER_TARGET",
                            "runner_type": "configured",
                            "target": target,
                            "parameters": {},
                            "linked_frameworks": [],
                            "confidence": 0.5,
                        }
                    )

        return configs, errors

    @staticmethod
    def _status_from_confidence(confidence: float) -> str:
        if confidence >= 0.75:
            return "confirmed"
        if confidence >= 0.5:
            return "likely"
        return "ambiguous"

    @staticmethod
    def _find_line(text: str, needle: str) -> Tuple[int, str]:
        for idx, line in enumerate(text.splitlines(), start=1):
            if needle in line:
                return idx, line.strip()
        return 1, ""

    @staticmethod
    def _infer_agent_type(path: Path) -> str:
        lowered = str(path).lower()
        if "input" in lowered:
            return "base_input_generator"
        if "experiment" in lowered or "simulation" in lowered:
            return "experiment_runner"
        if "insight" in lowered or "analysis" in lowered:
            return "insight_analyzer"
        return "integration_agent"

    @staticmethod
    def _find_declared_symbol(content: str) -> Optional[str]:
        match = re.search(r"class\s+([A-Za-z0-9_]+)\(", content)
        if match:
            return match.group(1)
        match = re.search(r"def\s+([A-Za-z0-9_]+)\(", content)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _load_yaml(path: Path) -> Optional[Dict]:
        if yaml is None:
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
            if isinstance(data, dict):
                return data
        except Exception:
            return None
        return None

    @staticmethod
    def _extract_runner_from_text(text: str) -> Optional[Dict]:
        runner_match = re.search(r"runner:\s*(\{.*\})", text, re.DOTALL)
        if runner_match:
            try:
                data = json.loads(runner_match.group(1))
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                return None

        # Fallback for simple key-value layout
        type_match = re.search(r"runner:\s*\n\s+type:\s*(.+)", text)
        target_match = re.search(r"runner:\s*\n(?:\s+.+\n)*\s+target:\s*(.+)", text)
        if type_match or target_match:
            return {
                "type": type_match.group(1).strip() if type_match else "unknown",
                "target": target_match.group(1).strip() if target_match else "",
                "parameters": {},
                "frameworks": [],
            }
        return None

    @staticmethod
    def _find_env_value(content: str, key: str) -> Optional[str]:
        pattern = re.compile(rf"^{re.escape(key)}=(.+)$", re.MULTILINE)
        match = pattern.search(content)
        if match:
            return match.group(1).strip()
        return None


