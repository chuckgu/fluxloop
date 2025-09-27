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
from .config import configure

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
