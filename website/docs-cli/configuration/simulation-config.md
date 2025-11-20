---
sidebar_position: 3
---

# Simulation Configuration

Configure experiment execution settings in `configs/simulation.yaml`.

## Overview

The simulation configuration controls how experiments execute:

- **Experiment Identity**: Name and description
- **Execution Settings**: Iterations, parallelism, delays
- **Runner Configuration**: How to call your agent code
- **Recording/Replay**: Argument capture and playback
- **Multi-Turn Mode**: Dynamic conversation extension
- **Output Settings**: Where and what to save

## File Location

```
fluxloop/my-agent/
└── configs/
    └── simulation.yaml    # ← This file
```

## Complete Example

```yaml
# FluxLoop Simulation Configuration
# ------------------------------------------------------------
# Controls how experiments execute (iterations, runner target, output paths).
# Adjust runner module/function to point at your agent entry point.
name: my_agent_experiment
description: AI agent simulation experiment

iterations: 1           # Number of times to cycle through inputs/personas
parallel_runs: 1          # Increase for concurrent execution (ensure thread safety)
run_delay_seconds: 0      # Optional delay between runs to avoid rate limits
seed: 42                  # Set for reproducibility; remove for randomness

runner:
  module_path: "examples.simple_agent"
  function_name: "run"
  target: "examples.simple_agent:run"
  working_directory: .    # Relative to project root; adjust if agent lives elsewhere
  python_path:            # Optional custom PYTHONPATH entries
  timeout_seconds: 120   # Abort long-running traces
  max_retries: 3         # Automatic retry attempts on error

replay_args:
  enabled: false
  recording_file: recordings/args_recording.jsonl
  override_param_path: data.content

multi_turn:
  enabled: false              # Enable to drive conversations via supervisor
  max_turns: 8                # Safety cap on total turns per conversation
  auto_approve_tools: true    # Automatically approve tool calls when supported
  persona_override: null      # Force a specific persona id (optional)
  supervisor:
    provider: openai          # openai (LLM generated) | mock (scripted playback)
    model: gpt-4o-mini
    system_prompt: |
      You supervise an AI assistant supporting customers.
      Review the entire transcript and decide whether to continue.
      When continuing, craft the next user message consistent with the persona.
      When terminating, explain the reason and provide any closing notes.
    metadata:
      scripted_questions: []  # Array of user utterances for sequential playback
      mock_decision: terminate        # Fallback when no scripted questions remain
      mock_reason: script_complete    # Termination reason for scripted runs
      mock_closing: "Thanks for the help. I have no further questions."

output_directory: experiments
save_traces: true
save_aggregated_metrics: true
```

---

## Experiment Settings

### name

**Type:** `string`  
**Required:** Yes  
**Example:** `my_agent_experiment`, `customer_support_test`

Experiment name used in output directories and reports.

```yaml
name: my_agent_experiment
```

**Output Directory:**
```
experiments/my_agent_experiment_20250117_143022/
```

### description

**Type:** `string`  
**Required:** Yes  
**Example:** `Testing customer support agent with various personas`

Human-readable description of the experiment.

---

## Execution Control

### iterations

**Type:** `integer`  
**Default:** `1`  
**Range:** `1-1000`

Number of times to cycle through all inputs.

```yaml
iterations: 10
```

**Formula:**
```
Total Runs = inputs × personas × iterations
```

**Example:**
- 50 inputs
- 2 personas
- 5 iterations
- **Total: 500 runs**

**Use Cases:**

| Iterations | Use Case |
|------------|----------|
| `1` | Quick validation, CI/CD |
| `5-10` | Standard testing |
| `20-50` | Statistical analysis |
| `100+` | Benchmarking, stress testing |

### parallel_runs

**Type:** `integer`  
**Default:** `1`  
**Range:** `1-20`

Number of experiments to run concurrently.

```yaml
parallel_runs: 4  # Run 4 experiments simultaneously
```

**Important:**
- Ensure your agent code is **thread-safe**
- Watch for rate limits from external APIs
- Monitor system resources (CPU, memory)

**Recommended Values:**

| Value | Use Case |
|-------|----------|
| `1` | Default, safest option |
| `2-4` | I/O-bound agents (API calls) |
| `5-10` | CPU-bound agents on multi-core machines |
| `10+` | Distributed systems, cluster environments |

### run_delay_seconds

**Type:** `number`  
**Default:** `0`  
**Range:** `0-60`

Delay between runs (in seconds) to avoid rate limits.

```yaml
run_delay_seconds: 0.5  # 500ms delay between runs
```

**When to Use:**
- Avoid API rate limits (OpenAI, external services)
- Prevent overwhelming downstream systems
- Simulate realistic user pacing

### seed

