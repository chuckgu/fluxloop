"""
Additional analysis utilities for evaluation summaries.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, quantiles
from typing import TYPE_CHECKING, Any, DefaultDict, Dict, List, Optional, Tuple

from ..config import EvaluationConfig

if TYPE_CHECKING:
    from .core import TraceOutcome


def _iqr_outliers(series: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
    if len(series) < 4:
        return []
    values = [value for _, value in series]
    try:
        quartiles = quantiles(values, n=4)
    except ValueError:
        return []
    q1, q3 = quartiles[0], quartiles[2]
    iqr = q3 - q1
    if iqr == 0:
        return []
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers: List[Dict[str, Any]] = []
    for trace_id, value in series:
        if value < lower or value > upper:
            outliers.append(
                {
                    "trace_id": trace_id,
                    "value": value,
                    "thresholds": {"lower": lower, "upper": upper},
                }
            )
    return outliers


def _metric_series(results: List["TraceOutcome"], key: str) -> List[Tuple[str, float]]:
    series: List[Tuple[str, float]] = []
    for outcome in results:
        value = outcome.trace.get(key)
        if not isinstance(value, (int, float)):
            continue
        trace_id = outcome.trace.get("trace_id") or f"trace_{len(series)+1}"
        series.append((str(trace_id), float(value)))
    return series


def _compute_trend(points: List[Tuple[int, float]]) -> Dict[str, Any]:
    if len(points) < 2:
        return {"trend": "stable", "slope": 0.0, "points": points}
    points_sorted = sorted(points, key=lambda item: item[0])
    first_iteration, first_value = points_sorted[0]
    last_iteration, last_value = points_sorted[-1]
    if last_iteration == first_iteration:
        return {"trend": "stable", "slope": 0.0, "points": points_sorted}
    slope = (last_value - first_value) / (last_iteration - first_iteration)
    tolerance = 0.01
    if slope > tolerance:
        trend = "increasing"
    elif slope < -tolerance:
        trend = "decreasing"
    else:
        trend = "stable"
    return {"trend": trend, "slope": slope, "points": points_sorted}


def _analyze_trends(results: List["TraceOutcome"]) -> Dict[str, Any]:
    by_iteration_scores: DefaultDict[int, List[float]] = defaultdict(list)
    by_iteration_duration: DefaultDict[int, List[float]] = defaultdict(list)

    for outcome in results:
        iteration = outcome.trace.get("iteration")
        if not isinstance(iteration, int):
            continue
        by_iteration_scores[iteration].append(float(outcome.final_score))
        duration = outcome.trace.get("duration_ms")
        if isinstance(duration, (int, float)):
            by_iteration_duration[iteration].append(float(duration))

    average_scores = sorted(
        ((iteration, mean(values)) for iteration, values in by_iteration_scores.items()),
        key=lambda item: item[0],
    )
    average_durations = sorted(
        ((iteration, mean(values)) for iteration, values in by_iteration_duration.items()),
        key=lambda item: item[0],
    )

    trends: Dict[str, Any] = {}
    if average_scores:
        trends["final_score"] = _compute_trend(average_scores)
    if average_durations:
        trends["duration_ms"] = _compute_trend(average_durations)
    return trends


def _categorize_reason(reason: str) -> str:
    lowered = reason.lower()
    if "timeout" in lowered or "latency" in lowered:
        return "latency"
    if "tool" in lowered:
        return "tool_calls"
    if "intent" in lowered:
        return "intent_recognition"
    if "error" in lowered:
        return "runtime_error"
    return "general"


def _analyze_failures(results: List["TraceOutcome"]) -> Dict[str, Any]:
    breakdown: DefaultDict[str, int] = defaultdict(int)
    for outcome in results:
        for reasons in outcome.reasons.values():
            for reason in reasons:
                category = _categorize_reason(reason)
                breakdown[category] += 1
    return dict(sorted(breakdown.items(), key=lambda item: item[1], reverse=True))


def _load_baseline_summary(experiment_dir: Path, path_str: str) -> Optional[Dict[str, Any]]:
    baseline_path = Path(path_str)
    if not baseline_path.is_absolute():
        baseline_path = (experiment_dir / baseline_path).resolve()
    if not baseline_path.exists():
        return None
    try:
        with baseline_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    data["_path"] = str(baseline_path)
    return data


def _compare_to_baseline(current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    metrics_to_compare = [
        "pass_rate",
        "average_score",
        "total_traces",
        "passed_traces",
    ]
    comparisons: Dict[str, Any] = {}

    for key in metrics_to_compare:
        if key in current and key in baseline:
            current_value = current[key]
            baseline_value = baseline[key]
            if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                comparisons[key] = {
                    "current": current_value,
                    "baseline": baseline_value,
                    "delta": current_value - baseline_value,
                }

    current_stats = current.get("evaluator_stats", {})
    baseline_stats = baseline.get("evaluator_stats", {})
    evaluator_deltas: Dict[str, Any] = {}
    if isinstance(current_stats, dict) and isinstance(baseline_stats, dict):
        evaluator_names = set(current_stats.keys()) | set(baseline_stats.keys())
        for name in sorted(evaluator_names):
            current_entry = current_stats.get(name, {})
            baseline_entry = baseline_stats.get(name, {})
            current_avg = current_entry.get("average")
            baseline_avg = baseline_entry.get("average")
            if isinstance(current_avg, (int, float)) and isinstance(baseline_avg, (int, float)):
                evaluator_deltas[name] = {
                    "current": current_avg,
                    "baseline": baseline_avg,
                    "delta": current_avg - baseline_avg,
                }
    if evaluator_deltas:
        comparisons["evaluator_averages"] = evaluator_deltas

    if "_path" in baseline:
        comparisons["baseline_path"] = baseline["_path"]

    return comparisons


def _format_percent(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.1f}%"


def _generate_recommendations(
    summary: Dict[str, Any],
    analysis: Dict[str, Any],
) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    pass_rate = summary.get("pass_rate")
    threshold = summary.get("threshold")
    if isinstance(pass_rate, (int, float)) and isinstance(threshold, (int, float)):
        if pass_rate < threshold:
            top_reason = None
            top_reasons = summary.get("top_reasons") or []
            if top_reasons:
                top_reason = top_reasons[0][0]
            summary_text = (
                f"Pass rate is {_format_percent(pass_rate)} (goal {_format_percent(threshold)})."
            )
            if top_reason:
                summary_text += f" Most common failure reason: {top_reason}."
            items.append(
                {
                    "title": "Boost overall pass rate",
                    "priority": "high",
                    "summary": summary_text,
                    "metrics": {
                        "pass_rate": pass_rate,
                        "threshold": threshold,
                    },
                }
            )

    persona_breakdown = summary.get("persona_breakdown") or {}
    if isinstance(persona_breakdown, dict) and isinstance(threshold, (int, float)):
        for persona, stats in persona_breakdown.items():
            persona_pass_rate = stats.get("pass_rate")
            if isinstance(persona_pass_rate, (int, float)) and persona_pass_rate < threshold:
                items.append(
                    {
                        "title": f"Target persona '{persona}'",
                        "priority": "medium",
                        "summary": (
                            f"{persona} pass rate is {_format_percent(persona_pass_rate)} "
                            f"(goal {_format_percent(threshold)}). Prioritize playbooks or prompts for this persona."
                        ),
                        "metrics": {
                            "persona": persona,
                            "pass_rate": persona_pass_rate,
                            "threshold": threshold,
                        },
                    }
                )

    comparison = analysis.get("comparison")
    if isinstance(comparison, dict):
        evaluator_deltas = comparison.get("evaluator_averages") or {}
        if isinstance(evaluator_deltas, dict):
            for evaluator_name, payload in evaluator_deltas.items():
                delta = payload.get("delta")
                if isinstance(delta, (int, float)) and delta < -0.05:
                    items.append(
                        {
                            "title": f"Recover regression in {evaluator_name}",
                            "priority": "high",
                            "summary": (
                                f"{evaluator_name} average score dropped by {delta:.3f} "
                                "vs. baseline. Investigate prompt or flow changes."
                            ),
                            "metrics": {
                                "evaluator": evaluator_name,
                                "delta": delta,
                                "baseline": payload.get("baseline"),
                                "current": payload.get("current"),
                            },
                        }
                    )

    failures = analysis.get("failures")
    if isinstance(failures, dict):
        categorized = failures.get("categorized") or {}
        if isinstance(categorized, dict) and categorized:
            top_failure = max(categorized.items(), key=lambda item: item[1])
            category, count = top_failure
            if count:
                items.append(
                    {
                        "title": f"Address {category.replace('_', ' ')} failures",
                        "priority": "medium",
                        "summary": (
                            f"{count} traces failed due to {category.replace('_', ' ')} issues. "
                            "Review tooling and guardrails for this category."
                        ),
                        "metrics": {
                            "category": category,
                            "count": count,
                        },
                    }
                )

    performance = analysis.get("performance")
    if isinstance(performance, dict):
        trends = performance.get("trends") or {}
        if isinstance(trends, dict):
            final_score_trend = trends.get("final_score")
            if isinstance(final_score_trend, dict) and final_score_trend.get("trend") == "decreasing":
                slope = final_score_trend.get("slope")
                items.append(
                    {
                        "title": "Investigate declining trend",
                        "priority": "medium",
                        "summary": (
                            "Average final score shows a decreasing trend. "
                            "Review recent dataset or agent updates."
                        )
                        + (f" Slope: {slope:.3f}." if isinstance(slope, (int, float)) else ""),
                        "metrics": {
                            "trend": final_score_trend.get("trend"),
                            "slope": slope,
                        },
                    }
                )

    # Deduplicate by title to avoid noisy recommendations.
    unique: Dict[str, Dict[str, Any]] = {}
    for item in items:
        unique.setdefault(item["title"], item)

    return list(unique.values())


def compute_additional_analysis(
    results: List["TraceOutcome"],
    summary: Dict[str, Any],
    config: EvaluationConfig,
    experiment_dir: Path,
    baseline_override: Optional[Path] = None,
) -> Dict[str, Any]:
    analysis: Dict[str, Any] = {}
    additional_cfg = config.additional_analysis

    if additional_cfg.persona.enabled:
        persona_data = summary.get("persona_breakdown", {})
        if additional_cfg.persona.focus_personas:
            focused = {
                persona: persona_data.get(persona)
                for persona in additional_cfg.persona.focus_personas
                if persona in persona_data
            }
            analysis["persona"] = {
                "focus_personas": additional_cfg.persona.focus_personas,
                "breakdown": focused,
            }
        else:
            analysis["persona"] = {"breakdown": persona_data}

    performance_analysis: Dict[str, Any] = {}
    performance_cfg = additional_cfg.performance

    if performance_cfg.detect_outliers:
        duration_series = _metric_series(results, "duration_ms")
        score_series = [
            (outcome.trace.get("trace_id") or f"trace_{index+1}", outcome.final_score)
            for index, outcome in enumerate(results)
        ]
        performance_analysis["outliers"] = {
            "duration_ms": _iqr_outliers(duration_series),
            "final_score": _iqr_outliers(score_series),
        }

    if performance_cfg.trend_analysis:
        performance_analysis["trends"] = _analyze_trends(results)

    if performance_analysis:
        analysis["performance"] = performance_analysis

    failures_cfg = additional_cfg.failures
    if failures_cfg.enabled:
        failure_details: Dict[str, Any] = {"top_reasons": summary.get("top_reasons", [])}
        if failures_cfg.categorize_causes:
            failure_details["categorized"] = _analyze_failures(results)
        analysis["failures"] = failure_details

    comparison_cfg = additional_cfg.comparison
    baseline_override_str = str(baseline_override) if baseline_override is not None else None
    baseline_path = baseline_override_str or comparison_cfg.baseline_path
    comparison_enabled = comparison_cfg.enabled or baseline_override is not None
    if comparison_enabled and baseline_path:
        baseline_summary = _load_baseline_summary(experiment_dir, baseline_path)
        if baseline_summary:
            analysis["comparison"] = _compare_to_baseline(summary, baseline_summary)
        else:
            analysis.setdefault("comparison", {})
            analysis["comparison"]["message"] = f"Baseline summary not found at '{baseline_path}'"
    elif comparison_enabled:
        analysis.setdefault("comparison", {})
        analysis["comparison"]["message"] = "Comparison enabled but no baseline path provided."

    recommendations = _generate_recommendations(summary, analysis)
    if recommendations:
        analysis["recommendations"] = recommendations

    return analysis


__all__ = ["compute_additional_analysis"]

