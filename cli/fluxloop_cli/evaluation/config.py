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
    model_parameters: Dict[str, Any] = field(default_factory=dict)
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
class EvaluationGoalConfig:
    """Describes the overall goal for the evaluation run."""

    text: str = ""


@dataclass
class ResponseTimeCriterion:
    enabled: bool = False
    threshold_ms: Optional[int] = None


@dataclass
class ErrorRateCriterion:
    enabled: bool = False
    threshold_percent: Optional[float] = None


@dataclass
class SuccessPerformanceConfig:
    all_traces_successful: Optional[bool] = None
    avg_response_time: ResponseTimeCriterion = field(default_factory=ResponseTimeCriterion)
    max_response_time: ResponseTimeCriterion = field(default_factory=ResponseTimeCriterion)
    error_rate: ErrorRateCriterion = field(default_factory=ErrorRateCriterion)


@dataclass
class SuccessQualityConfig:
    intent_recognition: bool = False
    response_consistency: bool = False
    response_clarity: bool = False
    information_completeness: bool = False


@dataclass
class ToolCallingCriteria:
    enabled: bool = False
    all_calls_successful: bool = False
    appropriate_selection: bool = False
    correct_parameters: bool = False
    proper_timing: bool = False
    handles_failures: bool = False


@dataclass
class SuccessFunctionalityConfig:
    tool_calling: ToolCallingCriteria = field(default_factory=ToolCallingCriteria)


@dataclass
class SuccessCriteriaConfig:
    performance: SuccessPerformanceConfig = field(default_factory=SuccessPerformanceConfig)
    quality: SuccessQualityConfig = field(default_factory=SuccessQualityConfig)
    functionality: SuccessFunctionalityConfig = field(default_factory=SuccessFunctionalityConfig)


@dataclass
class PersonaAnalysisConfig:
    enabled: bool = False
    focus_personas: List[str] = field(default_factory=list)


@dataclass
class PerformanceAnalysisConfig:
    detect_outliers: bool = False
    trend_analysis: bool = False


@dataclass
class FailuresAnalysisConfig:
    enabled: bool = False
    categorize_causes: bool = False


@dataclass
class ComparisonAnalysisConfig:
    enabled: bool = False
    baseline_path: Optional[str] = None


@dataclass
class AdditionalAnalysisConfig:
    persona: PersonaAnalysisConfig = field(default_factory=PersonaAnalysisConfig)
    performance: PerformanceAnalysisConfig = field(default_factory=PerformanceAnalysisConfig)
    failures: FailuresAnalysisConfig = field(default_factory=FailuresAnalysisConfig)
    comparison: ComparisonAnalysisConfig = field(default_factory=ComparisonAnalysisConfig)


ReportStyle = Literal["quick", "standard", "detailed"]
ReportTone = Literal["technical", "executive", "balanced"]
ReportOutput = Literal["md", "html", "both"]


@dataclass
class ReportSectionsConfig:
    executive_summary: bool = False
    key_metrics: bool = True
    detailed_results: bool = True
    statistical_analysis: bool = False
    failure_cases: bool = True
    success_examples: bool = False
    recommendations: bool = False
    action_items: bool = False


@dataclass
class ReportVisualizationsConfig:
    charts_and_graphs: bool = False
    tables: bool = True
    interactive: bool = False


@dataclass
class ReportConfig:
    style: ReportStyle = "standard"
    sections: ReportSectionsConfig = field(default_factory=ReportSectionsConfig)
    visualizations: ReportVisualizationsConfig = field(default_factory=ReportVisualizationsConfig)
    tone: ReportTone = "balanced"
    template_path: Optional[str] = None
    output: ReportOutput = "both"


@dataclass
class StatisticalTestsConfig:
    enabled: bool = False
    significance_level: float = 0.05
    confidence_interval: float = 0.95


OutlierHandlingStrategy = Literal["remove", "analyze_separately", "include"]


@dataclass
class OutlierHandlingConfig:
    detection: bool = False
    handling: OutlierHandlingStrategy = "include"


AlertOperator = Literal[">", "<", ">=", "<="]


@dataclass
class AlertCondition:
    metric: str
    threshold: float
    operator: AlertOperator = ">="


@dataclass
class AlertsConfig:
    enabled: bool = False
    conditions: List[AlertCondition] = field(default_factory=list)


@dataclass
class AdvancedConfig:
    statistical_tests: StatisticalTestsConfig = field(default_factory=StatisticalTestsConfig)
    outliers: OutlierHandlingConfig = field(default_factory=OutlierHandlingConfig)
    alerts: AlertsConfig = field(default_factory=AlertsConfig)


