"""Tests for context management."""

import pytest
from uuid import uuid4

import fluxloop 
from fluxloop.context import FluxLoopContext, get_current_context


class TestFluxLoopContext:
    """Test the FluxLoopContext class."""
    
    def test_context_creation(self):
        """Test creating a context."""
        ctx = FluxLoopContext(
            trace_name="test_trace",
            user_id="user-123",
            metadata={"version": "1.0"},
            tags=["test", "unit"]
        )
        
        assert ctx.trace.name == "test_trace"
        assert ctx.trace.user_id == "user-123"
        assert ctx.trace.metadata["version"] == "1.0"
        assert "test" in ctx.trace.tags
        assert "unit" in ctx.trace.tags
    
    def test_context_metadata_operations(self):
        """Test adding metadata to context."""
        ctx = FluxLoopContext(trace_name="test")
        
        ctx.add_metadata("key1", "value1")
        ctx.add_metadata("key2", 123)
        
        assert ctx.trace.metadata["key1"] == "value1"
        assert ctx.trace.metadata["key2"] == 123
    
    def test_context_tag_operations(self):
        """Test adding tags to context."""
        ctx = FluxLoopContext(trace_name="test")
        
        ctx.add_tag("tag1")
        ctx.add_tag("tag2")
        ctx.add_tag("tag1")  # Duplicate should not be added
        
        assert len(ctx.trace.tags) == 2
        assert "tag1" in ctx.trace.tags
        assert "tag2" in ctx.trace.tags
    
    def test_context_user_setting(self):
        """Test setting user ID."""
        ctx = FluxLoopContext(trace_name="test")
        
        ctx.set_user("user-456")
        assert ctx.trace.user_id == "user-456"
    
    def test_context_sampling(self):
        """Test context sampling."""
        # Set sample rate to 0 (never sample)
        fluxloop.configure(sample_rate=0.0)
        ctx = FluxLoopContext(trace_name="test")
        assert not ctx.is_sampled
        assert not ctx.is_enabled()
        
        # Set sample rate to 1 (always sample)
        fluxloop.configure(sample_rate=1.0)
        ctx = FluxLoopContext(trace_name="test")
        assert ctx.is_sampled
        assert ctx.is_enabled()


class TestInstrumentContextManager:
    """Test the instrument context manager."""
    
    def test_instrument_basic(self):
        """Test basic instrument usage."""
        fluxloop.configure(enabled=True, collector_url="http://test")
        
        with fluxloop.instrument("test_workflow") as ctx:
            assert ctx is not None
            assert ctx.trace.name == "test_workflow"
            
            # Context should be accessible
            current = get_current_context()
            assert current == ctx
        
        # Context should be cleared after exit
        assert get_current_context() is None
    
    def test_instrument_with_metadata(self):
        """Test instrument with metadata."""
        with fluxloop.instrument(
            "test",
            user_id="user-123",
            metadata={"env": "test"},
            tags=["experiment"]
        ) as ctx:
            assert ctx.trace.user_id == "user-123"
            assert ctx.trace.metadata["env"] == "test"
            assert "experiment" in ctx.trace.tags
    
    def test_nested_instrument_not_supported(self):
        """Test that nested instrument contexts work independently."""
        with fluxloop.instrument("outer") as outer_ctx:
            assert get_current_context() == outer_ctx
            
            # Inner context replaces outer
            with fluxloop.instrument("inner") as inner_ctx:
                assert get_current_context() == inner_ctx
                assert get_current_context() != outer_ctx
            
            # Outer context is restored
            assert get_current_context() == outer_ctx
    
    def test_instrument_with_error(self):
        """Test instrument handles errors properly."""
        fluxloop.configure(enabled=True, collector_url="http://test")
        
        with pytest.raises(ValueError):
            with fluxloop.instrument("error_test") as ctx:
                ctx.add_metadata("status", "running")
                raise ValueError("Test error")
        
        # Context should be cleaned up
        assert get_current_context() is None
    
    def test_instrument_disabled(self):
        """Test instrument when SDK is disabled."""
        fluxloop.configure(enabled=False)
        
        with fluxloop.instrument("test") as ctx:
            assert ctx is not None
            assert not ctx.is_enabled()
            
            # Operations should be no-ops
            ctx.add_metadata("key", "value")
            ctx.add_tag("tag")
