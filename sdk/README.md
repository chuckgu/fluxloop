# FluxLoop SDK

Python SDK for instrumenting and tracing AI agent executions.

## Installation

```bash
pip install fluxloop
```

## Quick Start

### Basic Usage

```python
import fluxloop 

# Configure the SDK (optional, uses environment variables by default)
fluxloop.configure(
    collector_url="http://localhost:8000",
    api_key="your-api-key"
)

# Use decorators to instrument your functions
@fluxloop.agent(name="MyAgent")
def process_request(query: str) -> str:
    # Your agent logic here
    response = generate_response(query)
    return response

@fluxloop.prompt(model="gpt-3.5-turbo")
def generate_response(query: str) -> str:
    # LLM call
    return llm.generate(query)

@fluxloop.tool(description="Search the web")
def web_search(query: str) -> list:
    # Tool implementation
    return search_engine.search(query)
```

### Context Manager

```python
import fluxloop 

# Use context manager for explicit tracing
with fluxloop.instrument("my_workflow") as ctx:
    # Add metadata
    ctx.add_metadata("version", "1.0.0")
    ctx.add_tag("production")
    ctx.set_user("user-123")
    
    # Your workflow code
    result = my_agent.process(input_data)
```

## Configuration

Configuration can be done via environment variables or programmatically:

### Environment Variables

```bash
export FLUXLOOP_COLLECTOR_URL=http://localhost:8000
export FLUXLOOP_API_KEY=your-api-key
export FLUXLOOP_ENABLED=true
export FLUXLOOP_DEBUG=false
export FLUXLOOP_SAMPLE_RATE=1.0
export FLUXLOOP_SERVICE_NAME=my-service
export FLUXLOOP_ENVIRONMENT=production
```

### Programmatic Configuration

```python
import fluxloop 

fluxloop.configure(
    collector_url="http://localhost:8000",
    api_key="your-api-key",
    enabled=True,
    debug=False,
    sample_rate=0.1,  # Sample 10% of traces
    service_name="my-service",
    environment="production"
)
```

## Decorators

### @fluxloop.agent

Instrument agent entry points:

```python
@fluxloop.agent(
    name="ChatBot",
    metadata={"version": "1.0"},
    capture_input=True,
    capture_output=True
)
def chat_bot(message: str) -> str:
    # Agent logic
    pass
```

### @fluxloop.prompt

Instrument LLM generation calls:

```python
@fluxloop.prompt(
    name="GenerateResponse",
    model="gpt-3.5-turbo",
    capture_tokens=True
)
def generate(prompt: str) -> str:
    # LLM call
    pass
```

### @fluxloop.tool

Instrument tool/function calls:

```python
@fluxloop.tool(
    name="WebSearch",
    description="Search the web for information"
)
def search(query: str) -> list:
    # Tool logic
    pass
```

## Advanced Usage

### Custom Metadata

```python
with fluxloop.instrument("workflow") as ctx:
    ctx.add_metadata("request_id", "req-123")
    ctx.add_metadata("user_type", "premium")
    ctx.add_tag("experiment-A")
```

### Async Support

All decorators support async functions:

```python
@fluxloop.agent()
async def async_agent(query: str) -> str:
    result = await async_operation(query)
    return result
```

### Sampling

Control sampling rate to reduce overhead:

```python
# Sample only 10% of traces
fluxloop.configure(sample_rate=0.1)
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Quality

```bash
# Formatting
black fluxloop tests

# Linting
ruff fluxloop tests

# Type checking
mypy fluxloop
```

## License

MIT