@dataclass
class EvaluationConfig:
    """Top-level evaluation configuration."""

    evaluators: List[EvaluatorConfig] = field(default_factory=list)
    aggregate: AggregateConfig = field(default_factory=AggregateConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)
    evaluation_goal: EvaluationGoalConfig = field(default_factory=EvaluationGoalConfig)
    success_criteria: SuccessCriteriaConfig = field(default_factory=SuccessCriteriaConfig)
    additional_analysis: AdditionalAnalysisConfig = field(default_factory=AdditionalAnalysisConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)

    def set_source_dir(self, source_dir: Path) -> None:
        """Remember the directory where this config file was loaded from."""
        self._source_dir = source_dir

    def get_source_dir(self) -> Optional[Path]:
        """Return the directory where the config file was loaded from."""
        return getattr(self, "_source_dir", None)


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

        model_parameters_raw = entry.get("model_parameters")
        if model_parameters_raw is None:
            model_parameters: Dict[str, Any] = {}
        elif isinstance(model_parameters_raw, dict):
            model_parameters = dict(model_parameters_raw)
        else:
            raise ValueError("model_parameters must be a mapping when provided")

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
            model_parameters=model_parameters,
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
                    "model_parameters",
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


def _parse_evaluation_goal(raw: Any) -> EvaluationGoalConfig:
    if raw is None:
        return EvaluationGoalConfig()
    if not isinstance(raw, dict):
        raise ValueError("evaluation_goal must be a mapping")
    text = str(raw.get("text", "")) if raw.get("text") is not None else ""
    return EvaluationGoalConfig(text=text)


def _parse_response_time_criterion(raw: Any) -> ResponseTimeCriterion:
    if raw is None:
        return ResponseTimeCriterion()
    if not isinstance(raw, dict):
        raise ValueError("response time criteria must be a mapping")
    enabled = bool(raw.get("enabled", False))
    threshold = raw.get("threshold_ms")
    if threshold is not None:
        threshold = int(threshold)
        if threshold < 0:
            raise ValueError("threshold_ms must be non-negative")
    return ResponseTimeCriterion(enabled=enabled, threshold_ms=threshold)


def _parse_error_rate_criterion(raw: Any) -> ErrorRateCriterion:
    if raw is None:
        return ErrorRateCriterion()
    if not isinstance(raw, dict):
        raise ValueError("error_rate criteria must be a mapping")
    enabled = bool(raw.get("enabled", False))
    threshold = raw.get("threshold_percent")
    if threshold is not None:
        threshold = float(threshold)
        if threshold < 0:
            raise ValueError("threshold_percent must be non-negative")
    return ErrorRateCriterion(enabled=enabled, threshold_percent=threshold)


def _parse_success_performance(raw: Any) -> SuccessPerformanceConfig:
    if raw is None:
        return SuccessPerformanceConfig()
    if not isinstance(raw, dict):
        raise ValueError("success_criteria.performance must be a mapping")

    all_traces = raw.get("all_traces_successful")
    if all_traces is not None:
        all_traces = bool(all_traces)

    return SuccessPerformanceConfig(
        all_traces_successful=all_traces,
        avg_response_time=_parse_response_time_criterion(raw.get("avg_response_time")),
        max_response_time=_parse_response_time_criterion(raw.get("max_response_time")),
        error_rate=_parse_error_rate_criterion(raw.get("error_rate")),
    )


def _parse_success_quality(raw: Any) -> SuccessQualityConfig:
    if raw is None:
        return SuccessQualityConfig()
    if not isinstance(raw, dict):
        raise ValueError("success_criteria.quality must be a mapping")

    return SuccessQualityConfig(
        intent_recognition=bool(raw.get("intent_recognition", False)),
        response_consistency=bool(raw.get("response_consistency", False)),
        response_clarity=bool(raw.get("response_clarity", False)),
        information_completeness=bool(raw.get("information_completeness", False)),
    )


def _parse_tool_calling(raw: Any) -> ToolCallingCriteria:
    if raw is None:
        return ToolCallingCriteria()
    if not isinstance(raw, dict):
        raise ValueError("success_criteria.functionality.tool_calling must be a mapping")
    return ToolCallingCriteria(
        enabled=bool(raw.get("enabled", False)),
        all_calls_successful=bool(raw.get("all_calls_successful", False)),
        appropriate_selection=bool(raw.get("appropriate_selection", False)),
        correct_parameters=bool(raw.get("correct_parameters", False)),
        proper_timing=bool(raw.get("proper_timing", False)),
        handles_failures=bool(raw.get("handles_failures", False)),
    )


