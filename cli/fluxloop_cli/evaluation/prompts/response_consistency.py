"""
Prompt bundle definition for response consistency review.
"""

from __future__ import annotations

from .base import PromptBundle, score_instructions


RESPONSE_CONSISTENCY = PromptBundle(
    key="response_consistency",
    title="Response Consistency Review",
    description="Evaluate whether the agent's response stays consistent with prior replies and policy guidance.",
    prompt_template="""
System role:
You ensure agents keep answers aligned with established guidance and previous explanations.

Context:
- Persona: {persona}
- Current user input: {input}
- Agent output: {output}
- Conversation history (if any): {history}
- Project notes: {guidelines}
- Known policies or product constraints: {policy_context}

Task:
Judge the response for consistency and coherence.
Consider:
1. Are statements compatible with prior agent replies and logged commitments?
2. Does messaging stay aligned with supplied project guidelines and policy context?
3. Are there contradictions, loops, or repeated phrases that add noise or confusion?
4. Does the response stay concise while covering required policy reminders, caveats, or disclaimers?

When deducting points, cite the conflicting sentence or missing alignment in the reason string.

{score_instructions}
""".replace(
        "{score_instructions}", score_instructions("response consistency")
    ),
    sample_response="Score: 6/10\nReason: Tone stays on-brand, but it repeats the refund policy twice and contradicts an earlier eligibility statement.",
)


__all__ = ["RESPONSE_CONSISTENCY"]


