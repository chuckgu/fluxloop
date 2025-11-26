"""
Rule-based evaluators for experiment traces.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Optional

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


def _coerce_usage_values(data: Dict[str, Any]) -> Dict[str, float]:
    usage: Dict[str, float] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = data.get(key)
        if isinstance(value, (int, float)):
            usage[key] = float(value)
    return usage


def _usage_from_candidate(candidate: Any) -> Dict[str, float]:
    if not isinstance(candidate, dict):
        return {}
    direct = _coerce_usage_values(candidate)
    if direct:
        return direct
    token_usage = candidate.get("token_usage")
    if isinstance(token_usage, dict):
        values = _coerce_usage_values(token_usage)
        if values:
            return values
    nested = candidate.get("usage")
    if isinstance(nested, dict):
        return _coerce_usage_values(nested)
    return {}


def _entry_token_usage(entry: Dict[str, Any]) -> Dict[str, float]:
    candidates = [entry]
    output = entry.get("output")
    if isinstance(output, dict):
        candidates.append(output)
        messages = output.get("messages")
        if isinstance(messages, dict):
            candidates.append(messages)
            response_metadata = messages.get("response_metadata")
            if isinstance(response_metadata, dict):
                candidates.append(response_metadata)
    raw = entry.get("raw")
    if isinstance(raw, dict):
        candidates.append(raw)
        raw_output = raw.get("output")
        if isinstance(raw_output, dict):
            candidates.append(raw_output)
            response_metadata = raw_output.get("response_metadata")
            if isinstance(response_metadata, dict):
                candidates.append(response_metadata)
            messages = raw_output.get("messages")
            if isinstance(messages, dict):
                candidates.append(messages)
                response_metadata = messages.get("response_metadata")
                if isinstance(response_metadata, dict):
                    candidates.append(response_metadata)
        metadata = raw.get("metadata")
        if isinstance(metadata, dict):
            candidates.append(metadata)
        response_metadata = raw.get("response_metadata")
        if isinstance(response_metadata, dict):
            candidates.append(response_metadata)
    for candidate in candidates:
        usage = _usage_from_candidate(candidate)
        if usage:
            return usage
    return {}


def _collect_token_usage(trace: Dict[str, Any]) -> Optional[Dict[str, float]]:
    totals = {"prompt_tokens": 0.0, "completion_tokens": 0.0, "total_tokens": 0.0}
    found = False

    summary = trace.get("summary")
    if isinstance(summary, dict):
        summary_usage = {}
        if isinstance(summary.get("token_usage"), dict):
            summary_usage = _usage_from_candidate(summary["token_usage"])
        if not summary_usage:
            raw = summary.get("raw")
            if isinstance(raw, dict) and isinstance(raw.get("token_usage"), dict):
                summary_usage = _usage_from_candidate(raw["token_usage"])
        if summary_usage:
            found = True
            for key, value in summary_usage.items():
                totals[key] += value

    timeline = trace.get("timeline")
    if isinstance(timeline, list):
        for entry in timeline:
            if not isinstance(entry, dict):
                continue
            usage = _entry_token_usage(entry)
            if not usage:
                continue
            found = True
            for key, value in usage.items():
                totals[key] += value

    if not found:
        return None

    prompt = totals["prompt_tokens"]
    completion = totals["completion_tokens"]
    total = totals["total_tokens"]
    if total <= 0:
        total = prompt + completion
    return {
        "prompt": prompt,
        "completion": completion,
        "total": total,
    }


def _coerce_budget_value(value: Any, label: str) -> Optional[float]:
    if value is None:
        return None
    try:
        budget = float(value)
    except (TypeError, ValueError) as exc:  # noqa: BLE001
        raise ValueError(f"token_usage_under {label} must be numeric") from exc
    if budget <= 0:
        raise ValueError(f"token_usage_under {label} must be greater than 0")
    return budget


def _evaluate_token_usage_under(context: RuleContext, definition: RuleDefinition) -> RuleResult:
    usage = _collect_token_usage(context.trace)
    if usage is None:
        return RuleResult(
            rule=definition,
            score=0.0,
            reason="token usage data not available",
        )

    max_total = _coerce_budget_value(definition.params.get("max_total_tokens"), "max_total_tokens")
    max_prompt = _coerce_budget_value(
        definition.params.get("max_prompt_tokens"),
        "max_prompt_tokens",
    )
    max_completion = _coerce_budget_value(
        definition.params.get("max_completion_tokens"),
        "max_completion_tokens",
    )

    if max_total is None and max_prompt is None and max_completion is None:
        raise ValueError("token_usage_under requires at least one max_*_tokens parameter")

    score = 1.0
    reasons: List[str] = []

    def apply_budget(actual: float, budget: Optional[float], label: str) -> None:
        nonlocal score
        if budget is None:
            return
        if actual <= budget:
            return
        ratio = budget / actual if actual > 0 else 0.0
        ratio = max(0.0, min(1.0, ratio))
        score = min(score, ratio)
        reasons.append(f"{label} {actual:.0f} exceeds budget {budget:.0f}")

    apply_budget(usage["total"], max_total, "total tokens")
    apply_budget(usage["prompt"], max_prompt, "prompt tokens")
    apply_budget(usage["completion"], max_completion, "completion tokens")

    reason = "; ".join(reasons) if reasons else None
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
    "token_usage_under": _evaluate_token_usage_under,
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


