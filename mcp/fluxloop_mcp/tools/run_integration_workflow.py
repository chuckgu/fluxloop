"""End-to-end integration workflow."""

from __future__ import annotations

from typing import Dict

from .analyze_repository import AnalyzeRepositoryTool
from .detect_frameworks import DetectFrameworksTool
from .generate_integration_steps import GenerateIntegrationStepsTool
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

    def run(self, payload: Dict) -> Dict:
        root = payload.get("root", ".")

        # Step 1: Analyze repository
        profile = self.analyze_tool.analyze({"root": root})
        if profile.get("error"):
            return {"error": profile["error"]}

        # Step 2: Detect frameworks
        detection_result = self.detect_tool.detect({"repository_profile": profile})
        frameworks = detection_result.get("frameworks", [])
        if not frameworks:
            return {
                "profile": profile,
                "detection": detection_result,
                "warnings": ["No supported frameworks detected."],
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

        return {
            "profile": profile,
            "detection": detection_result,
            "integration_steps": steps_result,
            "edit_plan": plan_result,
            "validation": validation_result,
        }

