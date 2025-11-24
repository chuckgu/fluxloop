---
sidebar_position: 5
---

# Pytest Integration

Integrate FluxLoop experiments into your pytest test suite for CI/CD pipelines.

## Overview

Starting with FluxLoop 0.2.29, you can run FluxLoop experiments as part of your pytest tests using specialized fixtures. This enables:

- **Familiar Testing Workflow**: Use `pytest` commands developers already know
- **CI/CD Integration**: Run experiments in GitHub Actions, GitLab CI, etc.
- **Assertion Support**: Use pytest assertions on experiment results
- **Test Discovery**: Automatically discover and run FluxLoop tests
- **Parallel Execution**: Run multiple experiment tests in parallel

## Quick Start

### 1. Install with Dev Dependencies

```bash
pip install -e packages/cli[dev]
# or for published package
pip install fluxloop-cli[dev]
```

### 2. Generate Test Template

```bash
# Generate pytest template in default location (tests/)
fluxloop init pytest-template

# Custom location
fluxloop init pytest-template --tests-dir integration_tests

# Custom filename
fluxloop init pytest-template --filename test_agent_smoke.py
```

**What gets created:**

```python
# tests/test_fluxloop_smoke.py
import pytest
from pathlib import Path
from fluxloop_cli.testing.pytest_plugin import fluxloop_runner

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_fluxloop_smoke(fluxloop_runner):
    """Smoke test: verify agent runs without errors."""
    result = fluxloop_runner(
        project_root=PROJECT_ROOT,
        simulation_config=PROJECT_ROOT / "configs" / "simulation.yaml",
        overrides={"iterations": 1},
        env={"PYTHONPATH": str(PROJECT_ROOT)},
    )
    
    # Assert on results
    assert result.total_runs > 0
    assert result.success_rate >= 0.8
    
    # Or use convenience method
    result.require_success(threshold=0.8)
```

### 3. Run Tests

```bash
# Run FluxLoop tests only
pytest -k fluxloop_smoke

# Run with verbose output
pytest -k fluxloop -v

# Stop on first failure
pytest -k fluxloop --maxfail=1

# Run all tests including FluxLoop
pytest
```

## Available Fixtures

### fluxloop_runner

Executes experiments using FluxLoop's `ExperimentRunner` directly (SDK mode).

**Signature:**

```python
def fluxloop_runner(
    project_root: Path,
    simulation_config: Path,
    overrides: dict | None = None,
    env: dict | None = None,
    timeout: int = 600,
) -> FluxLoopTestResult:
    ...
```

**Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `project_root` | `Path` | Project root directory | Required |
| `simulation_config` | `Path` | Path to simulation.yaml | Required |
| `overrides` | `dict` | Override config values | `None` |
| `env` | `dict` | Environment variables | `None` |
| `timeout` | `int` | Timeout in seconds | `600` |

**Example:**

```python
def test_basic_run(fluxloop_runner):
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 5},
        env={"PYTHONPATH": str(Path.cwd())},
    )
    
    assert result.total_runs == 5
    result.require_success()
```

### fluxloop_runner_multi_turn

Convenience fixture for multi-turn experiments (auto-enables multi-turn mode).

**Example:**

```python
def test_multi_turn(fluxloop_runner_multi_turn):
    result = fluxloop_runner_multi_turn(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={
            "iterations": 2,
            "multi_turn": {
                "max_turns": 8,
                "auto_approve_tools": True,
            }
        },
    )
    
    assert result.total_runs == 2
    result.require_success(threshold=0.7)
```

### fluxloop_cli (Advanced)

Executes experiments by calling `fluxloop run experiment` as a subprocess (CLI mode).

**When to Use:**

- Testing actual CLI commands
- Verifying command-line behavior
- Debugging CLI output
- Integration testing with full CLI stack

**Example:**

```python
def test_cli_execution(fluxloop_cli):
    result = fluxloop_cli(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        cli_args=["--iterations", "3", "--yes"],
    )
    
    # Check CLI execution
    assert result.success_rate > 0.8
    
    # Access CLI-specific info
    print(f"Command: {result.cli_command}")
    print(f"Stdout: {result.stdout_path}")
    print(f"Stderr: {result.stderr_path}")
```

## FluxLoopTestResult API

All fixtures return a `FluxLoopTestResult` object with test metrics and paths.

### Properties

```python
class FluxLoopTestResult:
    # Metrics
    total_runs: int              # Total experiment runs
    success_rate: float          # Success rate (0.0-1.0)
    avg_duration_ms: float       # Average duration in ms
    
    # File Paths
    experiment_dir: Path         # Experiment output directory
    trace_summary_path: Path     # trace_summary.jsonl path
    per_trace_path: Path | None  # per_trace.jsonl (if parsed)
    
    # CLI-specific (fluxloop_cli fixture only)
    cli_command: str | None      # Full CLI command
    stdout_path: Path | None     # Stdout log file
    stderr_path: Path | None     # Stderr log file
```

