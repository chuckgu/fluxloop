---
sidebar_position: 1
---

# init Command

Initialize FluxLoop projects, agents, and test templates.

## Subcommands

### init project

Create a new FluxLoop project with complete configuration structure.

#### Usage

```bash
fluxloop init project [PATH] [OPTIONS]
```

#### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `path` | Root directory for FluxLoop projects | `./fluxloop` |

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--name`, `-n` | Project name (required if not in project directory) | Current directory name |
| `--with-example/--no-example` | Include example agent code | `true` |
| `--force`, `-f` | Overwrite existing files without confirmation | `false` |

#### Examples

```bash
# Create new project with default path
fluxloop init project --name my-chatbot

# Create in custom location
fluxloop init project /path/to/projects --name my-agent

# Skip example agent
fluxloop init project --name my-agent --no-example

# Force overwrite existing files
fluxloop init project --name my-agent --force
```

#### What Gets Created

```
fluxloop/my-chatbot/
├── configs/
│   ├── project.yaml       # Project metadata, collector settings
│   ├── input.yaml         # Personas, base inputs, LLM settings
│   ├── simulation.yaml    # Runner configuration, iterations
│   └── evaluation.yaml    # Evaluators, success criteria
├── .env                   # Environment variables (API keys)
├── .gitignore            # Git ignore patterns
├── recordings/           # Recorded arguments (for replay)
└── examples/
    └── simple_agent.py   # Sample instrumented agent
```

#### Configuration Files

The command creates four configuration files under `configs/`:

1. **project.yaml**: Project metadata and collector settings
2. **input.yaml**: Personas, base inputs, and input generation configuration
3. **simulation.yaml**: Runner target, iterations, and multi-turn settings
4. **evaluation.yaml**: Evaluator definitions and success criteria

See [Configuration Reference](/cli/configuration/project-config) for detailed schemas.

---

### init pytest-template

Scaffold a pytest test file that uses FluxLoop's test fixtures.

#### Usage

```bash
fluxloop init pytest-template [PROJECT_ROOT] [OPTIONS]
```

#### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `project_root` | Project root containing configs/ or setting.yaml | Current directory |

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--tests-dir` | Directory for tests (relative to project root) | `tests` |
| `--filename` | Test file name to create | `test_fluxloop_smoke.py` |
| `--force` | Overwrite existing template without confirmation | `false` |

#### Examples

```bash
# Create test in default location (./tests/test_fluxloop_smoke.py)
fluxloop init pytest-template

# Custom test directory
fluxloop init pytest-template --tests-dir integration_tests

# Custom filename
fluxloop init pytest-template --filename test_agent_e2e.py

# Specify project root
fluxloop init pytest-template /path/to/project --force
```

#### Generated Test Template

The command creates a pytest test file that:

- Imports FluxLoop test fixtures (`fluxloop_runner`, `fluxloop_runner_multi_turn`)
- Includes a sample smoke test
- References your project's simulation configuration
- Demonstrates assertions on test results (`success_rate`, `total_runs`, etc.)

Example generated test:

```python
import pytest
from fluxloop_cli.testing.pytest_plugin import fluxloop_runner

def test_fluxloop_smoke(fluxloop_runner):
    """Smoke test: verify agent runs without errors."""
    result = fluxloop_runner(
        config_path="configs/simulation.yaml",
        iterations=5,
        input_text="Hello, test!"
    )
    
    # Assertions on result
    assert result.success_rate > 0.8
    assert result.total_runs == 5
    
    # Or use convenience method
    result.require_success(threshold=0.8)
```

#### Available Fixtures

| Fixture | Description | Use Case |
|---------|-------------|----------|
| `fluxloop_runner` | Single-turn test runner | Basic agent tests |
| `fluxloop_runner_multi_turn` | Multi-turn conversation runner | Multi-turn agent tests |

#### Running Pytest Tests

```bash
# Install dev dependencies
pip install -e packages/cli[dev]

# Run FluxLoop tests
pytest -k fluxloop_smoke

# Run with coverage
pytest --cov=. -k fluxloop

# Stop on first failure
pytest -k fluxloop_smoke --maxfail=1
```

#### CI Integration

The generated test works seamlessly in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
name: FluxLoop Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e packages/cli[dev]
      - run: pytest -k fluxloop_smoke
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

See [CI/CD Integration Guide](/cli/workflows/ci-cd-integration) for complete examples.

---

### init agent

Create a new agent from a template.

#### Usage

```bash
fluxloop init agent <name> [OPTIONS]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `name` | Name of the agent module |

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--path`, `-p` | Directory to create agent in | Current directory |
| `--template`, `-t` | Agent template (`simple`, `langchain`, `langgraph`) | `simple` |

#### Examples

```bash
# Create simple agent
fluxloop init agent my_chatbot

# Create in specific directory
fluxloop init agent support_agent --path ./agents

# Use different template (coming soon)
fluxloop init agent complex_agent --template langgraph
```

#### Generated Agent

Creates `agents/my_chatbot.py` with FluxLoop instrumentation:

```python
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    """Agent logic here."""
    # Process the input
    response = process_input(input_text)
    return response
```

#### Next Steps After Agent Creation

1. Update `configs/simulation.yaml` to reference your agent:
   ```yaml
   runner:
     target: "agents.my_chatbot:run"
   ```

2. Test your agent:
   ```bash
   fluxloop run experiment --iterations 1
   ```

---

## Common Workflows

### Starting a New Project

```bash
# 1. Create project
fluxloop init project --name my-agent

# 2. Navigate to project
cd fluxloop/my-agent

# 3. Configure LLM
fluxloop config set-llm openai sk-xxxxx

# 4. Create pytest tests
fluxloop init pytest-template

# 5. Run diagnostics
fluxloop doctor
```

### Adding Tests to Existing Project

```bash
# Create pytest template
fluxloop init pytest-template

# Run tests
pytest -k fluxloop_smoke

# Add to CI
cp examples/ci/fluxloop_pytest.yml .github/workflows/
```

### Creating Multiple Agents

```bash
# Create agents directory
mkdir agents

# Create different agents
fluxloop init agent chatbot --path agents
fluxloop init agent summarizer --path agents
fluxloop init agent classifier --path agents

# Test each agent
fluxloop config set runner.target "agents.chatbot:run"
fluxloop run experiment --iterations 5
```

---

## Troubleshooting

### "Directory already exists"

Use `--force` to overwrite:
```bash
fluxloop init project --name my-agent --force
```

### "Project name required"

Provide `--name` flag when not in project directory:
```bash
fluxloop init project --name my-agent
```

### "Config not found" for pytest-template

Ensure you're in project root or specify path:
```bash
fluxloop init pytest-template /path/to/project
```

---

## See Also

- [Project Setup Guide](/cli/getting-started/project-setup) - Detailed setup walkthrough
- [Pytest Bridge Guide](/docs/guides/pytest_bridge.md) - Complete pytest integration docs
- [Generate Command](/cli/commands/generate) - Generate input variations
- [Run Command](/cli/commands/run) - Execute experiments
- [Configuration Reference](/cli/configuration/project-config) - Config file schemas
