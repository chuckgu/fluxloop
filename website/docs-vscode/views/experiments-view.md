---
sidebar_position: 3
---

# Experiments View

Manage and run experiments from a centralized view in the FluxLoop Activity Bar.

## Overview

The **Experiments** view provides quick access to your current experiment configuration, recording controls, and recent experiment runs. It serves as the main control panel for experiment execution.

## Tree Structure

```
Experiments
├─ Configuration (configs/simulation.yaml)
│  ├─ Open configuration
│  ├─ Runner: my_module.agent
│  └─ Iterations: 10
├─ Run Experiment (action)
├─ Experiments
│  └─ customer_support_test_20251104_143610
│     ├─ summary.json
│     ├─ traces.jsonl
│     ├─ trace_summary.jsonl
│     ├─ observations.jsonl
│     ├─ errors.json
│     └─ logs.json
└─ Recording (Advanced)
   ├─ Enable Recording
   ├─ Disable Recording
   └─ (recordings/*.jsonl files)
```

## Features

### Configuration

Displays configuration from `configs/simulation.yaml`:
- **Open configuration**: Click to open in editor
- **Runner**: Shows `module_path` and `function_name`
- **Iterations**: Current iteration count from config

If no simulation config exists, shows placeholder message.

### Run Experiment

Root-level action button (no need to expand folders):
1. Click to start experiment execution
2. Select environment (Local Python/Dev Container/Docker)
3. Optionally override iteration count
4. Runs in new terminal at project root

See [Running Experiments](../user-guide/running-experiments.md) for details.

### Recording (Advanced)

Collapsible section for argument recording controls:
- **Enable Recording**: Turns on argument recording (updates `.env` and config)
- **Disable Recording**: Turns off argument recording

Below the controls, any existing recording files from `recordings/` are listed.

For complex agents (WebSocket handlers, callbacks), recording captures actual arguments for replay. See [Recording Mode Guide](../user-guide/recording-mode.md).

### Experiments Folder

Lists recent experiment runs (same as Results view):
- Grouped under **Experiments** for organization
- Shows up to 10 most recent runs
- Each displays timestamp and success rate
- Expand to see artifact files including `trace_summary.jsonl`

## Actions

### Run Experiment

Executes `fluxloop run experiment` with selected environment and optional iteration override.

### Open Configuration

Opens `configs/simulation.yaml` in editor for direct editing.

### Recording Controls

- **Enable Recording**: Runs `fluxloop record enable` (or uses VSCode command)
- **Disable Recording**: Runs `fluxloop record disable`

## File Watchers

The Experiments view automatically refreshes when:
- `configs/simulation.yaml` is modified
- `.env` file changes (affects recording status)
- New experiments complete in `experiments/`
- Recording files are added to `recordings/`

## Tips

- **Quick Run**: `Run Experiment` is always visible at root level for fast access
- **Config Editing**: Click `Open configuration` to directly edit simulation settings
- **Recording Toggle**: Enable/disable recording without manual config editing
- **Experiment History**: Recent runs appear here; full history in Results view

## Related

- [Running Experiments User Guide](../user-guide/running-experiments.md) - Detailed execution workflow
- [Recording Mode](../user-guide/recording-mode.md) - Argument replay setup
- [Results View](./results-view.md) - Viewing and parsing outputs
