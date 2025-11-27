"""
Helpers for extracting token usage information from traces and observations.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def _coerce_usage_values(data: Dict[str, Any]) -> Dict[str, float]:
    """Normalize any prompt/completion/total token fields to floats."""
    usage: Dict[str, float] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = data.get(key)
        if isinstance(value, (int, float)):
            usage[key] = float(value)
    return usage


def _usage_from_candidate(candidate: Any) -> Dict[str, float]:
    """Best-effort extraction of token usage from nested dictionaries."""
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
    """Search an observation entry (and nested payloads) for usage values."""
    candidates: List[Dict[str, Any]] = [entry]

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


def _init_totals() -> Dict[str, float]:
    return {"prompt_tokens": 0.0, "completion_tokens": 0.0, "total_tokens": 0.0}


def _accumulate_usage(totals: Dict[str, float], usage: Dict[str, float]) -> None:
    for key, value in usage.items():
        if key in totals:
            totals[key] += float(value)


def _finalize_totals(totals: Dict[str, float]) -> Dict[str, float]:
    if totals["total_tokens"] <= 0:
        totals["total_tokens"] = totals["prompt_tokens"] + totals["completion_tokens"]
    return totals


def extract_token_usage_from_trace(trace: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """
    Aggregate token usage stored anywhere inside a structured trace record.

    Returns:
        Dict with keys ``prompt``, ``completion``, ``total`` or ``None`` when unavailable.
    """

    totals = _init_totals()
    found = False

    summary = trace.get("summary")
    if isinstance(summary, dict):
        summary_usage = _usage_from_candidate(summary)
        if summary_usage:
            _accumulate_usage(totals, summary_usage)
            found = True

        raw_summary = summary.get("raw")
        if isinstance(raw_summary, dict):
            raw_usage = _usage_from_candidate(raw_summary)
            if raw_usage:
                _accumulate_usage(totals, raw_usage)
                found = True

    # Sanitized traces may not include a nested "summary" key. In that case,
    # inspect the trace dictionary itself for token usage fields.
    if "summary" not in trace:
        root_usage = _usage_from_candidate(trace)
        if root_usage:
            _accumulate_usage(totals, root_usage)
            found = True

    timeline = trace.get("timeline")
    if isinstance(timeline, list):
        for entry in timeline:
            if not isinstance(entry, dict):
                continue
            entry_usage = _entry_token_usage(entry)
            if entry_usage:
                _accumulate_usage(totals, entry_usage)
                found = True

    if not found:
        return None

    totals = _finalize_totals(totals)
    return {
        "prompt": totals["prompt_tokens"],
        "completion": totals["completion_tokens"],
        "total": totals["total_tokens"],
    }


def extract_token_usage_from_observations(
    observations: Iterable[Dict[str, Any]],
) -> Optional[Dict[str, float]]:
    """
    Aggregate token usage directly from observation records.

    Returns:
        Dict containing ``prompt_tokens``, ``completion_tokens``, ``total_tokens``,
        or ``None`` when usage data is missing.
    """

    totals = _init_totals()
    found = False

    for entry in observations:
        if not isinstance(entry, dict):
            continue
        usage = _entry_token_usage(entry)
        if usage:
            _accumulate_usage(totals, usage)
            found = True

    if not found:
        return None

    return _finalize_totals(totals)

