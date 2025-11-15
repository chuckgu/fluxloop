"""Tests for SDK decorators."""

import pytest

import fluxloop


class TestTraceDecorator:
    """Test the @trace decorator."""

    def test_trace_decorator_sync(self):
        """Trace decorator should record sync function execution."""
        fluxloop.configure(enabled=True, collector_url="http://test", sample_rate=1.0)

        @fluxloop.trace(name="strip_whitespace")
        def preprocess(text: str) -> str:
            return text.strip()

        with fluxloop.instrument("trace_test") as ctx:
            result = preprocess(" hello ")

            assert result == "hello"
            assert len(ctx.observations) == 1

            observation = ctx.observations[0]
            assert observation.name == "strip_whitespace"
            assert observation.type.value == "span"
            assert observation.input == {"text": " hello "}
            assert observation.output == "hello"

    @pytest.mark.asyncio
    async def test_trace_decorator_async(self):
        """Trace decorator should support async functions."""
        fluxloop.configure(enabled=True, collector_url="http://test", sample_rate=1.0)

        @fluxloop.trace(name="async_double")
        async def async_process(value: int) -> int:
            return value * 2

        with fluxloop.instrument("trace_test") as ctx:
            result = await async_process(4)

            assert result == 8
            assert len(ctx.observations) == 1
            observation = ctx.observations[0]
            assert observation.input == {"value": 4}
            assert observation.output == 8

    def test_trace_decorator_records_errors(self):
        """Trace decorator should capture error metadata when function fails."""
        fluxloop.configure(enabled=True, collector_url="http://test", sample_rate=1.0)

        @fluxloop.trace(name="failing_step")
        def failing():
            raise RuntimeError("boom")

        with fluxloop.instrument("trace_test") as ctx:
            with pytest.raises(RuntimeError, match="boom"):
                failing()

            observation = ctx.observations[0]
            assert observation.error == "boom"
            assert observation.metadata["error_type"] == "RuntimeError"
            assert "traceback" in observation.metadata

    def test_trace_decorator_accepts_string_observation_type(self):
        """Trace decorator accepts ObservationType as string."""
        fluxloop.configure(enabled=True, collector_url="http://test", sample_rate=1.0)

        @fluxloop.trace(name="tool_step", observation_type="tool")
        def tool_func() -> str:
            return "ok"

        with fluxloop.instrument("trace_test") as ctx:
            tool_func()

            observation = ctx.observations[0]
            assert observation.type.value == "tool"

    def test_trace_decorator_invalid_observation_type(self):
        """Invalid observation type should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid observation_type 'invalid'"):
            fluxloop.trace(observation_type="invalid")


class TestAgentDecorator:
    """Test the @agent decorator."""

    def test_agent_decorator_sync(self):
        """Test agent decorator with sync function."""
        # Reset config for testing
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.agent(name="TestAgent")
        def test_function(x: int, y: int) -> int:
            return x + y

        with fluxloop.instrument("test_trace"):
            result = test_function(2, 3)

        assert result == 5

    @pytest.mark.asyncio
    async def test_agent_decorator_async(self):
        """Test agent decorator with async function."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.agent(name="AsyncAgent")
        async def async_function(x: int) -> int:
            return x * 2

        with fluxloop.instrument("test_trace"):
            result = await async_function(5)

        assert result == 10

    def test_agent_decorator_with_error(self):
        """Test agent decorator handles errors properly."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.agent()
        def failing_function():
            raise ValueError("Test error")

        with fluxloop.instrument("test_trace"):
            with pytest.raises(ValueError, match="Test error"):
                failing_function()

    def test_agent_decorator_disabled(self):
        """Test agent decorator when SDK is disabled."""
        fluxloop.configure(enabled=False)

        @fluxloop.agent()
        def test_function(x: int) -> int:
            return x * 2

        # Should work normally without instrumentation
        result = test_function(5)
        assert result == 10


class TestPromptDecorator:
    """Test the @prompt decorator."""

    def test_prompt_decorator_basic(self):
        """Test prompt decorator basic functionality."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.prompt(model="test-model")
        def generate(prompt: str) -> str:
            return f"Response to: {prompt}"

        with fluxloop.instrument("test_trace"):
            result = generate("Hello")

        assert result == "Response to: Hello"

    def test_prompt_decorator_with_tokens(self):
        """Test prompt decorator with token capture."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.prompt(model="gpt-3.5-turbo", capture_tokens=True)
        def generate_with_usage(prompt: str) -> dict:
            return {
                "text": f"Response to: {prompt}",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                },
            }

        with fluxloop.instrument("test_trace"):
            result = generate_with_usage("Test prompt")

        assert result["text"] == "Response to: Test prompt"
        assert result["usage"]["total_tokens"] == 30


class TestToolDecorator:
    """Test the @tool decorator."""

    def test_tool_decorator(self):
        """Test tool decorator basic functionality."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.tool(description="Test tool")
        def search(query: str) -> list:
            return [f"Result for: {query}"]

        with fluxloop.instrument("test_trace"):
            results = search("test query")

        assert results == ["Result for: test query"]

    @pytest.mark.asyncio
    async def test_tool_decorator_async(self):
        """Test tool decorator with async function."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.tool(name="AsyncTool")
        async def async_tool(value: int) -> int:
            return value**2

        with fluxloop.instrument("test_trace"):
            result = await async_tool(4)

        assert result == 16


class TestDecoratorIntegration:
    """Test decorator integration scenarios."""

    def test_nested_decorators(self):
        """Test nested decorator calls."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.tool()
        def search(query: str) -> str:
            return f"Results for: {query}"

        @fluxloop.prompt()
        def generate(prompt: str) -> str:
            search_results = search(prompt)
            return f"Generated from: {search_results}"

        @fluxloop.agent()
        def agent(input: str) -> str:
            return generate(input)

        with fluxloop.instrument("test_trace"):
            result = agent("test")

        assert "Generated from: Results for: test" in result

    def test_decorator_without_context(self):
        """Test decorator without instrument context."""
        fluxloop.configure(enabled=True, collector_url="http://test")

        @fluxloop.agent()
        def standalone_function(x: int) -> int:
            return x * 2

        # Should work but not trace (no context)
        result = standalone_function(5)
        assert result == 10
