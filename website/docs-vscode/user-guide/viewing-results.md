---
sidebar_position: 4
---

# Viewing Results

View and analyze experiment results in the **Results** view.

## Overview

The **Results** view provides a comprehensive interface for browsing and analyzing experiment outputs. Results are automatically organized by timestamp, making it easy to track your latest experiments.

## Results Structure

### Experiments Folder

All experiment runs appear under a collapsible **Experiments** folder. Each experiment is displayed with:
- **Timestamp**: Extracted from folder name (YYYY-MM-DD HH:MM:SS)
- **Success Rate**: Percentage of successful runs (if available)
- **Experiment Name**: From `summary.json` or folder name

Example:
```
📁 Experiments
  └─ customer_support_test
     2025-11-04 14:36:10 • 100% success
```

### Experiment Contents

Expand any experiment folder to see:

#### Parse Results Action
- **Parse Results** - Click to convert experiment traces into human-readable Markdown
  - Prompts for output directory (default: `per_trace_analysis`)
  - Checks for existing output and confirms overwrite if needed
  - Generates one Markdown file per trace with timeline view

#### Analysis Outputs
- **per_trace_analysis/** - Folder containing parsed Markdown files (appears after parsing)
  - Recursively browsable for nested analysis outputs
  - Click any `.md` file to view formatted trace timeline

#### Artifact Files
- **summary.json** - Aggregate experiment statistics
- **traces.jsonl** - Detailed execution traces for all iterations
- **observations.jsonl** - Observation stream with inputs/outputs
- **errors.json** - Error logs (if any failures occurred)
- **logs.json** - Additional debug and runtime logs

## Parsing Results

### Using Parse Results Action

1. Navigate to **Results** view
2. Expand the experiment folder you want to parse
3. Click **Parse Results** at the top of the file list
4. (Optional) Enter custom output directory or press Enter for default
5. If output exists, confirm whether to overwrite
6. Wait for parsing to complete
7. Expand `per_trace_analysis/` to view generated Markdown files

### Using Command Palette

Alternatively, use:
```
FluxLoop: Parse Experiment
```

This will:
1. Prompt you to select an experiment folder (if not run from tree)
2. Ask for output directory
3. Check for overwrites
4. Execute `fluxloop parse experiment`

### Parse Output Format

Each trace generates a Markdown file with:
- **Trace Metadata**: ID, iteration number, duration
- **Summary**: Success/failure status, error details
- **Timeline**: Chronological observation list with:
  - Observation type and level
  - Timestamps and duration
  - Input and output in formatted JSON blocks

Example filename: `01_trace_abc123.md`

## Opening Result Files

Click any file in the Results view to open it in the editor:
- **JSON files**: Open in VS Code JSON editor with syntax highlighting
- **JSONL files**: Open as text with line-by-line records
- **Markdown files**: Rendered preview available (`Cmd+Shift+V`)

## Tips

- **Latest First**: Experiments are sorted newest to oldest by default
- **Quick Navigation**: Use timestamps to identify specific experiment runs
- **Batch Analysis**: Parse multiple experiments by running Parse Results on each
- **Custom Analysis**: Modify output directory to organize different analysis runs

## Next Steps

- Learn about [Recording Mode](./recording-mode.md) for complex argument replay
- Explore [Experiments View](../views/experiments-view.md) for running new experiments
