---
sidebar_position: 3
---

# Running Experiments

Execute experiments directly from VS Code using the Experiments view or Command Palette.

## Prerequisites

Before running experiments:
1. Create a FluxLoop project (see [Creating Projects](./creating-projects.md))
2. Configure `configs/simulation.yaml` with your runner settings
3. (Optional) Generate inputs via [Managing Inputs](./managing-inputs.md)

## Running from Experiments View

### Quick Start

1. Open the **Experiments** view from the FluxLoop Activity Bar
2. Click **Run Experiment** (located next to **Current Experiment**)
3. Select execution environment:
   - **Local Python**: Uses your current Python environment
   - **Dev Container**: Runs inside active Dev Container (if running in one)
   - **Docker**: Coming soon
4. (Optional) Enter custom iteration count or press Enter to use config default
5. Experiment runs in a new terminal at your project root

### Experiment Configuration

Click **Current Experiment → Open configuration** to view/edit `configs/simulation.yaml`:

```yaml
runner:
  module_path: "my_module.agent"
  function_name: "run"

iterations: 10

replay_args:
  enabled: false
  recording_file: "recordings/args_recording.jsonl"
```

See [CLI Runner Configuration](../../cli/configuration/runner-targets.md) for advanced runner patterns.

## Running from Command Palette

Alternative method:
1. Open Command Palette (`Cmd+Shift+P`)
2. Type and select **FluxLoop: Run Experiment**
3. Follow the same prompts as above

## Execution Environments

### Local Python

- **Use when**: Running on your local machine with direct Python access
- **Requirements**: FluxLoop CLI and SDK installed in current environment
- **Runs**: `fluxloop run experiment` in project root
- **Wrapper Support**: Configure via `FluxLoop: Configure Execution Wrapper` if using `uv`, `pipx`, etc.

### Dev Container

- **Use when**: VS Code is running inside a Dev Container
- **Requirements**: CLI/SDK installed in container, `REMOTE_CONTAINERS` env var present
- **Runs**: Same as Local Python, but within container context

### Docker (Coming Soon)

Currently shows informational message. Future support will enable running experiments in isolated Docker containers.

## Execution Wrapper (uv, pipx, etc.)

If you use a wrapper to run Python commands:

1. Open Command Palette
2. Select **FluxLoop: Configure Execution Wrapper**
3. Enter prefix (e.g., `uv run`)
4. All CLI commands will now be prefixed automatically

**Example**: With `uv run` configured, `fluxloop run experiment` becomes `uv run fluxloop run experiment`.

This setting is saved to `.vscode/settings.json`:
```json
{
  "fluxloop.executionWrapper": "uv run"
}
```

## Customizing Iterations

Override the iteration count from `configs/simulation.yaml`:
- Enter a number when prompted during experiment execution
- Leave empty to use config default
- The override only applies to the current run

## Monitoring Progress

### Terminal Output

The extension creates a new terminal named **FluxLoop** showing:
- Command being executed
- Working directory
- Real-time experiment progress
- Iteration results
- Final summary

### Results View

After completion, experiment outputs appear in the **Results** view:
- Navigate to **Results → Experiments**
- Find your experiment by timestamp
- Expand to see artifacts (`summary.json`, `traces.jsonl`, etc.)

## Tips

- **Quick Access**: Run Experiment is always visible at root level (no need to expand folders)
- **Default Environment**: Set preferred environment via `FluxLoop: Select Execution Environment`
- **Wrapper Setup**: Configure execution wrapper once; applies to all future runs
- **Iteration Override**: Useful for quick tests—override to 1 or 2 iterations without editing config

## Troubleshooting

### "FluxLoop CLI is required to run this command"

Install CLI in your environment:
```bash
pip install fluxloop-cli
# Or with uv:
uv pip install fluxloop-cli
```

### "Dev Container execution requires running inside a Dev Container"

The Dev Container option is only available when VS Code is actually running in a container. Use Local Python instead.

### "Docker execution from VSCode is not yet implemented"

Docker support is planned. Use Local Python or Dev Container for now.

## Next Steps

- [Viewing Results](./viewing-results.md) - Analyze experiment outputs
- [Recording Mode](./recording-mode.md) - Replay complex arguments
- [Workflow Commands](../commands/workflow-commands.md) - All available commands