**Type:** `integer | null`  
**Default:** `42`  
**Example:** `42`, `null`

Random seed for reproducibility.

```yaml
seed: 42      # Deterministic
seed: null    # Random each run
```

**Effects:**
- Input shuffling order
- Sampling decisions
- Any random behavior in your agent

**Use Cases:**

| Value | Use Case |
|-------|----------|
| Fixed (`42`) | Regression testing, CI/CD, reproducible experiments |
| `null` | Discovering edge cases, stress testing |

---

## Runner Configuration

The runner defines how FluxLoop calls your agent code.

### target (Recommended)

**Type:** `string`  
**Format:** `module:function` or `module:Class.method`  
**Example:** `examples.simple_agent:run`

Unified target specification (recommended over separate module_path/function_name).

```yaml
runner:
  target: "examples.simple_agent:run"
```

**Patterns:**

| Pattern | Example | Description |
|---------|---------|-------------|
| `module:function` | `my_agent:run` | Call module-level function |
| `module:Class.method` | `my_agent:Agent.process` | Call static/class method (zero-arg constructor) |
| `module:instance.method` | `my_agent:agent.handle` | Call method on module-level instance |

### module_path

**Type:** `string`  
**Example:** `examples.simple_agent`, `src.agents.customer_support`

Python module path (alternative to `target`).

```yaml
runner:
  module_path: "examples.simple_agent"
  function_name: "run"
```

**Import Behavior:**
```python
from examples.simple_agent import run
```

### function_name

**Type:** `string`  
**Example:** `run`, `process_message`, `handle_request`

Function name to call (used with `module_path`).

```yaml
runner:
  module_path: "examples.simple_agent"
  function_name: "run"
```

### working_directory

**Type:** `string`  
**Default:** `.`  
**Example:** `.`, `src/`, `../agent-code`

Working directory relative to project root.

```yaml
runner:
  working_directory: .
```

**Use Cases:**

| Path | Scenario |
|------|----------|
| `.` | Agent code in project root |
| `src/` | Agent code in subdirectory |
| `../agent-code` | Agent code outside project |

### python_path

**Type:** `list[string] | null`  
**Default:** `null`  
**Example:** `["src", "../shared"]`

Additional directories to add to `PYTHONPATH`.

```yaml
runner:
  python_path:
    - src
    - ../shared-libs
```

**Equivalent to:**
```bash
export PYTHONPATH="src:../shared-libs:$PYTHONPATH"
```

### timeout_seconds

**Type:** `integer`  
**Default:** `120`  
**Range:** `10-3600`

Maximum execution time per run (in seconds).

```yaml
runner:
  timeout_seconds: 180  # 3 minutes
```

**Behavior:**
- If agent exceeds timeout, run is aborted
- Trace marked as `TIMEOUT` status
- Error details captured in observations

**Recommended Values:**

| Timeout | Use Case |
|---------|----------|
| `30` | Simple agents, fast APIs |
| `120` | Standard agents (default) |
| `300-600` | Complex multi-step agents |
| `1800+` | Long-running batch operations |

### max_retries

**Type:** `integer`  
**Default:** `3`  
**Range:** `0-10`

Number of automatic retry attempts on transient errors.

```yaml
runner:
  max_retries: 5
```

**Retry Logic:**
- Exponential backoff between retries
- Only retries on specific error types (network, timeout)
- Does not retry on business logic errors

**Recommended:**

| Value | Use Case |
|-------|----------|
| `0` | No retries, fail fast |
| `3` | Standard (default) |
| `5-10` | Unstable external APIs |

---

## Recording and Replay

### Overview

Recording mode captures actual function arguments during live operation, then replays them during experiments. Useful for:
- Complex signatures (WebSocket handlers, callbacks)
- Non-standard argument passing
- Integration testing with real data

### replay_args.enabled

**Type:** `boolean`  
**Default:** `false`

Enable argument replay mode.

```yaml
replay_args:
  enabled: true
```

### replay_args.recording_file

**Type:** `string`  
**Default:** `recordings/args_recording.jsonl`

Path to JSONL file containing recorded arguments.

```yaml
replay_args:
  recording_file: recordings/args_recording.jsonl
```

**File Format:**
```jsonl
{"args": [], "kwargs": {"data": {"content": "user message"}}, "timestamp": "2025-01-17T14:30:22Z"}
{"args": [], "kwargs": {"data": {"content": "another message"}}, "timestamp": "2025-01-17T14:30:25Z"}
```

### replay_args.override_param_path

**Type:** `string`  
**Default:** `data.content`

Dot-notation path to override with generated input variation.

```yaml
replay_args:
  override_param_path: data.content
```

**Example:**

Original recorded argument:
```python
kwargs = {"data": {"content": "original message"}}
```

