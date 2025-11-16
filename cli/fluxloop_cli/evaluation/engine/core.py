"""
Core evaluation execution logic.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple, Literal

import shutil
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

from ..artifacts import PerTraceRecord, load_per_trace_records
from ..config import AggregateConfig, EvaluationConfig, EvaluatorConfig
from ..llm import LLMEvaluationManager, LLMResult
from ..rules import RuleContext, RuleResult, evaluate_rule
from .analysis import compute_additional_analysis
from .reporting import prepare_report_plan, write_reports
from .success import evaluate_success_criteria

console = Console()


@dataclass
class EvaluationOptions:
    """Runtime options controlling evaluation behaviour."""

    output_dir: Path
    overwrite: bool = False
    llm_api_key: Optional[str] = None
    sample_rate: Optional[float] = None
    max_llm_calls: Optional[int] = None
    verbose: bool = False
    report_format: Optional[Literal["md", "html", "both"]] = None
    report_template: Optional[Path] = None
    baseline_path: Optional[Path] = None
    per_trace_path: Optional[Path] = None


@dataclass
class EvaluatorOutcome:
    name: str
    score: float
    weight: float
    reasons: List[str] = field(default_factory=list)
    rule_results: List[RuleResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceOutcome:
    trace: Dict[str, Any]
    scores: Dict[str, float]
    reasons: Dict[str, List[str]]
    evaluator_outcomes: List[EvaluatorOutcome]
    final_score: float
    passed: bool


def _prepare_output_directory(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise FileExistsError(
                f"Output directory already exists: {path}. Use --overwrite to replace."
            )
        shutil.rmtree(path)
    else:
        path.mkdir(parents=True, exist_ok=True)
        return
    path.mkdir(parents=True, exist_ok=True)


def _evaluate_rule_based(trace: Dict[str, Any], evaluator: EvaluatorConfig) -> EvaluatorOutcome:
    context = RuleContext(trace=trace)
    rule_results: List[RuleResult] = []
    reasons: List[str] = []

    for definition in evaluator.rules:
        try:
            result = evaluate_rule(context, definition)
        except Exception as exc:  # noqa: BLE001
            result = RuleResult(rule=definition, score=0.0, reason=str(exc))
        rule_results.append(result)
        if result.reason:
            reasons.append(result.reason)

    if rule_results:
        avg_score = max(0.0, min(1.0, mean(result.score for result in rule_results)))
    else:
        avg_score = 0.0
        reasons.append("No rules configured")

    metadata = {"type": "rule_based", **(evaluator.metadata or {})}

    return EvaluatorOutcome(
        name=evaluator.name,
        score=avg_score,
        weight=evaluator.weight,
        reasons=reasons,
        rule_results=rule_results,
        metadata=metadata,
    )


def _aggregate_scores(
    outcomes: List[EvaluatorOutcome],
    aggregate: AggregateConfig,
) -> Tuple[float, Dict[str, float]]:
    scores = {outcome.name: outcome.score for outcome in outcomes}
    enabled_scores = [outcome.score for outcome in outcomes if outcome.weight > 0]
    enabled_weights = [outcome.weight for outcome in outcomes if outcome.weight > 0]

    if not enabled_scores:
        return 0.0, scores

    if aggregate.method == "average":
        final_score = sum(enabled_scores) / len(enabled_scores)
    else:
        weight_sum = sum(enabled_weights)
        if weight_sum == 0:
            final_score = sum(enabled_scores) / len(enabled_scores)
        else:
            final_score = sum(outcome.score * outcome.weight for outcome in outcomes) / weight_sum

    final_score = max(0.0, min(1.0, final_score))
    return final_score, scores


def _extract_reasons(outcomes: List[EvaluatorOutcome]) -> Dict[str, List[str]]:
    reason_map: Dict[str, List[str]] = {}
    for outcome in outcomes:
        if outcome.reasons:
            reason_map[outcome.name] = outcome.reasons
    return reason_map


def _evaluate_trace(
    trace: Dict[str, Any],
    config: EvaluationConfig,
    llm_manager: Optional[LLMEvaluationManager],
) -> TraceOutcome:
    evaluator_outcomes: List[EvaluatorOutcome] = []

    for evaluator in config.evaluators:
        if not evaluator.enabled:
            continue
        if evaluator.type == "rule_based":
            outcome = _evaluate_rule_based(trace, evaluator)
        elif evaluator.type == "llm_judge":
            if llm_manager is None:
                outcome = EvaluatorOutcome(
                    name=evaluator.name,
                    score=0.0,
                    weight=evaluator.weight,
                    reasons=["LLM manager unavailable"],
                    metadata={"type": "llm", **(evaluator.metadata or {})},
                )
            else:
                llm_result: LLMResult = llm_manager.evaluate(trace, evaluator)
                metadata = {"type": "llm", **llm_result.metadata, **(evaluator.metadata or {})}
                outcome = EvaluatorOutcome(
                    name=evaluator.name,
                    score=llm_result.score,
                    weight=evaluator.weight,
                    reasons=llm_result.reasons,
                    metadata=metadata,
                )
        else:
            raise ValueError(f"Unsupported evaluator type: {evaluator.type}")

        evaluator_outcomes.append(outcome)

    final_score, scores = _aggregate_scores(evaluator_outcomes, config.aggregate)
    passed = final_score >= config.aggregate.threshold
    reasons = _extract_reasons(evaluator_outcomes)

    return TraceOutcome(
        trace=trace,
        scores=scores,
        reasons=reasons,
        evaluator_outcomes=evaluator_outcomes,
        final_score=final_score,
        passed=passed,
    )


def _write_per_trace(results: List[TraceOutcome], path: Path) -> None:
    with (path / "per_trace.jsonl").open("w", encoding="utf-8") as handle:
        for outcome in results:
            reasons_serializable = {
                name: value[0] if len(value) == 1 else value for name, value in outcome.reasons.items()
            }
            payload = {
                "trace_id": outcome.trace.get("trace_id"),
                "iteration": outcome.trace.get("iteration"),
                "persona": outcome.trace.get("persona"),
                "success": outcome.trace.get("success"),
                "duration_ms": outcome.trace.get("duration_ms"),
                "scores": outcome.scores,
                "final_score": outcome.final_score,
                "pass": outcome.passed,
                "reasons": reasons_serializable,
                "meta": {
                    key: outcome.trace.get(key)
                    for key in ("input", "output")
                    if outcome.trace.get(key) is not None
                },
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _compute_evaluator_stats(results: List[TraceOutcome]) -> Dict[str, Dict[str, Any]]:
    stats: Dict[str, Dict[str, Any]] = {}
    score_buckets: Dict[str, List[float]] = defaultdict(list)
    for outcome in results:
        for name, score in outcome.scores.items():
            score_buckets[name].append(score)

    for name, values in score_buckets.items():
        stats[name] = {
            "average": float(mean(values)) if values else 0.0,
            "min": float(min(values)) if values else 0.0,
            "max": float(max(values)) if values else 0.0,
            "count": len(values),
        }
    return stats


def _compute_persona_breakdown(
    results: List[TraceOutcome],
    aggregate: AggregateConfig,
) -> Dict[str, Any]:
    if not aggregate.by_persona:
        return {}

    groups: Dict[str, List[TraceOutcome]] = defaultdict(list)
    for outcome in results:
        persona = outcome.trace.get("persona") or "default"
        groups[persona].append(outcome)

    breakdown: Dict[str, Any] = {}
    for persona, items in groups.items():
        scores = [item.final_score for item in items]
        passes = [item.passed for item in items]
        breakdown[persona] = {
            "count": len(items),
            "average_score": float(mean(scores)) if scores else 0.0,
            "pass_rate": sum(1 for flag in passes if flag) / len(passes) if passes else 0.0,
        }
    return breakdown


def _summarize_reasons(results: List[TraceOutcome]) -> List[Tuple[str, int]]:
    counter: Counter[str] = Counter()
    for outcome in results:
        for reasons in outcome.reasons.values():
            for reason in reasons:
                counter[reason] += 1
    return counter.most_common(10)




def _write_summary(summary: Dict[str, Any], path: Path) -> None:
    (path / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def run_evaluation(
    experiment_dir: Path,
    config: EvaluationConfig,
    options: EvaluationOptions,
) -> Dict[str, Any]:
    """
    Execute the evaluation pipeline and return summary stats.
    """

    if not experiment_dir.is_dir():
        raise NotADirectoryError(f"Experiment directory not found: {experiment_dir}")

    per_trace_records: List[PerTraceRecord] = load_per_trace_records(
        experiment_dir,
        options.per_trace_path,
    )
    traces = [record.trace for record in per_trace_records]

    if not traces:
        raise ValueError(
            "No per-trace records available. Run `fluxloop parse` before evaluating."
        )

    _prepare_output_directory(options.output_dir, options.overwrite)

    results: List[TraceOutcome] = []
    llm_manager: Optional[LLMEvaluationManager] = None
    if any(e.enabled and e.type == "llm_judge" for e in config.evaluators):
        llm_manager = LLMEvaluationManager.create(
            options_api_key=options.llm_api_key,
            options_sample_rate=options.sample_rate,
            options_max_calls=options.max_llm_calls,
            config=config,
            output_dir=options.output_dir,
        )

    console.print("\n[bold green]🧪 Evaluating traces...[/bold green]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TextColumn("({task.completed} of {task.total})"),
        console=console,
    ) as progress:
        task_id = progress.add_task(
            "Evaluating traces",
            total=len(traces),
        )

        for trace in traces:
            outcome = _evaluate_trace(trace, config, llm_manager)
            results.append(outcome)
            progress.advance(task_id)

    _write_per_trace(results, options.output_dir)

    final_scores = [outcome.final_score for outcome in results]
    passed_flags = [outcome.passed for outcome in results]
    pass_count = sum(1 for flag in passed_flags if flag)

    summary: Dict[str, Any] = {
        "total_traces": len(results),
        "passed_traces": pass_count,
        "pass_rate": pass_count / len(results) if results else 0.0,
        "average_score": float(mean(final_scores)) if final_scores else 0.0,
        "threshold": config.aggregate.threshold,
        "aggregate_method": config.aggregate.method,
        "evaluators": [e.name for e in config.evaluators if e.enabled],
        "evaluator_stats": _compute_evaluator_stats(results),
        "persona_breakdown": _compute_persona_breakdown(results, config.aggregate),
        "top_reasons": _summarize_reasons(results),
    }

    if config.evaluation_goal.text:
        summary["evaluation_goal"] = config.evaluation_goal.text

    success_results = evaluate_success_criteria(results, config)
    if success_results:
        summary["success_criteria_results"] = success_results
        summary["overall_success"] = success_results.get("overall_success")

    analysis = compute_additional_analysis(
        results,
        summary,
        config,
        experiment_dir,
        options.baseline_path,
    )
    if analysis:
        summary["analysis"] = analysis

    report_plan = prepare_report_plan(options, config)
    summary["report"] = {
        "format": report_plan["format"],
        "style": config.report.style,
        "tone": config.report.tone,
        "template": report_plan.get("template_source"),
    }

    if llm_manager is not None:
        summary["llm_calls"] = llm_manager.calls_made
        summary["llm_sample_rate"] = llm_manager.sample_rate

    _write_summary(summary, options.output_dir)
    write_reports(summary, results, options, report_plan)

    console.print(
        f"[bold green]Evaluation complete[/bold green] · traces: {len(results)} · "
        f"output: [cyan]{options.output_dir.resolve()}[/cyan]"
    )

    return summary


