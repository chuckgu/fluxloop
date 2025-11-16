import json
import textwrap
from pathlib import Path

from typer.testing import CliRunner

from fluxloop_cli import main as cli_main

runner = CliRunner()


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
        },
        {
            "trace_id": "trace-2",
            "iteration": 1,
            "persona": "helper",
            "input": "Need assistance",
            "output": "I cannot assist right now.",
            "duration_ms": 1500,
            "success": False,
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
          - check: latency_under
            budget_ms: 1200
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
          - name: llm_quality
            type: llm_judge
            enabled: true
            weight: 0.0
            model: gpt-4o-mini
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
        },
        {
            "trace_id": "p2-2",
            "iteration": 1,
            "persona": "novice_user",
            "input": "My tool invocation failed.",
            "output": "Retrying the tool call now.",
            "duration_ms": 1800,
            "success": True,
        },
        {
            "trace_id": "p2-3",
            "iteration": 2,
            "persona": "expert_user",
            "input": "Can you summarize the results?",
            "output": "",
            "duration_ms": 650,
            "success": False,
        },
        {
            "trace_id": "p2-4",
            "iteration": 3,
            "persona": "novice_user",
            "input": "Create an incident report.",
            "output": "Incident report created.",
            "duration_ms": 2100,
            "success": True,
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
      - name: latency_checker
        type: rule_based
        enabled: true
        weight: 1.0
        rules:
          - check: latency_under
            budget_ms: 1500
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
            "latency_checker": {"average": 0.75, "min": 0.0, "max": 1.0, "count": 4},
            "intent_recognition": {"average": 1.0, "min": 1.0, "max": 1.0, "count": 4},
        },
    }
    path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")


def test_evaluate_generates_outputs(tmp_path: Path) -> None:
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

    output_dir = experiment_dir / "evaluation"
    summary_path = output_dir / "summary.json"
    per_trace_path = output_dir / "per_trace.jsonl"
    report_path = output_dir / "report.md"

    assert summary_path.exists()
    assert per_trace_path.exists()
    assert report_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["total_traces"] == 2
    assert summary["passed_traces"] >= 1
    assert "completeness" in summary["evaluator_stats"]

    per_trace_lines = per_trace_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(per_trace_lines) == 2
    first_trace = json.loads(per_trace_lines[0])
    assert "completeness" in first_trace["scores"]
    assert "final_score" in first_trace


def test_evaluate_llm_without_api_key_is_recorded(tmp_path: Path) -> None:
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

    output_dir = experiment_dir / "evaluation"
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["llm_calls"] == 0

    per_trace_lines = (output_dir / "per_trace.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert per_trace_lines
    trace_entry = json.loads(per_trace_lines[0])
    reasons = trace_entry["reasons"]
    assert "llm_quality" in reasons
    assert "API key" in reasons["llm_quality"]


def test_evaluate_phase2_extended_outputs(tmp_path: Path) -> None:
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

    output_dir = experiment_dir / "evaluation"
    summary_path = output_dir / "summary.json"
    html_report_path = output_dir / "report.html"

    assert summary_path.exists()
    assert html_report_path.exists()
    assert not (output_dir / "report.md").exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["evaluation_goal"].startswith("Validate extended Phase 2")
    assert summary["report"]["format"] == "html"

    criteria_results = summary["success_criteria_results"]
    assert "performance" in criteria_results
    assert "avg_response_time" in criteria_results["performance"]
    assert "quality" in criteria_results
    assert "intent_recognition" in criteria_results["quality"]

    analysis = summary["analysis"]
    assert "persona" in analysis and analysis["persona"]["breakdown"]
    performance_analysis = analysis["performance"]
    assert "outliers" in performance_analysis and "trends" in performance_analysis
    comparison = analysis["comparison"]
    assert "baseline_path" in comparison and comparison["baseline_path"].endswith("baseline_summary.json")


def test_evaluate_loads_env_for_llm(tmp_path: Path, monkeypatch) -> None:
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

    captured: dict[str, object] = {}

    def fake_run_evaluation(exp_dir, config, options):
        captured["llm_api_key"] = options.llm_api_key
        captured["sample_rate"] = options.sample_rate
        return {}

    monkeypatch.delenv("FLUXLOOP_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "fluxloop_cli.commands.evaluate.run_evaluation", fake_run_evaluation
    )

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
    assert captured["llm_api_key"] == "sk-test-key"