def _parse_success_functionality(raw: Any) -> SuccessFunctionalityConfig:
    if raw is None:
        return SuccessFunctionalityConfig()
    if not isinstance(raw, dict):
        raise ValueError("success_criteria.functionality must be a mapping")
    return SuccessFunctionalityConfig(tool_calling=_parse_tool_calling(raw.get("tool_calling")))


def _parse_success_criteria(raw: Any) -> SuccessCriteriaConfig:
    if raw is None:
        return SuccessCriteriaConfig()
    if not isinstance(raw, dict):
        raise ValueError("success_criteria must be a mapping")
    return SuccessCriteriaConfig(
        performance=_parse_success_performance(raw.get("performance")),
        quality=_parse_success_quality(raw.get("quality")),
        functionality=_parse_success_functionality(raw.get("functionality")),
    )


def _parse_persona_analysis(raw: Any) -> PersonaAnalysisConfig:
    if raw is None:
        return PersonaAnalysisConfig()
    if not isinstance(raw, dict):
        raise ValueError("additional_analysis.persona must be a mapping")
    personas_raw = raw.get("focus_personas") or []
    if not isinstance(personas_raw, list):
        raise ValueError("persona.focus_personas must be a list")
    focus_personas = [str(item) for item in personas_raw]
    return PersonaAnalysisConfig(
        enabled=bool(raw.get("enabled", False)),
        focus_personas=focus_personas,
    )


def _parse_performance_analysis(raw: Any) -> PerformanceAnalysisConfig:
    if raw is None:
        return PerformanceAnalysisConfig()
    if not isinstance(raw, dict):
        raise ValueError("additional_analysis.performance must be a mapping")
    return PerformanceAnalysisConfig(
        detect_outliers=bool(raw.get("detect_outliers", False)),
        trend_analysis=bool(raw.get("trend_analysis", False)),
    )


def _parse_failures_analysis(raw: Any) -> FailuresAnalysisConfig:
    if raw is None:
        return FailuresAnalysisConfig()
    if not isinstance(raw, dict):
        raise ValueError("additional_analysis.failures must be a mapping")
    return FailuresAnalysisConfig(
        enabled=bool(raw.get("enabled", False)),
        categorize_causes=bool(raw.get("categorize_causes", False)),
    )


def _parse_comparison_analysis(raw: Any) -> ComparisonAnalysisConfig:
    if raw is None:
        return ComparisonAnalysisConfig()
    if not isinstance(raw, dict):
        raise ValueError("additional_analysis.comparison must be a mapping")
    baseline = raw.get("baseline_path")
    if baseline is not None:
        baseline = str(baseline)
    return ComparisonAnalysisConfig(
        enabled=bool(raw.get("enabled", False)),
        baseline_path=baseline,
    )


def _parse_additional_analysis(raw: Any) -> AdditionalAnalysisConfig:
    if raw is None:
        return AdditionalAnalysisConfig()
    if not isinstance(raw, dict):
        raise ValueError("additional_analysis must be a mapping")
    return AdditionalAnalysisConfig(
        persona=_parse_persona_analysis(raw.get("persona")),
        performance=_parse_performance_analysis(raw.get("performance")),
        failures=_parse_failures_analysis(raw.get("failures")),
        comparison=_parse_comparison_analysis(raw.get("comparison")),
    )


def _parse_report_sections(raw: Any) -> ReportSectionsConfig:
    if raw is None:
        return ReportSectionsConfig()
    if not isinstance(raw, dict):
        raise ValueError("report.sections must be a mapping")
    return ReportSectionsConfig(
        executive_summary=bool(raw.get("executive_summary", False)),
        key_metrics=bool(raw.get("key_metrics", True)),
        detailed_results=bool(raw.get("detailed_results", True)),
        statistical_analysis=bool(raw.get("statistical_analysis", False)),
        failure_cases=bool(raw.get("failure_cases", True)),
        success_examples=bool(raw.get("success_examples", False)),
        recommendations=bool(raw.get("recommendations", False)),
        action_items=bool(raw.get("action_items", False)),
    )


def _parse_report_visualizations(raw: Any) -> ReportVisualizationsConfig:
    if raw is None:
        return ReportVisualizationsConfig()
    if not isinstance(raw, dict):
        raise ValueError("report.visualizations must be a mapping")
    return ReportVisualizationsConfig(
        charts_and_graphs=bool(raw.get("charts_and_graphs", False)),
        tables=bool(raw.get("tables", True)),
        interactive=bool(raw.get("interactive", False)),
    )


