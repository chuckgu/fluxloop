---
sidebar_position: 2
---

# Environment Configuration

FluxLoop automatically detects and uses your project's Python environment to ensure experiments run with the correct dependencies.

## Quick Setup

After installing the FluxLoop VSCode extension:

1. **Create or activate a virtual environment** in your project:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install FluxLoop packages:**
   ```bash
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

3. **Verify detection** in VSCode:
   - Open Command Palette (`Cmd+Shift+P`)
   - Run `FluxLoop: Show Environment Info`
   - Confirm paths point to your `.venv/bin/` directory

4. **Set target source root** (if needed):
   - Expand your project in the **Projects** view
   - Click **Target Source Root…**
   - Select the directory containing `.venv`

FluxLoop will now use this environment for all commands.

## Automated Setup Script

For new projects or onboarding, use the setup script:

```bash
cd your-project
bash packages/cli/scripts/setup_fluxloop_env.sh
```

This automatically:
- Creates `.venv` if missing
- Installs FluxLoop packages
- Generates `.vscode/settings.json` with environment defaults
- Runs `fluxloop doctor` to verify setup

**With custom Python:**
```bash
bash packages/cli/scripts/setup_fluxloop_env.sh --python python3.11
```

**With target source root:**
```bash
bash packages/cli/scripts/setup_fluxloop_env.sh --target-source-root ./backend
```

## Execution Modes

FluxLoop supports four execution modes to match your workflow.

### Auto (Recommended)

Automatically detects project virtual environments (`.venv`, `venv`, `.conda`) and uses them. Falls back to global PATH if not found.

**When to use:**
- Standard projects with optional virtual environments
- Mixed teams (some use venv, others use global installs)

**Set via Command Palette:**
```
FluxLoop: Select Environment → Auto (detect project environment)
```

### Workspace Only

Requires a virtual environment in the project. Commands fail if venv is not detected.

**When to use:**
- Strict dependency isolation
- Teams that always use virtual environments
- CI/CD pipelines with project-specific dependencies

**Set via Command Palette:**
```
FluxLoop: Select Environment → Workspace only
```

### Global PATH

Always uses globally installed FluxLoop executables from PATH (e.g., installed via pipx).

**When to use:**
- Global FluxLoop installation (pipx)
- Simple projects without virtual environments
- Quick prototyping

**Set via Command Palette:**
```
FluxLoop: Select Environment → Global PATH
```

### Custom Executables

Manually specify absolute paths to Python and fluxloop-mcp executables.

**When to use:**
- Non-standard installation locations
- Multiple Python versions
- Advanced conda/pyenv setups

**Set via Command Palette:**
```
FluxLoop: Select Environment → Custom executables…
```

Then enter:
- Python executable path (e.g., `/opt/python3.11/bin/python`)
- fluxloop-mcp path (optional, e.g., `/custom/bin/fluxloop-mcp`)

## Checking Environment Status

### Show Environment Info

Quick modal summary of the active environment:

```
FluxLoop: Show Environment Info
```

Shows:
- Source root
- Environment type (venv, conda, global, etc.)
- Python path
- fluxloop path
- fluxloop-mcp path
- Any detection notes

### Run Doctor

Comprehensive diagnostics including MCP index and project config:

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
- Python version and executable
- Virtual environment status
- FluxLoop CLI version and path
- FluxLoop MCP availability
- MCP index location and size
- Project configuration state

Use `--json` for machine-readable output:
```bash
fluxloop doctor --json
```

### FluxLoop Output Channel

Detailed environment logs appear in the Output channel:

1. View → Output (or `Shift+Cmd+U`)
2. Select **FluxLoop** from dropdown
3. Review environment detection logs

Every time the environment is refreshed, you'll see:
```
[FluxLoop Env] ----------------------------------------
[FluxLoop Env] Source root: /path/to/project
[FluxLoop Env] Environment type: venv
[FluxLoop Env] Python: /path/.venv/bin/python
[FluxLoop Env] fluxloop: /path/.venv/bin/fluxloop
[FluxLoop Env] fluxloop-mcp: /path/.venv/bin/fluxloop-mcp
[FluxLoop Env] Notes:
[FluxLoop Env]  • Python detected but FluxLoop packages were not found in this environment.
[FluxLoop Env] ----------------------------------------
```

## Common Scenarios

### Using uv

1. Create uv project:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

2. FluxLoop automatically detects `.venv/`

3. (Optional) Set execution wrapper if you want to use `uv run`:
   ```
   FluxLoop: Configure Execution Wrapper → uv run
   ```

### Using Conda

1. Create and activate conda environment:
   ```bash
   conda create -n myproject python=3.11
   conda activate myproject
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

2. If conda env is in a non-standard location:
   ```
   FluxLoop: Select Environment → Custom executables…
   ```
   Enter conda Python path (e.g., `/opt/conda/envs/myproject/bin/python`)

### Multiple Projects

FluxLoop caches environment per project. When switching:

1. Environment is re-detected automatically
2. Each project can have different:
   - Execution mode
   - Target source root
   - Custom paths

Configure per-project in each project's `.vscode/settings.json`.

### Team Setup

For consistent team environments, commit to your repo:

**`.vscode/settings.json`:**
```json
{
  "fluxloop.executionMode": "workspace",
  "fluxloop.targetSourceRoot": "./src"
}
```

**`README.md` or setup script:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fluxloop doctor
```

Or use the automated script:
```bash
bash packages/cli/scripts/setup_fluxloop_env.sh --target-source-root ./src
```

## Settings Reference

### fluxloop.executionMode

Controls environment selection strategy.

- **Type:** `string`
- **Values:** `auto` | `workspace` | `global` | `custom`
- **Default:** `auto`
- **Scope:** Workspace or folder

### fluxloop.targetSourceRoot

Path to FluxLoop project source root for environment detection.

- **Type:** `string`
- **Default:** `""` (uses project root or `source_root` from project.yaml)
- **Scope:** Workspace or folder
- **Supports:** Relative paths (from project) or absolute paths

### fluxloop.pythonPath

Custom Python executable path (overrides detection).

- **Type:** `string`
- **Default:** `""` (auto-detect)
- **Scope:** Workspace or folder
- **Example:** `/Users/me/project/.venv/bin/python`

### fluxloop.mcpCommandPath

Custom fluxloop-mcp executable path.

- **Type:** `string`
- **Default:** `""` (auto-detect)
- **Scope:** Workspace or folder
- **Example:** `/Users/me/project/.venv/bin/fluxloop-mcp`

### fluxloop.executionWrapper

Command prefix for CLI invocations (e.g., `uv run`).

- **Type:** `string`
- **Default:** `""`
- **Scope:** Workspace
- **Example:** `uv run`, `pipx run`

## Next Steps

- [Create your first project](creating-first-project)
- [Run experiments](running-experiments)
- [Troubleshooting](../troubleshooting) if you encounter issues

