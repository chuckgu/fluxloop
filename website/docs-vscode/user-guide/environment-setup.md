---
sidebar_position: 6
---

# Environment Setup

FluxLoop VSCode extension automatically detects and uses your project's Python environment (venv, conda, uv, etc.) for all operations. This ensures experiments run with the correct dependencies and FluxLoop tools are executed in the right context.

## Automatic Detection

When you open a FluxLoop project or set a target source root, the extension scans for:

- `.venv/` (Python venv or uv)
- `venv/`, `env/` (alternative venv locations)
- `.conda/` (Conda environments)
- Global PATH executables (fallback)

Detected paths appear in the **FluxLoop Output** channel:

```
[FluxLoop Env] ----------------------------------------
[FluxLoop Env] Source root: /path/to/your/project
[FluxLoop Env] Environment type: venv
[FluxLoop Env] Python: /path/to/project/.venv/bin/python
[FluxLoop Env] fluxloop: /path/to/project/.venv/bin/fluxloop
[FluxLoop Env] fluxloop-mcp: /path/to/project/.venv/bin/fluxloop-mcp
[FluxLoop Env] ----------------------------------------
```

## Configuring Execution Mode

### Via Command Palette

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run `FluxLoop: Select Environment`
3. Choose an execution mode:
   - **Auto (recommended)**: Detect project environment, fallback to global
   - **Workspace only**: Require virtual environment in project
   - **Global PATH**: Always use globally installed executables
   - **Custom executables**: Manually specify Python and fluxloop-mcp paths

### Via Integration View

1. Open the **FluxLoop** Activity Bar
2. Navigate to **Integration** → **System Status**
3. Click **Select Environment**
4. Choose your preferred execution mode

### Via Settings File

Add to `.vscode/settings.json` in your workspace:

```json
{
  "fluxloop.executionMode": "auto",
  "fluxloop.pythonPath": "/custom/path/to/python",
  "fluxloop.mcpCommandPath": "/custom/path/to/fluxloop-mcp"
}
```

## Setting Target Source Root

The target source root defines where FluxLoop searches for virtual environments and project files.

### From Projects View

1. Expand your project in the **Projects** view
2. Click **Target Source Root…**
3. Choose **Choose Folder…** and select the directory
4. FluxLoop will:
   - Refresh environment detection
   - Show detected executables
   - Prompt to adjust environment settings if needed

### Via Configuration File

Edit `configs/project.yaml`:

```yaml
source_root: "./backend"  # Relative to project root
# or
source_root: "/absolute/path/to/source"
```

After editing, the extension automatically refreshes and re-detects the environment.

## Checking Environment Status

### FluxLoop Output Channel

View → Output → Select **FluxLoop** from the dropdown.

Every time the environment is refreshed, detailed logs appear showing:
- Source root path
- Environment type (venv, conda, global, etc.)
- Python executable path
- fluxloop CLI path
- fluxloop-mcp path
- Any warnings or notes

### Show Environment Info Command

Run `FluxLoop: Show Environment Info` for a quick modal summary of the current environment.

### Run Doctor Command

For comprehensive diagnostics, run:

**From Command Palette:**
```
FluxLoop: Run Doctor
```

**From Integration View:**
1. Open **Integration** → **System Status**
2. Click **Run Doctor**

**From Terminal:**
```bash
fluxloop doctor
```

Doctor output includes:
- Python version and path
- Virtual environment status
- FluxLoop CLI version and location
- FluxLoop MCP availability
- MCP index status
- Project configuration state

Use `--json` flag for machine-readable output:
```bash
fluxloop doctor --json
```

## Common Scenarios

### Using uv

If you manage your project with `uv`:

1. Install FluxLoop in the uv environment:
   ```bash
   uv pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

2. FluxLoop will automatically detect `.venv/` created by uv

3. (Optional) Set execution wrapper if needed:
   ```json
   {
     "fluxloop.executionWrapper": "uv run"
   }
   ```

### Using pipx

If you installed FluxLoop globally via pipx:

1. Ensure `~/.local/bin` is in your PATH
2. Set execution mode to **Global PATH**:
   ```
   FluxLoop: Select Environment → Global PATH
   ```

3. Verify with `FluxLoop: Show Environment Info`

### Multiple Projects with Different Environments

FluxLoop caches environment information per `targetSourceRoot`. When you switch projects:

1. Environment is automatically re-detected
2. Cached paths are used if available
3. FluxLoop Output channel shows the active environment

Each project can have its own:
- Execution mode (`fluxloop.executionMode`)
- Custom paths (`fluxloop.pythonPath`, `fluxloop.mcpCommandPath`)
- Target source root

Configure these per-workspace in `.vscode/settings.json` for each project.

### Conda Environments

FluxLoop detects conda environments if:
- `.conda/` directory exists in the project
- `CONDA_PREFIX` is set when running commands

To use a specific conda environment:

1. Activate it in your terminal:
   ```bash
   conda activate myenv
   ```

2. Install FluxLoop packages:
   ```bash
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

3. FluxLoop will detect and use the conda environment automatically

Or set custom paths via `FluxLoop: Select Environment → Custom executables`.

## Troubleshooting Environment Issues

### Environment Not Detected

1. Run `FluxLoop: Show Environment Info` to see what was detected
2. Check FluxLoop Output channel for error messages
3. Run `FluxLoop: Run Doctor` for detailed diagnostics
4. Ensure your virtual environment contains `fluxloop` and `fluxloop-mcp`:
   ```bash
   source .venv/bin/activate
   which fluxloop
   which fluxloop-mcp
   ```

### Wrong Environment Being Used

1. Check current execution mode: `FluxLoop: Show Environment Info`
2. Adjust via `FluxLoop: Select Environment`
3. Verify `.vscode/settings.json` doesn't have conflicting overrides
4. Clear cache by changing execution mode to a different value and back

### Commands Use Global Instead of Project Environment

1. Ensure `.venv` exists in your target source root directory
2. Set execution mode to **Workspace only** or **Auto**
3. Check FluxLoop Output channel to confirm venv was detected
4. Run `FluxLoop: Run Doctor` to verify paths

---

