---
sidebar_position: 2
---

# Managing Inputs

FluxLoop manages inputs through the **Inputs** view in the VSCode extension. Inputs are the prompts and data your AI agent processes during experiments.

## Viewing Inputs

The **Inputs** view shows:

- **Base Inputs**: Core inputs defined in `configs/input.yaml`
- **Generated Inputs**: Variations created by input generation
- **Recordings**: Captured argument traces for replay

Click any input to open its configuration file or navigate to the generated YAML.

## Base Inputs

Base inputs are defined in `configs/input.yaml`:

```yaml
base_inputs:
  - id: "customer_inquiry"
    content: "How can I track my order?"
    metadata:
      category: "support"
```

### Editing Base Inputs

1. Click any base input in the **Inputs** view
2. VSCode opens `configs/input.yaml`
3. Edit inputs directly
4. Save—the view refreshes automatically

Or use Command Palette:
```
FluxLoop: Open Input Configuration
```

## Generating Input Variations

Generate variations from base inputs using LLM or deterministic strategies.

### From Inputs View

1. Click **Generate New Inputs…** in the **Inputs** view
2. Follow the wizard:
   - **Mode**: Deterministic (rule-based) or LLM (requires API key)
   - **Strategies**: Select variation types (rephrase, verbose, error_prone, etc.)
   - **Limit**: Number of variations per base input
   - **Overwrite**: Replace existing generated inputs
   - **Dry Run**: Preview without writing files

Generated inputs appear under **Generated Inputs** in the Inputs view.

### From Command Palette

```
FluxLoop: Generate Inputs
```

### From Terminal

```bash
fluxloop generate inputs --mode llm --strategy rephrase --limit 5
```

## Input Strategies

Available variation strategies:

| Strategy | Description | Mode |
|----------|-------------|------|
| `rephrase` | Reword while preserving intent | LLM |
| `verbose` | Add detail and context | LLM |
| `concise` | Shorten to essential points | LLM |
| `error_prone` | Introduce typos or ambiguity | LLM |
| `edge_case` | Generate boundary scenarios | LLM |
| `shuffle_words` | Randomly reorder tokens | Deterministic |
| `remove_words` | Randomly drop tokens | Deterministic |

Configure default strategies in `configs/input.yaml`:

```yaml
strategies:
  - rephrase
  - verbose
```

## Recordings (Advanced)

Recordings capture actual function arguments during runtime for replay in experiments.

### Enable Recording Mode

```
FluxLoop: Enable Recording Mode
```

or

```bash
fluxloop record enable
```

This updates:
- `.env`: Sets `FLUXLOOP_RECORD_ARGS=true`
- `configs/simulation.yaml`: Enables `replay_args.enabled`

### Capture Arguments

1. Run your application normally
2. FluxLoop SDK captures arguments to `recordings/args_recording.jsonl`
3. Each entry includes function name, args, kwargs, timestamp

### Using Recorded Arguments in Experiments

Edit `configs/simulation.yaml`:

```yaml
replay_args:
  enabled: true
  recording_file: "recordings/args_recording.jsonl"
  override_param_path: "data.content"  # Path to inject generated input
```

Now when you run experiments, FluxLoop:
1. Loads recorded arguments
2. Replaces the field at `override_param_path` with generated input variations
3. Replays each modified call

### Disable Recording

```
FluxLoop: Disable Recording Mode
```

or

```bash
fluxloop record disable
```

## Environment Considerations

Input generation and experiments depend on your Python environment.

### Ensure Correct Environment

Before generating inputs or running experiments:

1. **Check environment:**
   ```
   FluxLoop: Show Environment Info
   ```

2. **Verify FluxLoop packages are installed:**
   - FluxLoop CLI detected
   - SDK available in Python path
   - Correct virtual environment active

3. **If using venv:**
   - Ensure FluxLoop is installed in `.venv`
   - Set execution mode to **Auto** or **Workspace only**

4. **If using global install:**
   - Use pipx for isolated CLI tools
   - Set execution mode to **Global PATH**

See [Environment Configuration](../getting-started/environment-configuration) for details.

## Next Steps

- [Running Experiments](running-experiments)
- [Viewing Results](viewing-results)
- [Recording Mode](recording-mode) (Advanced)

