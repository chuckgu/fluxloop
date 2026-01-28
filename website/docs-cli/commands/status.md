---
sidebar_position: 7
---

# status Command

Check FluxLoop system and experiment status.

## Overview

The `status` command provides utilities for checking FluxLoop installation status, configuration validity, and reviewing recent experiments. It's useful for quick health checks and browsing experiment history.

## Subcommands

### check

Verify FluxLoop system status and configuration.

```bash
# Quick status check
fluxloop status check

# Detailed status with verbose output
fluxloop status check --verbose

# Check specific project
fluxloop status check --project my-agent
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--verbose`, `-v` | Show detailed information | `false` |
| `--project` | Project name under FluxLoop root | Current directory |
| `--root` | FluxLoop root directory | `./fluxloop` |

**What Gets Checked:**

1. **SDK Installation**: Verifies FluxLoop SDK is installed and shows version
2. **Collector Connectivity**: Attempts to connect to collector service
3. **Configuration Files**: Checks for required config files in `configs/`
4. **Environment Variables**: Verifies API keys and settings

**Example Output:**

```
FluxLoop Status Check

╭──────────────────────────────────────────────────────────╮
│ Component  │ Status            │ Details                 │
│ SDK        │ ✓ Installed       │ Version 0.1.6           │
│ Collector  │ ? Unknown         │ URL: http://...         │
│ Config     │ ✓ Found           │ /path/to/configs        │
│ API Key    │ ✓ Set             │ Configured              │
╰──────────────────────────────────────────────────────────╯

Recommendations:
  • Set up API key in .env file
```

**Status Indicators:**

| Symbol | Meaning |
|--------|---------|
| ✓ | Component working correctly |
| ✗ | Component has errors |
| - | Component not configured |
| ? | Status unknown/uncertain |

**Common Issues:**

| Issue | Details | Recommendation |
|-------|---------|----------------|
| SDK not installed | FluxLoop SDK missing | `pip install fluxloop` |
| Config incomplete | Missing config files | `fluxloop init scenario` |
| API key not set | No `FLUXLOOP_API_KEY` | Set in `.env` file |
| Collector error | Cannot connect | Check collector URL |

---

### experiments

List recent experiments and their results.

```bash
# List recent experiments (default: 10 most recent)
fluxloop status experiments

# Show more experiments
fluxloop status experiments --limit 20

# Check specific output directory
fluxloop status experiments --output ./my-experiments

# Check for specific project
fluxloop status experiments --project production-agent
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--output`, `-o` | Directory containing experiment results | `./experiments` |
| `--project` | Project name | Current |
| `--root` | FluxLoop root directory | `./fluxloop` |
| `--limit`, `-l` | Number of experiments to show | `10` |

**Example Output:**

```
Recent Experiments (showing 3 of 15)

╭─ exp_20250117_143022 ───────────────────────────────╮
│ Name: my_agent_experiment                            │
│ Date: 2025-01-17 14:30:22                           │
│ Runs: 50                                            │
│ Success Rate: 94.0%                                  │
│ Avg Duration: 234ms                                  │
╰──────────────────────────────────────────────────────╯

╭─ exp_20250117_120015 ───────────────────────────────╮
│ Name: my_agent_experiment                            │
│ Date: 2025-01-17 12:00:15                           │
│ Runs: 100                                           │
│ Success Rate: 89.0%                                  │
│ Avg Duration: 312ms                                  │
╰──────────────────────────────────────────────────────╯

📁 exp_20250116_093045 (no summary available)
```

**Experiment Information:**

For each experiment with a `summary.json` file, displays:
- **Name**: Experiment name from configuration
- **Date**: Timestamp when experiment ran
- **Runs**: Total number of test runs executed
- **Success Rate**: Percentage of successful completions
- **Avg Duration**: Average execution time in milliseconds

**When No Experiments Found:**

```
No experiments found in: ./experiments

Run an experiment first: fluxloop test
```

---

### traces

List recent traces from experiments.

```bash
# View recent traces (requires collector service)
fluxloop status traces

# View traces for specific experiment
fluxloop status traces my_experiment_id

# Limit number of traces shown
fluxloop status traces --limit 20
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `experiment_id` | Optional experiment ID to filter traces |

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--limit`, `-l` | Number of traces to show | `10` |

**Note:**

This feature requires a running collector service. When the collector is not available:

```
Trace viewing requires collector service

This feature will be available when the collector is running.
For now, check the experiment output directories for trace data.
```

**Alternative: View Traces Locally**

Until the collector service is running, view traces in experiment directories:

```bash
# List trace files
ls results/exp_*/artifacts/

# View trace summary
cat results/exp_*/summary.json | jq

# View individual traces
cat results/exp_*/artifacts/traces.jsonl | head -n 5
```

---

## Common Workflows

### Pre-Experiment Health Check

Before running experiments, verify everything is configured:

```bash
# Quick status check
fluxloop status check

# Verify configuration
fluxloop config validate
```

### Post-Experiment Review

After running experiments, review results:

```bash
# List recent experiments
fluxloop status experiments --limit 5

# View latest experiment results
cat results/latest_run_*/summary.json
```

### Monitoring Experiment History

Track experiment performance over time:

```bash
# List all recent experiments
fluxloop status experiments --limit 20

# Check specific project's experiments
fluxloop status experiments --project production-agent

# Compare with specific output directory
fluxloop status experiments --output ./archived-experiments
```

### Troubleshooting Setup Issues

When things aren't working, use status commands to diagnose:

```bash
# 1. Check system status
fluxloop status check --verbose

# 2. Verify environment
fluxloop config env

# 3. Validate configuration
fluxloop config validate
```

---

## Output Interpretation

### SDK Status

| Status | Meaning | Action |
|--------|---------|--------|
| ✓ Installed | SDK found and loaded | None needed |
| ✗ Not installed | SDK missing | `pip install fluxloop` |

### Config Status

| Status | Meaning | Action |
|--------|---------|--------|
| ✓ Found | All required configs present | None needed |
| - Incomplete | Missing config files | `fluxloop init scenario` |
| ✗ Invalid | Config syntax errors | Fix YAML syntax |

### API Key Status

| Status | Meaning | Action |
|--------|---------|--------|
| ✓ Set | API key configured | None needed |
| - Not set | No API key found | Set in `.env` file |

---

## Tips

### Quick Status Alias

Create a shell alias for faster checks:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias fls='fluxloop status check'
alias fle='fluxloop status experiments'
```

Usage:
```bash
fls         # Quick status check
fle -l 20   # List 20 recent experiments
```

### Automated Health Checks

Add status checks to scripts:

```bash
#!/bin/bash
# run_experiment.sh

# Verify system ready
if ! fluxloop status check --verbose; then
    echo "System not ready!"
    exit 1
fi

# Run experiment
fluxloop test

# Show results
fluxloop status experiments --limit 1
```

### Monitoring Multiple Projects

Check status across different projects:

```bash
for project in agent-v1 agent-v2 agent-v3; do
    echo "=== $project ==="
    fluxloop status check --project $project
    echo
done
```

---

## Exit Codes

All `status` subcommands follow consistent exit code patterns:

| Exit Code | Meaning |
|-----------|---------|
| 0 | Status check completed (doesn't mean all checks passed) |
| 1 | Invalid arguments or runtime error |

**Note:** `status check` exits with 0 even if some components have issues. Check the output to see actual component status.

---

## See Also

- [config Command](/cli/commands/config) - Configuration management
- [run Command](/cli/commands/test) - Execute experiments
