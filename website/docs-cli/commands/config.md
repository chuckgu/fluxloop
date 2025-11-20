---
sidebar_position: 6
---

# config Command

Manage FluxLoop configuration settings.

## Overview

The `config` command provides utilities for viewing, updating, and validating FluxLoop configuration files. It supports both reading/writing YAML configs and managing environment variables.

## Subcommands

### show

Display configuration file contents.

```bash
# Show project configuration
fluxloop config show --file configs/project.yaml

# Show in JSON format
fluxloop config show --file configs/simulation.yaml --format json

# Show with syntax highlighting and line numbers
fluxloop config show
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | Configuration file to show | `configs/project.yaml` |
| `--project` | Project name under FluxLoop root | Current directory |
| `--root` | FluxLoop root directory | `./fluxloop` |
| `--format` | Output format (`yaml` or `json`) | `yaml` |

**Example:**

```bash
# View simulation config
fluxloop config show --file configs/simulation.yaml

# View as JSON for parsing
fluxloop config show --format json
```

---

### set

Update a specific configuration value.

```bash
# Set a simple value
fluxloop config set iterations 20

# Set nested value with dot notation
fluxloop config set runner.timeout_seconds 300

# Set boolean value
fluxloop config set multi_turn.enabled true
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `key` | Configuration key to set (use dot notation for nested keys) |
| `value` | Value to set (auto-detects type: int, float, bool, or string) |

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | Configuration file to update | `configs/project.yaml` |
| `--project` | Project name | Current |
| `--root` | FluxLoop root directory | `./fluxloop` |

**Type Detection:**

The command automatically detects value types:
- **Integer**: `20`, `100`
- **Float**: `0.5`, `3.14`
- **Boolean**: `true`, `false` (case-insensitive)
- **String**: Everything else

**Examples:**

```bash
# Update iteration count
fluxloop config set iterations 50 --file configs/simulation.yaml

# Set timeout in seconds
fluxloop config set runner.timeout_seconds 180

# Enable multi-turn mode
fluxloop config set multi_turn.enabled true

# Set temperature for variation
fluxloop config set variation_temperature 0.9 --file configs/input.yaml

# Set runner target
fluxloop config set runner.target "my_agent:run"
```

---

### env

Display environment variables used by FluxLoop.

```bash
# Show environment variables (masks API keys)
fluxloop config env

# Show all values including sensitive keys
fluxloop config env --show-values
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--show-values`, `-s` | Show actual values (including secrets) | `false` |
| `--project` | Project name | Current |
| `--root` | FluxLoop root directory | `./fluxloop` |

**Environment Variables Shown:**

| Variable | Description | Default |
|----------|-------------|---------|
| `FLUXLOOP_COLLECTOR_URL` | Collector service URL | `http://localhost:8000` |
| `FLUXLOOP_API_KEY` | API key for authentication | None |
| `FLUXLOOP_ENABLED` | Enable/disable tracing | `true` |
| `FLUXLOOP_DEBUG` | Enable debug mode | `false` |
| `FLUXLOOP_SAMPLE_RATE` | Trace sampling rate (0-1) | `1.0` |
| `FLUXLOOP_SERVICE_NAME` | Service name for traces | None |
| `FLUXLOOP_ENVIRONMENT` | Environment (dev/staging/prod) | `development` |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `ANTHROPIC_API_KEY` | Anthropic API key | None |

**Output:**

```
╭─ FluxLoop Environment Variables ──────────────────────────────────╮
│ Variable                  Description             Current Value   │
│ FLUXLOOP_COLLECTOR_URL    Collector service URL   Not set        │
│ FLUXLOOP_ENABLED          Enable/disable tracing  true           │
│ OPENAI_API_KEY            OpenAI API key          ****abc123     │
╰────────────────────────────────────────────────────────────────────╯

Loaded from: /path/to/.env
```

**Notes:**
- API keys are masked by default (shows last 4 characters)
- Use `--show-values` to see full keys (be careful with logs!)
- Environment files are merged: root `.env` → project `.env`

---

### set-llm

Configure LLM provider credentials and defaults.

```bash
# Set OpenAI as LLM provider
fluxloop config set-llm openai sk-xxxxx

# Set OpenAI with specific model
fluxloop config set-llm openai sk-xxxxx --model gpt-4o

# Set Anthropic provider
fluxloop config set-llm anthropic sk-ant-xxxxx --model claude-3-5-sonnet-20241022

# Overwrite existing API key
fluxloop config set-llm openai sk-newkey --overwrite-env
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `provider` | LLM provider (`openai`, `anthropic`, `gemini`) |
| `api_key` | API key or token for the provider |

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--model`, `-m` | Default model to use | Provider default |
| `--overwrite-env` | Overwrite existing key in .env | `false` |
| `--file`, `-f` | Config file to update | `configs/input.yaml` |
| `--env-file` | Path to environment file | `.env` |
| `--project` | Project name | Current |
| `--root` | FluxLoop root directory | `./fluxloop` |

