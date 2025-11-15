"""
Library exports for default GPT-5 prompt bundles used by Phase 2 evaluators.
"""

from __future__ import annotations

from typing import Dict, Iterable

from .base import PromptBundle, score_instructions
from .information_completeness import INFORMATION_COMPLETENESS
from .intent_recognition import INTENT_RECOGNITION
from .response_clarity import RESPONSE_CLARITY
from .response_consistency import RESPONSE_CONSISTENCY


PROMPT_BUNDLES: Dict[str, PromptBundle] = {
    bundle.key: bundle
    for bundle in (
        INTENT_RECOGNITION,
        RESPONSE_CONSISTENCY,
        RESPONSE_CLARITY,
        INFORMATION_COMPLETENESS,
    )
}


def list_prompt_bundles() -> Iterable[PromptBundle]:
    """Return all available prompt bundles."""

    return PROMPT_BUNDLES.values()


def get_prompt_bundle(key: str) -> PromptBundle:
    """Retrieve a prompt bundle by identifier."""

    if key not in PROMPT_BUNDLES:
        available = ", ".join(sorted(PROMPT_BUNDLES))
        raise KeyError(f"Unknown prompt bundle '{key}'. Available: {available}")
    return PROMPT_BUNDLES[key]


__all__ = [
    "PromptBundle",
    "get_prompt_bundle",
    "list_prompt_bundles",
    "PROMPT_BUNDLES",
    "score_instructions",
    "INTENT_RECOGNITION",
    "RESPONSE_CONSISTENCY",
    "RESPONSE_CLARITY",
    "INFORMATION_COMPLETENESS",
]

