---
sidebar_position: 3
---

# Experiments View

Manage and run experiments from a centralized view in the FluxLoop Activity Bar.

## Overview

The **Experiments** view provides quick access to your current experiment configuration, recording mode controls, and recent experiment runs. It serves as the main control panel for experiment execution.

## Tree Structure

```
Experiments
├─ Current Experiment (configs/simulation.yaml)
│  ├─ Open configuration
│  ├─ Runner: my_module.agent
│  ├─ Iterations: 10
│  └─ Record Mode: Disabled
├─ Run Experiment (action)
├─ Recording Mode
│  ├─ Enable Recording Mode
│  ├─ Disable Recording Mode
│  └─ Show Recording Status
├─ Experiments
│  └─ customer_support_test_20251104_143610
│     ├─ summary.json
│     ├─ traces.jsonl
│     ├─ observations.jsonl
│     ├─ errors.json
│     └─ logs.json
└─ Recordings
   └─ args_recording.jsonl
```

## Features

### Current Experiment

Displays configuration from `configs/simulation.yaml`:
- **Configuration file**: Click to open in editor
- **Runner**: Shows `module_path` and `function_name`
- **Iterations**: Current iteration count from config
- **Record Mode**: Shows if argument recording is enabled

If no simulation config exists, shows placeholder message.

### Run Experiment

Root-level action button (no need to expand folders):
1. Click to start experiment execution
2. Select environment (Local Python/Dev Container/Docker)
3. Optionally override iteration count
4. Runs in new terminal at project root

See [Running Experiments](../user-guide/running-experiments.md) for details.

### Recording Mode

Collapsible section with three actions:
- **Enable Recording Mode**: Turns on argument recording (updates `.env` and config)
- **Disable Recording Mode**: Turns off argument recording
- **Show Recording Status**: Displays current recording state in terminal

For complex agents (WebSocket handlers, callbacks), recording captures actual arguments for replay. See [Recording Mode Guide](../user-guide/recording-mode.md).

### Experiments Folder

Lists recent experiment runs (same as Results view):
- Grouped under **Experiments** for organization
- Shows up to 10 most recent runs
- Each displays timestamp and success rate
- Expand to see artifact files

### Recordings

Shows recorded argument files from `recordings/` directory:
- Lists up to 10 most recent `.jsonl` files
- Click to open recording file
- Used for argument replay during experiments

## Actions

### Run Experiment

Executes `fluxloop run experiment` with selected environment and optional iteration override.

### Open Configuration

Opens `configs/simulation.yaml` in editor for direct editing.

### Recording Controls

- **Enable**: Runs `fluxloop record enable` (or uses VSCode command)
- **Disable**: Runs `fluxloop record disable`
- **Status**: Runs `fluxloop record status`

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
