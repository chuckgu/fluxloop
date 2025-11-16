"""
Runner modules for executing experiments and agents.
"""

from __future__ import annotations

import asyncio
import contextvars
import json
import logging
import inspect
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

import fluxloop
import yaml

from fluxloop.buffer import EventBuffer
from fluxloop.schemas import ExperimentConfig, PersonaConfig, MultiTurnConfig
from rich.console import Console

from .environment import load_env_chain
from .target_loader import TargetLoader
from .arg_binder import ArgBinder
from .conversation_supervisor import ConversationSupervisor, SupervisorDecision

console = Console()
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Runner for full experiments with multiple iterations."""
    
    def __init__(self, config: ExperimentConfig, no_collector: bool = False):
        """
        Initialize the experiment runner.
        
        Args:
            config: Experiment configuration
            no_collector: If True, disable sending to collector
        """
        self.config = config
        self.no_collector = no_collector
        
        # Apply project environment (.env + inline environment variables)
        self._apply_environment()

        # Configure output directories (respect config location for relative paths)
        output_base = Path(config.output_directory)
        if not output_base.is_absolute():
            source_dir = config.get_source_dir()
            if source_dir:
                output_base = (source_dir / output_base).resolve()
            else:
                output_base = (Path.cwd() / output_base).resolve()

        output_base.mkdir(parents=True, exist_ok=True)

        offline_dir = output_base / "artifacts"
        offline_dir.mkdir(parents=True, exist_ok=True)
        # Ensure downstream load_env() calls don't re-enable collector unintentionally
        should_use_collector = (not no_collector) and bool(config.collector_url)
        if not should_use_collector:
            os.environ["FLUXLOOP_USE_COLLECTOR"] = "false"
        else:
            os.environ["FLUXLOOP_USE_COLLECTOR"] = "true"
        # Pin offline store dir in env so refresh_config respects our path
        os.environ.setdefault("FLUXLOOP_OFFLINE_DIR", str(offline_dir))
        os.environ.setdefault("FLUXLOOP_OFFLINE_ENABLED", "true")
        fluxloop.configure(
            use_collector=should_use_collector,
            collector_url=config.collector_url or None,
            api_key=config.collector_api_key,
            offline_store_enabled=True,
            offline_store_dir=str(offline_dir),
        )
        self.offline_dir = offline_dir

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = output_base / f"{config.name}_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Results storage
        self.results = {
            "total_runs": 0,
            "successful": 0,
            "failed": 0,
            "traces": [],
            "errors": [],
            "durations": [],
        }

        # Helpers for target loading and argument binding
        self._arg_binder = ArgBinder(config)
    
    def _apply_environment(self) -> None:
        """Load environment variables from .env and runner settings."""

        source_dir = self.config.get_source_dir()

        def _log_env_error(path: Path, exc: Exception) -> None:
            console.log(
                f"[yellow]Warning:[/yellow] Failed to load environment from {path}: {exc}"
            )

        load_env_chain(
            source_dir,
            refresh_config=True,
            on_error=_log_env_error,
        )

        env_vars = getattr(self.config.runner, "environment_vars", {}) or {}
        for key, value in env_vars.items():
            os.environ[key] = str(value)

    def _load_agent(self) -> Callable:
        """Load the agent function from module path."""
        loader = TargetLoader(self.config.runner, source_dir=self.config.get_source_dir())
        try:
            return loader.load()
        except ValueError as exc:
            raise RuntimeError(str(exc)) from exc

    async def run_experiment(
        self,
        progress_callback: Optional[Callable] = None,
        turn_progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Run the complete experiment.
        
        Args:
            progress_callback: Optional callback for progress updates
            turn_progress_callback: Optional callback for multi-turn progress updates
            
        Returns:
            Experiment results summary
        """
        start_time = time.time()
        
        # Load agent module
        agent_func = self._load_agent()
        
        inputs = await self._load_inputs()

        persona_map = {persona.name: persona for persona in (self.config.personas or [])}
        use_entry_persona = self.config.has_external_inputs()

        delay = getattr(self.config, "run_delay_seconds", 0) or 0

        # Run iterations
        for iteration in range(self.config.iterations):
            if use_entry_persona:
                for entry in inputs:
                    persona = self._resolve_entry_persona(entry, persona_map)
                    await self._run_single(
                        agent_func,
                        entry,
                        persona,
                        iteration,
                        turn_progress_callback=turn_progress_callback,
                    )

                    if progress_callback:
                        progress_callback()

                    if delay > 0:
                        await asyncio.sleep(delay)
            else:
                personas = self.config.personas or [None]
                for persona in personas:
                    for entry in inputs:
                        await self._run_single(
                            agent_func,
                            entry,
                            persona,
                            iteration,
                            turn_progress_callback=turn_progress_callback,
                        )

                        if progress_callback:
                            progress_callback()

                        if delay > 0:
                            await asyncio.sleep(delay)

        if use_entry_persona:
            self.config.set_resolved_persona_count(1)
        else:
            persona_multiplier = len(self.config.personas) if self.config.personas else 1
            self.config.set_resolved_persona_count(persona_multiplier)

        # Calculate summary statistics
        end_time = time.time()
        self.results["duration_seconds"] = end_time - start_time
        self.results["success_rate"] = (
            self.results["successful"] / self.results["total_runs"]
            if self.results["total_runs"] > 0
            else 0
        )
        
        if self.results["durations"]:
            self.results["avg_duration_ms"] = sum(self.results["durations"]) / len(self.results["durations"])
        else:
            self.results["avg_duration_ms"] = 0
        
        # Save results
        self._save_results()
        
        return {
            "total_runs": self.results["total_runs"],
            "successful": self.results["successful"],
            "failed": self.results["failed"],
            "success_rate": self.results["success_rate"],
            "avg_duration_ms": self.results["avg_duration_ms"],
            "output_dir": str(self.output_dir),
        }
    
    async def _load_inputs(self) -> List[Dict[str, Any]]:
        """Load input entries from configuration or external files."""
        if not self.config.inputs_file:
            raise ValueError(
                "inputs_file is not configured. Generate inputs with "
                "`fluxloop generate inputs --project <name>` and set the generated file "
                "in setting.yaml before running experiments."
            )

        inputs = self._load_external_inputs()
        self.config.set_resolved_input_count(len(inputs))
        if self.config.has_external_inputs():
            self.config.set_resolved_persona_count(1)
        else:
            persona_multiplier = len(self.config.personas) if self.config.personas else 1
            self.config.set_resolved_persona_count(persona_multiplier)
        return inputs

    def _load_external_inputs(self) -> List[Dict[str, Any]]:
        """Load variations from an external file."""
        source_dir = self.config.get_source_dir()
        raw_path = Path(self.config.inputs_file)  # type: ignore[arg-type]
        inputs_path = (source_dir / raw_path if source_dir and not raw_path.is_absolute() else raw_path).resolve()
        if not inputs_path.exists():
            raise FileNotFoundError(f"Inputs file not found: {inputs_path}")

        with open(inputs_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError(f"Inputs file is empty: {inputs_path}")

        # Support either top-level list or dict with "inputs"
        entries: List[Dict[str, Any]]
        variations: List[Dict[str, Any]] = []
        if isinstance(data, dict) and "inputs" in data:
            entries = data["inputs"]
        elif isinstance(data, list):
            entries = data
        else:
            raise ValueError(
                "Inputs file must be a list of inputs or a mapping containing an 'inputs' list"
            )

        for index, item in enumerate(entries):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Input entry at index {index} must be a mapping, got {type(item).__name__}"
                )

            input_value = item.get("input")
            if not input_value:
                raise ValueError(f"Input entry at index {index} is missing required 'input' field")

            variations.append({
                "input": input_value,
                "metadata": item.get("metadata", item),
                "source": "external_file",
                "source_index": index,
            })

        if not variations:
            raise ValueError(f"Inputs file {inputs_path} did not contain any inputs")

        return variations
    
    async def _run_single(
        self,
        agent_func: Callable,
        variation: Dict[str, Any],
        persona: Optional[PersonaConfig],
        iteration: int,
        *,
        turn_progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
    ) -> None:
        """Run a single execution."""

        if self._should_use_multi_turn():
            await self._run_multi_turn(
                agent_func,
                variation,
                persona,
                iteration,
                turn_progress_callback=turn_progress_callback,
            )
            return

        self.results["total_runs"] += 1
        
        # Create trace name
        trace_name = f"{self.config.name}_iter{iteration}"
        if persona:
            trace_name += f"_persona_{persona.name}"
        
        # Prepare input
        input_text = variation["input"]
        if persona and self.config.input_template:
            # Apply persona to input template
            input_text = self.config.input_template.format(
                input=input_text,
                persona=persona.to_prompt(),
            )
        
        # Run with instrumentation
        start_time = time.time()
        
        try:
            callback_messages: Dict[str, Any] = {}
            trace_id: Optional[str] = None
            result: Any

            with fluxloop.instrument(trace_name) as ctx:
                if hasattr(ctx, "trace") and getattr(ctx, "trace") is not None:
                    trace_id = str(ctx.trace.id)
                    ctx.add_metadata("trace_id", trace_id)
                
                # Add metadata
                ctx.add_metadata("iteration", iteration)
                ctx.add_metadata("variation", variation)
                if persona:
                    ctx.add_metadata("persona", persona.name)
                
                # Run agent
                result = await self._call_agent(
                    agent_func,
                    input_text,
                    iteration=iteration,
                    callback_store=callback_messages,
                    conversation_state=None,
                    persona=persona,
                    auto_approve=None,
                )

                # Allow background callbacks to flush
                await self._wait_for_callbacks(callback_messages)

                send_messages = callback_messages.get("send", [])
                error_messages = callback_messages.get("error", [])

                if send_messages or error_messages:
                    ctx.add_metadata(
                        "callback_messages",
                        {
                            "send": send_messages,
                            "error": error_messages,
                        },
                    )

            # Force flush buffered events so observations are persisted
            EventBuffer.get_instance().flush()

            observations: List[Dict[str, Any]] = []
            if trace_id:
                observations = self._load_observations_for_trace(trace_id)

            final_output = self._extract_final_output(callback_messages, observations)
            if final_output is not None:
                result = final_output
            else:
                # As a fallback, coerce async streams or objects into text
                coerced = await self._coerce_result_to_text(result)
                if coerced is not None:
                    result = coerced

            # Mark successful
            self.results["successful"] += 1
            
            # Record duration
            duration_ms = (time.time() - start_time) * 1000
            self.results["durations"].append(duration_ms)

            trace_entry = {
                "trace_id": trace_id,
                "iteration": iteration,
                "persona": persona.name if persona else None,
                "input": input_text,
                "output": result,
                "duration_ms": duration_ms,
                "success": True,
            }

            send_messages = callback_messages.get("send", [])
            error_messages = callback_messages.get("error", [])

            if send_messages or error_messages:
                trace_entry["callback_messages"] = {
                    "send": [self._serialize_callback(args, kwargs) for args, kwargs in send_messages],
                    "error": [self._serialize_callback(args, kwargs) for args, kwargs in error_messages],
                }

            if observations:
                trace_entry["observation_count"] = len(observations)

            self.results["traces"].append(trace_entry)
            
        except Exception as e:
            # Record failure
            self.results["failed"] += 1
            self.results["errors"].append({
                "iteration": iteration,
                "persona": persona.name if persona else None,
                "input": input_text,
                "error": str(e),
            })

    def _should_use_multi_turn(self) -> bool:
        cfg = getattr(self.config, "multi_turn", None)
        return bool(cfg and getattr(cfg, "enabled", False))

    async def _run_multi_turn(
        self,
        agent_func: Callable,
        variation: Dict[str, Any],
        persona: Optional[PersonaConfig],
        iteration: int,
        *,
        turn_progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
    ) -> None:
        """Execute a multi-turn conversation using the supervisor loop."""

        self.results["total_runs"] += 1

        multi_cfg: MultiTurnConfig = self.config.multi_turn or MultiTurnConfig()

        if multi_cfg.persona_override:
            persona = next(
                (
                    p
                    for p in (self.config.personas or [])
                    if p.name == multi_cfg.persona_override
                ),
                persona,
            )

        variation_metadata = variation.get("metadata") or {}
        input_text = variation["input"]

        if persona and not variation_metadata.get("persona"):
            variation_metadata["persona"] = persona.name
        if persona and not variation_metadata.get("persona_description"):
            variation_metadata["persona_description"] = persona.description

        persona_description = variation_metadata.get("persona_description")
        if persona and not persona_description:
            persona_description = persona.description

        service_context = variation_metadata.get("service_context")
        if not service_context:
            service_context = (self.config.metadata or {}).get("service_context")

        supervisor = ConversationSupervisor(multi_cfg.supervisor)

        conversation_state: Dict[str, Any] = {
            "turns": [
                {
                    "role": "user",
                    "content": input_text,
                }
            ],
            "metadata": {
                "iteration": iteration,
                "persona": persona.name if persona else None,
                "persona_description": persona_description,
                "service_context": service_context,
                "variation": variation_metadata,
                "auto_approve_tools": multi_cfg.auto_approve_tools,
            },
            "context": {},
        }

        trace_name = f"{self.config.name}_iter{iteration}"
        if persona:
            trace_name += f"_persona_{persona.name}"

        start_time = time.time()
        termination_reason: Optional[str] = None
        last_decision: Optional[SupervisorDecision] = None
        final_output: Optional[str] = None
        trace_id: Optional[str] = None

        try:
            with fluxloop.instrument(trace_name) as ctx:
                if hasattr(ctx, "trace") and getattr(ctx, "trace") is not None:
                    trace_id = str(ctx.trace.id)
                    ctx.add_metadata("trace_id", trace_id)

                ctx.add_metadata("iteration", iteration)
                ctx.add_metadata("variation", variation)
                if persona:
                    ctx.add_metadata("persona", persona.name)
                ctx.add_metadata("multi_turn", True)

                current_user_input = input_text
                turn_count = 0

                while True:
                    if turn_progress_callback:
                        preview = (
                            current_user_input
                            if isinstance(current_user_input, str)
                            else str(current_user_input)
                        )
                        turn_progress_callback(
                            turn_count + 1,
                            multi_cfg.max_turns or 1,
                            preview,
                        )

                    callback_messages: Dict[str, Any] = {}

                    logger.debug(
                        "multi-turn request: iteration=%s turn=%s input_type=%s preview=%r",
                        iteration,
                        turn_count,
                        type(current_user_input).__name__,
                        current_user_input if isinstance(current_user_input, str) else str(current_user_input),
                    )
                    result = await self._call_agent(
                        agent_func,
                        current_user_input,
                        iteration=iteration,
                        callback_store=callback_messages,
                        conversation_state=conversation_state,
                        persona=persona,
                        auto_approve=multi_cfg.auto_approve_tools,
                    )

                    await self._wait_for_callbacks(callback_messages)

                    EventBuffer.get_instance().flush()

                    observations: List[Dict[str, Any]] = []
                    if trace_id:
                        observations = self._load_observations_for_trace(trace_id)

                    assistant_output = self._extract_final_output(
                        callback_messages, observations
                    )
                    if assistant_output is None:
                        coerced = await self._coerce_result_to_text(result)
                        assistant_output = coerced if coerced is not None else str(result)

                    logger.debug(
                        "multi-turn agent output: raw_type=%s assistant_output_type=%s preview=%r",
                        type(result).__name__,
                        type(assistant_output).__name__,
                        assistant_output if isinstance(assistant_output, str) else str(assistant_output),
                    )

                    final_output = assistant_output

                    conversation_state["turns"].append(
                        {
                            "role": "assistant",
                            "content": assistant_output,
                        }
                    )

                    turn_count += 1
                    ctx.add_metadata("turn_count", turn_count)

                    if turn_count >= multi_cfg.max_turns:
                        termination_reason = "max_turns_reached"
                        ctx.add_metadata("termination_reason", termination_reason)
                        break

                    decision = await supervisor.decide(
                        conversation_state=conversation_state,
                        persona_description=persona_description,
                        service_context=service_context,
                    )
                    last_decision = decision
                    logger.debug(
                        "multi-turn supervisor decision: decision=%s termination=%r next_type=%s",
                        decision.decision,
                        decision.termination_reason,
                        type(decision.next_user_message).__name__
                        if decision.next_user_message is not None
                        else None,
                    )

                    if decision.decision == "terminate":
                        termination_reason = (
                            decision.termination_reason or "supervisor_terminate"
                        )
                        if decision.closing_user_message:
                            conversation_state["turns"].append(
                                {
                                    "role": "user",
                                    "content": decision.closing_user_message,
                                    "closing": True,
                                }
                            )
                        ctx.add_metadata("termination_reason", termination_reason)
                        break

                    next_user_message = decision.next_user_message
                    if not next_user_message:
                        raise ValueError(
                            "Supervisor decided to continue but provided no next_user_message."
                        )

                    logger.debug(
                        "multi-turn next user message: type=%s preview=%r",
                        type(next_user_message).__name__,
                        next_user_message if isinstance(next_user_message, str) else str(next_user_message),
                    )
                    conversation_state["turns"].append(
                        {
                            "role": "user",
                            "content": next_user_message,
                        }
                    )
                    current_user_input = next_user_message

                EventBuffer.get_instance().flush()

        except Exception as exc:
            self.results["failed"] += 1
            duration_ms = (time.time() - start_time) * 1000
            self.results["durations"].append(duration_ms)
            self.results["errors"].append(
                {
                    "iteration": iteration,
                    "persona": persona.name if persona else None,
                    "input": input_text,
                    "error": str(exc),
                }
            )
            raise
        else:
            self.results["successful"] += 1
            duration_ms = (time.time() - start_time) * 1000
            self.results["durations"].append(duration_ms)

            trace_entry = {
                "trace_id": trace_id,
                "iteration": iteration,
                "persona": persona.name if persona else None,
                "input": input_text,
                "output": final_output,
                "duration_ms": duration_ms,
                "success": True,
                "termination_reason": termination_reason,
                "conversation": conversation_state,
            }
            if last_decision and last_decision.raw_response:
                trace_entry["supervisor_response"] = last_decision.raw_response

            self.results["traces"].append(trace_entry)
        finally:
            if turn_progress_callback:
                turn_progress_callback(
                    turn_count,
                    multi_cfg.max_turns or max(turn_count, 1),
                    None,
                )
    
    def _resolve_entry_persona(
        self,
        entry: Dict[str, Any],
        persona_map: Dict[str, PersonaConfig],
    ) -> Optional[PersonaConfig]:
        """Select persona metadata from an input entry when available."""

        metadata = entry.get("metadata") or {}
        persona_name = metadata.get("persona")

        if persona_name and persona_name in persona_map:
            return persona_map[persona_name]

        return None
    
    async def _call_agent(
        self,
        agent_func: Callable,
        input_text: str,
        iteration: int = 0,
        callback_store: Optional[Dict[str, Any]] = None,
        conversation_state: Optional[Dict[str, Any]] = None,
        persona: Optional[PersonaConfig] = None,
        auto_approve: Optional[bool] = None,
    ) -> Any:
        """Call the agent with arguments bound by ArgBinder (sync or async)."""

        kwargs = self._arg_binder.bind_call_args(
            agent_func,
            runtime_input=input_text,
            iteration=iteration,
            conversation_state=conversation_state,
            persona=persona,
            auto_approve=auto_approve,
        )

        # Attach collector callback capture if present
        if callback_store is not None:
            send_cb = kwargs.get("send_message_callback")
            if callable(send_cb) and hasattr(send_cb, "messages"):
                callback_store["send"] = send_cb.messages

            error_cb = kwargs.get("send_error_callback")
            if callable(error_cb) and hasattr(error_cb, "errors"):
                callback_store["error"] = error_cb.errors

        if inspect.isasyncgenfunction(agent_func):
            return await self._consume_async_gen(agent_func, kwargs)

        if asyncio.iscoroutinefunction(agent_func):
            # Ensure current contextvars are preserved for the coroutine
            ctx = contextvars.copy_context()
            result = await ctx.run(lambda: agent_func(**kwargs))
        else:
            loop = asyncio.get_event_loop()
            # Preserve contextvars across thread execution
            ctx = contextvars.copy_context()
            def _call():
                return agent_func(**kwargs)
            result = await loop.run_in_executor(None, lambda: ctx.run(_call))

        # If an async generator/iterable is returned, consume it into a string
        if inspect.isasyncgen(result) or hasattr(result, "__aiter__"):
            return await self._consume_async_iterable(result)

        return result

    async def _wait_for_callbacks(
        self,
        callback_messages: Dict[str, Any],
        *,
        timeout_seconds: float = 5.0,
        poll_interval: float = 0.1,
    ) -> None:
        """Wait briefly for background callbacks to populate the capture lists."""
        if not callback_messages:
            return

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if callback_messages.get("send") or callback_messages.get("error"):
                break
            await asyncio.sleep(poll_interval)

    def _load_observations_for_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Load observations from the offline store that match the given trace_id."""
        observations_path = self.offline_dir / "observations.jsonl"
        if not observations_path.exists():
            return []

        matched: List[Dict[str, Any]] = []
        try:
            with observations_path.open("r", encoding="utf-8") as src:
                for line in src:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if data.get("trace_id") == trace_id:
                        matched.append(data)
        except OSError:
            return []

        return matched

    def _extract_final_output(
        self,
        callback_messages: Dict[str, Any],
        observations: List[Dict[str, Any]],
    ) -> Any:
        """Derive the final output from callbacks or observations."""
        for observation in reversed(observations):
            if observation.get("name") == "agent_final_response" and observation.get("output") is not None:
                val = observation.get("output")
                if not ExperimentRunner._looks_like_generator_repr(val):
                    return val

        for observation in reversed(observations):
            if observation.get("type") == "agent" and observation.get("output") is not None:
                val = observation.get("output")
                if not ExperimentRunner._looks_like_generator_repr(val):
                    return val

        send_messages = callback_messages.get("send") if callback_messages else None
        if send_messages:
            last_args, last_kwargs = send_messages[-1]
            return self._extract_payload(last_args, last_kwargs)

        return None

    @staticmethod
    def _looks_like_generator_repr(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        s = value.strip().lower()
        return s.startswith("<async_generator ") or s.startswith("<generator ") or " object at 0x" in s

    async def _consume_async_gen(self, func: Callable, kwargs: Dict[str, Any]) -> Any:
        """Consume an async generator function by joining text chunks resolved from events."""
        gen = func(**kwargs)
        return await self._consume_async_iterable(gen)

    async def _consume_async_iterable(self, agen: Any) -> Any:
        """Consume async iterable items, extracting text via runner.stream_output_path.

        Uses a copied contextvars context to ensure FluxLoop context is preserved
        across async iteration boundaries created by upstream frameworks.
        """
        # Prefer ChatKit-like path by default; configurable via runner.stream_output_path
        path = (getattr(self.config.runner, "stream_output_path", None) or "update.delta").split(".")
        chunks: List[str] = []

        ctx = contextvars.copy_context()

        while True:
            try:
                item = await ctx.run(agen.__anext__)
            except StopAsyncIteration:
                break

            val = self._get_by_path(item, path)
            if isinstance(val, str) and val:
                chunks.append(val)
                continue

            fallback = self._extract_stream_text(item)
            if fallback:
                chunks.append(fallback)
        return "".join(chunks) if chunks else None

    @staticmethod
    def _get_by_path(obj: Any, parts: List[str]) -> Any:
        cur: Any = obj
        for key in parts:
            if cur is None:
                return None
            if isinstance(cur, dict):
                cur = cur.get(key)
            else:
                cur = getattr(cur, key, None)
        return cur

    @staticmethod
    def _extract_stream_text(event: Any) -> Optional[str]:
        """Best-effort extraction of text payloads from streaming events."""

        update = getattr(event, "update", None)
        if update is not None:
            delta = getattr(update, "delta", None)
            if isinstance(delta, str) and delta:
                return delta

            content = getattr(update, "content", None)
            text = getattr(content, "text", None) if content is not None else None
            if isinstance(text, str) and text:
                return text

        item = getattr(event, "item", None)
        if item is not None:
            content = getattr(item, "content", None)
            if isinstance(content, list):
                parts: List[str] = []
                for piece in content:
                    text = getattr(piece, "text", None)
                    if isinstance(text, str) and text:
                        parts.append(text)
                if parts:
                    return " ".join(parts)

        text_attr = getattr(event, "text", None)
        if isinstance(text_attr, str) and text_attr:
            return text_attr
        # Final deep fallback: search common fields recursively
        return ExperimentRunner._deep_extract_text(event)

    @staticmethod
    def _deep_extract_text(obj: Any, *, _depth: int = 0) -> Optional[str]:
        if _depth > 3 or obj is None:
            return None
        if isinstance(obj, str):
            return obj if obj else None
        # dict-like
        if isinstance(obj, dict):
            for key in ("delta", "text"):
                val = obj.get(key)
                if isinstance(val, str) and val:
                    return val
            # content as list of parts with text
            content = obj.get("content")
            if isinstance(content, list):
                parts: List[str] = []
                for piece in content:
                    txt = ExperimentRunner._deep_extract_text(piece, _depth=_depth + 1)
                    if txt:
                        parts.append(txt)
                if parts:
                    return " ".join(parts)
            # Recurse selected fields
            for key in ("update", "message", "item", "data"):
                val = obj.get(key)
                txt = ExperimentRunner._deep_extract_text(val, _depth=_depth + 1)
                if txt:
                    return txt
            return None
        # object with attributes
        for attr in ("delta", "text"):
            val = getattr(obj, attr, None)
            if isinstance(val, str) and val:
                return val
        for attr in ("content",):
            val = getattr(obj, attr, None)
            if isinstance(val, list):
                parts: List[str] = []
                for piece in val:
                    txt = ExperimentRunner._deep_extract_text(piece, _depth=_depth + 1)
                    if txt:
                        parts.append(txt)
                if parts:
                    return " ".join(parts)
        for attr in ("update", "message", "item", "data"):
            val = getattr(obj, attr, None)
            txt = ExperimentRunner._deep_extract_text(val, _depth=_depth + 1)
            if txt:
                return txt
        return None

    @staticmethod
    def _extract_payload(args: Sequence[Any], kwargs: Dict[str, Any]) -> Any:
        if kwargs:
            return kwargs

        if not args:
            return None

        if len(args) == 1:
            return args[0]

        return list(args)
    
    @staticmethod
    def _serialize_callback(args: Sequence[Any], kwargs: Dict[str, Any]) -> Any:
        """Serialize callback arguments for JSON storage."""
        if len(args) == 1 and not kwargs:
            return args[0]
        return {
            "args": list(args),
            "kwargs": kwargs,
        }

    async def _coerce_result_to_text(self, value: Any) -> Optional[str]:
        """Best-effort conversion of agent result into text for summaries.

        Handles async generators/iterables, known streaming item shapes, and strings.
        """
        import inspect as _inspect

        if value is None:
            return None

        if isinstance(value, str):
            return value

        # Async iterable/generator → consume to text
        if _inspect.isasyncgen(value) or hasattr(value, "__aiter__"):
            try:
                return await self._consume_async_iterable(value)
            except Exception:
                return None

        # Try extracting text from known event-like objects
        fallback = self._extract_stream_text(value)
        if fallback:
            return fallback

        return None
    
    def _save_results(self) -> None:
        """Save results to output directory."""
        # Save summary
        summary_file = self.output_dir / "summary.json"
        summary = {
            "name": self.config.name,
            "date": datetime.now().isoformat(),
            "config": self.config.to_dict(),
            "results": {
                "total_runs": self.results["total_runs"],
                "successful": self.results["successful"],
                "failed": self.results["failed"],
                "success_rate": self.results["success_rate"],
                "avg_duration_ms": self.results["avg_duration_ms"],
                "duration_seconds": self.results["duration_seconds"],
            },
        }
        summary_file.write_text(json.dumps(summary, indent=2))
        
        if self.config.save_traces:
            self._save_trace_summary()
            self._save_experiment_observations()
        
        # Save errors
        if self.results["errors"]:
            errors_file = self.output_dir / "errors.json"
            errors_file.write_text(json.dumps(self.results["errors"], indent=2))

    def _save_trace_summary(self) -> None:
        """Persist detailed and summary trace information for the experiment."""
        full_traces_path = self.output_dir / "traces.jsonl"
        summary_path = self.output_dir / "trace_summary.jsonl"

        with full_traces_path.open("w", encoding="utf-8") as full_file:
            for trace in self.results["traces"]:
                full_file.write(json.dumps(trace) + "\n")

        with summary_path.open("w", encoding="utf-8") as summary_file:
            for trace in self.results["traces"]:
                summary_file.write(
                    json.dumps(
                        {
                            "trace_id": trace.get("trace_id"),
                            "iteration": trace.get("iteration"),
                            "persona": trace.get("persona"),
                            "input": trace.get("input"),
                            "output": trace.get("output"),
                            "duration_ms": trace.get("duration_ms"),
                            "success": trace.get("success"),
                        }
                    )
                    + "\n"
                )

    def _save_experiment_observations(self) -> None:
        """Copy matching observations from the offline store into the experiment directory."""
        trace_ids = {
            trace["trace_id"]
            for trace in self.results["traces"]
            if trace.get("trace_id")
        }

        if not trace_ids:
            return

        # Gather candidate offline stores
        candidates = []
        try:
            from fluxloop import get_config as _get_sdk_config  # type: ignore
            sdk_dir = Path(_get_sdk_config().offline_store_dir)
            candidates.append(sdk_dir / "observations.jsonl")
        except Exception:
            pass

        candidates.append(self.offline_dir / "observations.jsonl")
        # Legacy fallback removed now that SDK defaults to experiments/artifacts

        # Unique existing paths in priority order
        seen = set()
        existing: list[Path] = []
        for p in candidates:
            try:
                rp = p.resolve()
            except Exception:
                continue
            if rp in seen:
                continue
            seen.add(rp)
            if rp.exists():
                existing.append(rp)

        if not existing:
            return

        destination = self.output_dir / "observations.jsonl"
        copied = 0
        seen_lines = set()

        with destination.open("w", encoding="utf-8") as dst:
            for source_path in existing:
                try:
                    with source_path.open("r", encoding="utf-8") as src:
                        for line in src:
                            if not line.strip():
                                continue
                            try:
                                record = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            if record.get("trace_id") in trace_ids:
                                key = (record.get("id"), record.get("start_time"))
                                if key in seen_lines:
                                    continue
                                dst.write(json.dumps(record) + "\n")
                                seen_lines.add(key)
                                copied += 1
                except OSError:
                    continue

        console.print(
            f"[green]✅ Saved {copied} observations to {destination.name}[/green]"
        )


class SingleRunner:
    """Runner for single agent executions."""
    
    def __init__(
        self,
        module_path: str,
        function_name: str = "run",
        trace_name: Optional[str] = None,
        no_collector: bool = False,
    ):
        """
        Initialize single runner.
        
        Args:
            module_path: Module path to agent
            function_name: Function to call
            trace_name: Name for the trace
            no_collector: If True, disable collector
        """
        self.module_path = module_path
        self.function_name = function_name
        self.trace_name = trace_name or f"single_{module_path}"
        
        if no_collector:
            fluxloop.configure(enabled=False)
    
    async def run(self, input_text: str) -> Any:
        """
        Run the agent once.
        
        Args:
            input_text: Input for the agent
            
        Returns:
            Agent output
        """
        # Load agent
        try:
            module = importlib.import_module(self.module_path)
            agent_func = getattr(module, self.function_name)
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Failed to load agent: {e}")
        
        # Run with instrumentation
        with fluxloop.instrument(self.trace_name):
            if asyncio.iscoroutinefunction(agent_func):
                return await agent_func(input_text)
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, agent_func, input_text)
