---
sidebar_position: 9
---

# doctor Command

Diagnose FluxLoop environment setup and detect common configuration issues.

## Overview

The `doctor` command performs a comprehensive health check of your FluxLoop installation, including:

- **Python Environment**: Version, virtual environment detection, and executable path
- **FluxLoop CLI**: Installation status and version
- **FluxLoop MCP**: Installation status and availability
- **MCP Index**: Knowledge base presence and integrity
- **Project Configuration**: Config directory structure and files

This command is essential for troubleshooting installation issues and verifying that all FluxLoop components are correctly set up.

## Basic Usage

```bash
# Run diagnostics for current environment
fluxloop doctor

# Specify a project
fluxloop doctor --project my-agent

# Output as JSON for programmatic parsing
fluxloop doctor --json
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project`, `-p` | Project name under the FluxLoop root directory | None (uses current) |
| `--root` | FluxLoop root directory | `./fluxloop` |
| `--index-dir` | Override FluxLoop MCP index directory | `~/.fluxloop/mcp/index/dev` |
| `--json` | Output diagnostic information as JSON | `false` |

## What Gets Checked

### 1. Python Environment

Verifies:
- Python executable path
- Python version (requires 3.11+ for SDK/MCP, 3.8+ for CLI)
- Platform information
- Virtual environment detection (venv, conda, uv)

**Environment Variables Checked:**
- `VIRTUAL_ENV`
- `CONDA_PREFIX`
- `UV_PROJECT_ENV`

### 2. FluxLoop CLI

Checks:
- `fluxloop` command availability on PATH
- CLI version
- Installation location

### 3. FluxLoop MCP Server

Checks:
- `fluxloop-mcp` command availability
- MCP server installation
- Help output accessibility

### 4. MCP Knowledge Index

Verifies:
- Index directory existence
- `chunks.jsonl` presence and size
- Default location: `~/.fluxloop/mcp/index/dev`

### 5. Project Configuration

Validates:
- Project root directory
- `configs/` directory structure
- `configs/project.yaml` existence

## Output Examples

### Successful Diagnosis

```
╭──────────────────────────────────╮
│ FluxLoop Environment Doctor      │
╰──────────────────────────────────╯

Component       Status  Details
Python          ✓       3.11.5 (/Users/user/.venv/bin/python)
Virtual Env     ✓       /Users/user/project/.venv
FluxLoop CLI    ✓       /Users/user/.venv/bin/fluxloop
FluxLoop MCP    ✓       /Users/user/.venv/bin/fluxloop-mcp
MCP Index       ✓       ~/.fluxloop/mcp/index/dev • chunks.jsonl (1.2M bytes)
Project Config  ✓       fluxloop/my-agent/configs/project.yaml

╭─ fluxloop --version ──────────────╮
│ FluxLoop CLI v0.2.27              │
╰───────────────────────────────────╯

╭──────────────────╮
│ Doctor completed │
╰──────────────────╯
```

### Issues Detected

```
╭──────────────────────────────────╮
│ FluxLoop Environment Doctor      │
╰──────────────────────────────────╯

Component       Status  Details
Python          ✓       3.11.5 (/usr/bin/python3)
Virtual Env     –       Global interpreter
FluxLoop CLI    ✓       /usr/local/bin/fluxloop
FluxLoop MCP    ✗       Not found
MCP Index       –       ~/.fluxloop/mcp/index/dev
Project Config  –       Run: fluxloop init project

Errors
• fluxloop-mcp: fluxloop-mcp not found on PATH

╭──────────────────╮
│ Doctor completed │
╰──────────────────╯
```

## JSON Output

Use `--json` flag for machine-readable output:

```bash
fluxloop doctor --json
```

