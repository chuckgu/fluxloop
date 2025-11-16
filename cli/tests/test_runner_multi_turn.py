"""Unit tests covering multi-turn execution in the experiment runner."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from fluxloop import reset_config
from fluxloop.schemas import (
    ExperimentConfig,
    MultiTurnConfig,
    MultiTurnSupervisorConfig,
    RunnerConfig,
)

from fluxloop_cli.runner import ExperimentRunner


def _write_agent(module_path: Path) -> None:
    module_path.write_text(
        (
            "async def run(input: str, **kwargs):\n"
            "    return f\"Echo: {input}\"\n"
        ),
        encoding="utf-8",
    )


@pytest.mark.asyncio
async def test_run_multi_turn_invokes_turn_progress_callback(tmp_path: Path) -> None:
    agent_path = tmp_path / "dummy_agent.py"
    _write_agent(agent_path)

    inputs_path = tmp_path / "inputs.yaml"
    inputs_path.write_text(
        "inputs:\n  - input: \"Hello\"\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "outputs"

    config = ExperimentConfig(
        name="multi-turn-test",
        iterations=1,
        base_inputs=[],
        inputs_file="inputs.yaml",
        runner=RunnerConfig(
            module_path="dummy_agent",
            function_name="run",
            python_path=[str(tmp_path)],
        ),
        multi_turn=MultiTurnConfig(
            enabled=True,
            max_turns=3,
            auto_approve_tools=True,
            supervisor=MultiTurnSupervisorConfig(
                provider="mock",
                metadata={"scripted_questions": ["Follow up question"]},
            ),
        ),
        output_directory=str(output_dir),
    )
    config.set_source_dir(tmp_path)
    config.set_resolved_input_count(1)
    config.set_resolved_persona_count(1)

    runner = ExperimentRunner(config, no_collector=True)

    agent_func = runner._load_agent()

    turn_callback = Mock()

    variation = {"input": "Hello", "metadata": {}}

    try:
        await runner._run_multi_turn(
            agent_func,
            variation,
            persona=None,
            iteration=0,
            turn_progress_callback=turn_callback,
        )
    finally:
        reset_config()

    assert turn_callback.call_count == 3

    first_turn = turn_callback.call_args_list[0]
    assert first_turn.args == (1, 3, "Hello")

    second_turn = turn_callback.call_args_list[1]
    assert second_turn.args == (2, 3, "Follow up question")

    final_call = turn_callback.call_args_list[2]
    assert final_call.args == (2, 3, None)

