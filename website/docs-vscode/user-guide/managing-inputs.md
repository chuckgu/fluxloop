---
sidebar_position: 2
---

# Managing Inputs

FluxLoop manages inputs through the **Inputs** view in the VSCode extension. Inputs are the prompts and data your AI agent processes during experiments.

## Viewing Inputs

Open the **Inputs** view in the FluxLoop activity bar to see everything related to scenarios:

- **Configuration** – Settings and base input from `configs/input.yaml`
- **Generated Inputs** – Variations created via the wizard, annotated with strategy + persona

Clicking any entry opens the underlying YAML. The panel refreshes automatically whenever configuration files change.

## Configuration

The Configuration folder contains:

### Open Configuration
Click to open `configs/input.yaml` directly in the editor.

### Base Input
Shows the primary seed input (first entry in `base_inputs`) that drives generation:

```yaml
base_inputs:
  - input: "How can I track my order?"
    expected_intent: "order_tracking"
```

The base input is the foundation for all variation strategies. Only the first base input is displayed in the tree for simplicity.

## Generating Input Variations

Generate variations from base inputs using LLM or deterministic strategies.

### From Inputs View

1. Click **Generate New Inputs…**
2. Configure the wizard:
   - **Generation Mode** – Deterministic or LLM
   - **Base Input Confirmation** – Review the primary base input
     - Select **Use Input** to proceed
     - Select **Edit in configuration** to open `configs/input.yaml` and modify
   - **Strategies** – Pick one or more strategies (rephrase, verbose, concise, error_prone, etc.)
     - Pre-selected based on `variation_strategies` in `configs/input.yaml`
     - Your selections are saved back to `variation_strategies` for next time
   - **Variation Limit** – Number of outputs per base input
   - **Output File** – Defaults to `inputs/generated.yaml` (auto-populated from config)
   - **Overwrite / Append** – Control whether the existing file should be replaced
   - **Dry Run** – Preview results without writing files
   - **LLM Provider & API Key** – Prompt appears for LLM mode; the key can be saved to VS Code secret storage and appended to `.env` if you approve

Generated inputs immediately appear under **Generated Inputs** with metadata (strategy, persona, timestamp). Double-click any entry to open the YAML.

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
| `typo` | Add typos/errors | LLM |
| `persona_based` | Based on persona characteristics | LLM |
| `adversarial` | Edge cases and attacks | LLM |
| `multilingual` | Different languages | LLM |
| `custom` | Custom variation prompt | LLM |

Configure default strategies in `configs/input.yaml`:

```yaml
variation_strategies:
  - rephrase
  - verbose
```

These will be pre-selected in the wizard and updated when you make changes.

## Recordings (Advanced)

Recordings capture actual function arguments during runtime for replay in experiments.

### Enable Recording Mode

From the **Experiments** view, expand **Recording (Advanced)** and click:
- **Enable Recording** to turn on argument capture
- **Disable Recording** to turn it off

Or from terminal:

```bash
fluxloop record enable
fluxloop record disable
```

This updates:
- `.env`: Sets `FLUXLOOP_RECORD_ARGS=true/false`
- `configs/simulation.yaml`: Enables/disables `replay_args.enabled`

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

## Environment Considerations

Input generation and experiments depend on your Python environment.

### Ensure Correct Environment

Before generating inputs or running experiments:

1. Run `FluxLoop: Show Environment Info`
2. Confirm CLI, SDK, and MCP packages live inside the detected interpreter
3. Adjust with `FluxLoop: Select Environment` (Auto / Workspace / Global / Custom)
4. If you run commands with wrappers (`uv run`, `pipx run`), configure them once via `FluxLoop: Configure Execution Wrapper`

See [Environment Configuration](../getting-started/environment-configuration.md) for the full matrix.

## Next Steps

- [Running Experiments](running-experiments)
- [Viewing Results](viewing-results)
- [Recording Mode](recording-mode) (Advanced)
