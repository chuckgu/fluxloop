"""
Utilities for evaluating success criteria over trace outcomes.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, DefaultDict, Dict, List, Optional

from statistics import mean

from ..config import EvaluationConfig

if TYPE_CHECKING:
    from .core import TraceOutcome


def _has_active_success_criteria(config: EvaluationConfig) -> bool:
    criteria = config.success_criteria
    performance = criteria.performance
    quality = criteria.quality
    functionality = criteria.functionality

    if performance.all_traces_successful:
        return True
    if performance.avg_response_time.enabled:
        return True
    if performance.max_response_time.enabled:
        return True
    if performance.error_rate.enabled:
        return True
    if any(
        (
            quality.intent_recognition,
            quality.response_consistency,
            quality.response_clarity,
            quality.information_completeness,
        )
    ):
        return True
    tool = functionality.tool_calling
    if tool.enabled and any(
        (
            tool.all_calls_successful,
            tool.appropriate_selection,
            tool.correct_parameters,
            tool.proper_timing,
            tool.handles_failures,
        )
    ):
        return True
    return False


def _collect_tool_calling_metrics(results: List["TraceOutcome"]) -> DefaultDict[str, List[bool]]:
    metrics: DefaultDict[str, List[bool]] = defaultdict(list)
    candidate_keys = (
        "tool_calling",
        "tool_calling_metrics",
        "tool_metrics",
        "tool_usage",
    )
    for outcome in results:
        tool_payload: Any = None
        for key in candidate_keys:
            if key in outcome.trace:
                tool_payload = outcome.trace[key]
                break
        if isinstance(tool_payload, dict):
            for key, value in tool_payload.items():
                if isinstance(value, bool):
                    metrics[key].append(value)
                elif isinstance(value, (int, float)):
                    metrics[key].append(bool(value))
        elif isinstance(tool_payload, list):
            for entry in tool_payload:
                if not isinstance(entry, dict):
                    continue
                for key, value in entry.items():
                    if isinstance(value, bool):
                        metrics[key].append(value)
                    elif isinstance(value, (int, float)):
                        metrics[key].append(bool(value))
    return metrics


def evaluate_success_criteria(
    results: List["TraceOutcome"],
    config: EvaluationConfig,
) -> Dict[str, Any]:
    if not _has_active_success_criteria(config):
        return {}

    performance_results: Dict[str, Any] = {}
    quality_results: Dict[str, Any] = {}
    functionality_results: Dict[str, Any] = {}

    overall_success = True
    checks_evaluated = 0

    def record(section: Dict[str, Any], name: str, met: Optional[bool], details: Dict[str, Any]) -> None:
        nonlocal overall_success, checks_evaluated
        section[name] = {"met": met, **details}
        if met is not None:
            checks_evaluated += 1
            if not met:
                overall_success = False

    durations: List[float] = []
    for outcome in results:
        duration = outcome.trace.get("duration_ms")
        if isinstance(duration, (int, float)):
            durations.append(float(duration))

    success_flags: List[bool] = []
    for outcome in results:
        raw_success = outcome.trace.get("success")
        if raw_success is None:
            raw_success = outcome.passed
        success_flags.append(bool(raw_success))

    performance_cfg = config.success_criteria.performance
    if performance_cfg.all_traces_successful:
        met = all(success_flags) if success_flags else None
        record(
            performance_results,
            "all_traces_successful",
            met,
            {
                "expected": True,
                "total_traces": len(success_flags),
                "successful_traces": sum(1 for flag in success_flags if flag),
            },
        )

    if performance_cfg.avg_response_time.enabled:
        if durations:
            avg_duration = mean(durations)
            threshold = performance_cfg.avg_response_time.threshold_ms
            met = None
            if threshold is not None:
                met = avg_duration <= threshold
            record(
                performance_results,
                "avg_response_time",
                met,
                {
                    "average_ms": avg_duration,
                    "threshold_ms": threshold,
                    "trace_count": len(durations),
                },
            )
        else:
            record(
                performance_results,
                "avg_response_time",
                None,
                {
                    "average_ms": None,
                    "threshold_ms": performance_cfg.avg_response_time.threshold_ms,
                    "trace_count": 0,
                    "message": "No duration data available",
                },
            )

    if performance_cfg.max_response_time.enabled:
        if durations:
            max_duration = max(durations)
            threshold = performance_cfg.max_response_time.threshold_ms
            met = None
            if threshold is not None:
                met = max_duration <= threshold
            record(
                performance_results,
                "max_response_time",
                met,
                {
                    "max_ms": max_duration,
                    "threshold_ms": threshold,
                    "trace_count": len(durations),
                },
            )
        else:
            record(
                performance_results,
                "max_response_time",
                None,
                {
                    "max_ms": None,
                    "threshold_ms": performance_cfg.max_response_time.threshold_ms,
                    "trace_count": 0,
                    "message": "No duration data available",
                },
            )

    if performance_cfg.error_rate.enabled:
        if success_flags:
            failure_count = sum(1 for flag in success_flags if not flag)
            error_rate = (failure_count / len(success_flags)) * 100
            threshold = performance_cfg.error_rate.threshold_percent
            met = None
            if threshold is not None:
                met = error_rate <= threshold
            record(
                performance_results,
                "error_rate",
                met,
                {
                    "error_rate_percent": error_rate,
                    "threshold_percent": threshold,
                    "total_traces": len(success_flags),
                    "failure_count": failure_count,
                },
            )
        else:
            record(
                performance_results,
                "error_rate",
                None,
                {
                    "error_rate_percent": None,
                    "threshold_percent": performance_cfg.error_rate.threshold_percent,
                    "total_traces": 0,
                    "failure_count": 0,
                    "message": "No trace success data available",
                },
            )

    evaluator_scores: DefaultDict[str, List[float]] = defaultdict(list)
    for outcome in results:
        for name, score in outcome.scores.items():
            if isinstance(score, (int, float)):
                evaluator_scores[name].append(float(score))

    quality_cfg = config.success_criteria.quality
    quality_threshold = config.aggregate.threshold
    quality_map = {
        "intent_recognition": quality_cfg.intent_recognition,
        "response_consistency": quality_cfg.response_consistency,
        "response_clarity": quality_cfg.response_clarity,
        "information_completeness": quality_cfg.information_completeness,
    }

    for key, enabled in quality_map.items():
        if not enabled:
            continue
        scores = evaluator_scores.get(key, [])
        if not scores:
            record(
                quality_results,
                key,
                None,
                {
                    "average_score": None,
                    "threshold": quality_threshold,
                    "trace_count": 0,
                    "message": f"No evaluator scores found for '{key}'",
                },
            )
            continue
        average_score = mean(scores)
        pass_rate = sum(1 for value in scores if value >= quality_threshold) / len(scores)
        met = average_score >= quality_threshold
        record(
            quality_results,
            key,
            met,
            {
                "average_score": average_score,
                "threshold": quality_threshold,
                "pass_rate": pass_rate,
                "trace_count": len(scores),
            },
        )

    functionality_cfg = config.success_criteria.functionality.tool_calling
    if functionality_cfg.enabled:
        tool_metrics = _collect_tool_calling_metrics(results)

        def evaluate_tool_metric(metric_key: str, required: bool) -> None:
            if not required:
                return
            values = tool_metrics.get(metric_key, [])
            if not values:
                record(
                    functionality_results,
                    metric_key,
                    None,
                    {
                        "ratio": None,
                        "trace_count": 0,
                        "message": f"No tool calling data found for '{metric_key}'",
                    },
                )
                return
            ratio = sum(1 for value in values if value) / len(values)
            met = ratio == 1.0
            record(
                functionality_results,
                metric_key,
                met,
                {
                    "ratio": ratio,
                    "trace_count": len(values),
                },
            )

        evaluate_tool_metric("all_calls_successful", functionality_cfg.all_calls_successful)
        evaluate_tool_metric("appropriate_selection", functionality_cfg.appropriate_selection)
        evaluate_tool_metric("correct_parameters", functionality_cfg.correct_parameters)
        evaluate_tool_metric("proper_timing", functionality_cfg.proper_timing)
        evaluate_tool_metric("handles_failures", functionality_cfg.handles_failures)

    overall = overall_success if checks_evaluated > 0 else None

    return {
        "performance": performance_results,
        "quality": quality_results,
        "functionality": functionality_results,
        "overall_success": overall,
    }


__all__ = ["evaluate_success_criteria"]

