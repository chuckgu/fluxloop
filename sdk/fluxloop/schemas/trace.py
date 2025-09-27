"""
Trace and Observation models based on Langfuse data model.

References:
- https://langfuse.com/docs/observability/data-model
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TraceStatus(str, Enum):
    """Status of a trace execution."""
    
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ObservationType(str, Enum):
    """Type of observation in the trace hierarchy."""
    
    SPAN = "span"  # Generic span
    EVENT = "event"  # Single event
    GENERATION = "generation"  # LLM generation
    TOOL = "tool"  # Tool/function call
    AGENT = "agent"  # Agent execution
    CHAIN = "chain"  # Chain of operations
    EVALUATION = "evaluation"  # Evaluation result


class ObservationLevel(str, Enum):
    """Log level for observations."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ScoreDataType(str, Enum):
    """Data type of score values."""
    
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"


class Score(BaseModel):
    """Score/evaluation result for a trace or observation."""
    
    id: UUID = Field(default_factory=uuid4)
    trace_id: UUID
    observation_id: Optional[UUID] = None
    name: str  # e.g., "accuracy", "relevance", "latency"
    value: Union[float, bool, str]
    data_type: ScoreDataType
    comment: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("value")
    def validate_value_type(cls, v, info):
        """Ensure value matches the declared data type."""
        data_type = info.data.get("data_type")
        if data_type == ScoreDataType.NUMERIC and not isinstance(v, (int, float)):
            raise ValueError("Numeric score must be int or float")
        elif data_type == ScoreDataType.BOOLEAN and not isinstance(v, bool):
            raise ValueError("Boolean score must be bool")
        elif data_type == ScoreDataType.CATEGORICAL and not isinstance(v, str):
            raise ValueError("Categorical score must be str")
        return v


class Observation(BaseModel):
    """Single observation within a trace."""
    
    id: UUID = Field(default_factory=uuid4)
    trace_id: UUID
    parent_observation_id: Optional[UUID] = None
    type: ObservationType
    name: str
    
    # Timing
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    
    # Content
    input: Optional[Any] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    
    # Metadata
    level: ObservationLevel = ObservationLevel.INFO
    status_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # LLM specific (for GENERATION type)
    model: Optional[str] = None
    llm_parameters: Optional[Dict[str, Any]] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    # Scores attached to this observation
    scores: List[Score] = Field(default_factory=list)
    
    def duration_ms(self) -> Optional[float]:
        """Calculate duration in milliseconds."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() * 1000
        return None


class Trace(BaseModel):
    """Root trace representing a complete execution flow."""
    
    id: UUID = Field(default_factory=uuid4)
    session_id: Optional[UUID] = None
    name: str
    
    # Timing
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    
    # Status
    status: TraceStatus = TraceStatus.PENDING
    error: Optional[str] = None
    
    # Context
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    
    # Experiment specific
    experiment_id: Optional[str] = None
    iteration: Optional[int] = None
    persona: Optional[str] = None
    variation_seed: Optional[str] = None
    
    # Input/Output
    input: Optional[Any] = None
    output: Optional[Any] = None
    
    # Hierarchical data
    observations: List[Observation] = Field(default_factory=list)
    scores: List[Score] = Field(default_factory=list)
    
    # Metrics
    total_cost: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    def duration_ms(self) -> Optional[float]:
        """Calculate total duration in milliseconds."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() * 1000
        return None
    
    def get_observation_tree(self) -> Dict[UUID, List[Observation]]:
        """Build parent-child relationship tree of observations."""
        tree: Dict[UUID, List[Observation]] = {None: []}
        
        for obs in self.observations:
            parent_id = obs.parent_observation_id
            if parent_id not in tree:
                tree[parent_id] = []
            tree[parent_id].append(obs)
        
        return tree
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate metrics for the trace."""
        metrics = {
            "duration_ms": self.duration_ms(),
            "observation_count": len(self.observations),
            "score_count": len(self.scores),
            "error_count": sum(1 for o in self.observations if o.error),
            "total_tokens": self.total_tokens or 0,
        }
        
        # Calculate success rate from scores
        success_scores = [s for s in self.scores if s.name == "success" and s.data_type == ScoreDataType.BOOLEAN]
        if success_scores:
            success_rate = sum(1 for s in success_scores if s.value) / len(success_scores)
            metrics["success_rate"] = success_rate
        
        return metrics
