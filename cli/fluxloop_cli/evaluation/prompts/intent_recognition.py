"""
Prompt bundle definition for intent recognition quality review.
"""

from __future__ import annotations

from .base import PromptBundle, score_instructions


INTENT_RECOGNITION = PromptBundle(
    key="intent_recognition",
    title="Intent Recognition Quality Review",
    description="Judge if the agent correctly inferred the user's intent and responded accordingly.",
    prompt_template="""
System role:
You are an expert QA analyst reviewing customer-support conversations with a focus on intent alignment.

Context:
- Persona: {persona}
- User input: {input}
- Agent output: {output}
- Additional metadata: {metadata}
- Conversation history (if any): {history}
- Project guidelines or playbooks: {guidelines}

Task:
Evaluate how accurately the agent identified the user's intent and aligned the response with that intent.
Consider:
1. Does the response address the true intent behind the request, including implied goals?
2. Are any key goals, constraints, policies, or required escalations ignored?
3. Does the tone and stance match persona expectations and scenario urgency?
4. Does the agent avoid repetition while providing concrete, sequenced next steps where appropriate?

Reasoning notes should point to specific sentences or omissions when deducting points.

{score_instructions}
""".replace(
        "{score_instructions}", score_instructions("intent recognition")
    ),
    sample_response="Score: 8/10\nReason: Intent is identified and tone matches, but the response skips the required escalation checklist.",
)


__all__ = ["INTENT_RECOGNITION"]