**Supported Providers:**

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| `openai` | `OPENAI_API_KEY` | `gpt-5` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-3-haiku-20240307` |
| `gemini` | `GEMINI_API_KEY` | `gemini-2.5-flash` |

**What This Command Does:**

1. **Saves API key to `.env`:**
   ```bash
   OPENAI_API_KEY=sk-xxxxx
   ```

2. **Updates `configs/input.yaml`:**
   ```yaml
   input_generation:
     llm:
       enabled: true
       provider: openai
       model: gpt-4o
       api_key: null  # References OPENAI_API_KEY from .env
   ```

**Examples:**

```bash
# Quick setup for OpenAI
fluxloop config set-llm openai sk-proj-abc123

# Use specific Anthropic model
fluxloop config set-llm anthropic sk-ant-xyz789 \
  --model claude-3-5-sonnet-20241022

# Update existing key
fluxloop config set-llm openai sk-new-key --overwrite-env

# Set for specific project
fluxloop config set-llm openai sk-key --project my-agent
```

---

### validate

Validate configuration file structure and values.

```bash
# Validate default project config
fluxloop config validate

# Validate specific config file
fluxloop config validate --file configs/simulation.yaml

# Validate for specific project
fluxloop config validate --project my-agent
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--file`, `-f` | Configuration file to validate | `configs/project.yaml` |
| `--project` | Project name | Current |
| `--root` | FluxLoop root directory | `./fluxloop` |

**What Gets Validated:**

- YAML syntax correctness
- Required fields present
- Field types match schema
- Runner configuration valid
- Persona definitions valid
- Evaluator configurations valid

**Success Output:**

```
✓ Configuration is valid!

╭──────────────────────────────────────╮
│ Property      │ Value                │
│ Experiment    │ my_agent_experiment  │
│ Iterations    │ 10                   │
│ Personas      │ 2                    │
│ Variations    │ 5                    │
│ Total Runs    │ 100                  │
│ Runner Module │ examples.simple_agent│
│ Evaluators    │ 3                    │
╰──────────────────────────────────────╯
```

**Error Output:**

```
✗ Validation failed: Missing required field: runner.module_path
```

**Common Validation Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| Missing required field | Config missing mandatory key | Add the required field |
| Invalid YAML syntax | Malformed YAML | Check indentation and quotes |
| Type mismatch | Wrong value type | Use correct type (int, str, etc.) |
| Runner module not found | Module path incorrect | Verify module exists |
| Invalid persona | Malformed persona definition | Check persona structure |

---

## Common Workflows

### Initial Setup

```bash
# 1. Initialize project
fluxloop init project --name my-agent

# 2. Set LLM provider
fluxloop config set-llm openai sk-xxxxx --model gpt-4o

# 3. Validate configuration
fluxloop config validate

# 4. Check environment
fluxloop config env
```

### Tuning Experiment Settings

```bash
# Increase iterations for more samples
fluxloop config set iterations 50 --file configs/simulation.yaml

# Adjust variation temperature
fluxloop config set variation_temperature 0.8 --file configs/input.yaml

# Enable multi-turn mode
fluxloop config set multi_turn.enabled true --file configs/simulation.yaml
fluxloop config set multi_turn.max_turns 10 --file configs/simulation.yaml
```

### Switching LLM Providers

```bash
# Switch from OpenAI to Anthropic
fluxloop config set-llm anthropic sk-ant-xxxxx \
  --model claude-3-5-sonnet-20241022 \
  --overwrite-env
```

### Verifying Configuration Before Running

```bash
# Full validation check
fluxloop config validate --file configs/simulation.yaml
fluxloop config validate --file configs/input.yaml
fluxloop config validate --file configs/evaluation.yaml

# Check environment setup
fluxloop config env

# Or use doctor command for complete diagnostics
fluxloop doctor
```

---

## Configuration File Locations

Default configuration structure:

```
fluxloop/my-agent/
├── configs/
│   ├── project.yaml       # Project metadata
│   ├── input.yaml         # Personas and input generation
│   ├── simulation.yaml    # Runner and experiment settings
│   └── evaluation.yaml    # Evaluators and success criteria
├── .env                   # Environment variables (gitignored)
├── inputs/
│   └── generated.yaml
├── recordings/
└── experiments/
```

---

## Tips

### Dot Notation for Nested Keys

Use dot notation to set deeply nested values:

```bash
# Set nested runner config
fluxloop config set runner.timeout_seconds 300
fluxloop config set runner.max_retries 5

# Set multi-turn supervisor settings
fluxloop config set multi_turn.supervisor.model gpt-4o
fluxloop config set multi_turn.supervisor.provider openai
```

### Viewing Before Modifying

Always check current values before changing:

```bash
# Show current config
fluxloop config show --file configs/simulation.yaml

# Make change
fluxloop config set iterations 20 --file configs/simulation.yaml

# Verify change
fluxloop config show --file configs/simulation.yaml
```

### Project-Specific vs Global

Use `--project` flag to manage multiple projects:

```bash
# Set config for specific project
fluxloop config set iterations 100 --project production-agent

# Different config for dev project
fluxloop config set iterations 10 --project dev-agent
```

---

## See Also

- [Project Configuration](/cli/configuration/project-config) - Detailed config reference
- [Input Configuration](/cli/configuration/input-config) - Persona and input settings
- [Simulation Configuration](/cli/configuration/simulation-config) - Runner and experiment settings
- [Evaluation Configuration](/cli/configuration/evaluation-config) - Evaluator configuration
- [doctor Command](/cli/commands/doctor) - Environment diagnostics
- [status Command](/cli/commands/status) - System status checks
