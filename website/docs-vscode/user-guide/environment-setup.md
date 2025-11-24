---
sidebar_position: 6
---

# Environment Setup

FluxLoop automatically detects and uses your project’s Python environment so experiments, CLI commands, and the Integration Assistant run inside the correct interpreter.

> **Python Requirements**  
> • FluxLoop CLI → Python 3.8+  
> • FluxLoop SDK & MCP → Python 3.11+ (required for Flux Agent)

## Quick Setup

1. **Create / activate a venv**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
2. **Install FluxLoop packages**
   ```bash
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```
3. **Select execution mode**
   - Command Palette → `FluxLoop: Select Environment`
   - Choose **Auto (detect project environment)** or **Workspace only**
   - If dependencies are missing the wizard offers automatic install or manual instructions
4. **Verify detection**
   - Command Palette → `FluxLoop: Show Environment Info`
   - Confirm Python/fluxloop/fluxloop-mcp paths point to `.venv`
   - View → Output → **FluxLoop** for detailed logs
5. **Set Target Source Root…**
   - Projects view → **Target Source Root…**
   - Select the directory containing your actual agent code (Flux Agent uses this for analysis)

FluxLoop now uses this environment for experiments, CLI commands, and Integration Assistant runs.

## Automated Setup Script

For faster onboarding run:

```bash
cd your-project
bash packages/cli/scripts/setup_fluxloop_env.sh \
  --python python3.11 \
  --target-source-root ./src
```

The script:
- Creates `.venv` (if needed)
- Installs CLI, SDK, MCP
- Writes `.vscode/settings.json` with `fluxloop.executionMode`, `fluxloop.targetSourceRoot`, `fluxloop.projectRoot`
- Updates `configs/project.yaml → source_root`
- Runs `fluxloop doctor`

The VS Code project wizard exposes this as **Run Setup Script**.

## Execution Modes

Choose how FluxLoop locates executables:

| Mode | Description | Use When |
|------|-------------|----------|
| **Auto** (default) | Detect `.venv`, Poetry, Conda, uv; fallback to PATH | General use |
| **Workspace only** | Require a project-local venv; fail otherwise | Teams enforcing per-project envs |
| **Global PATH** | Always use global executables (pipx, Homebrew) | Quick prototyping |
| **Custom executables** | Manually specify Python + `fluxloop-mcp` paths | Complex Conda/pyenv setups |

Set via:
- Command Palette → `FluxLoop: Select Environment`
- Integration view → System Status → **Select Environment**
- `.vscode/settings.json`:
  ```json
  {
    "fluxloop.executionMode": "auto",
    "fluxloop.pythonPath": "/custom/python",
    "fluxloop.mcpCommandPath": "/custom/fluxloop-mcp"
  }
  ```

## Target Source Root

Defines where FluxLoop searches for envs and source files (also used by Flux Agent).

**Projects view workflow**
1. Expand your project
2. Click **Target Source Root…**
3. Choose a folder (relative paths stored automatically)
4. FluxLoop refreshes detection and logs the results

**Manual configuration**
```yaml
# configs/project.yaml
source_root: "./backend"
```

## Monitoring Environment Status

### Show Environment Info
`FluxLoop: Show Environment Info` → quick modal with:
- Source root
- Execution mode
- Python/fluxloop/fluxloop-mcp paths
- Detection notes (missing packages, etc.)

### Output Channel
View → Output → select **FluxLoop**. Every refresh prints:
```
[FluxLoop Env] Source root: /Users/me/src/app
[FluxLoop Env] Environment: venv
[FluxLoop Env] Python: .../.venv/bin/python
[FluxLoop Env] fluxloop: .../.venv/bin/fluxloop
[FluxLoop Env] fluxloop-mcp: .../.venv/bin/fluxloop-mcp
[FluxLoop Env] Notes:
[FluxLoop Env]  • fluxloop-mcp not found; install fluxloop-mcp in this environment.
```

### Doctor

Run comprehensive diagnostics:
- Command Palette → `FluxLoop: Run Doctor`
- Integration view → System Status → **Run Doctor**
- Terminal → `fluxloop doctor [--json]`

Doctor checks Python, venv, CLI, SDK, MCP, knowledge index, and config structure.

## Common Scenarios

### uv
1. `uv venv && source .venv/bin/activate`
2. `uv pip install fluxloop-cli fluxloop fluxloop-mcp`
3. (Optional) `FluxLoop: Configure Execution Wrapper → uv run`

### pipx
1. `pipx install fluxloop-cli` / `pipx install fluxloop-mcp`
2. Install `fluxloop` SDK in your project venv
3. Set execution mode to **Global PATH**

### Conda
1. `conda create -n agent python=3.11`
2. `conda activate agent`
3. `pip install fluxloop-cli fluxloop fluxloop-mcp`
4. If VS Code doesn’t detect it automatically, use **Custom executables** and point to `/opt/conda/envs/agent/bin/python`

### Multiple Projects
- Each project stores its own execution mode, target source root, wrapper, etc.
- Switching projects triggers a fresh detection using the cached settings.

## Troubleshooting

### “Environment not detected”
1. Run `FluxLoop: Show Environment Info`
2. Check FluxLoop Output for errors
3. Run `FluxLoop: Run Doctor`
4. Ensure the selected interpreter actually contains `fluxloop` and `fluxloop-mcp`:
   ```bash
   source .venv/bin/activate
   which fluxloop
   which fluxloop-mcp
   ```

### “Commands use global Python instead of venv”
1. Ensure `.venv` exists under your target source root
2. Set execution mode to **Auto** or **Workspace only**
3. Confirm `fluxloop.targetSourceRoot` points at the folder containing `.venv`

### “Flux Agent says MCP missing”
1. Verify MCP installed in active env
2. Check doctor output for index path
3. Rebuild index: `packages/mcp/scripts/rebuild_index.sh`
4. Confirm `fluxloop.mcpCommandPath` isn’t pointing to an old installation

### “Wrong project analyzed”
- Run **Target Source Root…** again and choose the correct folder
- Ensure `configs/project.yaml → source_root` matches your selection
- Integration view displays the currently active source root in System Status

## Next Steps

- [Creating Projects](./creating-projects.md)
- [Managing Inputs](./managing-inputs.md)
- [Integration Assistant Overview](../integration-assistant/overview.md)

