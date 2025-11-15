"""
Prompt bundle definition for response clarity review.
"""

from __future__ import annotations

from .base import PromptBundle, score_instructions


RESPONSE_CLARITY = PromptBundle(
    key="response_clarity",
    title="Response Clarity Review",
    description="Assess clarity, structure, and helpfulness of the agent's answer.",
    prompt_template="""
System role:
You review answers for clarity, actionable direction, and persona-fit presentation.

Context:
- Persona: {persona}
- User input: {input}
- Agent output: {output}
- Supporting data or attachments: {supporting_data}

Task:
Judge whether the response is easy to understand and provides actionable next steps.
Consider:
1. Clarity of language (avoids jargon, uses organized structure, highlights key decisions).
2. Completeness of steps or explanations, including concrete instructions or escalation paths.
3. Tone appropriateness for the persona, addressing confidence level and empathy needs.
4. Does the answer avoid redundant repetition while remaining specific and helpful?

Mention the sentence, bullet, or missing detail that most drives your score.

{score_instructions}
""".replace(
        "{score_instructions}", score_instructions("response clarity")
    ),
    sample_response="Score: 5/10\nReason: Structure is readable, but it repeats the same reassurance twice and omits next-step instructions.",
)


__all__ = ["RESPONSE_CLARITY"]


