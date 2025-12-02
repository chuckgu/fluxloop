"""Integration context retrieval without prompt generation."""

from __future__ import annotations

from typing import Dict

from .run_integration_workflow import RunIntegrationWorkflowTool


class IntegrationContextTool:
    """Collects workflow artifacts required for client-side planning."""

    def __init__(self) -> None:
        self.workflow_tool = RunIntegrationWorkflowTool()

    def fetch(self, payload: Dict) -> Dict:
        prepared_payload = dict(payload)
        question = str(prepared_payload.get("question") or "").strip()
        if not question:
            prepared_payload["question"] = "Prepare FluxLoop integration context."

        workflow = self.workflow_tool.run(prepared_payload)
        if workflow.get("error"):
            return workflow

        llm_inputs = dict(workflow.get("llm_inputs") or {})
        structure_context = llm_inputs.get("structure_context") or {}
        rag_topics = llm_inputs.get("rag_topics") or []

        clean_workflow = {k: v for k, v in workflow.items() if k != "llm_inputs"}

        return {
            "workflow": clean_workflow,
                "repo_profile": workflow.get("repo_profile"),
                "integration_context": workflow.get("integration_context"),
                "structure_context": structure_context,
            "rag_topics": rag_topics,
            "warnings": workflow.get("warnings") or [],
        }


__all__ = ["IntegrationContextTool"]

