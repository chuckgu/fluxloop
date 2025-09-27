"""
Context management for tracing.
"""

import contextvars
import random
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from .buffer import EventBuffer
from .config import get_config
from .models import ObservationData, TraceData


# Context variable for current FluxLoop context
_context_var: contextvars.ContextVar[Optional["FluxLoopContext"]] = contextvars.ContextVar(
    "fluxloop_context", default=None
)


class FluxLoopContext:
    """
    Context for managing trace and observation hierarchy.
    """
    
    def __init__(
        self,
        trace_name: str,
        trace_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        trace_id_override: Optional[Union[UUID, str]] = None,
    ):
        """
        Initialize a new context.
        
        Args:
            trace_name: Name for the trace
            trace_id: Optional trace ID (generated if not provided)
            session_id: Optional session ID for grouping traces
            user_id: Optional user identifier
            metadata: Additional metadata
            tags: Tags for categorization
        """
        self.config = get_config()
        self.buffer = EventBuffer.get_instance()
        
        # Create trace
        trace_uuid = self._coerce_uuid(trace_id_override) or trace_id or uuid4()

        self.trace = TraceData(
            id=trace_uuid,
            name=trace_name,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {},
            tags=tags or [],
        )
        
        # Observation stack for hierarchy
        self.observation_stack: List[ObservationData] = []
        self.observations: List[ObservationData] = []
        
        # Sampling decision
        self.is_sampled = random.random() < self.config.sample_rate
    
    def is_enabled(self) -> bool:
        """Check if tracing is enabled and sampled."""
        return self.config.enabled and self.is_sampled
    
    def push_observation(self, observation: ObservationData) -> None:
        """
        Push a new observation onto the stack.
        
        Args:
            observation: Observation to push
        """
        if not self.is_enabled():
            return
        
        # Set trace ID
        observation.trace_id = self.trace.id
        
        # Set parent if there's an observation on the stack
        if self.observation_stack:
            parent = self.observation_stack[-1]
            observation.parent_observation_id = parent.id
        
        # Add to stack and list
        self.observation_stack.append(observation)
        self.observations.append(observation)
        
        # Send to buffer if it's complete (has end_time)
        if observation.end_time:
            self.buffer.add_observation(self.trace.id, observation)
    
    def pop_observation(self) -> Optional[ObservationData]:
        """
        Pop the current observation from the stack.
        
        Returns:
            The popped observation, or None if stack is empty
        """
        if not self.is_enabled() or not self.observation_stack:
            return None
        
        observation = self.observation_stack.pop()
        
        # If observation doesn't have end_time, set it now
        if not observation.end_time:
            observation.end_time = datetime.now(timezone.utc)
        
        # Send to buffer
        self.buffer.add_observation(self.trace.id, observation)
        
        return observation
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the current trace."""
        if self.is_enabled():
            self.trace.metadata[key] = value
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the current trace."""
        if self.is_enabled() and tag not in self.trace.tags:
            self.trace.tags.append(tag)
    
    @staticmethod
    def _coerce_uuid(value: Optional[Union[UUID, str]]) -> Optional[UUID]:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except Exception:
            return None

    def set_user(self, user_id: str) -> None:
        """Set the user ID for the trace."""
        if self.is_enabled():
            self.trace.user_id = user_id
    
    def finalize(self) -> None:
        """Finalize the trace and send all data."""
        if not self.is_enabled():
            return
        
        # Pop any remaining observations
        while self.observation_stack:
            self.pop_observation()
        
        # Set trace end time
        if not self.trace.end_time:
            self.trace.end_time = datetime.now(timezone.utc)
        
        # Send trace to buffer
        self.buffer.add_trace(self.trace)
        
        # Trigger flush if needed
        self.buffer.flush_if_needed()


def get_current_context() -> Optional[FluxLoopContext]:
    """
    Get the current FluxLoop context.
    
    Returns:
        Current context or None if not in a context
    """
    return _context_var.get()


@contextmanager
def instrument(
    name: str,
    session_id: Optional[UUID] = None,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    trace_id: Optional[UUID] = None,
):
    """
    Context manager for instrumenting code blocks.
    
    Args:
        name: Name for the trace
        session_id: Optional session ID
        user_id: Optional user identifier
        metadata: Additional metadata
        tags: Tags for categorization
        
    Example:
        >>> with fluxloop.instrument("my_workflow"):
        ...     result = my_agent.process(input_data)
    """
    # Create new context
    context = FluxLoopContext(
        trace_name=name,
        session_id=session_id,
        user_id=user_id,
        metadata=metadata,
        tags=tags,
        trace_id_override=trace_id,
    )
    
    # Set as current context
    token = _context_var.set(context)
    
    try:
        yield context
    finally:
        # Finalize and reset context
        context.finalize()
        _context_var.reset(token)
