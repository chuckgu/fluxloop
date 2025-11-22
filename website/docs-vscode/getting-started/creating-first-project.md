---
sidebar_position: 2
---

# Creating First Project

Create your first FluxLoop project in VSCode.

## 1. Launch the Project Wizard

1. Open the **FluxLoop** activity bar.
2. Click **Create New Project…** (or run `FluxLoop: Create FluxLoop Project` from the Command Palette).
3. Choose a flow:
   - **Default (recommended)** – Reuses the workspace you have open as the agent source, auto-detects its Python environment, and creates the FluxLoop project inside the shared root (default `~/FluxLoopProjects`).
   - **Custom (advanced)** – Lets you manually pick both the FluxLoop project location and the Python environment (same experience as previous releases).

## 2. Default Flow in Detail

When you pick **Default**, the wizard guides you through:

1. **Project name** – Enter the name; the target path preview updates (e.g. `~/FluxLoopProjects/agent-e2e`).
2. **Environment selection** – FluxLoop lists detected interpreters from:
   - VSCode Python extension’s active interpreter
   - `.venv`, `poetry`, `conda`, or `pyenv` folders under your workspace
   - Manual browse option (`Choose another environment…`) and a safety fallback (`Use system Python` – not recommended)
3. **Example content** – Decide whether to include the sample agent.

If required packages (`fluxloop-cli`, `fluxloop`, `fluxloop-mcp`) are missing, a modal dialog offers:

- **Install Automatically** (runs pip install)
- **Open Terminal & Install Manually** (pre-fills instructions)
- **Select Different Environment**

All checks are logged to **View → Output → FluxLoop**.

## 3. Custom Flow (previous behavior)

When you choose **Custom**, you:

1. Select the FluxLoop project root manually.
2. Enter the project name (created inside the folder you picked).
3. Choose or browse to the environment to use.
4. Decide on including the example agent.

This is useful for mono-repo setups, remote folders, or when you want the FluxLoop project alongside your source code.

## 4. Initialization

After the environment is validated (in either flow), the extension:

- Runs `fluxloop init project`.
- Generates `configs/` (project/input/simulation/evaluation) plus `.env`, `examples/`, `inputs/`, `recordings/`, `experiments/`.
- Registers the project and sets it as active.
- Saves `.vscode/settings.json` with the selected environment (`fluxloop.executionMode`, `fluxloop.targetSourceRoot`).  
- Stores/updates the shared project root in `fluxloop.projectRoot` (change it later via Settings → FluxLoop → Project Root).

## 4. Verify the Environment

Use these commands at any time:

- `FluxLoop: Show Environment Info` – quick summary of Python/FluxLoop/MCP paths.
- `FluxLoop: Run Doctor` – detailed diagnostics (virtual env status, MCP index, project config).

All environment activity is logged in **View → Output → FluxLoop**.

## Next Steps

- [Environment Configuration](./environment-configuration)
- [Running Experiments](./running-experiments)
