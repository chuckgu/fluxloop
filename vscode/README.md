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
- Browse experiment outputs organized by run timestamp under an **Experiments** folder
- Open traces, summaries, observations, and artifacts with one click
- Parse results into human-readable Markdown timelines with **Parse Results** action
- Evaluate experiments with rule-based and LLM evaluators using **Evaluate Results** action
- View parsed analysis outputs in the `per_trace_analysis/` folder
- Review evaluation outputs in the `evaluation/` folder:
  - `summary.json` – aggregate statistics, success criteria results, analysis (persona, outliers, trends, baseline comparison)
  - `per_trace.jsonl` – per-trace scores and failure reasons
  - `report.md` – human-readable Markdown report
  - `report.html` – interactive HTML report with charts and visualizations (Phase 2)

### 🔴 Recording Mode (Advanced)
- Toggle argument recording for complex function signatures
- Enable/disable recording mode from Command Palette or Experiments view
- Status panel shows current recording state and target file

### 🤖 Integration Assistant (Multi-Mode Flux Agent)
- Dedicated **Integration** view with MCP connection status and recent suggestions
- One-click document search backed by the FluxLoop MCP server
- Flux Agent now supports four modes selectable per run:
  - **Integration** – classic repository analysis + edit plan workflow
  - **Base Input** – inspects `inputs/` & service configs to draft new base input candidates
  - **Experiment** – summarizes runner configs + experiment history to propose simulation updates
  - **Insight** – ingests evaluation logs (`summary.json`, `traces.jsonl`) to surface findings & follow-up actions
- Suggestion history stores file context, selected code, mode metadata, and the generated plan

---

## Installation

### Recommended: Install from Extension Marketplace

#### 🎯 Cursor Users

1. Open **Extensions** sidebar (`Cmd+Shift+X` or click Extensions icon)
2. Search for **"FluxLoop"**
3. Click **Install**
4. Restart Cursor

> Extension is automatically downloaded from [Open VSX Registry](https://open-vsx.org/extension/fluxloop/fluxloop)

#### 💻 VS Code Users

1. Open **Extensions** (`Cmd+Shift+X` / `Ctrl+Shift+X`)
2. Search for **"FluxLoop"**
3. Click **Install**
4. Restart VS Code

> Or install directly from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop)

### Alternative: Manual Installation from VSIX

If you prefer manual installation:

