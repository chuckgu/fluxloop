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


@pytest.mark.asyncio
async def test_run_single_records_conversation(tmp_path: Path) -> None:
    agent_path = tmp_path / "single_agent.py"
    agent_path.write_text(
        (
            "async def run(input: str, **kwargs):\n"
            "    return {'message': input.upper()}\n"
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "outputs_single"

    config = ExperimentConfig(
        name="single-turn-test",
        iterations=1,
        base_inputs=[{"input": "stub"}],
        runner=RunnerConfig(
            module_path="single_agent",
            function_name="run",
            python_path=[str(tmp_path)],
        ),
        output_directory=str(output_dir),
    )
    config.set_source_dir(tmp_path)
    config.set_resolved_input_count(1)

    runner = ExperimentRunner(config, no_collector=True)
    agent_func = runner._load_agent()

    try:
        await runner._run_single(
            agent_func,
            variation={"input": "hello"},
            persona=None,
            iteration=0,
        )
    finally:
        reset_config()

    assert runner.results["traces"], "Expected at least one trace entry"
    trace = runner.results["traces"][0]
    conversation = trace["conversation"]

    assert len(conversation) == 2
    user_turn, assistant_turn = conversation

    assert user_turn["role"] == "user"
    assert user_turn["content"] == "hello"
    assert user_turn["source"] == "input"

    assert assistant_turn["role"] == "assistant"
    assert assistant_turn["content"] == "HELLO"
    assert assistant_turn["source"] == "agent"
    assert assistant_turn["metadata"] == {}

    state_turns = trace["conversation_state"]["turns"]
    assert state_turns[0]["content"] == "hello"
    assert state_turns[1]["content"] == assistant_turn["content"]
    assert trace["output"] == assistant_turn["content"]


@pytest.mark.asyncio
async def test_run_multi_turn_records_normalized_conversation(tmp_path: Path) -> None:
    agent_path = tmp_path / "multi_agent.py"
    agent_path.write_text(
        (
            "async def run(input: str, **kwargs):\n"
            "    return f'Reply: {input}'\n"
        ),
        encoding="utf-8",
    )

    inputs_path = tmp_path / "inputs.yaml"
    inputs_path.write_text("inputs:\n  - input: \"First\"\n", encoding="utf-8")

    output_dir = tmp_path / "outputs_multi"

    config = ExperimentConfig(
        name="multi-turn-conversation-test",
        iterations=1,
        base_inputs=[],
        inputs_file="inputs.yaml",
        runner=RunnerConfig(
            module_path="multi_agent",
            function_name="run",
            python_path=[str(tmp_path)],
        ),
        multi_turn=MultiTurnConfig(
            enabled=True,
            max_turns=3,
            auto_approve_tools=True,
            supervisor=MultiTurnSupervisorConfig(
                provider="mock",
                metadata={
                    "scripted_questions": ["Second turn question"],
                    "mock_reason": "done",
                    "mock_closing": "Appreciate the help.",
                },
            ),
        ),
        output_directory=str(output_dir),
    )
    config.set_source_dir(tmp_path)
    config.set_resolved_input_count(1)
    config.set_resolved_persona_count(1)

    runner = ExperimentRunner(config, no_collector=True)
    agent_func = runner._load_agent()

    try:
        await runner._run_multi_turn(
            agent_func,
            variation={"input": "First", "metadata": {}},
            persona=None,
            iteration=0,
            turn_progress_callback=None,
        )
    finally:
        reset_config()

    assert runner.results["traces"], "Expected a recorded trace"
    trace = runner.results["traces"][0]
    conversation = trace["conversation"]

    # Expect initial user, assistant reply, supervisor follow-up, assistant reply, closing message
    assert [entry["role"] for entry in conversation] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]
    assert conversation[0]["source"] == "input"
    assert conversation[1]["source"] == "agent"
    assert conversation[2]["source"] == "supervisor"
    assert conversation[2]["content"] == "Second turn question"
    assert conversation[3]["content"] == "Reply: Second turn question"
    assert conversation[3]["source"] == "agent"
    assert conversation[4]["metadata"].get("closing") is True
    assert conversation[4]["content"] == "Appreciate the help."

    state_turns = trace["conversation_state"]["turns"]
    assert len(state_turns) == len(conversation)
    assert state_turns[-1]["content"] == "Appreciate the help."

