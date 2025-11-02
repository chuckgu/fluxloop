---
sidebar_position: 5
---

# record Command

Toggle FluxLoop argument recording across `.env` and `configs/simulation.yaml`.

## Summary

```bash
fluxloop record enable    # turn on recording
fluxloop record disable   # turn it off
fluxloop record status    # show current state
```

When you run `enable`/`disable`, the CLI updates:

- Project `.env` → `FLUXLOOP_RECORD_ARGS`, `FLUXLOOP_RECORDING_FILE`
- `configs/simulation.yaml` → `replay_args.enabled`, `replay_args.recording_file`

Agents that call `fluxloop.load_env()` + `fluxloop.configure()` on startup should read these environment variables so that CLI toggles take effect.

## Commands

### `fluxloop record enable`

- Ensures the `recordings/` directory exists
- Writes/updates `.env` with `FLUXLOOP_RECORD_ARGS=true`
- Sets `replay_args.enabled: true` and `recording_file` in `configs/simulation.yaml`
- Prints the resolved recording path

### `fluxloop record disable`

- Sets `FLUXLOOP_RECORD_ARGS=false`
- Sets `replay_args.enabled: false` in `configs/simulation.yaml`
- Leaves the last `recording_file` path intact for future use

### `fluxloop record status`

- Reads the effective state from `.env` and `configs/simulation.yaml`
- Warns if code is not configured to honor the environment values

## Best Practices

- At service startup load your project `.env` (or pass the resolved values into `fluxloop.configure`).
- Configure the SDK using environment values instead of hard-coding `record_args=True`, e.g.:

```python
import os
from pathlib import Path
import fluxloop

project_root = Path(__file__).resolve().parents[2]
fluxloop.load_env(project_root / ".env")        # ensures CLI toggles are visible

record_on = os.getenv("FLUXLOOP_RECORD_ARGS", "false").lower() == "true"
record_file = os.getenv("FLUXLOOP_RECORDING_FILE")

fluxloop.configure(
    debug=True,
    record_args=record_on,
    recording_file=record_file,
)
```
- Verify the CLI output after `fluxloop record enable`—it should show the absolute path.
- During local development you can still override the path manually via `.env`.

## Troubleshooting

- **No `.jsonl` file appears** → Ensure the process read `.env` and configure was called before `fluxloop.record_call_args`.
- **File created in unexpected directory** → Use an absolute path or ensure the service CWD is the project root.
- **Recording stays on** → Remove hard-coded `record_args=True`; rely on environment toggles.
