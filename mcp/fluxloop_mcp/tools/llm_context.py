"""Utilities for preparing LLM/RAG inputs from integration workflow data."""

from __future__ import annotations

from typing import Dict, List, Sequence


class LlmContextBuilder:
    """Derives structure summaries and RAG topics from repo_profile + workflow outputs."""

    def build(
        self,
        *,
        repo_profile: Dict,
        detection: Dict,
        integration_steps: Dict,
        edit_plan: Dict,
        validation: Dict,
        integration_context: Optional[Dict] = None,
    ) -> Dict:
        structure_context = self._build_structure_context(
            repo_profile=repo_profile,
            detection=detection,
            integration_steps=integration_steps,
            edit_plan=edit_plan,
            validation=validation,
        )
        rag_topics = self._build_rag_topics(structure_context, integration_context)
        return {
            "structure_context": structure_context,
            "rag_topics": rag_topics,
            "integration_context": integration_context or {},
        }

    def _build_structure_context(
        self,
        *,
        repo_profile: Dict,
        detection: Dict,
        integration_steps: Dict,
        edit_plan: Dict,
        validation: Dict,
    ) -> Dict:
        framework_candidates = self._trim(repo_profile.get("framework_signals") or [], 3)
        agent_components = self._trim(repo_profile.get("agent_signals") or [], 5)
        runner_configs = self._trim(repo_profile.get("runner_configs") or [], 3)

        structure = {
            "framework_candidates": framework_candidates,
            "agent_components": agent_components,
            "runner_configs": runner_configs,
            "detection_summary": self._trim(detection.get("frameworks") or [], 3),
            "integration_steps": self._trim(integration_steps.get("steps") or [], 5),
            "edit_plan_summary": edit_plan.get("summary", ""),
            "edit_plan_edits": self._trim(edit_plan.get("edits") or [], 3),
            "validation": {
                "valid": validation.get("valid"),
                "issues": self._trim(validation.get("issues") or [], 5),
                "warnings": self._trim(validation.get("warnings") or [], 5),
            },
        }
        return structure

    def _build_rag_topics(self, structure_context: Dict, integration_context: Optional[Dict]) -> List[Dict]:
        topics: List[Dict] = []

        for framework in structure_context.get("framework_candidates", [])[:3]:
            topics.append(
                {
                    "id": f"framework-{framework.get('name')}",
                    "query": f"FluxLoop integration steps for {framework.get('name')}",
                    "reasons": framework.get("rationale") or [],
                }
            )

        for runner in structure_context.get("runner_configs", []):
            runner_type = runner.get("runner_type", "unknown")
            topics.append(
                {
                    "id": f"runner-{runner_type}",
                    "query": f"{runner_type} runner configuration details",
                    "reasons": [runner.get("path", "")],
                }
            )

        if structure_context.get("validation", {}).get("warnings"):
            topics.append(
                {
                    "id": "validation-warnings",
                    "query": "FluxLoop validation troubleshooting",
                    "reasons": structure_context["validation"]["warnings"],
                }
            )

        if integration_context:
            for file_item in integration_context.get("files", [])[:3]:
                topics.append(
                    {
                        "id": f"context-{file_item.get('path')}",
                        "query": f"FluxLoop integration guidance for {file_item.get('path')}",
                        "reasons": [integration_context.get("scope", "workspace")],
                    }
                )

        if not topics:
            topics.append(
                {
                    "id": "general-integration",
                    "query": "FluxLoop integration overview",
                    "reasons": [],
                }
            )

        return topics[:8]

    @staticmethod
    def _trim(sequence: Sequence, limit: int) -> List:
        if not sequence:
            return []
        return list(sequence)[:limit]