```json
{
  "python": {
    "executable": "/Users/user/.venv/bin/python",
    "version": "3.11.5",
    "platform": "macOS-14.0-arm64",
    "command_output": "Python 3.11.5"
  },
  "virtual_environment": {
    "python_executable": "/Users/user/.venv/bin/python",
    "python_version": "3.11.5",
    "platform": "macOS-14.0-arm64",
    "virtual_env": true,
    "virtual_env_path": "/Users/user/project/.venv",
    "environment_variables": {
      "VIRTUAL_ENV": "/Users/user/project/.venv"
    }
  },
  "fluxloop_cli": {
    "success": true,
    "path": "/Users/user/.venv/bin/fluxloop",
    "output": "FluxLoop CLI v0.2.27",
    "error": null
  },
  "fluxloop_mcp": {
    "success": true,
    "path": "/Users/user/.venv/bin/fluxloop-mcp",
    "output": "Usage: fluxloop-mcp [OPTIONS]",
    "error": null
  },
  "project": {
    "root": "/Users/user/project/fluxloop",
    "config_directory": "/Users/user/project/fluxloop/my-agent/configs",
    "project_yaml": "/Users/user/project/fluxloop/my-agent/configs/project.yaml",
    "project_yaml_exists": true,
    "config_directory_exists": true
  },
  "mcp_index": {
    "exists": true,
    "path": "/Users/user/.fluxloop/mcp/index/dev",
    "chunks_exists": true,
    "chunks_size": 1245678
  }
}
```

## Common Issues and Solutions

### Issue: FluxLoop CLI Not Found

**Symptom:**
```
FluxLoop CLI    ✗       fluxloop not found on PATH
```

**Solution:**
```bash
# Install in active virtual environment
pip install fluxloop-cli

# Or install globally
pip install --user fluxloop-cli

# Or with uv
uv pip install fluxloop-cli
```

### Issue: FluxLoop MCP Not Found

**Symptom:**
```
FluxLoop MCP    ✗       Not found
```

**Solution:**
```bash
# Install in active virtual environment
pip install fluxloop-mcp

# Rebuild the knowledge index
packages/mcp/scripts/rebuild_index.sh
```

### Issue: Missing MCP Index

**Symptom:**
```
MCP Index       –       ~/.fluxloop/mcp/index/dev
```

**Solution:**
```bash
# Build the index manually
fluxloop-mcp rebuild-index

# Or run the build script from source
packages/mcp/scripts/rebuild_index.sh
```

### Issue: No Virtual Environment

**Symptom:**
```
Virtual Env     –       Global interpreter
```

**Recommendation:**
```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Reinstall FluxLoop packages
pip install fluxloop-cli fluxloop fluxloop-mcp
```

### Issue: Missing Project Configuration

**Symptom:**
```
Project Config  –       Run: fluxloop init project
```

**Solution:**
```bash
# Initialize a new project
fluxloop init project --name my-agent
```

## Integration with VSCode Extension

The VSCode extension uses `fluxloop doctor` internally to:

- Validate environment on startup
- Display status in the Integration view
- Provide actionable feedback when packages are missing

You can also run doctor from Command Palette:
```
FluxLoop: Run Doctor
```

## When to Use Doctor

Run `fluxloop doctor` in these scenarios:

1. **After Fresh Installation**: Verify all components are correctly installed
2. **Before Starting a Project**: Check that your environment is ready
3. **Troubleshooting**: Diagnose why commands aren't working
4. **CI/CD Setup**: Validate build environment configuration
5. **Version Upgrades**: Confirm new versions are properly detected

## Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Diagnostics completed successfully (doesn't mean all checks passed) |
| 1 | Invalid arguments or runtime error |

Note: `doctor` always exits with 0 if it completes the diagnostic scan, even if some components are missing. Check the output or JSON for actual status.

## See Also

- [Installation Guide](/cli/getting-started/installation) - Initial setup
- [status Command](/cli/commands/status) - Check experiment and recording status
- [VSCode Environment Configuration](/vscode/getting-started/environment-configuration) - IDE-specific setup