With override path `data.content` and generated input `"test input"`:
```python
kwargs = {"data": {"content": "test input"}}  # Overridden
```

### Recording Workflow

**1. Enable recording in .env:**
```bash
FLUXLOOP_RECORD_ARGS=true
FLUXLOOP_RECORDING_FILE=recordings/args_recording.jsonl
```

**2. Run your application normally:**
```bash
# Your agent will record arguments
python my_app.py
```

**3. Configure replay:**
```yaml
replay_args:
  enabled: true
  recording_file: recordings/args_recording.jsonl
  override_param_path: data.content
```

**4. Run experiment:**
```bash
fluxloop run experiment
```

See [Recording Workflow](/cli/workflows/recording-workflow) for details.

---

## Multi-Turn Conversations

### Overview

Multi-turn mode extends single-input experiments into dynamic conversations. Instead of one question and one answer, FluxLoop:

1. Sends initial user message
2. Gets agent response
3. Asks AI supervisor: "Should we continue?"
4. If yes, supervisor generates next realistic user message
5. Repeats until natural completion or `max_turns`

### multi_turn.enabled

**Type:** `boolean`  
**Default:** `false`

Enable multi-turn conversation mode.

```yaml
multi_turn:
  enabled: true
```

### multi_turn.max_turns

**Type:** `integer`  
**Default:** `8`  
**Range:** `2-50`

Maximum conversation turns (safety cap).

```yaml
multi_turn:
  max_turns: 12
```

**What Counts as a Turn:**
- One user message + one agent response = 1 turn

**Recommended:**

| Turns | Use Case |
|-------|----------|
| `3-5` | Quick exchanges |
| `8-12` | Standard conversations (default) |
| `15-30` | Complex troubleshooting |
| `30+` | Extended sessions |

### multi_turn.auto_approve_tools

**Type:** `boolean`  
**Default:** `true`

Automatically approve tool calls (vs prompting user).

```yaml
multi_turn:
  auto_approve_tools: true
```

**Effects:**
- `true`: Tool calls execute automatically
- `false`: Prompt user for approval (not practical in experiments)

### multi_turn.persona_override

**Type:** `string | null`  
**Default:** `null`

Force a specific persona (override input metadata).

```yaml
multi_turn:
  persona_override: expert_user  # All conversations use expert_user
```

**Use Cases:**
- Testing specific persona behavior
- Debugging persona-specific issues
- Controlled experiments

---

## Supervisor Configuration

The supervisor is an LLM that decides when to continue conversations and generates realistic follow-up messages.

### supervisor.provider

**Type:** `string`  
**Options:** `openai` | `mock`  
**Default:** `openai`

Supervisor implementation.

```yaml
supervisor:
  provider: openai  # LLM-driven (dynamic)
  # or
  provider: mock    # Scripted playback (deterministic)
```

**OpenAI Provider:**
- Uses LLM to decide continuation
- Generates contextual follow-ups
- Non-deterministic, realistic

**Mock Provider:**
- Plays back scripted questions
- Deterministic, reproducible
- Perfect for regression testing

### supervisor.model

**Type:** `string`  
**Default:** `gpt-4o-mini`  
**Example:** `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`

LLM model for supervision (OpenAI provider only).

```yaml
supervisor:
  provider: openai
  model: gpt-4o  # More capable, higher cost
  # or
  model: gpt-4o-mini  # Faster, cheaper
```

### supervisor.system_prompt

**Type:** `string | null`  
**Default:** Built-in prompt

Custom system prompt for supervisor.

```yaml
supervisor:
  system_prompt: |
    You supervise a customer support AI for an e-commerce platform.
    
    Review the conversation and decide:
    1. Should we continue? (customer needs more help)
    2. What should the customer say next? (realistic follow-up)
    
    Termination reasons:
    - Issue resolved
    - All questions answered
    - Customer satisfied
    
    When generating follow-ups:
    - Match the persona characteristics
    - Build on conversation history
    - Stay in the service domain
```

**Prompt Guidelines:**
- Explain supervisor role
- Define termination conditions
- Describe follow-up generation strategy
- Reference persona and service context

### supervisor.metadata

**Type:** `object`

Additional supervisor configuration.

#### For Mock Provider (Scripted Playback):