### Methods

#### require_success()

Assert that success rate meets threshold.

```python
result.require_success(threshold=0.8)
# Raises AssertionError if success_rate < 0.8
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `threshold` | `float` | `1.0` | Minimum success rate (0.0-1.0) |
| `message` | `str` | Auto-generated | Custom error message |

**Examples:**

```python
# Require 100% success
result.require_success()

# Require at least 80% success
result.require_success(threshold=0.8)

# Custom error message
result.require_success(
    threshold=0.9,
    message="Agent quality below 90%"
)
```

#### require_min_runs()

Assert minimum number of runs.

```python
result.require_min_runs(min_runs=10)
# Raises AssertionError if total_runs < 10
```

#### require_max_duration()

Assert average duration is below threshold.

```python
result.require_max_duration(max_ms=500)
# Raises AssertionError if avg_duration_ms > 500
```

## Complete Examples

### Basic Smoke Test

```python
def test_agent_smoke(fluxloop_runner):
    """Quick validation that agent runs."""
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 1},
    )
    
    # Just verify it completes
    assert result.total_runs > 0
```

### Regression Test

```python
def test_agent_regression(fluxloop_runner):
    """Ensure agent maintains quality standards."""
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 10},
    )
    
    # Strict success requirements
    result.require_success(threshold=0.95)
    result.require_max_duration(max_ms=1000)
```

### Performance Test

```python
def test_agent_performance(fluxloop_runner):
    """Verify agent meets latency SLAs."""
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 50},
    )
    
    # Check latency
    assert result.avg_duration_ms < 500, \
        f"Agent too slow: {result.avg_duration_ms}ms"
    
    # Still require reasonable quality
    result.require_success(threshold=0.85)
```

### Multi-Turn Conversation Test

```python
def test_multi_turn_conversation(fluxloop_runner_multi_turn):
    """Test agent handles multi-turn dialogues."""
    result = fluxloop_runner_multi_turn(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={
            "iterations": 5,
            "multi_turn": {
                "max_turns": 10,
                "auto_approve_tools": True,
            }
        },
    )
    
    result.require_success(threshold=0.80)
    result.require_min_runs(min_runs=5)
```

### Persona-Specific Test

```python
def test_expert_persona(fluxloop_runner):
    """Test agent with expert user persona."""
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={
            "iterations": 10,
            "personas": ["expert_user"],  # Filter to specific persona
        },
    )
    
    # Expert users should get faster responses
    result.require_max_duration(max_ms=300)
    result.require_success(threshold=0.90)
```

### Custom Assertions

```python
def test_custom_metrics(fluxloop_runner):
    """Test with custom evaluation logic."""
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 20},
    )
    
    # Read per-trace data for custom checks
    import json
    with open(result.trace_summary_path) as f:
        traces = [json.loads(line) for line in f]
    
    # Custom assertions
    long_traces = [t for t in traces if t["duration_ms"] > 1000]
    assert len(long_traces) < 2, "Too many slow responses"
    
    failed_traces = [t for t in traces if not t.get("success")]
    assert len(failed_traces) == 0, "Found failed traces"
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/fluxloop-tests.yml`:

```yaml
name: FluxLoop Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -U pip
          pip install -e packages/cli[dev]
      
      - name: Run FluxLoop tests
        env:
          PYTHONPATH: ${{ github.workspace }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          source .venv/bin/activate
          pytest -k fluxloop --maxfail=1 -v
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: fluxloop-results
          path: experiments/
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
test:fluxloop:
  stage: test
  image: python:3.11
  
  before_script:
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install -U pip
    - pip install -e packages/cli[dev]
  
  script:
    - export PYTHONPATH=$CI_PROJECT_DIR
    - pytest -k fluxloop --maxfail=1 -v
  
  artifacts:
    when: always
    paths:
      - experiments/
    expire_in: 1 week
```

### Example Workflow

Full example at `examples/ci/fluxloop_pytest.yml`:

```yaml
name: fluxloop-pytest

on:
  workflow_dispatch:
  workflow_call:

jobs:
  smoke:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install deps
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -U pip
          pip install -e packages/cli[dev]
      
      - name: Run FluxLoop Pytest suite
        env:
          PYTHONPATH: ${{ github.workspace }}
        run: |
          source .venv/bin/activate
          pytest -k fluxloop_smoke --maxfail=1 --disable-warnings
```

## Best Practices

### 1. Start with Minimal Iterations

Use low iteration counts for fast feedback:

```python
def test_quick_smoke(fluxloop_runner):
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 1},  # Fast validation
    )
    result.require_success()
