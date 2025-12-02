import json
import textwrap
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fluxloop_cli import main as cli_main
from fluxloop_cli.evaluation.report.pipeline import ReportArtifacts

runner = CliRunner()


@pytest.fixture
def pipeline_stub(monkeypatch):
    instances = []

    class StubPipeline:
        def __init__(self, config, output_dir, api_key):
            self.config = config
            self.output_dir = output_dir
            self.api_key = api_key
            instances.append(self)

        async def run(self, trace_records, summary_records=None):
            self.trace_records = trace_records
            self.summary_records = summary_records
            self.output_dir.mkdir(parents=True, exist_ok=True)
            html_path = self.output_dir / "report.html"
            html_path.write_text("<html>stub</html>", encoding="utf-8")
            return ReportArtifacts(html_path=html_path)

    monkeypatch.setattr("fluxloop_cli.commands.evaluate.ReportPipeline", StubPipeline)
    return instances


def _write_trace_summary(path: Path) -> None:
    traces = [
        {
            "trace_id": "trace-1",
            "iteration": 0,
            "persona": "helper",
            "input": "Hello",
            "output": "Sure, I can help you.",
            "duration_ms": 500,
            "success": True,
            "token_usage": {
                "prompt_tokens": 600,
                "completion_tokens": 200,
                "total_tokens": 800,
            },
        },
        {
            "trace_id": "trace-2",
            "iteration": 1,
            "persona": "helper",
            "input": "Need assistance",
            "output": "I cannot assist right now.",
            "duration_ms": 1500,
            "success": False,
            "token_usage": {
                "prompt_tokens": 900,
                "completion_tokens": 500,
                "total_tokens": 1400,
            },
        },
    ]
    lines = [json.dumps(item) for item in traces]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_eval_config(path: Path, include_llm: bool = False) -> None:
    config_body = """
    evaluators:
      - name: completeness
        type: rule_based
        enabled: true
        weight: 1.0
        rules:
          - check: output_not_empty
          - check: token_usage_under
            max_total_tokens: 1200
          - check: success

    aggregate:
      method: weighted_sum
      threshold: 0.5
    """

    if include_llm:
        config_body = """
        evaluators:
          - name: completeness
            type: rule_based
            enabled: true
            weight: 1.0
            rules:
              - check: output_not_empty
              - check: token_usage_under
                max_total_tokens: 1200
          - name: llm_quality
            type: llm_judge
            enabled: true
            weight: 0.0
            model: gpt-5-mini
            prompt_template: |
              Score the assistant response from 1-10.
              Input: {input}
              Output: {output}
            max_score: 10
            parser: first_number_1_10

        aggregate:
          method: weighted_sum
          threshold: 0.5
        """

    path.write_text(textwrap.dedent(config_body).strip() + "\n", encoding="utf-8")


