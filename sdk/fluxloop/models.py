"""
Internal SDK models for observations and traces.
These are lightweight versions optimized for SDK use.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ObservationType(str, Enum):
    """Type of observation."""
    
    SPAN = "span"
    EVENT = "event"
    GENERATION = "generation"
    TOOL = "tool"
    AGENT = "agent"
    CHAIN = "chain"
    EVALUATION = "evaluation"


class ObservationLevel(str, Enum):
    """Log level for observations."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ObservationData(BaseModel):
    """Lightweight observation data for SDK use."""
    
    id: UUID = Field(default_factory=uuid4)
    type: ObservationType
    name: str
    
    # Timing
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    
    # Content
    input: Optional[Any] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    
    # Metadata
    level: ObservationLevel = ObservationLevel.INFO
    status_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # LLM specific
    model: Optional[str] = None
    llm_parameters: Optional[Dict[str, Any]] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    # Parent reference (set by context)
    parent_observation_id: Optional[UUID] = None
    trace_id: Optional[UUID] = None


class TraceData(BaseModel):
    """Lightweight trace data for SDK use."""
    
    id: UUID = Field(default_factory=uuid4)
    name: str
    
    # Timing
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    
    # Context
    session_id: Optional[UUID] = None
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
