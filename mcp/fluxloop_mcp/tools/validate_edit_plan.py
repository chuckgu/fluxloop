"""Validate edit plan tool with filesystem checks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


REQUIRED_PLAN_FIELDS = {"summary", "edits"}
REQUIRED_EDIT_FIELDS = {"filepath", "strategy"}


class ValidateEditPlanTool:
    """Performs structural validation on edit plans."""

    def validate(self, payload: Dict) -> Dict:
        plan = payload.get("plan")
        if not isinstance(plan, dict):
            return {"error": "plan must be an object"}

        root = Path(payload.get("root", ".")).expanduser().resolve()
        issues: List[str] = []
        warnings: List[str] = []

        missing_fields = REQUIRED_PLAN_FIELDS - plan.keys()
        if missing_fields:
            issues.append(f"Missing fields: {', '.join(sorted(missing_fields))}")

        edits_input = plan.get("edits")
        edits = edits_input if isinstance(edits_input, list) else []
        if not edits:
            issues.append("No edits defined in plan.")
        else:
            for idx, edit in enumerate(edits):
                if not isinstance(edit, dict):
                    issues.append(f"Edit #{idx} is not an object.")
                    continue
                missing_edit_fields = REQUIRED_EDIT_FIELDS - edit.keys()
                if missing_edit_fields:
                    issues.append(
                        f"Edit #{idx} missing fields: {', '.join(sorted(missing_edit_fields))}"
                    )

                filepath = edit.get("filepath")
                anchors = edit.get("anchors", [])
                payload_content = edit.get("payload", {})
                warnings.extend(
                    self._validate_file_and_anchors(root, filepath, anchors, payload_content, idx)
                )

        post_checks = plan.get("postChecks", [])
        if not post_checks:
            warnings.append("plan.postChecks is empty; add verification steps.")

        rollback = plan.get("rollback")
        if not isinstance(rollback, dict) or "instruction" not in rollback:
            warnings.append("rollback instruction missing; add guidance for reverting changes.")

        valid = not issues

        return {
            "valid": valid,
            "issues": issues,
            "warnings": warnings,
        }

    def _validate_file_and_anchors(
        self,
        root: Path,
        filepath: str,
        anchors: List[Dict],
        payload: Dict,
        index: int,
    ) -> List[str]:
        warnings: List[str] = []
        if not filepath:
            warnings.append(f"Edit #{index} missing filepath; cannot evaluate anchors.")
            return warnings

        target = root / filepath
        if not target.exists():
            warnings.append(f"Edit #{index}: file '{filepath}' does not exist.")
            return warnings

        try:
            text = target.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            warnings.append(f"Edit #{index}: unable to read '{filepath}'.")
            return warnings

        if not anchors:
            warnings.append(f"Edit #{index}: no anchors specified; manual placement required.")
        else:
            for anchor in anchors:
                pattern = anchor.get("pattern")
                if pattern and pattern not in text:
                    warnings.append(
                        f"Edit #{index}: anchor pattern '{pattern}' not found in '{filepath}'."
                    )

        import_snippet = payload.get("import")
        if import_snippet and import_snippet in text:
            warnings.append(f"Edit #{index}: import snippet already present in '{filepath}'.")

        code_snippet = payload.get("code")
        if code_snippet and code_snippet in text:
            warnings.append(f"Edit #{index}: code snippet already present in '{filepath}'.")

        return warnings

