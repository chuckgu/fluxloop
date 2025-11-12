"""
Rule-based evaluators for experiment traces.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .config import RuleDefinition


@dataclass
class RuleContext:
    """Context available to rule evaluators."""

    trace: Dict[str, Any]


@dataclass
class RuleResult:
    """Outcome of a single rule evaluation."""

    rule: RuleDefinition
    score: float
    reason: Optional[str] = None


def _extract_nested(data: Dict[str, Any], path: str) -> Any:
    if not path:
        return data

    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return str(value)
    return str(value)


def _coerce_keywords(raw: Any) -> List[str]:
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, Iterable):
        return [str(item) for item in raw]
    raise ValueError("keywords must be a string or a list of strings")


def _evaluate_output_not_empty(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    target = definition.params.get("target", "output")
    value = (
        context.trace.get(target)
        if target in context.trace
        else _extract_nested(context.trace, str(target))
    )
    text = _normalize_text(value).strip()
    score = 1.0 if text else 0.0
    reason = None if score == 1.0 else "output is empty"
    return RuleResult(rule=definition, score=score, reason=reason)


def _evaluate_contains(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    target = definition.params.get("target", "output")
    value = (
        context.trace.get(target)
        if target in context.trace
        else _extract_nested(context.trace, str(target))
    )
    haystack = _normalize_text(value)
    case_sensitive = bool(definition.params.get("case_sensitive", False))
    keywords = _coerce_keywords(definition.params.get("keywords", []))

    if not keywords:
        return RuleResult(rule=definition, score=1.0)

    haystack_cmp = haystack if case_sensitive else haystack.lower()
    missing: List[str] = []
    hits = 0
    for keyword in keywords:
        keyword_cmp = keyword if case_sensitive else keyword.lower()
        if keyword_cmp in haystack_cmp:
            hits += 1
        else:
            missing.append(keyword)

    score = hits / len(keywords)
    reason = None if not missing else f"missing keywords: {', '.join(missing)}"
    return RuleResult(rule=definition, score=score, reason=reason)


def _evaluate_not_contains(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    target = definition.params.get("target", "output")
    value = (
        context.trace.get(target)
        if target in context.trace
        else _extract_nested(context.trace, str(target))
    )
    haystack = _normalize_text(value)
    case_sensitive = bool(definition.params.get("case_sensitive", False))
    keywords = _coerce_keywords(definition.params.get("keywords", []))

    if not keywords:
        return RuleResult(rule=definition, score=1.0)

    haystack_cmp = haystack if case_sensitive else haystack.lower()
    violations: List[str] = []
    for keyword in keywords:
        keyword_cmp = keyword if case_sensitive else keyword.lower()
        if keyword_cmp in haystack_cmp:
            violations.append(keyword)

    score = 0.0 if violations else 1.0
    reason = None if score == 1.0 else f"found forbidden keywords: {', '.join(violations)}"
    return RuleResult(rule=definition, score=score, reason=reason)


def _evaluate_matches_regex(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    target = definition.params.get("target", "output")
    value = (
        context.trace.get(target)
        if target in context.trace
        else _extract_nested(context.trace, str(target))
    )
    haystack = _normalize_text(value)
    pattern = definition.params.get("pattern")
    if not pattern:
        raise ValueError("matches_regex requires a 'pattern' parameter")

    flags = 0
    flag_names = definition.params.get("flags", [])
    if isinstance(flag_names, str):
        flag_names = [flag_names]

    flag_map = {
        "IGNORECASE": re.IGNORECASE,
        "MULTILINE": re.MULTILINE,
        "DOTALL": re.DOTALL,
    }
    for name in flag_names:
        if str(name).upper() in flag_map:
            flags |= flag_map[str(name).upper()]

    match = re.search(str(pattern), haystack, flags=flags)
    score = 1.0 if match else 0.0
    reason = None if match else f"pattern '{pattern}' not found"
    return RuleResult(rule=definition, score=score, reason=reason)


def _evaluate_latency_under(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    budget = definition.params.get("budget_ms")
    duration = context.trace.get("duration_ms")

    if budget is None:
        raise ValueError("latency_under requires 'budget_ms'")

    try:
        budget = float(budget)
    except (TypeError, ValueError) as exc:
        raise ValueError("latency_under budget_ms must be numeric") from exc

    if duration is None:
        return RuleResult(rule=definition, score=0.0, reason="duration_ms missing")

    try:
        duration = float(duration)
    except (TypeError, ValueError) as exc:
        raise ValueError("duration_ms must be numeric in trace summary") from exc

    if duration <= 0:
        return RuleResult(rule=definition, score=1.0)

    if duration <= budget:
        score = 1.0
        reason = None
    else:
        score = max(0.0, min(1.0, budget / duration))
        reason = f"duration {duration:.1f}ms exceeds budget {budget:.1f}ms"
    return RuleResult(rule=definition, score=score, reason=reason)


def _evaluate_similarity(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    target = definition.params.get("target", "output")
    expected_path = definition.params.get("expected_path")

    actual_value = (
        context.trace.get(target)
        if target in context.trace
        else _extract_nested(context.trace, str(target))
    )
    expected_value = (
        _extract_nested(context.trace, str(expected_path))
        if expected_path
        else None
    )

    actual_text = _normalize_text(actual_value)
    expected_text = _normalize_text(expected_value)

    if not expected_text:
        return RuleResult(rule=definition, score=0.0, reason="expected value not provided")
    if not actual_text:
        return RuleResult(rule=definition, score=0.0, reason="actual output missing")

    ratio = SequenceMatcher(None, expected_text, actual_text).ratio()
    min_score = float(definition.params.get("min_score", 0.0))
    ratio = max(0.0, min(1.0, ratio))

    reason = None if ratio >= min_score else f"similarity {ratio:.2f} below min_score {min_score:.2f}"
    return RuleResult(rule=definition, score=ratio, reason=reason)


def _evaluate_success_flag(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    success = context.trace.get("success")
    score = 1.0 if bool(success) else 0.0
    reason = None if score == 1.0 else "trace marked as failed"
    return RuleResult(rule=definition, score=score, reason=reason)


RULE_DISPATCH = {
    "output_not_empty": _evaluate_output_not_empty,
    "contains": _evaluate_contains,
    "not_contains": _evaluate_not_contains,
    "matches_regex": _evaluate_matches_regex,
    "latency_under": _evaluate_latency_under,
    "similarity": _evaluate_similarity,
    "success": _evaluate_success_flag,
}


def evaluate_rule(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    handler = RULE_DISPATCH.get(definition.check)
    if not handler:
        raise ValueError(f"Unsupported rule check: {definition.check}")
    return handler(context, definition)


def evaluate_rules(
    context: RuleContext,
    definitions: List[RuleDefinition],
) -> List[RuleResult]:
    """
    Evaluate a sequence of rules and return their results.
    """

    results: List[RuleResult] = []
    for definition in definitions:
        result = evaluate_rule(context, definition)
        results.append(result)
    return results


