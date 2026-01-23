"""
Test command to run pull -> run -> upload workflow.
"""

from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
import yaml
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..config_loader import load_experiment_config, load_project_config
from ..constants import DEFAULT_CONFIG_PATH, DEFAULT_ROOT_DIR_NAME
from ..project_paths import resolve_config_path
from ..runner import ExperimentRunner
from ..turns import (
    TurnRecorder,
    format_warning_for_display,
    load_criteria_items,
    load_guardrails_from_config,
    render_result_markdown,
    write_latest_result_link,
)
from . import sync


app = typer.Typer(help="Run pull -> run -> upload test workflow.")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    config_file: Path = typer.Option(
        DEFAULT_CONFIG_PATH, "--config", "-c", help="Experiment configuration file"
    ),
    project: Optional[str] = typer.Option(None, "--project", help="Project name"),
    root: Path = typer.Option(Path(DEFAULT_ROOT_DIR_NAME), "--root", help="Root dir"),
    skip_pull: Optional[bool] = typer.Option(
        None, "--skip-pull/--no-skip-pull", help="Skip sync pull step"
    ),
    skip_upload: Optional[bool] = typer.Option(
        None, "--skip-upload/--no-skip-upload", help="Skip sync upload step"
    ),
    stream_turns: Optional[bool] = typer.Option(
        None, "--stream-turns/--no-stream-turns", help="Stream turns to Web while running"
    ),
    smoke: bool = typer.Option(False, "--smoke", help="Run a smoke test"),
    full: bool = typer.Option(False, "--full", help="Run full test"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    no_collector: bool = typer.Option(False, "--no-collector", help="Disable collector"),
):
    """
    Run FluxLoop test workflow (pull -> run -> upload).
    """
    project_config, project_root = load_project_config(
        config_file, project=project, root=root
    )
    test_config = project_config.get("test", {}) if isinstance(project_config, dict) else {}

    if smoke and full:
        raise typer.BadParameter("Choose only one of --smoke or --full.")

    mode = "smoke" if smoke else ("full" if full else test_config.get("default_mode", "full"))
    do_pull = (
        not skip_pull if skip_pull is not None else bool(test_config.get("auto_pull", True))
    )
    do_upload = (
        not skip_upload
        if skip_upload is not None
        else bool(test_config.get("auto_upload", True))
    )

    if do_pull:
        if not quiet:
            console.print("[Sync] Pulling from Web...")
        sync.pull(
            project_id=None,
            bundle_version_id=None,
            config_file=config_file,
            project=project,
            root=root,
            api_url=None,
            api_key=None,
            quiet=quiet,
        )

    resolved_config = resolve_config_path(config_file, project, root)
    config = load_experiment_config(
        resolved_config,
        project=project,
        root=root,
        require_inputs_file=False,
    )

    if mode == "smoke":
        config.iterations = 1
        inputs_path = Path(config.inputs_file) if config.inputs_file else None
        if inputs_path:
            source_dir = config.get_source_dir()
            resolved_inputs = (
                (source_dir / inputs_path).resolve() if source_dir and not inputs_path.is_absolute() else inputs_path
            )
            if resolved_inputs.exists():
                payload = yaml.safe_load(resolved_inputs.read_text()) or {}
                entries = payload.get("inputs") if isinstance(payload, dict) else payload
                if isinstance(entries, list) and entries:
                    smoke_payload = (
                        {"inputs": entries[:1]} if isinstance(payload, dict) else entries[:1]
                    )
                    smoke_path = project_root / ".fluxloop" / "smoke_inputs.yaml"
                    smoke_path.parent.mkdir(parents=True, exist_ok=True)
                    smoke_path.write_text(
                        yaml.safe_dump(smoke_payload, sort_keys=False, allow_unicode=True),
                        encoding="utf-8",
                    )
                    config.inputs_file = str(smoke_path)

    guardrails = load_guardrails_from_config(project_config)
    runner = ExperimentRunner(config, no_collector=no_collector)
    recorder = TurnRecorder(runner.output_dir / "turns.jsonl", guardrails)
    criteria_items = load_criteria_items(project_root / ".fluxloop" / "criteria")
    result_path = runner.output_dir / "result.md"
    result_path.write_text("", encoding="utf-8")
    latest_path = write_latest_result_link(project_root, result_path)

    stream_enabled = stream_turns
    if stream_enabled is None:
        stream_enabled = bool(
            test_config.get("turn_streaming", False)
            or os.getenv("FLUXLOOP_TURN_STREAMING") in ("1", "true", "True")
        )
    stream_endpoint = test_config.get("turn_stream_endpoint") or os.getenv(
        "FLUXLOOP_TURN_STREAM_ENDPOINT"
    )
    stream_retries = int(test_config.get("turn_stream_retry_max", 3))
    stream_backoff = float(test_config.get("turn_stream_backoff_seconds", 1.0))
    stream_timeout = float(test_config.get("turn_stream_timeout_seconds", 10.0))
    stream_executor = ThreadPoolExecutor(max_workers=2) if stream_enabled else None
    stream_futures = []
    if stream_enabled:
        sync._load_env(project, root)

    if not quiet:
        console.print(f"[Run] Executing {mode} test...")

    def _turn_record_callback(turn_payload: dict) -> None:
        record = recorder.record_turn(turn_payload)
        if stream_enabled and stream_executor:
            stream_futures.append(
                stream_executor.submit(
                    sync.stream_turn,
                    turn=record,
                    experiment_id=runner.output_dir.name,
                    project_root=project_root,
                    api_url=None,
                    api_key=None,
                    endpoint=stream_endpoint,
                    max_retries=stream_retries,
                    backoff_seconds=stream_backoff,
                    timeout_seconds=stream_timeout,
                    quiet=quiet,
                )
            )
        if quiet:
            return
        if record.get("role") != "assistant":
            return
        run_id = record["run_id"]
        turn_index = recorder.get_assistant_turn_count(run_id)
        duration_ms = record.get("duration_ms")
        duration = f"{duration_ms / 1000:.1f}s" if duration_ms is not None else "-"
        warning_msg = format_warning_for_display(record.get("warnings", []))
        if warning_msg:
            status = f"⚠️ - {warning_msg}"
        else:
            status = "✓"
        console.print(f"  Turn {turn_index}: {status} assistant ({duration})")
        # Update result.md progressively so latest_result is always available.
        result_path.write_text(
            render_result_markdown(list(recorder.iter_turns()), recorder.get_overall_summary(), criteria_items),
            encoding="utf-8",
        )

    try:
        asyncio.run(
            runner.run_experiment(
                turn_record_callback=_turn_record_callback,
            )
        )
    except KeyboardInterrupt:
        console.print("[yellow]Test interrupted by user[/yellow]")
        raise typer.Exit(1)
    except Exception as exc:
        console.print(f"[red]Test failed:[/red] {exc}")
        raise typer.Exit(1)

    summary = recorder.get_overall_summary()
    turns = list(recorder.iter_turns())
    result_path.write_text(
        render_result_markdown(turns, summary, criteria_items), encoding="utf-8"
    )
    if stream_executor:
        for future in stream_futures:
            try:
                future.result()
            except Exception:
                continue
        stream_executor.shutdown(wait=True)

    if do_upload:
        if not quiet:
            console.print("[Upload] Uploading to Web...")
        sync.upload(
            experiment_dir=runner.output_dir,
            config_file=config_file,
            project=project,
            root=root,
            api_url=None,
            api_key=None,
            bundle_version_id=None,
            quiet=quiet,
        )

    if quiet:
        console.print(
            f"result: {summary.total_turns} turns, {summary.warning_count} warnings"
        )
        return

    console.print("═══════════════════════════════════════════")
    console.print(
        f"결과: {summary.total_turns} turns, {summary.warning_turns} warning turns"
    )
    if criteria_items:
        console.print("\n[평가 기준]")
        for item in criteria_items:
            console.print(f"- {item}")
    console.print("───────────────────────────────────────────")
    console.print(f"📁 상세 확인: cat {latest_path}")
    console.print("═══════════════════════════════════════════")
