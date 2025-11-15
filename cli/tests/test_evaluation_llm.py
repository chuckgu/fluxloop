from pathlib import Path

import pytest

from fluxloop_cli.evaluation.config import EvaluatorConfig, EvaluationConfig
from fluxloop_cli.evaluation.llm import LLMEvaluationManager
from fluxloop_cli.templates import create_evaluation_config


@pytest.fixture()
def manager(tmp_path: Path) -> LLMEvaluationManager:
    cfg = EvaluationConfig()
    return LLMEvaluationManager(
        config=cfg,
        output_dir=tmp_path,
        api_key=None,
        sample_rate=1.0,
        max_calls=None,
        cache_path=None,
    )


def test_build_model_parameters_defaults(manager: LLMEvaluationManager) -> None:
    evaluator = EvaluatorConfig(name="llm", type="llm_judge", model="gpt-5-mini")
    max_tokens, params = manager._build_model_parameters(evaluator)

    assert max_tokens == 512
    assert params == {
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "medium"},
    }


def test_build_model_parameters_custom(manager: LLMEvaluationManager) -> None:
    evaluator = EvaluatorConfig(
        name="llm",
        type="llm_judge",
        model="gpt-5-mini",
        model_parameters={
            "max_output_tokens": 256,
            "reasoning": {"effort": "high"},
            "text": {"verbosity": "high"},
            "seed": 1234,
        },
    )

    max_tokens, params = manager._build_model_parameters(evaluator)

    assert max_tokens == 256
    assert params["max_output_tokens"] == 256
    assert params["reasoning"] == {"effort": "high"}
    assert params["text"] == {"verbosity": "high"}
    assert params["seed"] == 1234


def test_cache_key_includes_model_parameters(manager: LLMEvaluationManager) -> None:
    prompt = "Rate this"
    trace = {"trace_id": "t-1"}

    evaluator_one = EvaluatorConfig(
        name="llm",
        type="llm_judge",
        model="gpt-5-mini",
        model_parameters={"reasoning": {"effort": "medium"}},
    )
    evaluator_two = EvaluatorConfig(
        name="llm",
        type="llm_judge",
        model="gpt-5-mini",
        model_parameters={"reasoning": {"effort": "high"}},
    )

    key_one = manager._cache_key(evaluator_one, prompt, trace)
    key_two = manager._cache_key(evaluator_two, prompt, trace)

    assert key_one != key_two


def test_non_gpt5_does_not_set_reasoning(manager: LLMEvaluationManager) -> None:
    evaluator = EvaluatorConfig(name="llm", type="llm_judge", model="gpt-4o-mini")
    max_tokens, params = manager._build_model_parameters(evaluator)

    assert max_tokens == 512
    assert params == {}


def test_phase2_template_includes_prompt_bundles() -> None:
    config_text = create_evaluation_config()
    assert "Intent Recognition Quality Review" in config_text
    assert "Response Consistency Review" in config_text
    assert "Response Clarity Review" in config_text
    assert "Information Completeness Review" in config_text
