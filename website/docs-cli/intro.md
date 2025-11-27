---
sidebar_position: 1
slug: /
---

# FluxLoop CLI

Command-line interface for managing FluxLoop projects, generating inputs, and running agent simulations.

## Installation

```bash
pip install fluxloop-cli
```

## Version

Current version: **0.2.30**

## Features

- 🎯 **Project Management**: Initialize and configure simulation projects
- 📝 **Input Generation**: Create test input variations using LLM or deterministic strategies
- 🧪 **Experiment Execution**: Run batch simulations with configurable iterations
- 💬 **Multi-Turn Conversations**: Automatically extend experiments into dynamic dialogues with AI supervisor
- 📊 **Result Parsing & Evaluation**: Convert raw artifacts to human-readable formats and score with evaluators
- 🔴 **Recording Mode**: Capture and replay complex function arguments
- ⚙️ **Configuration**: Structured YAML-based configuration system
- 🩺 **Environment Diagnostics**: Verify installation and detect configuration issues

## Quick Example

```bash
# Initialize a new project
fluxloop init project --name my-agent
cd fluxloop/my-agent

# Generate 50 input variations
fluxloop generate inputs --limit 50

# Run experiment
fluxloop run experiment

# Parse results
fluxloop parse experiment experiments/exp_*/

# Evaluate results (writes evaluation_report/report.html by default)
fluxloop evaluate experiment experiments/exp_*/

# Check environment
fluxloop doctor
```

## Key Commands

### Project Initialization

```bash
fluxloop init project --name <project-name>
```

Creates a new FluxLoop project with:
- `configs/` directory (project, input, simulation, evaluation configs)
- `.env` file for environment variables
- `examples/` with sample agent code
- `inputs/`, `recordings/`, `experiments/` directories

### Input Generation

```bash
fluxloop generate inputs [--limit 100] [--mode llm]
```

Generate input variations from base inputs defined in `configs/input.yaml`.

### Experiment Execution

```bash
fluxloop run experiment [--iterations 10]

# Multi-turn conversations (LLM-driven)
fluxloop run experiment --multi-turn --max-turns 12 --auto-approve

# Multi-turn scripted playback (deterministic)
# Set supervisor.provider to 'mock' and supply scripted_questions in simulation.yaml
fluxloop run experiment --multi-turn --supervisor-provider mock
```

Run simulation experiment using configuration from `configs/simulation.yaml`. Enable multi-turn mode to automatically extend single inputs into dynamic conversations. Use `provider: openai` for AI-driven follow-ups or `provider: mock` for scripted question playback.

### Recording Mode

```bash
fluxloop record enable   # Enable argument recording
fluxloop record disable  # Disable recording
fluxloop record status   # Check recording state
```

### Configuration

```bash
fluxloop config set-llm <provider> <api-key> [--model <model>]
```

Update LLM provider settings in `configs/input.yaml`.

## Configuration Files (v0.2.0)

FluxLoop CLI uses a multi-file configuration structure:

| File | Purpose |
|------|---------|
| `configs/project.yaml` | Project metadata, service context, collector settings |
| `configs/input.yaml` | Personas, base inputs, LLM settings |
| `configs/simulation.yaml` | Runner, iterations, multi-turn settings |
| `configs/evaluation.yaml` | Evaluator definitions |

## What's Next?

- **[Installation](/cli/getting-started/installation)** - Detailed installation guide
- **[Project Setup](/cli/getting-started/project-setup)** - Initialize your first project
- **[Commands Reference](/cli/commands/init)** - Full command documentation
- **[Doctor Command](/cli/commands/doctor)** - Diagnose environment and configuration
- **[Configuration](/cli/configuration/project-config)** - Config file reference
- **[Multi-Turn Workflow](/cli/workflows/multi-turn-workflow)** - Run dynamic conversations
- **[Runner Targets](/cli/configuration/runner-targets)** - Connect your code to simulations

---

Need help? Run `fluxloop --help` or check [GitHub Issues](https://github.com/chuckgu/fluxloop/issues).

