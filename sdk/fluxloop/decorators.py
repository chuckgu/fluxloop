"""
Decorators for instrumenting agent code.
"""

import functools
import inspect
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from uuid import UUID, uuid4

from .context import get_current_context
from .models import ObservationData, ObservationType

F = TypeVar("F", bound=Callable[..., Any])


def agent(
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    capture_input: bool = True,
    capture_output: bool = True,
) -> Callable[[F], F]:
    """
    Decorator for agent entry points.
    
    Args:
        name: Name for the agent trace (defaults to function name)
        metadata: Additional metadata to attach
        capture_input: Whether to capture function arguments
        capture_output: Whether to capture return value
        
    Example:
        >>> @fluxloop.agent(name="ChatBot")
        ... def process_message(message: str) -> str:
        ...     return f"Response to: {message}"
    """
    
    def decorator(func: F) -> F:
        agent_name = name or func.__name__
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = get_current_context()
            if not context or not context.is_enabled():
                return func(*args, **kwargs)
            
            # Create observation
            obs_id = uuid4()
            start_time = datetime.now(timezone.utc)
            
            # Capture input
            input_data = None
            if capture_input:
                input_data = _serialize_arguments(func, args, kwargs)
            
            # Create observation data
            observation = ObservationData(
                id=obs_id,
                type=ObservationType.AGENT,
                name=agent_name,
                start_time=start_time,
                input=input_data,
                metadata=metadata or {},
            )
            
            # Push to context
            context.push_observation(observation)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Capture output
                if capture_output:
                    observation.output = _serialize_value(result)
                
                return result
                
            except Exception as e:
                # Capture error
                observation.error = str(e)
                observation.metadata["error_type"] = type(e).__name__
                observation.metadata["traceback"] = traceback.format_exc()
                raise
                
            finally:
                # Finalize observation
                observation.end_time = datetime.now(timezone.utc)
                context.pop_observation()
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = get_current_context()
            if not context or not context.is_enabled():
                return await func(*args, **kwargs)
            
            # Create observation
            obs_id = uuid4()
            start_time = datetime.now(timezone.utc)
            
            # Capture input
            input_data = None
            if capture_input:
                input_data = _serialize_arguments(func, args, kwargs)
            
            # Create observation data
            observation = ObservationData(
                id=obs_id,
                type=ObservationType.AGENT,
                name=agent_name,
                start_time=start_time,
                input=input_data,
                metadata=metadata or {},
            )
            
            # Push to context
            context.push_observation(observation)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Capture output
                if capture_output:
                    observation.output = _serialize_value(result)
                
                return result
                
            except Exception as e:
                # Capture error
                observation.error = str(e)
                observation.metadata["error_type"] = type(e).__name__
                observation.metadata["traceback"] = traceback.format_exc()
                raise
                
            finally:
                # Finalize observation
                observation.end_time = datetime.now(timezone.utc)
                context.pop_observation()
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def prompt(
    name: Optional[str] = None,
    model: Optional[str] = None,
    capture_tokens: bool = True,
) -> Callable[[F], F]:
    """
    Decorator for prompt/LLM generation functions.
    
    Args:
        name: Name for the generation (defaults to function name)
        model: Model name being used
        capture_tokens: Whether to try to capture token usage
        
    Example:
        >>> @fluxloop.prompt(model="gpt-3.5-turbo")
        ... def generate_response(prompt: str) -> str:
        ...     return llm.generate(prompt)
    """
    
    def decorator(func: F) -> F:
        prompt_name = name or func.__name__
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = get_current_context()
            if not context or not context.is_enabled():
                return func(*args, **kwargs)
            
            # Create observation
            obs_id = uuid4()
            start_time = datetime.now(timezone.utc)
            
            # Capture input
            input_data = _serialize_arguments(func, args, kwargs)
            
            # Create observation data
            observation = ObservationData(
                id=obs_id,
                type=ObservationType.GENERATION,
                name=prompt_name,
                start_time=start_time,
                input=input_data,
                model=model,
                metadata={},
            )
            
            # Push to context
            context.push_observation(observation)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Capture output
                observation.output = _serialize_value(result)
                
                # Try to extract token usage if result is a dict-like object
                if capture_tokens and hasattr(result, "get"):
                    if "usage" in result:
                        usage = result["usage"]
                        observation.prompt_tokens = usage.get("prompt_tokens")
                        observation.completion_tokens = usage.get("completion_tokens")
                        observation.total_tokens = usage.get("total_tokens")
                
                return result
                
            except Exception as e:
                # Capture error
                observation.error = str(e)
                observation.metadata["error_type"] = type(e).__name__
                observation.metadata["traceback"] = traceback.format_exc()
                raise
                
            finally:
                # Finalize observation
                observation.end_time = datetime.now(timezone.utc)
                context.pop_observation()
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = get_current_context()
            if not context or not context.is_enabled():
                return await func(*args, **kwargs)
            
            # Create observation
            obs_id = uuid4()
            start_time = datetime.now(timezone.utc)
            
            # Capture input
            input_data = _serialize_arguments(func, args, kwargs)
            
            # Create observation data
            observation = ObservationData(
                id=obs_id,
                type=ObservationType.GENERATION,
                name=prompt_name,
                start_time=start_time,
                input=input_data,
                model=model,
                metadata={},
            )
            
            # Push to context
            context.push_observation(observation)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Capture output
                observation.output = _serialize_value(result)
                
                # Try to extract token usage if result is a dict-like object
                if capture_tokens and hasattr(result, "get"):
                    if "usage" in result:
                        usage = result["usage"]
                        observation.prompt_tokens = usage.get("prompt_tokens")
                        observation.completion_tokens = usage.get("completion_tokens")
                        observation.total_tokens = usage.get("total_tokens")
                
                return result
                
            except Exception as e:
                # Capture error
                observation.error = str(e)
                observation.metadata["error_type"] = type(e).__name__
                observation.metadata["traceback"] = traceback.format_exc()
                raise
                
            finally:
                # Finalize observation
                observation.end_time = datetime.now(timezone.utc)
                context.pop_observation()
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Decorator for tool/function calls.
    
    Args:
        name: Name for the tool (defaults to function name)
        description: Description of what the tool does
        
    Example:
        >>> @fluxloop.tool(description="Search the web")
        ... def web_search(query: str) -> List[str]:
        ...     return search_engine.search(query)
    """
    
    def decorator(func: F) -> F:
        tool_name = name or func.__name__
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = get_current_context()
            if not context or not context.is_enabled():
                return func(*args, **kwargs)
            
            # Create observation
            obs_id = uuid4()
            start_time = datetime.now(timezone.utc)
            
            # Capture input
            input_data = _serialize_arguments(func, args, kwargs)
            
            # Create observation data
            observation = ObservationData(
                id=obs_id,
                type=ObservationType.TOOL,
                name=tool_name,
                start_time=start_time,
                input=input_data,
                metadata={"description": description} if description else {},
            )
            
            # Push to context
            context.push_observation(observation)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Capture output
                observation.output = _serialize_value(result)
                
                return result
                
            except Exception as e:
                # Capture error
                observation.error = str(e)
                observation.metadata["error_type"] = type(e).__name__
                observation.metadata["traceback"] = traceback.format_exc()
                raise
                
            finally:
                # Finalize observation
                observation.end_time = datetime.now(timezone.utc)
                context.pop_observation()
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = get_current_context()
            if not context or not context.is_enabled():
                return await func(*args, **kwargs)
            
            # Create observation
            obs_id = uuid4()
            start_time = datetime.now(timezone.utc)
            
            # Capture input
            input_data = _serialize_arguments(func, args, kwargs)
            
            # Create observation data
            observation = ObservationData(
                id=obs_id,
                type=ObservationType.TOOL,
                name=tool_name,
                start_time=start_time,
                input=input_data,
                metadata={"description": description} if description else {},
            )
            
            # Push to context
            context.push_observation(observation)
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Capture output
                observation.output = _serialize_value(result)
                
                return result
                
            except Exception as e:
                # Capture error
                observation.error = str(e)
                observation.metadata["error_type"] = type(e).__name__
                observation.metadata["traceback"] = traceback.format_exc()
                raise
                
            finally:
                # Finalize observation
                observation.end_time = datetime.now(timezone.utc)
                context.pop_observation()
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _serialize_arguments(func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Serialize function arguments for storage."""
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    
    serialized = {}
    for param_name, param_value in bound.arguments.items():
        serialized[param_name] = _serialize_value(param_value)
    
    return serialized


def _serialize_value(value: Any) -> Any:
    """Serialize a value for storage."""
    # Handle common types
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    
    # Handle UUIDs
    if isinstance(value, UUID):
        return str(value)
    
    # Handle datetime
    if isinstance(value, datetime):
        return value.isoformat()
    
    # Handle lists/tuples
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    
    # Handle dicts
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    
    # Handle objects with dict representation
    if hasattr(value, "dict"):
        return value.dict()
    
    # Handle objects with model_dump (Pydantic v2)
    if hasattr(value, "model_dump"):
        return value.model_dump()
    
    # Fallback to string representation
    try:
        return str(value)
    except:
        return f"<{type(value).__name__}>"