def _write_phase2_trace_summary(path: Path) -> None:
    traces = [
        {
            "trace_id": "p2-1",
            "iteration": 0,
            "persona": "expert_user",
            "input": "How do I configure alerts?",
            "output": "Alerts configured successfully.",
            "duration_ms": 900,
            "success": True,
            "token_usage": {
                "prompt_tokens": 500,
                "completion_tokens": 200,
                "total_tokens": 700,
            },
        },
        {
            "trace_id": "p2-2",
            "iteration": 1,
            "persona": "novice_user",
            "input": "My tool invocation failed.",
            "output": "Retrying the tool call now.",
            "duration_ms": 1800,
            "success": True,
            "token_usage": {
                "prompt_tokens": 650,
                "completion_tokens": 250,
                "total_tokens": 900,
            },
        },
        {
            "trace_id": "p2-3",
            "iteration": 2,
            "persona": "expert_user",
            "input": "Can you summarize the results?",
            "output": "",
            "duration_ms": 650,
            "success": False,
            "token_usage": {
                "prompt_tokens": 450,
                "completion_tokens": 300,
                "total_tokens": 750,
            },
        },
        {
            "trace_id": "p2-4",
            "iteration": 3,
            "persona": "novice_user",
            "input": "Create an incident report.",
            "output": "Incident report created.",
            "duration_ms": 2100,
            "success": True,
            "token_usage": {
                "prompt_tokens": 800,
                "completion_tokens": 350,
                "total_tokens": 1150,
            },
        },
    ]
    lines = [json.dumps(item) for item in traces]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_phase2_eval_config(path: Path) -> None:
    config_body = """
    evaluation_goal:
      text: |
        Validate extended Phase 2 evaluation outputs for persona-aware runs.

    evaluators:
      - name: token_checker
        type: rule_based
        enabled: true
        weight: 1.0
        rules:
          - check: token_usage_under
            max_total_tokens: 1500
      - name: intent_recognition
        type: rule_based
        enabled: true
        weight: 1.0
        rules:
          - check: output_not_empty

    aggregate:
      method: weighted_sum
      threshold: 0.6
      by_persona: true

    success_criteria:
      performance:
        all_traces_successful: false
        avg_response_time:
          enabled: true
          threshold_ms: 1600
        error_rate:
          enabled: true
          threshold_percent: 60
      quality:
        intent_recognition: true
      functionality:
        tool_calling:
          enabled: false

    additional_analysis:
      persona:
        enabled: true
      performance:
        detect_outliers: true
        trend_analysis: true
      failures:
        enabled: true
        categorize_causes: true
      comparison:
        enabled: true
        baseline_path: "baseline_summary.json"

    report:
      style: detailed
      sections:
        executive_summary: true
        key_metrics: true
        detailed_results: true
        failure_cases: true
      visualizations:
        charts_and_graphs: true
        tables: true
      tone: executive
      output: html
    """
    path.write_text(textwrap.dedent(config_body).strip() + "\n", encoding="utf-8")


def _write_baseline_summary(path: Path) -> None:
    baseline = {
        "pass_rate": 0.75,
        "average_score": 0.7,
        "total_traces": 4,
        "passed_traces": 3,
        "evaluator_stats": {
            "token_checker": {"average": 0.75, "min": 0.0, "max": 1.0, "count": 4},
            "intent_recognition": {"average": 1.0, "min": 1.0, "max": 1.0, "count": 4},
        },
    }
    path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")