def _parse_report(raw: Any) -> ReportConfig:
    if raw is None:
        return ReportConfig()
    if not isinstance(raw, dict):
        raise ValueError("report must be a mapping")

    style = raw.get("style", "standard")
    if style not in {"quick", "standard", "detailed"}:
        raise ValueError("report.style must be one of: quick, standard, detailed")

    tone = raw.get("tone", "balanced")
    if tone not in {"technical", "executive", "balanced"}:
        raise ValueError("report.tone must be one of: technical, executive, balanced")

    template_path = raw.get("template_path")
    if template_path is not None:
        template_path = str(template_path)

    output = raw.get("output", "both")
    if output not in {"md", "html", "both"}:
        raise ValueError("report.output must be one of: md, html, both")

    return ReportConfig(
        style=style,  # type: ignore[arg-type]
        sections=_parse_report_sections(raw.get("sections")),
        visualizations=_parse_report_visualizations(raw.get("visualizations")),
        tone=tone,  # type: ignore[arg-type]
        template_path=template_path,
        output=output,  # type: ignore[arg-type]
    )


def _parse_statistical_tests(raw: Any) -> StatisticalTestsConfig:
    if raw is None:
        return StatisticalTestsConfig()
    if not isinstance(raw, dict):
        raise ValueError("advanced.statistical_tests must be a mapping")
    significance_level = float(raw.get("significance_level", 0.05))
    confidence_interval = float(raw.get("confidence_interval", 0.95))
    if not 0 < significance_level < 1:
        raise ValueError("significance_level must be between 0 and 1")
    if not 0 < confidence_interval <= 1:
        raise ValueError("confidence_interval must be between 0 and 1")
    return StatisticalTestsConfig(
        enabled=bool(raw.get("enabled", False)),
        significance_level=significance_level,
        confidence_interval=confidence_interval,
    )


def _parse_outliers(raw: Any) -> OutlierHandlingConfig:
    if raw is None:
        return OutlierHandlingConfig()
    if not isinstance(raw, dict):
        raise ValueError("advanced.outliers must be a mapping")
    handling = raw.get("handling", "include")
    if handling not in {"remove", "analyze_separately", "include"}:
        raise ValueError("advanced.outliers.handling must be remove, analyze_separately, or include")
    return OutlierHandlingConfig(
        detection=bool(raw.get("detection", False)),
        handling=handling,  # type: ignore[arg-type]
    )


def _parse_alert_condition(raw: Any) -> AlertCondition:
    if not isinstance(raw, dict):
        raise ValueError("advanced.alerts.conditions entries must be mappings")

    if "metric" not in raw or "threshold" not in raw:
        raise ValueError("alert conditions require 'metric' and 'threshold'")

    metric = str(raw["metric"])
    threshold = float(raw["threshold"])
    operator = raw.get("operator", ">=")
    if operator not in {">", "<", ">=", "<="}:
        raise ValueError("alert condition operator must be one of: >, <, >=, <=")

    return AlertCondition(metric=metric, threshold=threshold, operator=operator)  # type: ignore[arg-type]


def _parse_alerts(raw: Any) -> AlertsConfig:
    if raw is None:
        return AlertsConfig()
    if not isinstance(raw, dict):
        raise ValueError("advanced.alerts must be a mapping")

    conditions_raw = raw.get("conditions") or []
    if not isinstance(conditions_raw, list):
        raise ValueError("advanced.alerts.conditions must be a list")

    conditions = [_parse_alert_condition(entry) for entry in conditions_raw]

    return AlertsConfig(
        enabled=bool(raw.get("enabled", False)),
        conditions=conditions,
    )


def _parse_advanced(raw: Any) -> AdvancedConfig:
    if raw is None:
        return AdvancedConfig()
    if not isinstance(raw, dict):
        raise ValueError("advanced must be a mapping")
    return AdvancedConfig(
        statistical_tests=_parse_statistical_tests(raw.get("statistical_tests")),
        outliers=_parse_outliers(raw.get("outliers")),
        alerts=_parse_alerts(raw.get("alerts")),
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
    evaluation_goal = _parse_evaluation_goal(data.get("evaluation_goal"))
    success_criteria = _parse_success_criteria(data.get("success_criteria"))
    additional_analysis = _parse_additional_analysis(data.get("additional_analysis"))
    report = _parse_report(data.get("report"))
    advanced = _parse_advanced(data.get("advanced"))

    config_dir = path.parent.resolve()

    config = EvaluationConfig(
        evaluators=evaluators,
        aggregate=aggregate,
        limits=limits,
        evaluation_goal=evaluation_goal,
        success_criteria=success_criteria,
        additional_analysis=additional_analysis,
        report=report,
        advanced=advanced,
    )

    config.set_source_dir(config_dir)

    return config


