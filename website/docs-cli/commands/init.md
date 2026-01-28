---
sidebar_position: 1
---

# init Command

Initialize local FluxLoop scenarios and test templates.

## Subcommands

### init scenario

Initialize a new local scenario folder structure. This is the starting point for testing a specific agent behavior locally.

#### Usage

```bash
fluxloop init scenario [NAME] [OPTIONS]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `name` | Name of the scenario (creates `.fluxloop/scenarios/{name}/`) |

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--link <id>` | Link to an existing Web Scenario ID | None |
| `--create-remote` | Also create the Scenario on the Web Platform | `false` |
| `--force`, `-f` | Overwrite existing files | `false` |

#### Examples

```bash
# Create a new local scenario
fluxloop init scenario my-chatbot

# Create and link to a web scenario
fluxloop init scenario onboarding-flow --link sc_12345

# Create local and remote scenarios simultaneously
fluxloop init scenario search-test --create-remote
```

#### What Gets Created

```
.fluxloop/scenarios/my-chatbot/
├── configs/
│   ├── scenario.yaml      # Scenario metadata
│   ├── input.yaml         # Personas and input settings
│   └── simulation.yaml    # Runner and experiment config
├── agents/                # Agent wrapper code
├── inputs/                # Local input data
├── experiments/           # Local test results
└── .env                   # Scenario-specific environment variables
```

---

### init pytest-template

Scaffold a pytest test file that uses FluxLoop's test fixtures. This allows you to integrate FluxLoop into your existing CI/CD or automated testing suite.

#### Usage

```bash
fluxloop init pytest-template [SCENARIO_ROOT] [OPTIONS]
```

#### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `scenario_root` | Path containing the scenario's `configs/` | Current directory |

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--tests-dir` | Directory for tests (relative to root) | `tests` |
| `--filename` | Test file name to create | `test_fluxloop_smoke.py` |
| `--force` | Overwrite existing template | `false` |

#### Examples

```bash
# Create test in default location (./tests/test_fluxloop_smoke.py)
fluxloop init pytest-template

# Custom test directory and filename
fluxloop init pytest-template --tests-dir integration_tests --filename test_agent_e2e.py
```

#### Generated Test Template

The command creates a pytest file that demonstrates how to use the `fluxloop_runner` fixture:

```python
import pytest
from fluxloop_cli.testing.pytest_plugin import fluxloop_runner

def test_fluxloop_smoke(fluxloop_runner):
    """Smoke test: verify agent runs without errors."""
    result = fluxloop_runner(
        config_path="configs/simulation.yaml",
        iterations=1,
        input_text="Hello, test!"
    )
    
    # Assertions on result
    assert result.success_rate > 0.8
    assert result.total_runs >= 1
```

---

## Related Commands

- [`fluxloop test`](./test) - Run the initialized scenario
- [`fluxloop projects select`](./projects) - Select a project before initializing scenarios
- [`fluxloop sync pull`](./sync) - Pull scenario data from the web
