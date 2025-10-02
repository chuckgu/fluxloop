"""
FluxLoop Shared Schemas

Common data models shared across all FluxLoop components.
Based on Langfuse data model for compatibility.
"""

from .trace import (
    Trace,
    Observation,
    ObservationType,
    Score,
    ScoreDataType,
    TraceStatus,
    ObservationLevel,
)
from .config import (
    ExperimentConfig,
    InputGenerationConfig,
    InputGenerationMode,
    LLMGeneratorConfig,
    PersonaConfig,
    ReplayArgsConfig,
    VariationStrategy,
    EvaluatorConfig,
    RunnerConfig,
)

__all__ = [
    # Trace models
    "Trace",
    "Observation",
    "ObservationType",
    "Score",
    "ScoreDataType",
    "TraceStatus",
    "ObservationLevel",
    # Config models
    "ExperimentConfig",
    "InputGenerationConfig",
    "InputGenerationMode",
    "LLMGeneratorConfig",
    "PersonaConfig",
    "ReplayArgsConfig",
    "VariationStrategy",
    "EvaluatorConfig",
    "RunnerConfig",
]
