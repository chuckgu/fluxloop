---
sidebar_position: 3
---

# Recording Commands

FluxLoop provides dedicated commands for toggling and inspecting recording mode. Recording captures actual function arguments at runtime so you can replay them during experiments with generated variations.

> Recording commands affect the `.env` file and `configs/simulation.yaml`. The Status view reflects the current state.

---

## FluxLoop: Enable Recording Mode

**Command ID:** `fluxloop.enableRecording`

### What It Does
- Sets `FLUXLOOP_RECORD_ARGS=true` in `.env`
- Enables `replay_args.enabled` in `configs/simulation.yaml`
- Creates `recordings/` folder if missing
- Updates Status view to **Record Mode: Enabled**

### Usage
- Command Palette → `FluxLoop: Enable Recording Mode`
- Equivalent CLI: `fluxloop record enable`

### When to Use
- Before running your application to capture real requests/responses
- When preparing high-fidelity replay datasets for experiments

---

## FluxLoop: Disable Recording Mode

**Command ID:** `fluxloop.disableRecording`

### What It Does
- Sets `FLUXLOOP_RECORD_ARGS=false` in `.env`
- Optionally prompts to disable `replay_args` (leave enabled if you still want to replay)
- Updates Status view to **Record Mode: Disabled**

### Usage
- Command Palette → `FluxLoop: Disable Recording Mode`
- Equivalent CLI: `fluxloop record disable`

Use this after you’ve collected enough recordings or want to prevent further capture in production.

---

## FluxLoop: Show Recording Status

**Command ID:** `fluxloop.showRecordingStatus`

Displays a modal summary of the current recording configuration:
- Enabled / disabled state
- Recording file path (e.g., `recordings/args_recording.jsonl`)
- Override parameter path configured in `configs/simulation.yaml`
- Last modified timestamp (if file exists)

### Usage
- Command Palette → `FluxLoop: Show Recording Status`
- Equivalent CLI: `fluxloop record status`

---

## Related Commands

- `FluxLoop: Run Experiment` – Honors `replay_args` settings when executing
- `FluxLoop: Manage Inputs` – Generate variations that get injected into recorded traces
- [Recording Mode user guide](../user-guide/recording-mode.md) – End-to-end workflow
