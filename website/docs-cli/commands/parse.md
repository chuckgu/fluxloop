---
sidebar_position: 4
---

# parse Command

Generate human-readable and machine-readable artifacts for each experiment trace.

## Overview

`fluxloop parse experiment` processes the raw outputs produced by `fluxloop run experiment` and creates:

- Markdown files under `per_trace_analysis/*.md` containing per-trace summaries, timelines, and observation details.
- A structured JSONL file at `per_trace_analysis/per_trace.jsonl` that captures summary fields, conversation metadata, and observation timelines for every trace.  
  This file is the canonical input for `fluxloop evaluate` starting with CLI v0.2.26.

Running `parse` is now a required step before evaluation unless you manually supply a compatible `--per-trace` path to the `evaluate` command.

## Basic Usage

```bash
# Parse the latest experiment in ./experiments/demo_run
fluxloop parse experiment experiments/demo_run

# Overwrite an existing per_trace_analysis directory
fluxloop parse experiment experiments/demo_run --overwrite
```

By default the command creates/updates an output directory named `per_trace_analysis` within the experiment folder. Use `--output` to pick a different directory name.

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `experiment_dir` | Path to the experiment output directory | Required |
| `--output`, `-o` | Directory name (relative to `experiment_dir`) where artifacts are written | `per_trace_analysis` |
| `--format`, `-f` | Output format for human-readable files (currently only `md`) | `md` |
| `--overwrite` | Replace the output directory if it already exists | `false` |

## Generated Files

```
per_trace_analysis/
├── 00_trace-1.md          # Markdown summary with timeline, observations, and metadata
├── 01_trace-2.md
└── per_trace.jsonl        # Structured per-trace records consumed by `fluxloop evaluate`
```

Each JSONL entry includes:

- Top-level trace metadata (`trace_id`, `iteration`, `persona`, `input`, `output`, `duration_ms`, `success`)
- A `summary` object mirroring the original `trace_summary.jsonl` row
- A `timeline` array with serialized observations (type, timestamps, inputs/outputs)
- Derived metrics such as `observation_count`

This structure allows downstream tooling to evaluate or analyze multi-turn traces without re-reading large observation logs.

## Relationship to `fluxloop evaluate`

After parsing, run:

```bash
fluxloop evaluate experiment experiments/demo_run
```

`evaluate` automatically looks for `per_trace_analysis/per_trace.jsonl`. If you store the structured file elsewhere, pass its path via `--per-trace`.
