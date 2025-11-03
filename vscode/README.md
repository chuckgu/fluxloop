# FluxLoop VSCode Extension

Visual Studio Code extension for managing FluxLoop AI agent simulation projects.

## Features

### 🎯 Project-Centric Workflow
- Create and manage multiple FluxLoop projects from the Activity Bar
- Switch between projects with a single click
- Automatic project discovery and configuration validation

### 📝 Input Management
- View and edit base inputs from `configs/input.yaml`
- Generate input variations using LLM or deterministic strategies
- Browse generated inputs and recordings in dedicated views

### 🧪 Experiment Execution
- Run experiments directly from VSCode
- Monitor execution progress with real-time feedback
- View runner configuration and iteration settings at a glance

### 📊 Results Exploration
- Browse experiment outputs organized by run timestamp
- Open traces, summaries, and artifacts with one click
- Parse results into human-readable Markdown timelines

### 🔴 Recording Mode (Advanced)
- Toggle argument recording for complex function signatures
- Enable/disable recording mode from Command Palette or Experiments view
- Status panel shows current recording state and target file

### ℹ️ System Status
- Real-time CLI and SDK installation checks
- Configuration validation for `configs/` structure
- Recording mode and environment status at a glance

---

## Installation

### Option 1: From VSIX (Cursor Users - Recommended)

1. Download the latest `.vsix` file from [GitHub Releases](https://github.com/fluxloop/fluxloop/releases)
2. In Cursor/VS Code:
   - Extensions → `...` → `Install from VSIX...`
   - Select the downloaded `.vsix` file
3. Restart Cursor/VS Code

### Option 2: From VS Code Marketplace

1. Search for "FluxLoop" in the Extensions marketplace
2. Click Install
3. Restart VS Code

### Required Dependencies

Install FluxLoop CLI and SDK:
```bash
pip install fluxloop-cli fluxloop
```

---

## Quick Start

### 1. Create a Project

Open the **FluxLoop** Activity Bar and click **"Create New Project…"** or use Command Palette:
```
FluxLoop: Create FluxLoop Project
```

This will:
- Prompt you to select a parent folder
- Generate `configs/` directory with project/input/simulation/evaluation configs
- Create `.env`, `examples/`, `inputs/`, `recordings/`, `experiments/` directories
- Register the project and set it as active

### 2. Review Configuration

Navigate to the **Inputs** view to inspect base inputs from `configs/input.yaml`. Click any base input to open the config file directly.

Alternatively, go to **Experiments** → **Current Experiment** → **Open configuration** to review `configs/simulation.yaml`.

### 3. Generate Inputs

From the **Inputs** view, click **"Generate New Inputs…"** to launch the wizard:
- Choose generation mode (Deterministic/LLM)
- Select variation strategies (rephrase, verbose, error_prone, etc.)
- Set limit and overwrite options
- Enter LLM API key if needed (saved to VS Code secrets and `.env`)

Generated inputs will appear under **Inputs → Generated Inputs**.

### 4. Run Experiment

From the **Experiments** view:
- Expand **Current Experiment**
- Click **Run Experiment**
- Select execution environment (Local Python/Docker/Dev Container)
- Optionally override iterations

Results will be saved to `experiments/` and appear in the **Results** view.

### 5. View Results

The **Results** view lists recent experiment runs. Expand any run to see:
- `summary.json` – aggregate statistics
- `traces.jsonl` – detailed execution traces
- `observations.jsonl` – observation stream
- `errors.json` – error logs (if any)

Click any file to open it in the editor.

---

## Recording Mode (Advanced)

For agents with complex call signatures (WebSocket handlers, callbacks, etc.), you can record actual arguments and replay them during experiments.

### Enable Recording
Use Command Palette:
```
FluxLoop: Enable Recording Mode
```

Or run in terminal:
```bash
fluxloop record enable
```

This updates `.env` and `configs/simulation.yaml` to enable recording. The **Status** panel will show "Record Mode: Enabled".

### Capture Arguments

Run your application normally. FluxLoop SDK will capture arguments to `recordings/args_recording.jsonl`.

### Disable Recording

Use Command Palette:
```
FluxLoop: Disable Recording Mode
```

Or run:
```bash
fluxloop record disable
```

### Configure Replay

Edit `configs/simulation.yaml` to use recorded arguments:
```yaml
replay_args:
  enabled: true
  recording_file: "recordings/args_recording.jsonl"
  override_param_path: "data.content"
```

Now run experiments—FluxLoop will replay recorded arguments with generated input variations.

---

## Configuration Files (v0.2.0)

FluxLoop projects use a multi-file configuration structure:

| File | Purpose | Edited From |
|------|---------|-------------|
| `configs/project.yaml` | Project metadata, collector settings | Projects view → Configure Project |
| `configs/input.yaml` | Personas, base inputs, LLM settings | Inputs view → Base Inputs (click to open) |
| `configs/simulation.yaml` | Runner, iterations, replay args | Experiments view → Open configuration |
| `configs/evaluation.yaml` | Evaluator definitions | (Future: Results view) |

All configs are YAML files that can be edited directly. The extension watches for changes and automatically refreshes views.

---

## Available Commands

Access via Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):

**Project Management:**
- `FluxLoop: Create FluxLoop Project`
- `FluxLoop: Add Existing FluxLoop Project`
- `FluxLoop: Switch FluxLoop Project`
- `FluxLoop: Remove FluxLoop Project`

**Workflow:**
- `FluxLoop: Generate Inputs`
- `FluxLoop: Run Experiment`
- `FluxLoop: Run Single Execution`
- `FluxLoop: Show Status`

**Recording:**
- `FluxLoop: Enable Recording Mode`
- `FluxLoop: Disable Recording Mode`
- `FluxLoop: Show Recording Status`

**Configuration:**
- `FluxLoop: Open Configuration`
- `FluxLoop: Select Execution Environment`

---

## Troubleshooting

### CLI Not Found
Ensure FluxLoop CLI is installed:
```bash
pip install fluxloop-cli
```

Check the **Status** panel for installation status.

### SDK Not Found
Install the FluxLoop SDK:
```bash
pip install fluxloop
```

The **Status** panel will verify SDK availability in your Python environment.

### No Configuration Found
Make sure your project has a `configs/` directory with required files:
- `project.yaml`
- `input.yaml`
- `simulation.yaml`

Create a new project using `FluxLoop: Create FluxLoop Project` to scaffold this structure automatically.

### Recording Not Working
1. Verify `.env` contains `FLUXLOOP_RECORD_ARGS=true`
2. Check `configs/simulation.yaml` → `replay_args.enabled: true`
3. Use `FluxLoop: Show Recording Status` to inspect current state

---

## Development

### Build Extension

```bash
cd packages/vscode
npm install
npm run compile
```

### Package Extension

```bash
npm install -g vsce
vsce package
```

This produces a `.vsix` file that can be installed locally.

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

---

## License

Apache License 2.0 - see [LICENSE](../../LICENSE) for details.

