---
sidebar_position: 3
---

# run Command

Execute simulation experiments with your agent.

## Usage

```bash
fluxloop run experiment [OPTIONS]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--iterations` | Number of runs per input | From config |
| `--inputs` | Input file path | `inputs/generated.yaml` |
| `--output-dir` | Output directory | `experiments/` |
| `--name` | Experiment name | Auto-generated |

## Examples

### Basic Experiment

Run with default settings:

```bash
fluxloop run experiment
```

### Custom Iterations

Override iteration count:

```bash
fluxloop run experiment --iterations 20
```

### Named Experiment

Give your experiment a name:

```bash
fluxloop run experiment --name "baseline-test"
```

### Custom Input File

Use different input file:

```bash
fluxloop run experiment --inputs my-custom-inputs.yaml
```

## How It Works

### 1. Load Configuration

Reads `configs/simulation.yaml`:

```yaml
runner:
  target: "examples.my_agent:run"
  iterations: 10

output:
  directory: "experiments"
  format: jsonl
```

### 2. Load Inputs

Loads generated inputs from `inputs/generated.yaml`:

```yaml
generated_inputs:
  - input: "How do I start?"
    persona: novice_user
  - input: "What are advanced options?"
    persona: expert_user
```

### 3. Execute Agent

For each input, runs your agent `iterations` times:

```python
# Your agent (examples/my_agent.py)
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    return process(input_text)
```

### 4. Collect Traces

Captures:
- Input/output pairs
- Execution time
- Observations
- Errors (if any)

### 5. Save Results

Outputs to `experiments/experiment_YYYYMMDD_HHMMSS/`:

```
experiments/my_agent_20241101_143022/
├── summary.json           # Aggregate stats
├── trace_summary.jsonl    # Per-trace summaries
├── traces.jsonl           # Detailed traces
├── observations.jsonl     # Observation stream
└── config.yaml            # Experiment config snapshot
```

## Output Files

### summary.json

Aggregate statistics:

```json
{
  "total_traces": 100,
  "successful": 98,
  "failed": 2,
  "avg_duration_ms": 250.5,
  "started_at": "2024-11-01T14:30:22Z",
  "completed_at": "2024-11-01T14:35:10Z"
}
```

### trace_summary.jsonl

One line per trace:

```jsonl
{"trace_id": "trace_001", "input": "How do I start?", "output": "...", "duration_ms": 245}
{"trace_id": "trace_002", "input": "What are options?", "output": "...", "duration_ms": 267}
```

### traces.jsonl

Complete trace data with all observations.

## Configuration

### Runner Target

Point to your agent function:

```yaml
runner:
  target: "examples.my_agent:run"  # module:function
```

### Iterations

Number of times to run each input:

```yaml
runner:
  iterations: 10  # Run each input 10 times
```

Why multiple iterations?
- Measure consistency
- Account for LLM randomness
- Statistical significance

## Argument Replay (Advanced)

Replay recorded arguments:

```yaml
replay_args:
  enabled: true
  recording_file: "recordings/args.jsonl"
  override_param_path: "data.content"
```

See [Recording Workflow](../workflows/recording-workflow) for details.

## Progress Tracking

The command shows real-time progress:

```
[INFO] Starting experiment...
[INFO] Loaded 50 inputs
[INFO] Running 10 iterations per input (500 total runs)
[▓▓▓▓▓▓▓▓░░] 250/500 (50%) - ETA: 2m 15s
```

## Error Handling

### Graceful Failures

If an agent run fails:
- Error is captured in trace
- Experiment continues with next input
- Summary shows failure count

### Critical Failures

If configuration is invalid:
- Experiment stops immediately
- Error message shows what to fix

## Performance Tips

### Parallel Execution (Coming Soon)

```bash
fluxloop run experiment --parallel 4  # Run 4 agents in parallel
```

### Batch Processing

For large input sets, split into batches:

```bash
# Generate in batches
fluxloop generate inputs --limit 100 --output inputs/batch1.yaml
fluxloop generate inputs --limit 100 --output inputs/batch2.yaml

# Run separately
fluxloop run experiment --inputs inputs/batch1.yaml --name batch1
fluxloop run experiment --inputs inputs/batch2.yaml --name batch2
```

## Next Steps

- [Parse Command](./parse) - Convert results to readable format
- [Simulation Config](../configuration/simulation-config) - Configure runner settings
- [Workflows](../workflows/basic-workflow) - End-to-end examples
