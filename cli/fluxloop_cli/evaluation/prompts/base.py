"""
Shared utilities for defining evaluator prompt bundles.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptBundle:
    """A reusable prompt template and metadata for LLM evaluators."""

    key: str
    title: str
    description: str
    prompt_template: str
    parser: str = "first_number_1_10"
    sample_response: str = ""

    def with_header(self) -> str:
        """Return prompt template with a standard guidance header."""

        header = (
            f"# {self.title}\n"
            "# Provide a JSON-friendly rating from 1-10 inclusive.\n"
            "# Respond using the format: 'Score: <number>/10\\nReason: <short explanation>'\n"
        )
        return header + self.prompt_template.strip()


def score_instructions(metric: str) -> str:
    """Standard scoring instructions appended to evaluator prompts."""

    return (
        "Score each criterion from **1 (very poor)** to **10 (excellent)**. "
        "A score of 7 or higher indicates the agent met the expectation."
        f" Focus on {metric} when judging.\n"
        "Output format:\n"
        "Score: <number>/10\n"
        "Reason: <one sentence summary>\n"
        "Only produce the score and reason lines."
    )


__all__ = ["PromptBundle", "score_instructions"]


