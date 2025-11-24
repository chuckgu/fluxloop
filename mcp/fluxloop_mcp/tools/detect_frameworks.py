"""Detect frameworks tool leveraging repository profiles and recipes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from fluxloop_mcp.recipes.registry import DEFAULT_REGISTRY


@dataclass
class FrameworkDetectionResult:
    name: str
    confidence: float
    insert_anchors: List[Dict[str, str]]
    reasons: List[str]


class DetectFrameworksTool:
    """Heuristic detector that combines repository metadata with recipe knowledge."""

    def __init__(self) -> None:
        self.registry = DEFAULT_REGISTRY

    def detect(self, payload: Dict) -> Dict:
        profile = payload.get("repository_profile") or {}
        languages = {lang.lower() for lang in profile.get("languages", [])}
        package_managers = {pm.lower() for pm in profile.get("packageManagers", [])}
        entrypoints = profile.get("entryPoints", [])
        declared_frameworks = {fw.lower() for fw in profile.get("frameworkCandidates", [])}

        detections: List[FrameworkDetectionResult] = []

        def add_detection(
            name: str,
            base_confidence: float,
            anchors: List[Dict[str, str]],
            reason: str,
        ) -> None:
            existing = next((d for d in detections if d.name == name), None)
            if existing:
                existing.confidence = min(0.99, existing.confidence + base_confidence * 0.2)
                existing.reasons.append(reason)
                existing.insert_anchors.extend(a for a in anchors if a not in existing.insert_anchors)
            else:
                detections.append(
                    FrameworkDetectionResult(
                        name=name,
                        confidence=base_confidence,
                        insert_anchors=anchors,
                        reasons=[reason],
                    )
                )

        # Language/package hints
        if {"typescript", "javascript"} & languages or "npm" in package_managers:
            add_detection(
                "express",
                0.6,
                [{"filepath": "src/server.ts", "pattern": "const app = express()"}],
                "JavaScript/TypeScript project with npm detected.",
            )

        if "python" in languages or "pip" in package_managers:
            add_detection(
                "fastapi",
                0.55,
                [{"filepath": "app/main.py", "pattern": "FastAPI("}],
                "Python project with pip detected.",
            )

        # Entry point hints
        for path in entrypoints:
            lowered = path.lower()
            if lowered.endswith("src/server.ts"):
                add_detection(
                    "express",
                    0.7,
                    [{"filepath": path, "pattern": "const app = express()"}],
                    f"Entry point {path} suggests Express usage.",
                )
            if lowered.endswith("app/main.py"):
                add_detection(
                    "fastapi",
                    0.7,
                    [{"filepath": path, "pattern": "FastAPI("}],
                    f"Entry point {path} suggests FastAPI usage.",
                )
            if lowered.endswith("pages/api/fluxloop.ts") or lowered.endswith("app/api/fluxloop/route.ts"):
                add_detection(
                    "nextjs",
                    0.65,
                    [{"filepath": path, "pattern": "export default"}],
                    f"Entry point {path} indicates Next.js API route.",
                )
            if lowered.endswith("src/main.ts"):
                add_detection(
                    "nestjs",
                    0.65,
                    [{"filepath": path, "pattern": "NestFactory.create"}],
                    f"Entry point {path} indicates NestJS bootstrap file.",
                )

        # Declared frameworks from dependency analysis
        for candidate in declared_frameworks:
            if candidate in {"fastapi", "django", "flask"}:
                add_detection(
                    candidate,
                    0.8,
                    [],
                    f"Dependency analysis found {candidate}.",
                )
            if candidate in {"express", "nextjs", "nestjs"}:
                add_detection(
                    candidate,
                    0.85,
                    [],
                    f"package.json suggests {candidate}.",
                )

        # Promote recipes without detections if strongly implied by recipes
        if not detections and declared_frameworks:
            for candidate in declared_frameworks:
                recipe = self.registry.get(candidate)
                if recipe:
                    add_detection(
                        candidate,
                        0.5,
                        [],
                        f"Recipe available for declared framework {candidate}.",
                    )

        # Assemble response
        frameworks_response = [
            {
                "name": detection.name,
                "confidence": round(min(detection.confidence, 0.99), 2),
                "insertAnchors": detection.insert_anchors,
                "reasons": detection.reasons,
            }
            for detection in detections
        ]

        recommended_patterns = []
        for detection in detections:
            recipe = self.registry.get(detection.name)
            if recipe:
                recommended_patterns.append(
                    {
                        "framework": recipe.framework,
                        "runner_pattern": recipe.runner_pattern,
                        "doc_url": recipe.doc_url,
                        "confidence": round(min(detection.confidence, 0.99), 2),
                    }
                )

        return {
            "frameworks": frameworks_response,
            "recommended_patterns": recommended_patterns,
        }

