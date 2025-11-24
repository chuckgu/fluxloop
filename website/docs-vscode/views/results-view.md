---
sidebar_position: 4
---

# Results View

Browse and analyze experiment outputs in a structured tree interface.

## Overview

The **Results** view displays all experiment runs from the `experiments/` directory, organized in a hierarchical tree structure. It provides quick access to experiment artifacts and analysis tools.

## Tree Structure

```
Results
├─ Configure Evaluation… (opens configs/evaluation.yaml)
└─ Experiments
   └─ customer_support_test_20251104_143610
      ├─ Parse Results (action)
      ├─ Evaluate Results (action)
      ├─ per_trace_analysis/ (folder, appears after parsing)
      │  ├─ 01_trace_abc123.md
      │  └─ 02_trace_def456.md
      ├─ summary.json
      ├─ traces.jsonl
      ├─ observations.jsonl
      ├─ errors.json
      └─ logs.json
```

## Features

### Experiments Folder

All experiment runs are grouped under a collapsible **Experiments** folder:
- Shows up to 15 most recent experiments
- Sorted newest to oldest by folder name
- Each experiment displays:
  - **Name**: From `summary.json` or folder name
  - **Timestamp**: Formatted as `YYYY-MM-DD HH:MM:SS`
  - **Statistics**: Success rate and run count (if available)

Example label: `customer_support_test` with description `2025-11-04 14:36:10 • 10 runs • 100% success`

### Parse Results Action

Click **Parse Results** inside an experiment folder to generate per-trace Markdown:
1. Prompts for output directory (default: `per_trace_analysis`)
2. Checks if output already exists
3. Confirms overwrite if needed
4. Runs `fluxloop parse experiment <folder> --output <dir>`
5. Refreshes view to show new `per_trace_analysis/` folder

### Evaluate Results Action

Generates evaluator reports defined in `configs/evaluation.yaml`:

1. Prompts for output directory (default: `evaluation`)
2. Confirms overwrite if directory exists
3. Runs `fluxloop evaluate experiment <folder> --output <dir>`
4. Refreshes the tree to show the new `evaluation/` folder

The `evaluation/` folder contains:
- `summary.json`
- `per_trace.jsonl`
- `report.md`
- `report.html` (Phase 2 interactive report)

### Per-Trace Analysis Folder

After parsing, a `per_trace_analysis/` folder appears:
- Contains one Markdown file per trace
- Files are named: `<iteration>_<trace_id>.md`
- Recursively browsable for nested outputs
- Click any file to open in editor

### Artifact Files

Standard experiment output files:
- **summary.json**
- **traces.jsonl**
- **observations.jsonl**
- **errors.json**
- **logs.json**
- **per_trace_analysis/** (appears after parsing)
- **evaluation/** (appears after running Evaluate Results)

Files only appear if present in the experiment directory.

## Actions

### Configure Evaluation

Top-level button that opens `configs/evaluation.yaml` for editing evaluator definitions.

### Parse Results

Appears inside each experiment folder. Executes:
```bash
fluxloop parse experiment <experiment_path> --output <dir> [--overwrite]
```

### Evaluate Results

Runs the evaluator pipeline:
```bash
fluxloop evaluate experiment <experiment_path> --output evaluation [--overwrite]
```

Outputs land in the `evaluation/` folder under the selected experiment.

### Open Files

Click any artifact file to open it in the appropriate editor:
- JSON files: Syntax-highlighted JSON editor
- JSONL files: Line-by-line text view
- Markdown files: Markdown editor with preview support

## File Watchers

The Results view automatically refreshes when:
- New experiments are created in `experiments/`
- Existing experiment files are modified
- Parse operations complete

## Tips

- **Quick Parse**: Use Parse Results directly from the tree instead of Command Palette
- **Timestamp Sorting**: Most recent experiments appear at the top
- **Multi-Parse**: Parse different experiments with different output directories for comparison
- **Nested Analysis**: `per_trace_analysis/` can contain subdirectories; all are browsable

## Related

- [Viewing Results User Guide](../user-guide/viewing-results.md) - Detailed parsing workflow
- [Experiments View](./experiments-view.md) - Running new experiments
- [Workflow Commands](../commands/workflow-commands.md) - Parse command details
