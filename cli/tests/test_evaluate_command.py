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


def test_evaluate_generates_outputs(tmp_path: Path) -> None:
    experiment_dir = tmp_path / "experiments" / "demo"
    experiment_dir.mkdir(parents=True)
    _write_trace_summary(experiment_dir / "trace_summary.jsonl")

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

