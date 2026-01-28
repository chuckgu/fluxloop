---
sidebar_position: 1
---

# SDK Installation

Install the FluxLoop SDK for Python agent instrumentation.

## Requirements

- **Python 3.11 or higher**
- pip

:::info Python Version Requirement
The FluxLoop SDK requires Python 3.11+ due to advanced type hints and protocol features used for tracing context management.
:::

## Install via pip

```bash
pip install fluxloop
```

### With Optional Dependencies

Install with framework-specific extras:

```bash
# For LangChain integration
pip install fluxloop[langchain]

# For LangGraph integration
pip install fluxloop[langgraph]

# For development (includes test tools)
pip install fluxloop[dev]

# Multiple extras
pip install fluxloop[langchain,langgraph]
```

## Verify Installation

Check that the SDK is installed correctly:

```python
import fluxloop

# Check version
print(fluxloop.__version__)  # Should print: 0.1.7

# Test basic functionality
fluxloop.configure(enabled=True, debug=True)
print("FluxLoop SDK ready!")
```

**Expected output:**
```
0.1.7
FluxLoop SDK ready!
```

## Quick Test

Create a simple test file to verify tracing works:

```python
# test_fluxloop.py
import fluxloop

@fluxloop.agent(name="TestAgent")
def test_agent(message: str) -> str:
    return f"Echo: {message}"

# Run the agent
result = test_agent("Hello, FluxLoop!")
print(result)
```

Run it:
```bash
python test_fluxloop.py
```

**Expected:**
- Prints: `Echo: Hello, FluxLoop!`
- Creates `./traces/` directory with JSONL files
- Check `./traces/traces_YYYYMMDD.jsonl` for trace data

## Troubleshooting

### "Python version 3.11 required"

**Issue:** SDK requires Python 3.11+

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.11+ if needed
# macOS (Homebrew):
brew install python@3.11

# Ubuntu/Debian:
sudo apt install python3.11

# Then create venv with correct version
python3.11 -m venv .venv
source .venv/bin/activate
pip install fluxloop
```

### "ModuleNotFoundError: No module named 'fluxloop'"

**Issue:** SDK not installed or wrong Python environment

**Solution:**
```bash
# Verify installation
pip list | grep fluxloop

# Reinstall if missing
pip install --force-reinstall fluxloop

# Check Python environment
which python
```

### Import Errors for Optional Dependencies

**Issue:** Using LangChain/LangGraph without installing extras

**Solution:**
```bash
# Install with extras
pip install fluxloop[langchain]
# or
pip install fluxloop[langgraph]
```

## Virtual Environment Setup

It's recommended to use a virtual environment:

### Using venv

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install FluxLoop
pip install fluxloop
```

### Using Poetry

```bash
# Initialize project
poetry init

# Add FluxLoop
poetry add fluxloop

# With extras
poetry add fluxloop[langchain,langgraph]
```

### Using pipenv

```bash
# Install with pipenv
pipenv install fluxloop

# With extras
pipenv install fluxloop[langchain]
```

## Upgrading

Upgrade to the latest version:

```bash
# Upgrade via pip
pip install --upgrade fluxloop

# Check new version
python -c "import fluxloop; print(fluxloop.__version__)"
```

## Development Installation

For contributing or local development:

```bash
# Clone repository
git clone https://github.com/chuckgu/fluxloop.git
cd fluxloop/packages/sdk

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy fluxloop

# Run linter
ruff check fluxloop
```

## Platform-Specific Notes

### macOS

Works out of the box with Homebrew Python:

```bash
brew install python@3.11
pip3 install fluxloop
```

### Linux (Ubuntu/Debian)

```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Install FluxLoop
python3.11 -m pip install fluxloop
```

### Windows

```powershell
# Install Python 3.11 from python.org

# Install FluxLoop
pip install fluxloop

# Note: Use `python` instead of `python3`
```

## Docker Installation

Include FluxLoop in your Docker image:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install FluxLoop
RUN pip install --no-cache-dir fluxloop

# Copy your agent code
COPY . .

CMD ["python", "my_agent.py"]
```

## Configuration After Installation

After installing, configure the SDK:

```python
import fluxloop

# Basic configuration
fluxloop.configure(
    enabled=True,
    storage="file",
    base_path="./traces",
    debug=False
)
```

Or use environment variables:

```bash
# .env
FLUXLOOP_ENABLED=true
FLUXLOOP_STORAGE=file
FLUXLOOP_BASE_PATH=./traces
FLUXLOOP_DEBUG=false
```

Load with:

```python
fluxloop.load_env(".env")
```

See [Client Configuration](/sdk/configuration/client-config) for all options.

## Next Steps

- **[Basic Usage](/sdk/getting-started/basic-usage)** - Your first traced agent
- **[Async Support](/sdk/getting-started/async-support)** - Async patterns
- **[Client Configuration](/sdk/configuration/client-config)** - Configure storage and options
- **[API Reference](/sdk/api/decorators)** - Full decorator API

---

Having issues? Check [GitHub Issues](https://github.com/chuckgu/fluxloop/issues) or the [Troubleshooting section](#troubleshooting).

