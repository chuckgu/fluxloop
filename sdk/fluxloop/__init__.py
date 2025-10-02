"""
FluxLoop SDK - Agent instrumentation and tracing library.
"""

from .context import FluxLoopContext, get_current_context, instrument
from .decorators import agent, prompt, tool
from .schemas import (
    ExperimentConfig,
    PersonaConfig,
    RunnerConfig,
    VariationStrategy,
    Trace,
    Observation,
    ObservationType,
    ObservationLevel,
    Score,
    ScoreDataType,
    TraceStatus,
)
from .client import FluxLoopClient
from .config import configure, get_config, reset_config
from .recording import disable_recording, enable_recording, record_call_args, set_recording_options

__version__ = "0.1.0"

__all__ = [
    # Decorators
    "agent",
    "prompt",
    "tool",
    # Context
    "instrument",
    "get_current_context",
    "FluxLoopContext",
    # Client
    "FluxLoopClient",
    # Config
    "configure",
    "get_config",
    "reset_config",
    "enable_recording",
    "disable_recording",
    "set_recording_options",
    "record_call_args",
    # Schemas - configs
    "ExperimentConfig",
    "PersonaConfig",
    "RunnerConfig",
    "VariationStrategy",
    # Schemas - tracing
    "Trace",
    "Observation",
    "ObservationType",
    "ObservationLevel",
    "Score",
    "ScoreDataType",
    "TraceStatus",
]
