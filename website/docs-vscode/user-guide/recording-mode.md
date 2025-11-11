---
sidebar_position: 5
---

# Recording Mode

Recording mode captures actual function arguments during runtime so you can replay them in experiments with generated input variations.

## When to Use Recording

Use recording mode when:

- Your agent function has complex signatures (WebSocket handlers, callbacks)
- You want to replay real production scenarios
- Testing requires specific argument combinations
- Base inputs alone don't capture the full context

## Enabling Recording

### From VSCode

```
FluxLoop: Enable Recording Mode
```

### From Terminal

```bash
fluxloop record enable
```

This automatically:
- Sets `FLUXLOOP_RECORD_ARGS=true` in `.env`
- Enables `replay_args.enabled` in `configs/simulation.yaml`
- Updates Status panel to show "Record Mode: Enabled"

## Capturing Arguments

1. **Ensure recording is enabled** (check Status panel)

2. **Run your application** as you normally would

3. **FluxLoop SDK captures arguments** to `recordings/args_recording.jsonl`

Each line in the recording file contains:
```json
{
  "function": "handle_request",
  "args": [],
  "kwargs": {"user_id": "123", "message": "Hello"},
  "timestamp": "2025-11-11T10:30:00Z"
}
```

## Configuring Replay

Edit `configs/simulation.yaml` to use recordings:

```yaml
replay_args:
  enabled: true
  recording_file: "recordings/args_recording.jsonl"
  override_param_path: "kwargs.message"  # Where to inject generated inputs
```

### override_param_path

Specifies which field in the recorded arguments should be replaced with generated input variations:

- `"kwargs.message"` – Replace `kwargs["message"]`
- `"args.0"` – Replace first positional argument
- `"data.content"` – Replace nested field `kwargs["data"]["content"]`

## Running Experiments with Replay

Once configured, run experiments normally:

```
FluxLoop: Run Experiment
```

FluxLoop will:
1. Load recordings from `recordings/args_recording.jsonl`
2. For each recording, create variations by replacing `override_param_path` with generated inputs
3. Execute your agent function with the modified arguments
4. Collect traces and results

## Viewing Recording Status

### From Status Panel

The **Status** view shows:
- **Record Mode**: Enabled/Disabled
- **Recording File**: Path to current recording file

### From Command Palette

```
FluxLoop: Show Recording Status
```

### From Terminal

```bash
fluxloop record status
```

## Disabling Recording

### From VSCode

```
FluxLoop: Disable Recording Mode
```

### From Terminal

```bash
fluxloop record disable
```

This:
- Sets `FLUXLOOP_RECORD_ARGS=false` in `.env`
- Optionally disables `replay_args` in simulation config
- Updates Status panel

## Environment Considerations

Recording and replay use the same Python environment as experiments.

### Ensure Packages Are Available

1. **Check environment:**
   ```
   FluxLoop: Show Environment Info
   ```

2. **Ensure SDK is installed:**
   ```bash
   source .venv/bin/activate
   pip install fluxloop
   ```

3. **Verify with Doctor:**
   ```
   FluxLoop: Run Doctor
   ```

### Using Different Environments

If you recorded arguments in one environment but want to replay in another:

1. Ensure both environments have compatible SDK versions
2. Recording file paths are relative to project root
3. Check that `override_param_path` matches your agent's signature in both environments

## Example Workflow

1. **Enable recording:**
   ```bash
   fluxloop record enable
   ```

2. **Run your app and capture arguments:**
   ```bash
   python app/main.py
   # Interact with your agent to generate diverse argument patterns
   ```

3. **Check recordings:**
   ```bash
   cat recordings/args_recording.jsonl
   ```

4. **Configure replay** in `configs/simulation.yaml`:
   ```yaml
   replay_args:
     enabled: true
     recording_file: "recordings/args_recording.jsonl"
     override_param_path: "kwargs.prompt"
   ```

5. **Generate inputs:**
   ```
   FluxLoop: Generate Inputs
   ```

6. **Run experiment:**
   ```
   FluxLoop: Run Experiment
   ```

7. **Disable recording** when done:
   ```bash
   fluxloop record disable
   ```

## Troubleshooting

### Arguments Not Being Recorded

1. Verify `.env` contains `FLUXLOOP_RECORD_ARGS=true`
2. Check that FluxLoop SDK is imported in your code
3. Ensure the target function is decorated with `@fluxloop.trace()`
4. Review application logs for SDK initialization messages

### Replay Fails During Experiment

1. **Check `override_param_path`** matches your function signature
2. **Verify recording file exists:**
   ```bash
   ls recordings/args_recording.jsonl
   ```

3. **Inspect recording format:**
   ```bash
   head -1 recordings/args_recording.jsonl | python -m json.tool
   ```

4. **Run with verbose logging:**
   ```bash
   fluxloop run experiment --verbose
   ```

### Wrong Arguments Replayed

1. Ensure `override_param_path` points to the correct field
2. Check that recordings match your current agent signature
3. Clear old recordings if agent signature changed:
   ```bash
   rm recordings/args_recording.jsonl
   fluxloop record enable
   # Re-record with updated signature
   ```

## Next Steps

- [Running Experiments](running-experiments)
- [Viewing Results](viewing-results)
- [Troubleshooting](../troubleshooting)