1. Download the latest `.vsix` file from [GitHub Releases](https://github.com/chuckgu/fluxloop/releases)
2. Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
3. Type and select **"Extensions: Install from VSIX..."**
4. Select the downloaded `.vsix` file
5. Restart your editor

### Required Dependencies

Install FluxLoop CLI and SDK:
```bash
pip install fluxloop-cli fluxloop
```

Install the FluxLoop MCP server:
```bash
pip install fluxloop-mcp
```

Build (or download) the MCP knowledge index:
```bash
packages/mcp/scripts/rebuild_index.sh
```

Verify you have Python 3.11 or newer:
```bash
python3 --version
```

> Flux Agent also requires an OpenAI API key. You can supply it per run or store it securely after the first prompt.

---

## Quick Start

### 1. Create a Project

Open the **FluxLoop** Activity Bar and click **"Create New Project…"** or run:
```
FluxLoop: Create FluxLoop Project
```

You’ll first choose between two flows:

- **Default (Recommended)** – Use your current workspace as the agent source, detect its Python environment, and create the FluxLoop project inside the shared root (default `~/FluxLoopProjects`).  
- **Custom (Advanced)** – Manually pick both the FluxLoop project location and the environment (original flow retained for power users).

#### Default Flow
1. **Project name** – Enter a name; the extension previews the target path (e.g. `~/FluxLoopProjects/agent-e2e`).
2. **Environment selection** – FluxLoop auto-discovers interpreters from:
   - VSCode Python extension’s active interpreter
   - `.venv`, `poetry`, `conda`, `pyenv` folders under your workspace
   - Manual browse option and a fall-back “Use system Python (not recommended)”
3. **Example content** – Decide whether to include the sample agent.
4. The project is generated inside the shared root, the environment is validated (with guided retries/install options), and the project is registered/activated.  
   - The shared root is stored in `fluxloop.projectRoot` (change via Settings → FluxLoop → Project Root).

#### Custom Flow
Follow the original prompts:
- Pick the FluxLoop project root manually
- Enter the project name
- Choose/Create the environment (including project-local `.venv`)
- Decide on example content

In both flows the extension runs `fluxloop init project`, creates `configs/`, `.env`, `examples/`, `inputs/`, `recordings/`, `experiments/`, and saves workspace settings that point to the chosen environment.

Check the detected environment anytime via:
```
FluxLoop: Show Environment Info
```

For full diagnostics (Python/FluxLoop/MCP/index), run:
```
FluxLoop: Run Doctor
```

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
- Click **Run Experiment** (located next to **Current Experiment**)
- Select execution environment (Local Python/Dev Container)
  - **Local Python**: Runs with your current Python environment
  - **Dev Container**: Runs inside an active Dev Container
  - **Docker**: Coming soon
- Optionally override iterations

Results will be saved to `experiments/` and appear in the **Results** view.

### 5. View Results

The **Results** view lists recent experiment runs under an **Experiments** folder. Expand any run to see:
- **Parse Results** – Generate human-readable Markdown timelines from traces
- **Evaluate Results** – Run rule-based + optional LLM evaluation pipeline
- `per_trace_analysis/` – Parsed analysis outputs (appears after parsing)
- `evaluation/` – Evaluation outputs (summary, per-trace JSONL, markdown report)
- `summary.json` – aggregate statistics
- `traces.jsonl` – detailed execution traces
- `observations.jsonl` – observation stream
- `errors.json` – error logs (if any)
- `logs.json` – additional logs

Click **Parse Results** to convert experiment outputs into per-trace Markdown files. You can specify a custom output directory or use the default `per_trace_analysis`.

Click **Evaluate Results** to run rule-based and LLM-based evaluators, compute success criteria, perform advanced analysis (persona breakdown, outlier detection, trend analysis, baseline comparison), and generate Markdown and HTML reports. Configure evaluators, thresholds, and report settings in `configs/evaluation.yaml`. Results are stored under `evaluation/` with:
- `summary.json` – aggregate statistics and Phase 2 analysis
- `per_trace.jsonl` – detailed per-trace scores
- `report.md` – human-readable Markdown report
- `report.html` – interactive HTML report with charts (Phase 2)

Use the prompt dialog to override the output directory or keep the default `evaluation`.

---

### 6. Use the Integration Assistant

1. Open the **Integration** view in the FluxLoop activity bar.
2. Press **Connect MCP** to verify `fluxloop-mcp` is available and the knowledge index is present.
3. Press **Search in Documents** to run a one-off documentation query (`fluxloop-mcp --once --query "<question>"`).
4. Open a file, highlight any relevant snippet, and press **Run Flux Agent**.
5. When prompted, choose a mode:
   - **Integration**: full repo analysis + edit plan workflow (default)
   - **Base Input**: drafts candidate inputs using existing `inputs/` and service configs
   - **Experiment**: proposes `simulation.yaml` updates using past runs + runner settings
   - **Insight**: summarizes evaluation logs and suggests next improvements
6. The extension will:
   - Execute `run_integration_workflow` inside your repo
   - Collect the result and feed it to the configured OpenAI model
   - Render the plan (summary, step list, validation checklist) in a dedicated panel
7. Provide your OpenAI API key when prompted (the extension can store it in Secret Storage).
8. Revisit previous answers from **Recent Suggestions**; each entry reopens the full plan, including the mode that produced it.

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
| `configs/evaluation.yaml` | Evaluators (rule-based, LLM), success criteria, analysis options, report settings | Edit directly |

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
- `FluxLoop: Connect MCP`
- `FluxLoop: Search in Documents`
- `FluxLoop: Run Flux Agent`
- `FluxLoop: Refresh Integration View`
- `FluxLoop: Clear Integration Suggestion History`

**Recording:**
- `FluxLoop: Enable Recording Mode`
- `FluxLoop: Disable Recording Mode`
- `FluxLoop: Show Recording Status`

**Configuration:**
- `FluxLoop: Open Configuration`
- `FluxLoop: Select Environment`
- `FluxLoop: Show Environment Info`
- `FluxLoop: Run Doctor`
- `FluxLoop: Configure Execution Wrapper`

**Results:**
- `FluxLoop: Parse Experiment` – Convert experiment traces to Markdown

---

## Advanced Configuration

### Execution Wrapper (uv, pipx, etc.)

If you use `uv`, `pipx`, or any other wrapper to run FluxLoop CLI, configure it via:

**Command Palette:**
```
FluxLoop: Configure Execution Wrapper
```

Enter the prefix (e.g., `uv run`) and the extension will automatically prepend it to all CLI commands.

**Or manually in `.vscode/settings.json`:**
```json
{
  "fluxloop.executionWrapper": "uv run"
}
```

This setting is saved to your workspace and will be applied to all FluxLoop commands.

### Environment Configuration

FluxLoop automatically detects your project's Python environment (venv, conda, uv, etc.) and uses it for all commands. You can configure this behavior via:

**Command Palette:**
```
FluxLoop: Select Environment
```

Choose from:
- **Auto (recommended)**: Uses project `.venv`/conda if found, otherwise global PATH
- **Workspace only**: Requires a virtual environment in the project
- **Global PATH**: Always uses globally installed executables
- **Custom executables**: Manually specify python and fluxloop-mcp paths

**Or in `.vscode/settings.json`:**
```json
{
  "fluxloop.executionMode": "auto",
  "fluxloop.pythonPath": "/path/to/python",
  "fluxloop.mcpCommandPath": "/path/to/fluxloop-mcp"
}
```

**Check environment status:**
- Use `FluxLoop: Show Environment Info` or `FluxLoop: Run Doctor` from Command Palette
- Or click **Run Doctor** in the Integration view → System Status

**Setting Target Source Root:**
When you select `Target Source Root…` in the Projects view, FluxLoop:
1. Detects virtual environments in that directory
2. Updates FluxLoop Output channel with detected paths
3. Prompts you to review/adjust the environment via Select Environment

See the FluxLoop Output channel for detailed environment logs.

---

## Troubleshooting

### CLI Not Found
Ensure FluxLoop CLI is installed:
```bash
pip install fluxloop-cli
# Or with uv:
uv pip install fluxloop-cli
```

Check the **Status** panel for installation status.

### SDK Not Found
Install the FluxLoop SDK:
```bash
pip install fluxloop
```

The **Status** panel will verify SDK availability in your Python environment.

### fluxloop-mcp Not Found
- Confirm installation: `pip install fluxloop-mcp`
- Verify environment: Run `FluxLoop: Show Environment Info` to check if `fluxloop-mcp` is detected in your project venv or global PATH
- Check with `fluxloop doctor` command for detailed diagnostics
- Rebuild the knowledge index: `packages/mcp/scripts/rebuild_index.sh`
- The **Integration** view shows the package and index state; refresh with **FluxLoop: Refresh Integration View**

### OpenAI Key Prompt Keeps Appearing
- Store the key when prompted (Secret Storage) or set `"fluxloop.openaiApiKey": "sk-..."` in `.vscode/settings.json`
- Review and adjust the model with `"fluxloop.openaiModel": "gpt-4o-mini"` (or any compatible Chat Completions model)

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

