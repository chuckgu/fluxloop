"""
Utilities for loading and validating evaluation configuration files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import yaml


@dataclass
class RuleDefinition:
    """Configuration for an individual rule within a rule-based evaluator."""

    check: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluatorConfig:
    """Configuration for a single evaluator (rule-based or LLM)."""

    name: str
    type: Literal["rule_based", "llm_judge"]
    enabled: bool = True
    weight: float = 1.0
    rules: List[RuleDefinition] = field(default_factory=list)
    model: Optional[str] = None
    prompt_template: Optional[str] = None
    max_score: Optional[float] = None
    parser: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregateConfig:
    """Configuration for aggregating evaluator results."""

    method: Literal["weighted_sum", "average"] = "weighted_sum"
    threshold: float = 0.5
    by_persona: bool = False


@dataclass
class LimitsConfig:
    """Configuration for controlling evaluation runtime and cost."""

    sample_rate: float = 1.0
    max_llm_calls: Optional[int] = None
    timeout_seconds: Optional[int] = None
    cache: Optional[str] = None


@dataclass
class EvaluationConfig:
    """Top-level evaluation configuration."""

    evaluators: List[EvaluatorConfig] = field(default_factory=list)
    aggregate: AggregateConfig = field(default_factory=AggregateConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Evaluation config not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError("Evaluation config must be a mapping at the root level")
    return data


def _parse_rules(raw_rules: Any) -> List[RuleDefinition]:
    rules: List[RuleDefinition] = []
    if not raw_rules:
        return rules

    if not isinstance(raw_rules, list):
        raise ValueError("rules must be a list of rule definitions")

    for entry in raw_rules:
        if not isinstance(entry, dict):
            raise ValueError("Each rule definition must be a mapping")
        if "check" not in entry:
            raise ValueError("Rule definition missing required 'check' field")

        params = {k: v for k, v in entry.items() if k != "check"}
        rules.append(RuleDefinition(check=str(entry["check"]), params=params))

    return rules


def _parse_evaluators(raw_evaluators: Any) -> List[EvaluatorConfig]:
    if not raw_evaluators:
        return []

    if not isinstance(raw_evaluators, list):
        raise ValueError("evaluators must be a list")

    evaluators: List[EvaluatorConfig] = []
    for entry in raw_evaluators:
        if not isinstance(entry, dict):
            raise ValueError("Each evaluator must be a mapping")

        if "name" not in entry or "type" not in entry:
            raise ValueError("Each evaluator requires 'name' and 'type'")

        evaluator_type = entry["type"]
        if evaluator_type not in {"rule_based", "llm_judge"}:
            raise ValueError(f"Unsupported evaluator type: {evaluator_type}")

        config = EvaluatorConfig(
            name=str(entry["name"]),
            type=evaluator_type,  # type: ignore[arg-type]
            enabled=bool(entry.get("enabled", True)),
            weight=float(entry.get("weight", 1.0)),
            rules=_parse_rules(entry.get("rules", [])),
            model=entry.get("model"),
            prompt_template=entry.get("prompt_template"),
            max_score=entry.get("max_score"),
            parser=entry.get("parser"),
            metadata={
                k: v
                for k, v in entry.items()
                if k
                not in {
                    "name",
                    "type",
                    "enabled",
                    "weight",
                    "rules",
                    "model",
                    "prompt_template",
                    "max_score",
                    "parser",
                }
            },
        )
        evaluators.append(config)

    return evaluators


def _parse_aggregate(raw: Any) -> AggregateConfig:
    if raw is None:
        return AggregateConfig()

    if not isinstance(raw, dict):
        raise ValueError("aggregate section must be a mapping")

    method = raw.get("method", "weighted_sum")
    if method not in {"weighted_sum", "average"}:
        raise ValueError("aggregate.method must be 'weighted_sum' or 'average'")

    threshold = float(raw.get("threshold", 0.5))
    by_persona = bool(raw.get("by_persona", False))

    return AggregateConfig(method=method, threshold=threshold, by_persona=by_persona)


def _parse_limits(raw: Any) -> LimitsConfig:
    if raw is None:
        return LimitsConfig()

    if not isinstance(raw, dict):
        raise ValueError("limits section must be a mapping")

    sample_rate = float(raw.get("sample_rate", 1.0))
    sample_rate = max(0.0, min(1.0, sample_rate))

    max_llm_calls = raw.get("max_llm_calls")
    if max_llm_calls is not None:
        max_llm_calls = int(max_llm_calls)
        if max_llm_calls < 0:
            max_llm_calls = 0

    timeout_seconds = raw.get("timeout_seconds")
    if timeout_seconds is not None:
        timeout_seconds = int(timeout_seconds)
        if timeout_seconds < 0:
            timeout_seconds = None

    cache = raw.get("cache")
    if cache is not None:
        cache = str(cache)

    return LimitsConfig(
        sample_rate=sample_rate,
        max_llm_calls=max_llm_calls,
        timeout_seconds=timeout_seconds,
        cache=cache,
    )


def load_evaluation_config(path: Path) -> EvaluationConfig:
    """
    Load an evaluation configuration file.

    Args:
        path: Path to the evaluation configuration YAML file.

    Returns:
        Parsed EvaluationConfig instance.
    """

    data = _load_yaml(path)

    evaluators = _parse_evaluators(data.get("evaluators", []))
    aggregate = _parse_aggregate(data.get("aggregate"))
    limits = _parse_limits(data.get("limits"))

    return EvaluationConfig(
        evaluators=evaluators,
        aggregate=aggregate,
        limits=limits,
    )


