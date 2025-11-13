---
sidebar_position: 2
---

# Creating First Project

Create your first FluxLoop project in VSCode.

## 1. Launch the Project Wizard

1. Open the **FluxLoop** activity bar.
2. Click **Create New Project…** (or run `FluxLoop: Create FluxLoop Project` from the Command Palette).
3. Pick the parent folder where the project folder should be created.
4. Enter a project name (the extension creates `<parent>/<name>`).

## 2. Select the Python Environment

After you pick the project name, FluxLoop detects available environments and prompts you to choose:

- **Use project folder** – create/use `.venv` inside the new project directory.
- **Choose another folder…** – point to an existing virtual environment (conda, uv, etc.).
- **Use Global PATH** – run with globally installed `fluxloop` (not recommended unless you know you want it).

If FluxLoop packages are missing, you can:

- Click **Run Setup Script** to launch `setup_fluxloop_env.sh --target-source-root <path>` in a terminal.
- Click **Open Terminal** to install manually (instructions are pre-filled).
- Install the packages yourself and press **Retry** when ready.

The wizard shows exactly which components are missing (Python, `fluxloop`, `fluxloop-mcp`) and logs all checks in the **FluxLoop** Output channel.

## 3. Initialization

Once the environment is ready, the extension:

- Runs `fluxloop init project` with the selected environment.
- Generates `configs/` (project/input/simulation/evaluation) plus `.env`, `examples/`, `inputs/`, `recordings/`, `experiments/`.
- Registers the project and sets it as active.
- Saves `.vscode/settings.json` with `fluxloop.executionMode` and `fluxloop.targetSourceRoot`.

## 4. Verify the Environment

Use these commands at any time:

- `FluxLoop: Show Environment Info` – quick summary of Python/FluxLoop/MCP paths.
- `FluxLoop: Run Doctor` – detailed diagnostics (virtual env status, MCP index, project config).

All environment activity is logged in **View → Output → FluxLoop**.

## Next Steps

- [Environment Configuration](./environment-configuration)
- [Running Experiments](./running-experiments)