```

### 2. Use Fixtures for Setup

Share common configuration:

```python
import pytest
from pathlib import Path

@pytest.fixture
def project_root():
    return Path(__file__).parents[1]

@pytest.fixture
def simulation_config(project_root):
    return project_root / "configs" / "simulation.yaml"

def test_agent(fluxloop_runner, project_root, simulation_config):
    result = fluxloop_runner(
        project_root=project_root,
        simulation_config=simulation_config,
        overrides={"iterations": 5},
    )
    result.require_success()
```

### 3. Set PYTHONPATH

Ensure agent modules are importable:

```python
def test_agent(fluxloop_runner):
    project_root = Path.cwd()
    result = fluxloop_runner(
        project_root=project_root,
        simulation_config=project_root / "configs/simulation.yaml",
        env={"PYTHONPATH": str(project_root)},  # Important!
    )
    result.require_success()
```

### 4. Use Timeouts

Prevent hanging tests:

```python
def test_agent(fluxloop_runner):
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        timeout=300,  # 5 minute timeout
    )
    result.require_success()
```

### 5. Organize Tests by Category

```python
# tests/test_fluxloop_smoke.py
def test_smoke(fluxloop_runner):
    """Quick validation."""
    ...

# tests/test_fluxloop_regression.py
def test_regression(fluxloop_runner):
    """Quality regression tests."""
    ...

# tests/test_fluxloop_performance.py
def test_performance(fluxloop_runner):
    """Latency and throughput tests."""
    ...
```

Run by category:

```bash
pytest tests/test_fluxloop_smoke.py  # Fast smoke tests
pytest tests/test_fluxloop_regression.py  # Quality checks
pytest -k fluxloop  # All FluxLoop tests
```

## Advanced Usage

### Parameterized Tests

Test multiple configurations:

```python
import pytest

@pytest.mark.parametrize("iterations", [1, 5, 10])
def test_varying_iterations(fluxloop_runner, iterations):
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": iterations},
    )
    result.require_success(threshold=0.8)
```

### Custom Result Processing

```python
def test_with_custom_processing(fluxloop_runner):
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 10},
    )
    
    # Parse per-trace results
    import json
    traces = []
    with open(result.trace_summary_path) as f:
        for line in f:
            traces.append(json.loads(line))
    
    # Custom analysis
    durations = [t["duration_ms"] for t in traces]
    p95 = sorted(durations)[int(len(durations) * 0.95)]
    
    assert p95 < 1000, f"P95 latency too high: {p95}ms"
```

### Integration with Other Tools

Combine with other testing tools:

```python
def test_with_deepeval(fluxloop_runner):
    """Integrate with DeepEval for LLM evaluation."""
    result = fluxloop_runner(
        project_root=Path.cwd(),
        simulation_config=Path("configs/simulation.yaml"),
        overrides={"iterations": 5},
    )
    
    # Use per_trace_path with DeepEval
    from deepeval import evaluate
    from deepeval.metrics import AnswerRelevancyMetric
    
    # Read traces and evaluate
    with open(result.per_trace_path) as f:
        traces = [json.loads(line) for line in f]
    
    metric = AnswerRelevancyMetric()
    scores = [metric.measure(t["input"], t["output"]) for t in traces]
    
    avg_score = sum(scores) / len(scores)
    assert avg_score > 0.7
```

## Troubleshooting

### Tests Hang or Timeout

**Issue:** Tests don't complete.

**Solutions:**

1. Set explicit timeout:
   ```python
   result = fluxloop_runner(..., timeout=300)
   ```

2. Use `pytest-timeout`:
   ```bash
   pip install pytest-timeout
   pytest -k fluxloop --timeout=600
   ```

3. Add `--maxfail=1` to stop early:
   ```bash
   pytest -k fluxloop --maxfail=1
   ```

### Module Not Found

**Issue:** `ModuleNotFoundError: No module named 'my_agent'`

**Solution:** Set PYTHONPATH:

```python
result = fluxloop_runner(
    ...,
    env={"PYTHONPATH": str(project_root)},
)
```

Or in CI:

```yaml
env:
  PYTHONPATH: ${{ github.workspace }}
```

### API Key Not Found

**Issue:** LLM provider errors.

**Solution:** Set API keys in environment:

```yaml
# CI configuration
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

Or locally:

```bash
export OPENAI_API_KEY=sk-your-key
pytest -k fluxloop
```

## See Also

- [CI/CD Integration](/cli/workflows/ci-cd-integration) - Full CI/CD guide
- [Run Command](/cli/commands/run) - CLI reference
- [Basic Workflow](/cli/workflows/basic-workflow) - Complete workflow
- [init pytest-template](/cli/commands/init#init-pytest-template) - Template generation