```yaml
supervisor:
  provider: mock
  metadata:
    scripted_questions:
      - "What are your hours?"
      - "Do you offer refunds?"
      - "Thanks, that's all I need."
    mock_decision: terminate
    mock_reason: script_complete
    mock_closing: "Thanks for the help. I have no further questions."
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `scripted_questions` | `list[string]` | Ordered list of user messages |
| `mock_decision` | `string` | What to do when script ends (`terminate`) |
| `mock_reason` | `string` | Termination reason |
| `mock_closing` | `string` | Final user message |

**Behavior:**
1. Plays questions in order
2. When list exhausted, terminates with `mock_decision`
3. Adds `mock_closing` as final message

---

## Output Settings

### output_directory

**Type:** `string`  
**Default:** `experiments`

Directory for experiment outputs (relative to project root).

```yaml
output_directory: experiments
```

**Structure:**
```
experiments/
└── my_agent_experiment_20250117_143022/
    ├── summary.json
    ├── metadata.json
    ├── artifacts/
    │   ├── traces.jsonl
    │   └── observations.jsonl
    └── logs/
```

### save_traces

**Type:** `boolean`  
**Default:** `true`

Save detailed trace data.

```yaml
save_traces: true
```

**Output:**
- `artifacts/traces.jsonl` - Complete trace data
- `artifacts/observations.jsonl` - Observation stream

### save_aggregated_metrics

**Type:** `boolean`  
**Default:** `true`

Save summary statistics.

```yaml
save_aggregated_metrics: true
```

**Output:**
- `summary.json` - Aggregate metrics
- `metadata.json` - Experiment configuration

---

## Complete Examples

### Minimal Configuration

```yaml
name: quick_test
description: Quick validation test
iterations: 1

runner:
  target: "my_agent:run"
```

### Standard Configuration

```yaml
name: agent_test
description: Standard agent testing
iterations: 10
seed: 42

runner:
  target: "examples.simple_agent:run"
  timeout_seconds: 120
  max_retries: 3

output_directory: experiments
save_traces: true
```

### Multi-Turn LLM Supervisor

```yaml
name: conversation_test
description: Multi-turn conversation testing
iterations: 5

runner:
  target: "my_agent:run"
  timeout_seconds: 300

multi_turn:
  enabled: true
  max_turns: 12
  auto_approve_tools: true
  supervisor:
    provider: openai
    model: gpt-4o-mini
    system_prompt: |
      You supervise an AI assistant for a travel booking platform.
      Continue if customer needs more help with flights, hotels, or bookings.
      Terminate when reservation is complete or all questions answered.
```

### Multi-Turn Scripted (Deterministic)

```yaml
name: scripted_conversation
description: Deterministic multi-turn testing
iterations: 1
seed: 42

runner:
  target: "my_agent:run"

multi_turn:
  enabled: true
  max_turns: 5
  supervisor:
    provider: mock
    metadata:
      scripted_questions:
        - "What are your business hours?"
        - "Do you have weekend availability?"
        - "Great, thanks for the info!"
      mock_decision: terminate
      mock_reason: script_complete
```

### With Recording Replay

```yaml
name: replay_test
description: Test with recorded arguments
iterations: 3

runner:
  target: "my_handler:handle_request"
  timeout_seconds: 60

replay_args:
  enabled: true
  recording_file: recordings/production_args.jsonl
  override_param_path: request.body.message

output_directory: experiments
```

### Production Stress Test

```yaml
name: production_stress_test
description: High-volume production simulation
iterations: 100
parallel_runs: 5
run_delay_seconds: 0.1
seed: null  # Random for diversity

runner:
  target: "my_agent:run"
  timeout_seconds: 180
  max_retries: 5

multi_turn:
  enabled: true
  max_turns: 15
  supervisor:
    provider: openai
    model: gpt-4o

output_directory: stress_tests
save_traces: true
save_aggregated_metrics: true
```

---

## CLI Overrides

Override configuration from command line:

```bash
# Basic overrides
fluxloop run experiment --iterations 20

# Multi-turn overrides
fluxloop run experiment \
  --multi-turn \
  --max-turns 15 \
  --auto-approve \
  --supervisor-model gpt-4o \
  --supervisor-temperature 0.3

# Persona override
fluxloop run experiment --persona expert_user
```

---

## Tips and Best Practices

### Development

```yaml
iterations: 1
parallel_runs: 1
save_traces: true
multi_turn:
  enabled: false
```

### Testing

```yaml
iterations: 5-10
seed: 42  # Reproducible
parallel_runs: 2-4
multi_turn:
  enabled: true
  max_turns: 8
  supervisor:
    provider: mock  # Deterministic
```

### Production Validation

```yaml
iterations: 50-100
seed: null  # Explore variations
parallel_runs: 5-10
multi_turn:
  enabled: true
  supervisor:
    provider: openai
    model: gpt-4o
```

---

## See Also

- [Runner Targets](/cli/configuration/runner-targets) - Detailed runner patterns
- [Multi-Turn Workflow](/cli/workflows/multi-turn-workflow) - Complete guide
- [Recording Workflow](/cli/workflows/recording-workflow) - Recording mode
- [run Command](/cli/commands/run) - CLI reference
- [Project Configuration](/cli/configuration/project-config) - Project settings
