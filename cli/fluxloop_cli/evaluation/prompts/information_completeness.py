"""
Prompt bundle definition for information completeness review.
"""

from __future__ import annotations

from .base import PromptBundle, score_instructions


INFORMATION_COMPLETENESS = PromptBundle(
    key="information_completeness",
    title="Information Completeness Review",
    description="Determine whether the agent included all required information or follow-up details.",
    prompt_template="""
System role:
You verify that responses include all critical information the user needs to succeed.

Context:
- Persona: {persona}
- User request: {input}
- Agent output: {output}
- Required artifacts or data: {requirements}
- Knowledge-base guidance or SOPs: {knowledge_base}

Task:
Assess whether the response covers all required facts, steps, and caveats.
Consider:
1. Does the agent supply each required data point or link listed in the requirements?
2. Are disclaimers, prerequisites, risks, or service limits clearly stated?
3. Would the user need additional clarification, or is follow-up content missing?
4. Does the answer stay focused and avoid filler repetition while delivering specifics?

Highlight the missing artifact or redundant section when lowering the score.

{score_instructions}
""".replace(
        "{score_instructions}", score_instructions("information completeness")
    ),
    sample_response="Score: 4/10\nReason: Mentions the entitlement check but skips the billing URL and repeats the SLA paragraph verbatim.",
)


__all__ = ["INFORMATION_COMPLETENESS"]


