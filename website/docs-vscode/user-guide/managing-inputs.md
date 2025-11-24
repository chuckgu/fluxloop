---
sidebar_position: 2
---

# Managing Inputs

FluxLoop manages inputs through the **Inputs** view in the VSCode extension. Inputs are the prompts and data your AI agent processes during experiments.

## Viewing Inputs

Open the **Inputs** view in the FluxLoop activity bar to see everything related to scenarios:

- **Base Inputs** – Personas + prompts from `configs/input.yaml`
- **Generated Inputs** – Variations created via the wizard, annotated with strategy + persona
- **Recordings** – Argument captures saved to `recordings/*.jsonl`

Clicking any entry opens the underlying YAML/JSONL. The panel refreshes automatically whenever configuration files change.

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

1. Click **Generate New Inputs…**
2. Configure the wizard:
   - **Generation Mode** – Deterministic or LLM
   - **Strategies** – Pick one or more strategies (rephrase, verbose, concise, error_prone, persona_mix, multilingual, etc.)
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

1. Run `FluxLoop: Show Environment Info`
2. Confirm CLI, SDK, and MCP packages live inside the detected interpreter
3. Adjust with `FluxLoop: Select Environment` (Auto / Workspace / Global / Custom)
4. If you run commands with wrappers (`uv run`, `pipx run`), configure them once via `FluxLoop: Configure Execution Wrapper`

See [Environment Configuration](../getting-started/environment-configuration.md) for the full matrix.

## Next Steps

- [Running Experiments](running-experiments)
- [Viewing Results](viewing-results)
- [Recording Mode](recording-mode) (Advanced)

