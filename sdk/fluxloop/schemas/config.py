"""
Configuration schemas for experiments and simulations.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator


class VariationStrategy(str, Enum):
    """Strategy for generating prompt variations."""
    
    REPHRASE = "rephrase"  # Rephrase the same intent
    TYPO = "typo"  # Add typos/errors
    VERBOSE = "verbose"  # Make more verbose
    CONCISE = "concise"  # Make more concise
    PERSONA_BASED = "persona_based"  # Based on persona characteristics
    ADVERSARIAL = "adversarial"  # Edge cases and attacks
    MULTILINGUAL = "multilingual"  # Different languages
    CUSTOM = "custom"  # Custom variation prompt


class InputGenerationMode(str, Enum):
    """Supported input generation approaches."""

    DETERMINISTIC = "deterministic"
    LLM = "llm"


class LLMGeneratorConfig(BaseModel):
    """Configuration for LLM-backed input generation."""

    enabled: bool = False
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    strategy_prompts: Dict[str, str] = Field(default_factory=dict)
    max_outputs: int = Field(default=3, ge=1, le=20)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=16, le=4096)
    request_timeout: int = Field(default=60, ge=1, le=600)
    batch_size: int = Field(default=1, ge=1, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # GPT-5 specific controls
    reasoning_effort: Optional[str] = Field(
        default=None,
        description="Reasoning effort for GPT-5 models: minimal, low, medium, high",
    )
    text_verbosity: Optional[str] = Field(
        default=None,
        description="Output verbosity for GPT-5 models: low, medium, high",
    )


class InputGenerationConfig(BaseModel):
    """Wrapper around input generation options."""

    mode: InputGenerationMode = InputGenerationMode.LLM
    llm: LLMGeneratorConfig = Field(default_factory=LLMGeneratorConfig)


class PersonaConfig(BaseModel):
    """User persona for simulation."""
    
    name: str
    description: str
    characteristics: List[str] = Field(default_factory=list)
    language: str = "en"
    expertise_level: str = "intermediate"  # novice, intermediate, expert
    goals: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)
    
    def to_prompt(self) -> str:
        """Convert persona to a prompt description."""
        prompt_parts = [
            f"User Persona: {self.name}",
            f"Description: {self.description}",
        ]
        
        if self.characteristics:
            prompt_parts.append(f"Characteristics: {', '.join(self.characteristics)}")
        
        if self.goals:
            prompt_parts.append(f"Goals: {', '.join(self.goals)}")
        
        if self.constraints:
            prompt_parts.append(f"Constraints: {', '.join(self.constraints)}")
        
        prompt_parts.append(f"Language: {self.language}")
        prompt_parts.append(f"Expertise Level: {self.expertise_level}")
        
        return "\n".join(prompt_parts)


class EvaluatorConfig(BaseModel):
    """Configuration for evaluation methods."""
    
    name: str
    type: str  # "llm_judge", "rule_based", "metric", "custom"
    enabled: bool = True
    
    # For LLM judge
    model: Optional[str] = None
    prompt_template: Optional[str] = None
    
    # For rule-based
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    
    # For metrics
    metric_name: Optional[str] = None
    threshold: Optional[float] = None
    
    # Custom evaluator
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    
    # Common
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RunnerConfig(BaseModel):
    """Configuration for agent execution."""
    
    # Entry point
    module_path: str  # e.g., "my_agent.main"
    function_name: str = "run"  # Function to call
    target: Optional[str] = Field(
        default=None,
        description=(
            "Optional combined target specification. Use 'module:function' or "
            "'module:Class.method'. When provided, takes precedence over "
            "module_path + function_name."
        ),
    )
    
    # Execution environment
    working_directory: Optional[str] = None
    python_path: Optional[str] = None
    environment_vars: Dict[str, str] = Field(default_factory=dict)
    
    # Dependencies
    requirements_file: Optional[str] = None
    setup_commands: List[str] = Field(default_factory=list)
    
    # Execution settings
    timeout_seconds: int = 300
    max_retries: int = 3
    retry_delay: int = 5
    
    # Docker settings (optional)
    use_docker: bool = False
    docker_image: Optional[str] = None
    docker_build_context: Optional[str] = None
    docker_volumes: List[str] = Field(default_factory=list)


class ExperimentConfig(BaseModel):
    """Complete experiment configuration."""

    _source_dir: Optional[Path] = PrivateAttr(default=None)
    _resolved_input_count: Optional[int] = PrivateAttr(default=None)
    _resolved_persona_count: Optional[int] = PrivateAttr(default=None)

    # Basic info
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"

    # Simulation settings
    iterations: int = Field(default=10, ge=1, le=1000)
    parallel_runs: int = Field(default=1, ge=1, le=10)
    seed: Optional[int] = None
    run_delay_seconds: float = Field(default=0.0, ge=0.0)

    # Personas
    personas: List[PersonaConfig] = Field(default_factory=list)

    # Variation settings
    variation_strategies: List[VariationStrategy] = Field(default_factory=list)
    variation_count: int = Field(default=1, ge=1, le=10)
    variation_temperature: float = Field(default=0.7, ge=0, le=2)
    variation_model: str = "gpt-3.5-turbo"
    custom_variation_prompt: Optional[str] = None

    # Base prompts/inputs
    base_inputs: List[Dict[str, Any]] = Field(default_factory=list)
    inputs_file: Optional[str] = None
    input_template: Optional[str] = None
    input_generation: InputGenerationConfig = Field(default_factory=InputGenerationConfig)

    # Runner configuration
    runner: RunnerConfig

    # Argument replay (optional)
    replay_args: Optional["ReplayArgsConfig"] = None

    # Evaluators
    evaluators: List[EvaluatorConfig] = Field(default_factory=list)

    # Output settings
    output_directory: str = "./experiments"
    save_traces: bool = True
    save_aggregated_metrics: bool = True

    # Collector settings
    collector_url: Optional[str] = None
    collector_api_key: Optional[str] = None

    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator("iterations")
    def validate_iterations(cls, v):
        """Ensure reasonable iteration count."""
        if v > 1000:
            raise ValueError("iterations must be <= 1000 for safety")
        return v
    
    @model_validator(mode="after")
    def validate_input_sources(cls, values: "ExperimentConfig") -> "ExperimentConfig":
        """Ensure at least one input source is configured."""
        if not values.base_inputs and not values.inputs_file:
            # Allow both sources to be disabled if base_inputs is provided
            if not values.base_inputs:
                raise ValueError("Either base_inputs or inputs_file must be provided")
        return values

    def has_external_inputs(self) -> bool:
        """Return True when inputs should be loaded from an external file."""
        return bool(self.inputs_file)

    def set_source_dir(self, source_dir: Path) -> None:
        """Remember the directory where this config file was loaded from."""
        self._source_dir = source_dir

    def get_source_dir(self) -> Optional[Path]:
        """Return the directory where the config file was loaded from."""
        return self._source_dir

    def set_resolved_input_count(self, count: int) -> None:
        """Record the effective input count after resolution."""
        if count < 0:
            raise ValueError("resolved input count must be non-negative")
        self._resolved_input_count = count

    def get_resolved_input_count(self) -> Optional[int]:
        """Return the resolved input count if it has been set."""
        return self._resolved_input_count

    def set_resolved_persona_count(self, count: int) -> None:
        """Record the effective persona multiplier after resolution."""
        if count < 1:
            raise ValueError("resolved persona count must be >= 1")
        self._resolved_persona_count = count

    def get_resolved_persona_count(self) -> Optional[int]:
        """Return the resolved persona multiplier if available."""
        return self._resolved_persona_count

    def _default_input_count(self) -> int:
        """Fallback calculation when no resolved count is available."""
        base_count = len(self.base_inputs)
        if self.has_external_inputs():
            return base_count if base_count else 1
        variation_multiplier = max(1, self.variation_count)
        return base_count * variation_multiplier if base_count else variation_multiplier

    def get_input_count(self) -> int:
        """Return the effective number of inputs that will be executed."""
        return self._resolved_input_count if self._resolved_input_count is not None else self._default_input_count()

    def estimate_total_runs(self) -> int:
        """Calculate total number of runs."""
        if self._resolved_persona_count is not None:
            persona_count = self._resolved_persona_count
        else:
            persona_count = len(self.personas) if self.personas else 1
        input_count = self.get_input_count()
        return self.iterations * persona_count * input_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(exclude_none=True)


class ReplayArgsConfig(BaseModel):
    """Configuration for argument replay (MVP scope)."""

    enabled: bool = False
    recording_file: Optional[str] = None
    callable_providers: Dict[str, str] = Field(
        default_factory=lambda: {
            "send_message_callback": "builtin:collector.send",
            "send_error_callback": "builtin:collector.error",
        },
        description="Mapping of callable parameter names to builtin providers",
    )
    override_param_path: Optional[str] = Field(
        default="data.content",
        description="Single dot-notation path whose value should be overridden with runtime input",
    )
