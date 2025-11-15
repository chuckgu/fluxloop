from fluxloop_cli.evaluation.config import EvaluationConfig
from fluxloop_cli.evaluation.engine.core import TraceOutcome, EvaluatorOutcome
from fluxloop_cli.evaluation.engine.success import evaluate_success_criteria


def _make_trace_outcome(score: float) -> TraceOutcome:
    return TraceOutcome(
        trace={"trace_id": "t-1"},
        scores={"intent_recognition": score},
        reasons={"intent_recognition": ["ok"]},
        evaluator_outcomes=[
            EvaluatorOutcome(
                name="intent_recognition",
                score=score,
                weight=1.0,
                reasons=["ok"],
            )
        ],
        final_score=score,
        passed=True,
    )


def test_quality_success_met() -> None:
    config = EvaluationConfig()
    config.aggregate.threshold = 0.7
    config.success_criteria.quality.intent_recognition = True

    outcome = _make_trace_outcome(0.8)
    result = evaluate_success_criteria([outcome], config)

    assert result["quality"]["intent_recognition"]["met"] is True
    assert result["quality"]["intent_recognition"]["average_score"] == 0.8
    assert result["quality"]["intent_recognition"]["threshold"] == 0.7


def test_quality_success_missing_scores() -> None:
    config = EvaluationConfig()
    config.aggregate.threshold = 0.7
    config.success_criteria.quality.intent_recognition = True

    empty_outcome = TraceOutcome(
        trace={"trace_id": "t-2"},
        scores={},
        reasons={},
        evaluator_outcomes=[],
        final_score=0.0,
        passed=False,
    )

    result = evaluate_success_criteria([empty_outcome], config)

    assert result["quality"]["intent_recognition"]["met"] is None
    assert result["quality"]["intent_recognition"]["trace_count"] == 0
