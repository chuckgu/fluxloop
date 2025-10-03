"""
Runner modules for executing experiments and agents.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

import fluxloop
import yaml

from fluxloop.schemas import ExperimentConfig, PersonaConfig
from rich.console import Console

from .target_loader import TargetLoader
from .arg_binder import ArgBinder

console = Console()


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
        fluxloop.configure(
            use_collector=not no_collector and bool(config.collector_url),
            collector_url=config.collector_url or None,
            api_key=config.collector_api_key,
            offline_store_enabled=True,
            offline_store_dir=str(offline_dir),
        )

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
    
    def _load_agent(self) -> Callable:
        """Load the agent function from module path."""
        loader = TargetLoader(self.config.runner, source_dir=self.config.get_source_dir())
        try:
            return loader.load()
        except ValueError as exc:
            raise RuntimeError(str(exc)) from exc

    async def run_experiment(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Run the complete experiment.
        
        Args:
            progress_callback: Optional callback for progress updates
            
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
    ) -> None:
        """Run a single execution."""
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
            with fluxloop.instrument(trace_name) as ctx:
                # Add metadata
                ctx.add_metadata("iteration", iteration)
                ctx.add_metadata("variation", variation)
                if persona:
                    ctx.add_metadata("persona", persona.name)
                
                # Prepare collector callback storage
                callback_messages: Dict[str, Any] = {}

                # Run agent
                result = await self._call_agent(
                    agent_func,
                    input_text,
                    iteration=iteration,
                    callback_store=callback_messages,
                )

                # If collector callbacks captured messages, include them
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

                if send_messages:
                    last_args, last_kwargs = send_messages[-1]
                    result = self._extract_payload(last_args, last_kwargs)
                
                # Mark successful
                self.results["successful"] += 1
                
                # Record duration
                duration_ms = (time.time() - start_time) * 1000
                self.results["durations"].append(duration_ms)

                trace_entry = {
                    "iteration": iteration,
                    "persona": persona.name if persona else None,
                    "input": input_text,
                    "output": result,
                    "duration_ms": duration_ms,
                    "success": True,
                }

                if send_messages or error_messages:
                    trace_entry["callback_messages"] = {
                        "send": [self._serialize_callback(args, kwargs) for args, kwargs in send_messages],
                        "error": [self._serialize_callback(args, kwargs) for args, kwargs in error_messages],
                    }

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
    ) -> Any:
        """Call the agent with arguments bound by ArgBinder (sync or async)."""

        kwargs = self._arg_binder.bind_call_args(
            agent_func,
            runtime_input=input_text,
            iteration=iteration,
        )

        # Attach collector callback capture if present
        if callback_store is not None:
            send_cb = kwargs.get("send_message_callback")
            if callable(send_cb) and hasattr(send_cb, "messages"):
                callback_store["send"] = send_cb.messages

            error_cb = kwargs.get("send_error_callback")
            if callable(error_cb) and hasattr(error_cb, "errors"):
                callback_store["error"] = error_cb.errors

        if asyncio.iscoroutinefunction(agent_func):
            return await agent_func(**kwargs)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: agent_func(**kwargs))

    @staticmethod
    def _extract_payload(args: Sequence[Any], kwargs: Dict[str, Any]) -> Any:
        if kwargs:
            return kwargs

        if not args:
            return None

        if len(args) == 1:
            return args[0]

        return list(args)
    
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
        
        # Save traces
        if self.config.save_traces:
            traces_file = self.output_dir / "traces.jsonl"
            with open(traces_file, "w") as f:
                for trace in self.results["traces"]:
                    f.write(json.dumps(trace) + "\n")
        
        # Save errors
        if self.results["errors"]:
            errors_file = self.output_dir / "errors.json"
            errors_file.write_text(json.dumps(self.results["errors"], indent=2))


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
