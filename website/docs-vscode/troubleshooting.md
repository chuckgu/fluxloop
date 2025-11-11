---
sidebar_position: 10
---

# Troubleshooting

Common issues and solutions for FluxLoop VSCode Extension.

## Environment & Installation Issues

### CLI Not Found

**Symptoms:**
- FluxLoop commands fail with "CLI not found"
- System Status shows FluxLoop CLI as "not installed"

**Solutions:**

1. **Install FluxLoop CLI in your project environment:**
   ```bash
   # If using venv
   source .venv/bin/activate
   pip install fluxloop-cli
   
   # If using uv
   uv pip install fluxloop-cli
   
   # If using pipx (global install)
   pipx install fluxloop-cli
   ```

2. **Verify installation:**
   ```bash
   fluxloop --version
   ```

3. **Check environment detection:**
   - Run `FluxLoop: Show Environment Info`
   - Ensure the correct Python environment is selected
   - If needed, use `FluxLoop: Select Environment` to choose the right execution mode

4. **Run diagnostics:**
   ```
   FluxLoop: Run Doctor
   ```
   or
   ```bash
   fluxloop doctor
   ```

### fluxloop-mcp Not Found

**Symptoms:**
- Integration view shows "fluxloop-mcp is not installed"
- Knowledge Search and Flux Agent commands fail

**Solutions:**

1. **Install in the same environment as FluxLoop CLI:**
   ```bash
   # Project venv
   source .venv/bin/activate
   pip install fluxloop-mcp
   
   # uv
   uv pip install fluxloop-mcp
   
   # pipx (global)
   pipx install fluxloop-mcp
   ```

2. **Verify detection:**
   - Run `FluxLoop: Show Environment Info`
   - Check that `fluxloop-mcp` path is listed
   - Ensure it's in the same environment as your project

3. **Rebuild the knowledge index:**
   ```bash
   packages/mcp/scripts/rebuild_index.sh
   ```

4. **Check MCP server manually:**
   ```bash
   fluxloop-mcp --help
   ```

### Environment Not Detected

**Symptoms:**
- FluxLoop Output shows "Environment type: global" when you have a venv
- Commands use wrong Python version

**Solutions:**

1. **Ensure virtual environment exists:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

2. **Set target source root:**
   - In Projects view, click **Target Source Root…**
   - Select the directory containing `.venv`
   - FluxLoop will re-detect the environment

3. **Check execution mode:**
   - Run `FluxLoop: Select Environment`
   - Choose **Workspace only** to require project venv
   - Or **Auto** to fallback to global if venv is missing

4. **Verify with Doctor:**
   ```
   FluxLoop: Run Doctor
   ```
   Check the "Virtual Env" row shows your `.venv` path

### Wrong Python Version

**Symptoms:**
- Experiments fail due to missing packages
- `fluxloop doctor` shows different Python than expected

**Solutions:**

1. **Check active environment:**
   ```
   FluxLoop: Show Environment Info
   ```

2. **Set custom Python path:**
   - Run `FluxLoop: Select Environment`
   - Choose **Custom executables…**
   - Enter absolute path to desired Python interpreter

3. **Rebuild virtual environment:**
   ```bash
   rm -rf .venv
   python3.11 -m venv .venv  # Use specific version
   source .venv/bin/activate
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

4. **Update target source root** to trigger re-detection

## SDK Not Found

**Symptoms:**
- Experiments fail with import errors
- Status panel shows SDK not installed

**Solutions:**

1. **Install FluxLoop SDK:**
   ```bash
   source .venv/bin/activate
   pip install fluxloop
   ```

2. **Verify:**
   ```bash
   python -c "import fluxloop; print(fluxloop.__version__)"
   ```

3. **Check with doctor:**
   ```bash
   fluxloop doctor
   ```

## Configuration Issues

### No Configuration Found

**Symptoms:**
- Projects view shows project without checkmark
- Experiments fail to run

**Solutions:**

1. **Initialize project structure:**
   ```
   FluxLoop: Initialize FluxLoop Project
   ```
   or
   ```bash
   fluxloop init project
   ```

2. **Verify required files exist:**
   - `configs/project.yaml`
   - `configs/input.yaml`
   - `configs/simulation.yaml`

3. **Check Projects view** for validation status

### Target Source Root Not Working

**Symptoms:**
- Setting source root doesn't change detected environment
- FluxLoop still uses wrong directory

**Solutions:**

1. **Ensure configs/project.yaml exists** in the project
2. **Check the value** in `configs/project.yaml`:
   ```yaml
   source_root: "./backend"  # Relative path
   # or
   source_root: "/absolute/path"
   ```

3. **Refresh environment manually:**
   - Run `FluxLoop: Select Environment`
   - Or click **Refresh Status** in Integration view

4. **View output logs** to see which directory FluxLoop is scanning

## Integration Assistant Issues

### MCP Connection Fails

**Symptoms:**
- "fluxloop-mcp package is not installed" warning
- Knowledge Search returns errors

**Solutions:**

1. **Install fluxloop-mcp** in the same environment as FluxLoop CLI
2. **Verify with:**
   ```bash
   fluxloop-mcp --help
   ```

3. **Check environment:**
   ```
   FluxLoop: Show Environment Info
   ```
   Ensure `fluxloop-mcp` path is detected

4. **Rebuild MCP index** if missing:
   ```bash
   packages/mcp/scripts/rebuild_index.sh
   ```

### OpenAI Key Prompt Keeps Appearing

**Solutions:**

1. **Store key in Secret Storage** when prompted
2. **Or add to workspace settings:**
   ```json
   {
     "fluxloop.openaiApiKey": "sk-..."
   }
   ```

3. **Verify model configuration:**
   ```json
   {
     "fluxloop.openaiModel": "gpt-4o-mini"
   }
   ```

### Flux Agent Returns Generic Response

**Symptoms:**
- Agent doesn't use repository-specific context
- Recommendations feel too generic

**Solutions:**

1. **Ensure MCP index is built** and contains your docs
2. **Run Knowledge Search first** to verify index works
3. **Select relevant code** before running Flux Agent
4. **Check FluxLoop Output** for workflow execution errors

## Common Setup Script

For new projects or team onboarding, use the automated setup script:

```bash
# From packages/cli or your FluxLoop project
bash scripts/setup_fluxloop_env.sh

# With custom Python
bash scripts/setup_fluxloop_env.sh --python python3.11

# With target source root
bash scripts/setup_fluxloop_env.sh --target-source-root ./backend
```

This script:
- Creates `.venv` if missing
- Installs FluxLoop packages
- Generates `.vscode/settings.json` with environment defaults
- Runs `fluxloop doctor` to verify setup

## Getting Help

If issues persist:

1. **Collect diagnostics:**
   ```bash
   fluxloop doctor --json > diagnostics.json
   ```

2. **Check FluxLoop Output channel** for detailed logs

3. **Review settings:**
   - `.vscode/settings.json`
   - `configs/project.yaml` (source_root)
   - Environment variables in terminal

4. **Open an issue** on GitHub with:
   - Doctor output
   - FluxLoop Output channel logs
   - Your OS and Python version
   - Installation method (pip, uv, pipx, etc.)

