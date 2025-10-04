---
title: End-to-End Workflow (Init → Record → Generate → Configure → Run → Parse)
---

## Overview

This guide walks you through the full FluxLoop workflow on a local machine:

1) Project initialization
2) Recording arguments from a real handler
3) Generating inputs from the recording
4) Configuring the experiment
5) Running the experiment
6) Parsing results into human-readable per-trace files

## 1) Initialize Project

```bash
pip install fluxloop-cli fluxloop
fluxloop init project --name my-agent
cd fluxloop/my-agent
```

Generated structure:

```
fluxloop/
└── my-agent/
    ├── setting.yaml          # Experiment configuration
    ├── .env                  # Project-specific overrides
    ├── experiments/          # Results output
    ├── inputs/               # Generated input datasets
    └── recordings/           # Recorded arguments (optional)
```

## 2) Record Arguments (Staging or Dev)

Record the real kwargs for your target function (e.g., a WebSocket handler) while the code runs.

```python
import fluxloop

fluxloop.configure(record_args=True, recording_file="./recordings/args.jsonl")

class MessageHandler:
    async def handle_message(self, connection_id, data, user_connection, send_callback, error_callback):
        fluxloop.record_call_args(
            target="app.handler:MessageHandler.handle_message",
            connection_id=connection_id,
            data=data,
            user_connection=user_connection,
            send_callback=send_callback,
            error_callback=error_callback,
        )
        # ... your logic ...
```

## 3) Generate Inputs (Local)

```bash
fluxloop generate inputs \
  --config setting.yaml \
  --from-recording recordings/args.jsonl \
  --limit 50
```

This uses the recorded kwargs as a template and produces `inputs/generated.yaml` by default.

## 4) Configure Experiment

Example snippet for `setting.yaml`:

```yaml
runner:
  target: "app.handler:MessageHandler.handle_message"
  working_directory: "."

replay_args:
  enabled: true
  recording_file: "recordings/args.jsonl"
  callable_providers:
    send_callback: "builtin:collector.send"
    error_callback: "builtin:collector.error"
  override_param_path: "data.content"

inputs_file: "inputs/generated.yaml"
iterations: 50
output_directory: "experiments"
```

## 5) Run Experiment

```bash
fluxloop run experiment --config setting.yaml
```

This executes the experiment and writes artifacts into `experiments/<name>_<timestamp>/` including:

- `summary.json`
- `trace_summary.jsonl`
- `observations.jsonl`
- `traces.jsonl`

## 6) Parse Results (Human-Readable)

Use the parse command to convert raw JSONL artifacts into per-trace Markdown timelines:

```bash
fluxloop parse experiment experiments/<your_experiment_dir> --output per_trace_analysis --overwrite
```

Output example:

```
experiments/<your_experiment_dir>/per_trace_analysis/
  ├── 00_<trace-id-1>.md
  ├── 00_<trace-id-2>.md
  └── ...
```

Each Markdown file contains:

- Header: trace metadata (trace_id, persona, duration, success)
- Summary: input and final output
- Timeline: ordered steps with input/output snapshots per observation

## Tips

- Large `observations.jsonl` files are processed via streaming to keep memory usage modest.
- If a timeline step shows `(no data)` for output, that observation did not include an explicit output payload. The final answer is always present in `trace_summary.jsonl` and is reflected in the file Summary block.
- For custom formatting or JSON export, extend `fluxloop parse` with additional `--format` options.


