---
sidebar_position: 1
---

# Project Commands

FluxLoop exposes project management commands through the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) and the Projects view. Use these commands to create, register, or inspect FluxLoop projects without leaving VS Code.

---

## FluxLoop: Create FluxLoop Project

**Command ID:** `fluxloop.createProject`  
**Purpose:** Scaffold a new FluxLoop project using the default or custom flow.

### Options
1. **Default (Recommended)** – Reuses current workspace as agent source, auto-detects its Python environment, and creates the FluxLoop project inside the shared root (`fluxloop.projectRoot`, default `~/FluxLoopProjects`).
2. **Custom (Advanced)** – Lets you choose both the project location and Python interpreter manually.

### What Happens
- Validates/installs `fluxloop-cli`, `fluxloop`, `fluxloop-mcp` in the selected interpreter
- Runs `fluxloop init project`
- Registers the project in the Projects view
- Updates `.vscode/settings.json` with `fluxloop.executionMode`, `fluxloop.targetSourceRoot`, and `fluxloop.projectRoot`

---

## FluxLoop: Add Existing FluxLoop Project

**Command ID:** `fluxloop.addProject`  
**Purpose:** Attach an existing FluxLoop project (one containing `configs/`) to the workspace.

### Usage
1. Run the command
2. Select the folder containing `configs/project.yaml`
3. Optionally set a custom display name

The project appears in the Projects view and inherits the folder’s environment settings (or prompts you to configure them).

---

## FluxLoop: Switch FluxLoop Project

**Command ID:** `fluxloop.switchProject`  
**Purpose:** Change the active project (affects Inputs/Experiments/Integration views, commands, and environment detection).

### Usage
1. Run the command or click the desired project in the Projects view
2. FluxLoop re-detects the environment and refreshes all views

The status bar displays the active project: `FluxLoop: <project-name>`.

---

## FluxLoop: Remove FluxLoop Project

**Command ID:** `fluxloop.removeProject`  
**Purpose:** Remove a project from the workspace list (files remain untouched).

### Usage
1. Right-click the project in the Projects view → **Remove Project**
2. Or run the command and pick the project to remove

> This only removes the entry from VS Code; it does **not** delete files.

---

## FluxLoop: Target Source Root…

**Command ID:** `fluxloop.targetSourceRoot`  
**Purpose:** Tell FluxLoop where your agent source code lives. This path drives environment detection and Integration Assistant analysis.

### Usage
1. Select the command or click **Target Source Root…** in the Projects view
2. Choose a folder (relative paths are stored automatically)
3. FluxLoop refreshes detection and logs the results in the Output channel

The selected path is stored in both `.vscode/settings.json → fluxloop.targetSourceRoot` and `configs/project.yaml → source_root`.

---

## FluxLoop: Show Environment Info

**Command ID:** `fluxloop.showEnvironmentInfo`  
**Purpose:** Display a quick summary of the currently detected interpreter.

### Output Includes
- Source root
- Execution mode (auto / workspace / global / custom)
- Python / `fluxloop` / `fluxloop-mcp` paths
- Detection notes (missing packages, version mismatch, etc.)

Use this command whenever a CLI task fails to confirm which interpreter is active.

---

## FluxLoop: Run Doctor

**Command ID:** `fluxloop.runDoctor`  
**Purpose:** Run `fluxloop doctor` and show the results inside VS Code.

### Why Run It
- Verify Python version, virtual environment, CLI/SDK/MCP installations
- Check MCP index location + size
- Validate project configuration files
- Troubleshoot Integration Assistant warnings

You can also run the CLI version manually:
```bash
fluxloop doctor --json
```

---

## FluxLoop: Configure Execution Wrapper

**Command ID:** `fluxloop.configureExecutionWrapper`  
**Purpose:** Add a command prefix (e.g., `uv run`, `pipx run`) to every FluxLoop CLI invocation.

### Usage
1. Run the command
2. Enter the prefix (leave blank to clear)
3. Setting is stored in `.vscode/settings.json → fluxloop.executionWrapper`

All subsequent commands (generate inputs, run experiment, parse, evaluate, etc.) will use the wrapper.

---

## FluxLoop: Select Environment

**Command ID:** `fluxloop.selectEnvironment`  
**Purpose:** Switch between Auto / Workspace / Global / Custom execution modes.

### Workflow
1. Run the command
2. Choose the desired mode
3. If you pick **Custom executables**, provide paths for Python and optionally `fluxloop-mcp`

FluxLoop re-detects immediately and logs results to the Output channel.

---

## Related

- [Workflow Commands](./workflow-commands.md) – Input generation, experiments, parsing
- [Recording Commands](./recording-commands.md) – Toggle and inspect recording mode
- [Projects View](../views/projects-view.md) – UI reference for project management