def test_evaluate_generates_outputs(tmp_path: Path, pipeline_stub) -> None:
    experiment_dir = tmp_path / "experiments" / "demo"
    experiment_dir.mkdir(parents=True)
    _write_trace_summary(experiment_dir / "trace_summary.jsonl")

    parse_result = runner.invoke(
        cli_main.app,
        [
            "parse",
            "experiment",
            str(experiment_dir),
        ],
    )
    assert parse_result.exit_code == 0, parse_result.output

    parsed_per_trace_path = experiment_dir / "per_trace_analysis" / "per_trace.jsonl"
    parsed_records = [
        json.loads(line)
        for line in parsed_per_trace_path.read_text(encoding="utf-8").strip().splitlines()
        if line.strip()
    ]
    assert parsed_records, "Expected parsed per-trace records"
    assert "conversation" in parsed_records[0]
    assert isinstance(parsed_records[0]["conversation"], list)

    config_path = tmp_path / "configs" / "evaluation.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _write_eval_config(config_path)

    result = runner.invoke(
        cli_main.app,
        [
            "evaluate",
            "experiment",
            str(experiment_dir),
            "--config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0, result.output

    output_dir = experiment_dir / "evaluation_report"
    html_report = output_dir / "report.html"
    assert html_report.exists()

    assert len(pipeline_stub) == 1
    stub_instance = pipeline_stub[0]
    assert len(stub_instance.trace_records) == 2
    assert len(stub_instance.summary_records) == 2


def test_evaluate_llm_without_api_key_is_recorded(tmp_path: Path, pipeline_stub) -> None:
    experiment_dir = tmp_path / "experiments" / "demo_llm"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    _write_trace_summary(experiment_dir / "trace_summary.jsonl")

    parse_result = runner.invoke(
        cli_main.app,
        [
            "parse",
            "experiment",
            str(experiment_dir),
        ],
    )
    assert parse_result.exit_code == 0, parse_result.output

    config_path = tmp_path / "configs" / "evaluation_llm.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _write_eval_config(config_path, include_llm=True)

    result = runner.invoke(
        cli_main.app,
        [
            "evaluate",
            "experiment",
            str(experiment_dir),
            "--config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0, result.output

    output_dir = experiment_dir / "evaluation_report"
    assert (output_dir / "report.html").exists()

    assert len(pipeline_stub) == 1
    assert pipeline_stub[0].api_key is None


def test_evaluate_phase2_extended_outputs(tmp_path: Path, pipeline_stub) -> None:
    experiment_dir = tmp_path / "experiments" / "phase2"
    experiment_dir.mkdir(parents=True)
    _write_phase2_trace_summary(experiment_dir / "trace_summary.jsonl")
    _write_baseline_summary(experiment_dir / "baseline_summary.json")

    parse_result = runner.invoke(
        cli_main.app,
        [
            "parse",
            "experiment",
            str(experiment_dir),
        ],
    )
    assert parse_result.exit_code == 0, parse_result.output

    config_path = tmp_path / "configs" / "evaluation_phase2.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _write_phase2_eval_config(config_path)

    result = runner.invoke(
        cli_main.app,
        [
            "evaluate",
            "experiment",
            str(experiment_dir),
            "--config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0, result.output

    output_dir = experiment_dir / "evaluation_report"
    assert (output_dir / "report.html").exists()

    assert len(pipeline_stub) == 1
    stub_instance = pipeline_stub[0]
    assert stub_instance.config["evaluation"]["evaluation_goal"]["text"].startswith(
        "Validate extended Phase 2"
    )
    assert stub_instance.config["evaluation"]["aggregate"]["by_persona"] is True
    assert stub_instance.config["input"] == {}
    assert len(stub_instance.trace_records) == 4
    assert len(stub_instance.summary_records) == 4


def test_evaluate_loads_env_for_llm(tmp_path: Path, monkeypatch, pipeline_stub) -> None:
    project_dir = tmp_path
    configs_dir = project_dir / "configs"
    configs_dir.mkdir()

    env_path = project_dir / ".env"
    env_path.write_text("FLUXLOOP_LLM_API_KEY=sk-test-key\n", encoding="utf-8")

    eval_config = configs_dir / "evaluation.yaml"
    _write_eval_config(eval_config, include_llm=True)

    experiment_dir = project_dir / "experiments" / "run_1"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    _write_trace_summary(experiment_dir / "trace_summary.jsonl")
    (experiment_dir / "per_trace_analysis").mkdir(parents=True, exist_ok=True)
    per_trace_path = experiment_dir / "per_trace_analysis" / "per_trace.jsonl"
    per_trace_path.write_text(
        json.dumps(
            {
                "trace_id": "trace-1",
                "iteration": 0,
                "persona": "helper",
                "input": "Hello",
                "output": "Hi!",
                "final_output": "Hi!",
                "duration_ms": 1000,
                "success": True,
                "summary": {
                    "trace_id": "trace-1",
                    "iteration": 0,
                    "persona": "helper",
                    "input": "Hello",
                    "output": "Hi!",
                    "duration_ms": 1000,
                    "success": True,
                },
                "timeline": [],
                "metrics": {"observation_count": 0},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.delenv("FLUXLOOP_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = runner.invoke(
        cli_main.app,
        [
            "evaluate",
            "experiment",
            str(experiment_dir),
            "--config",
            str(eval_config),
            "--output",
            "evaluation",
        ],
    )

    monkeypatch.delenv("FLUXLOOP_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert result.exit_code == 0, result.output
    assert len(pipeline_stub) == 1
    assert pipeline_stub[0].api_key == "sk-test-key"
