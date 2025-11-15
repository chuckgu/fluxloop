import json
from pathlib import Path

import pytest

from fluxloop_cli.evaluation.config import EvaluationConfig
from fluxloop_cli.evaluation.engine.analysis import compute_additional_analysis
from fluxloop_cli.evaluation.engine.core import TraceOutcome


def _make_trace(trace_id: str, persona: str, score: float, passed: bool, reason: str) -> TraceOutcome:
    return TraceOutcome(
        trace={
            "trace_id": trace_id,
            "persona": persona,
            "duration_ms": 1200,
            "success": passed,
        },
        scores={"intent_recognition": score},
        reasons={"intent_recognition": [reason]},
        evaluator_outcomes=[],
        final_score=score,
        passed=passed,
    )


@pytest.fixture()
def evaluation_config(tmp_path: Path) -> EvaluationConfig:
    cfg = EvaluationConfig()
    cfg.additional_analysis.persona.enabled = True
    cfg.additional_analysis.performance.detect_outliers = True
    cfg.additional_analysis.performance.trend_analysis = True
    cfg.additional_analysis.failures.enabled = True
    cfg.additional_analysis.failures.categorize_causes = True
    cfg.additional_analysis.comparison.enabled = True
    baseline_path = tmp_path / "baseline_summary.json"
    baseline_path.write_text(
        json.dumps(
            {
                "pass_rate": 0.72,
                "average_score": 0.75,
                "evaluator_stats": {
                    "intent_recognition": {"average": 0.74},
                },
            }
        ),
        encoding="utf-8",
    )
    cfg.additional_analysis.comparison.baseline_path = str(baseline_path)
    return cfg


def test_recommendations_surface_action_items(tmp_path: Path, evaluation_config: EvaluationConfig) -> None:
    results = [
        _make_trace("t-1", "expert", 0.55, False, "Intent missed"),
        _make_trace("t-2", "expert", 0.60, True, "Slight drift"),
        _make_trace("t-3", "novice", 0.48, False, "Tool timeout"),
    ]

    summary = {
        "total_traces": 3,
        "passed_traces": 1,
        "pass_rate": 1 / 3,
        "average_score": 0.543,
        "threshold": 0.7,
        "persona_breakdown": {
            "expert": {"count": 2, "pass_rate": 0.5, "average_score": 0.575},
            "novice": {"count": 1, "pass_rate": 0.0, "average_score": 0.48},
        },
        "top_reasons": [("intent_recognition", 2), ("tool_calls", 1)],
        "evaluator_stats": {
            "intent_recognition": {"average": 0.55, "min": 0.48, "max": 0.60, "count": 3},
        },
    }

    analysis = compute_additional_analysis(results, summary, evaluation_config, tmp_path)

    recommendations = analysis.get("recommendations")
    assert recommendations, "Expected recommendations to be generated"
    titles = {item["title"] for item in recommendations}
    assert "Boost overall pass rate" in titles
    assert any("persona" in item["summary"].lower() for item in recommendations)
