"""
Runner modules for executing experiments and agents.
"""

import asyncio
import importlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import fluxloop_sdk as fluxloop
from rich.console import Console

# Add shared schemas to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from schemas.config import ExperimentConfig, PersonaConfig

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
        
        # Configure SDK
        offline_dir = Path(config.output_directory) / "artifacts"
        fluxloop.configure(
            use_collector=not no_collector and bool(config.collector_url),
            collector_url=config.collector_url or None,
            api_key=config.collector_api_key,
            offline_store_enabled=True,
            offline_store_dir=str(offline_dir),
        )
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(config.output_directory) / f"{config.name}_{timestamp}"
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
        
        # Generate all variations
        variations = await self._generate_variations()
        
        # Run iterations
        for iteration in range(self.config.iterations):
            for persona in self.config.personas or [None]:
                for variation in variations:
                    await self._run_single(
                        agent_func,
                        variation,
                        persona,
                        iteration,
                    )
                    
                    if progress_callback:
                        progress_callback()
        
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
    
    def _load_agent(self) -> Callable:
        """Load the agent function from module path."""
        try:
            module = importlib.import_module(self.config.runner.module_path)
            func = getattr(module, self.config.runner.function_name)
            return func
        except (ImportError, AttributeError) as e:
            raise RuntimeError(f"Failed to load agent: {e}")
    
    async def _generate_variations(self) -> List[Dict[str, Any]]:
        """Generate input variations."""
        variations = []
        
        for base_input in self.config.base_inputs:
            # For now, just use base inputs
            # TODO: Implement actual variation generation with LLM
            for i in range(self.config.variation_count):
                variations.append({
                    "input": base_input.get("input"),
                    "metadata": base_input,
                    "variation_index": i,
                })
        
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
                
                # Run agent
                result = await self._call_agent(agent_func, input_text)
                
                # Mark successful
                self.results["successful"] += 1
                
                # Record duration
                duration_ms = (time.time() - start_time) * 1000
                self.results["durations"].append(duration_ms)
                
                # Store trace info
                self.results["traces"].append({
                    "iteration": iteration,
                    "persona": persona.name if persona else None,
                    "input": input_text,
                    "output": result,
                    "duration_ms": duration_ms,
                    "success": True,
                })
                
        except Exception as e:
            # Record failure
            self.results["failed"] += 1
            self.results["errors"].append({
                "iteration": iteration,
                "persona": persona.name if persona else None,
                "input": input_text,
                "error": str(e),
            })
    
    async def _call_agent(self, agent_func: Callable, input_text: str) -> Any:
        """Call the agent function (handles sync/async)."""
        if asyncio.iscoroutinefunction(agent_func):
            return await agent_func(input_text)
        else:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, agent_func, input_text)
    
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
