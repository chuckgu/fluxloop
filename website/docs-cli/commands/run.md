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
| `--config`, `-c` | Path to configuration file | `configs/simulation.yaml` |
| `--project` | Project name under FluxLoop root | Current directory |
| `--root` | FluxLoop root directory | `./fluxloop` |
| `--iterations`, `-i` | Number of runs per input | From config |
| `--personas`, `-p` | Comma-separated list of personas to use | All personas |
| `--multi-turn/--no-multi-turn` | Enable/disable multi-turn conversations | From config |
| `--max-turns` | Maximum turns per conversation | From config |
| `--auto-approve-tools/--manual-approve-tools` | Tool approval behavior | From config |
| `--persona-override` | Force specific persona ID for multi-turn | None |
| `--supervisor-provider` | Override supervisor provider (openai, anthropic, mock) | From config |
| `--supervisor-model` | Override supervisor model | From config |
| `--supervisor-temperature` | Override supervisor temperature | From config |
| `--supervisor-api-key` | API key for supervisor calls | From env |
| `--output-dir` | Output directory for results | `experiments/` |
| `--experiment-name` | Custom experiment name | Auto-generated |
| `--yes`, `-y` | Skip confirmation prompt (for CI/automation) | `false` |

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
fluxloop run experiment --experiment-name "baseline-test"
```

### Skip Confirmation (CI Mode)

Run without interactive prompt for automation:

```bash
fluxloop run experiment --yes

# Or short form
fluxloop run experiment -y
```

This is ideal for CI/CD pipelines and pytest integration.

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
  "experiment_name": "my_agent_experiment",
  "total_traces": 100,
  "successful": 98,
  "failed": 2,
  "avg_duration_ms": 250.5,
  "started_at": "2024-11-01T14:30:22Z",
  "completed_at": "2024-11-01T14:35:10Z",
  "config_snapshot": {...}
}
```

### trace_summary.jsonl

One line per trace with summary information:

```jsonl
{"trace_id": "trace_001", "iteration": 0, "persona": "novice_user", "input": "How do I start?", "output": "...", "duration_ms": 245, "success": true}
{"trace_id": "trace_002", "iteration": 1, "persona": "expert_user", "input": "What are options?", "output": "...", "duration_ms": 267, "success": true}
```

### observations.jsonl (optional)

Detailed observation stream with all events:

```jsonl
{"trace_id": "trace_001", "type": "span_start", "timestamp": "...", "name": "agent_run", ...}
{"trace_id": "trace_001", "type": "span_end", "timestamp": "...", "name": "agent_run", ...}
```

## Multi-Turn Conversations

FluxLoop supports extending single inputs into dynamic multi-turn conversations using a supervisor agent.

### Enable Multi-Turn Mode

```bash
# Enable multi-turn with defaults
fluxloop run experiment --multi-turn

# Set maximum turns
fluxloop run experiment --multi-turn --max-turns 12

# Auto-approve tools during conversation
fluxloop run experiment --multi-turn --auto-approve-tools
```

### Supervisor Configuration

The supervisor decides when to continue the conversation and generates realistic follow-up questions.

**LLM-Driven Supervisor (Dynamic):**

```bash
# Use OpenAI for supervisor decisions
fluxloop run experiment --multi-turn \
  --supervisor-provider openai \
  --supervisor-model gpt-4o \
  --supervisor-temperature 0.7
```

**Mock Supervisor (Scripted Playback):**

For deterministic testing, use scripted questions:

```yaml
# configs/simulation.yaml
multi_turn:
  enabled: true
  supervisor:
    provider: mock
    metadata:
      scripted_questions:
        - "Can you explain more?"
        - "What about edge cases?"
        - "How does error handling work?"
```

```bash
# Run with scripted questions
fluxloop run experiment --multi-turn --supervisor-provider mock
```

The mock supervisor replays questions sequentially and terminates when the script ends.

### Multi-Turn Options

| Option | Description | Use Case |
|--------|-------------|----------|
| `--multi-turn` | Enable multi-turn mode | Dynamic conversations |
| `--max-turns` | Limit conversation depth | Prevent infinite loops |
| `--auto-approve-tools` | Auto-approve tool calls | Reduce manual intervention |
| `--persona-override` | Force specific persona | Consistent testing |
| `--supervisor-provider` | Supervisor LLM provider | openai, anthropic, mock |
| `--supervisor-model` | Supervisor model name | gpt-4o, claude-3-5-sonnet |
| `--supervisor-temperature` | Sampling temperature | 0.0-1.0 |
| `--supervisor-api-key` | API key for supervisor | Override env var |

### Output for Multi-Turn

Multi-turn experiments produce additional fields:

- `conversation_state`: Current state (active, completed, terminated)
- `termination_reason`: Why conversation ended (max_turns, supervisor_stop, error)
- `turn_count`: Number of turns executed
- `conversation_history`: Full dialogue transcript

See [Multi-Turn Workflow](/cli/workflows/multi-turn-workflow) for detailed guide.

---

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
