---
sidebar_position: 2
---

# Workflow Commands

Commands for managing the FluxLoop experiment workflow.

## FluxLoop: Generate Inputs

**Command ID:** `fluxloop.generateInputs`

Generate input variations from base inputs defined in `configs/input.yaml`.

### Usage

1. Open Command Palette (`Cmd+Shift+P`)
2. Type and select **FluxLoop: Generate Inputs**
3. Follow the wizard prompts:
   - **Mode**: Deterministic or LLM-based generation
   - **Base Input Confirmation**: Review the primary base input from `configs/input.yaml`
     - **Use Input**: Proceed with the displayed base input
     - **Edit in configuration**: Open `configs/input.yaml` to modify
   - **Strategies**: Select variation strategies (pre-checked based on config)
     - Selections are saved back to `variation_strategies` in `configs/input.yaml`
   - **Limit**: Maximum number of inputs to generate (optional)
   - **Overwrite**: Whether to replace existing output file
   - **Dry Run**: Preview generation without writing files
   - **LLM API Key**: Required for LLM mode (saved to VS Code secrets and `.env`)

### Output

Generated inputs are written to the file specified in `configs/input.yaml` (default: `inputs/generated.yaml`).

### Options

- **Mode**:
  - `deterministic`: Rule-based variations without LLM
  - `llm`: AI-powered variations using configured LLM provider

- **Strategies**: `rephrase`, `error_prone`, `typo`, `verbose`, `concise`, `persona_based`, `adversarial`, `multilingual`, `custom`

## FluxLoop: Run Experiment

**Command ID:** `fluxloop.runExperiment`

Execute an experiment based on `configs/simulation.yaml`.

### Usage

1. Open Command Palette
2. Select **FluxLoop: Run Experiment**
3. Choose execution environment:
   - **Local Python**: Run with current Python environment
   - **Dev Container**: Run inside active Dev Container
   - **Docker**: Coming soon (shows info message)
4. (Optional) Override iteration count

### Execution

Runs `fluxloop run experiment [--iterations N]` in a new terminal at the project root.

### Environment Selection

The extension remembers your last selected environment. Change the default via:
```
FluxLoop: Select Execution Environment
```

Or manually in settings:
```json
{
  "fluxloop.defaultEnvironment": "Local Python"
}
```

### Execution Wrapper

If you use `uv`, `pipx`, or similar wrappers, configure via:
```
FluxLoop: Configure Execution Wrapper
```

Enter prefix (e.g., `uv run`) to prepend to all CLI commands.

## FluxLoop: Parse Experiment

**Command ID:** `fluxloop.parseExperiment`

Convert experiment traces into human-readable Markdown timelines.

### Usage

1. Open Command Palette
2. Select **FluxLoop: Parse Experiment**
3. If not invoked from Results view, select experiment folder from list
4. Enter output directory (default: `per_trace_analysis`)
5. Confirm overwrite if output already exists

### Output

Generates one Markdown file per trace in the specified output directory:
- Filename format: `<iteration>_<trace_id>.md`
- Contains trace metadata, summary, and chronological observation timeline
- Appears in Results view under `per_trace_analysis/` folder

### CLI Equivalent

```bash
fluxloop parse experiment experiments/<folder> --output per_trace_analysis [--overwrite]
```

---

## FluxLoop: Evaluate Experiment

**Command ID:** `fluxloop.evaluateExperiment`

Run rule-based and LLM-based evaluators defined in `configs/evaluation.yaml`, compute success criteria, and generate Markdown/HTML reports.

### Usage

1. Open Command Palette
2. Select **FluxLoop: Evaluate Experiment**
3. Choose the experiment folder (if not triggered from Results view)
4. **Goal Confirmation**: Review the evaluation goal from `configs/evaluation.yaml`
   - **Use Goal**: Proceed with the displayed evaluation goal
   - **Edit in configuration**: Open `configs/evaluation.yaml` to modify
5. Choose evaluation output directory (default: `evaluation`)
6. Confirm overwrite if the directory already exists

### Goal Confirmation

The wizard reads `evaluation_goal.text` from `configs/evaluation.yaml`:

```yaml
evaluation_goal:
  text: "Verify that the agent provides clear, persona-aware responses while meeting latency and accuracy targets."
```

This step ensures you're evaluating against the intended criteria before running.

### Output

Produces:

- `evaluation/summary.json` – Aggregate stats, success criteria, persona/outlier/trend/baseline analysis
- `evaluation/per_trace.jsonl` – Per-trace scores + reasons
- `evaluation/report.md` – Markdown report
- `evaluation/report.html` – Interactive report with charts (Phase 2)

### CLI Equivalent

```bash
fluxloop evaluate experiment experiments/<folder> --output evaluation [--overwrite]
```

## FluxLoop: Run Single Execution

**Command ID:** `fluxloop.runSingle`

Run a single agent execution with custom input.

### Usage

1. Open a Python file containing your agent
2. Open Command Palette
3. Select **FluxLoop: Run Single Execution**
4. Enter function name (default: `run`)
5. Enter input text for the agent

### Requirements

- Active Python file must be within the selected FluxLoop project
- Function must accept input as first argument

### CLI Equivalent

```bash
fluxloop run single <module_path> "<input>" --function <function_name>
```

## FluxLoop: Show Status

**Command ID:** `fluxloop.showStatus`

Check CLI and SDK installation status, along with current configuration.

### Usage

Open Command Palette and select **FluxLoop: Show Status**.

Output is displayed in the integrated terminal.

### CLI Equivalent

```bash
fluxloop status check --verbose
```

## Related

- [Recording Commands](./recording-commands.md) - Argument recording workflow
- [Project Commands](./project-commands.md) - Project management
- [Results View](../views/results-view.md) - Viewing experiment outputs
