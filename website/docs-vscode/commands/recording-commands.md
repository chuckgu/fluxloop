---
sidebar_position: 3
---

# Recording Commands

FluxLoop provides dedicated commands for toggling recording mode. Recording captures actual function arguments at runtime so you can replay them during experiments with generated variations.

> Recording commands affect the `.env` file and `configs/simulation.yaml`. The Experiments view reflects the current state in the **Recording (Advanced)** section.

---

## FluxLoop: Enable Recording

**Command ID:** `fluxloop.enableRecording`

### What It Does
- Sets `FLUXLOOP_RECORD_ARGS=true` in `.env`
- Enables `replay_args.enabled` in `configs/simulation.yaml`
- Creates `recordings/` folder if missing

### Usage
- Experiments view → Recording (Advanced) → **Enable Recording**
- Command Palette → `FluxLoop: Enable Recording`
- Equivalent CLI: `fluxloop record enable`

### When to Use
- Before running your application to capture real requests/responses
- When preparing high-fidelity replay datasets for experiments

---

## FluxLoop: Disable Recording

**Command ID:** `fluxloop.disableRecording`

### What It Does
- Sets `FLUXLOOP_RECORD_ARGS=false` in `.env`
- Optionally prompts to disable `replay_args` (leave enabled if you still want to replay)

### Usage
- Experiments view → Recording (Advanced) → **Disable Recording**
- Command Palette → `FluxLoop: Disable Recording`
- Equivalent CLI: `fluxloop record disable`

Use this after you've collected enough recordings or want to prevent further capture in production.

---

## Viewing Recording Status

Recording status can be checked via:

### From Experiments View
Expand **Recording (Advanced)** to see:
- Recording control buttons (Enable/Disable)
- List of recording files from `recordings/` directory

### From Terminal
```bash
fluxloop record status
```

This displays:
- Enabled / disabled state
- Recording file path (e.g., `recordings/args_recording.jsonl`)
- Override parameter path configured in `configs/simulation.yaml`
- Last modified timestamp (if file exists)

---

## Related Commands

- `FluxLoop: Run Experiment` – Honors `replay_args` settings when executing
- `FluxLoop: Generate Inputs` – Generate variations that get injected into recorded traces
- [Recording Mode user guide](../user-guide/recording-mode.md) – End-to-end workflow
