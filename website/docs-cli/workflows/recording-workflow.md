---
sidebar_position: 2
---

# Recording Workflow

Capture real-world arguments from running services and replay them inside FluxLoop experiments.

## 1. Prerequisites

- FluxLoop project initialized (`configs/` + `.env`)
- Application code uses `fluxloop.record_call_args(...)` at the points you want to capture
- Startup code calls `fluxloop.load_env(...)` and `fluxloop.configure(...)` to read recording environment variables (see [record command](../commands/record))

## 2. Enable Recording

```bash
fluxloop record enable
```

This toggles `.env` and `configs/simulation.yaml` to point at `recordings/args_recording.jsonl` (or your custom path). The CLI prints the resolved absolute path.

## 3. Restart / Run Your Service

Ensure the service reloads configuration so the SDK sees `FLUXLOOP_RECORD_ARGS=true`.

Optional sanity check in code:

```python
from pathlib import Path
fluxloop.load_env(Path(__file__).resolve().parents[2] / ".env")
config = fluxloop.get_config()
print("Recording?", config.record_args, config.recording_file)
```

## 4. Exercise Real Traffic

- Interact with your application (web UI, API calls, etc.)
- Each call to `fluxloop.record_call_args` appends a JSONL entry with the kwargs
- Sensitive keys are automatically masked (token/key/secret…)

## 5. Verify Output

```bash
tail -f recordings/args_recording.jsonl
```

You should see `_version`, `target`, `kwargs`, and `timestamp` fields. If the file is empty, confirm the service imported `.env` before configure.

## 6. Disable Recording

```bash
fluxloop record disable
```

Records stop appending, but the last file path remains for re-use. Keep the file under version control ignore rules.

## 7. Configure Replay for Experiments

Edit `configs/simulation.yaml` to enable `replay_args`:

```yaml
runner:
  target: "app.main:support_server.respond"
  stream_output_path: "message.delta"

replay_args:
  enabled: true
  recording_file: recordings/args_recording.jsonl
  override_param_path: "item.content.0.text"   # optional override of the user message
```

During experiments the CLI will:

1. Load recorded kwargs
2. Inject the runtime input at `override_param_path`
3. Restore callable placeholders (collector callbacks)
4. Execute your real code with the recorded structure

## 8. Run Experiment

```bash
fluxloop generate inputs --limit 10   # optional refresher
fluxloop run experiment
```

Each generated input is replayed against the recorded argument skeleton, producing reproducible artifacts.

## Tips

- Keep separate recording files per scenario (`recordings/login.jsonl`, `recordings/support.jsonl`, …)
- Use versioned naming (e.g., `args_2024-11-02.jsonl`) for audit trails
- If recordings are large, prune or sample before committing
- Coordinate with CI/CD: disable recording in automated environments (`FLUXLOOP_RECORD_ARGS=false`)
