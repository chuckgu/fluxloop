# FluxLoop CLI

Command-line interface for running AI agent simulations and experiments with argument replay support.

## Installation

```bash
pip install fluxloop-cli
```

## Quick Start

### 1. Initialize a FluxLoop Project

```bash
fluxloop init project --name my-agent
cd fluxloop/my-agent
```

**Scaffold after init:**
```
fluxloop/
├── .env                      # Global environment variables
└── my-agent/
    ├── setting.yaml          # Experiment configuration
    ├── .env                  # (optional) project-specific overrides
    ├── examples/
    │   └── simple_agent.py   # Sample instrumented agent
    ├── experiments/          # Run outputs
    ├── inputs/               # Generated input datasets
    └── recordings/           # (optional) Recorded arguments
```

### 2. Configure Credentials

Set up API keys in `.env`:

```bash
# FluxLoop Collector
FLUXLOOP_COLLECTOR_URL=http://localhost:8000
FLUXLOOP_API_KEY=your-collector-key

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Recording (optional)
FLUXLOOP_RECORD_ARGS=false
FLUXLOOP_RECORDING_FILE=/tmp/fluxloop_args.jsonl
```

Or use the CLI helper:
```bash
fluxloop config set-llm openai sk-xxxx --model gpt-4o-mini
fluxloop config env --show-values  # Verify loaded config
```

---

## 🔄 Two Workflow Modes

### Mode 1: Simple Functions (No Recording)

For agents with simple string inputs:

```python
# examples/simple_agent.py
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    return f"Processed: {input_text}"
```

**Configuration:**
```yaml
# setting.yaml
name: simple_test

runner:
  target: "examples.simple_agent:run"
  working_directory: "."

base_inputs:
  - input: "Hello world"
  - input: "Test message"

iterations: 10
output_directory: "experiments"
```

**Run:**
```bash
fluxloop run experiment --config setting.yaml
```

---

### Mode 2: Complex Methods with Argument Replay

For methods with complex arguments (WebSocket callbacks, session data, etc.):

#### Step 1: Record Arguments (Staging Environment)

```python
# examples/pluto_duck/message_handler.py
import fluxloop

# Reset configuration (handy in tests) and enable recording
fluxloop.reset_config()
fluxloop.configure(record_args=True, recording_file="/tmp/pluto_args.jsonl")

class MessageHandler:
    @fluxloop.agent()
    async def handle_message(
        self,
        connection_id: str,
        data: Dict[str, Any],
        user_connection: Dict[str, Any],
        send_message_callback: Callable,
        send_error_callback: Callable
    ) -> None:
        # Record all arguments
        fluxloop.record_call_args(
            target="examples.pluto_duck.message_handler:MessageHandler.handle_message",
            connection_id=connection_id,
            data=data,
            user_connection=user_connection,
            send_message_callback=send_message_callback,
            send_error_callback=send_error_callback,
        )
        
        # Existing logic...
```

Deploy to staging, send test message, then download:
```bash
scp staging:/tmp/pluto_args.jsonl ./recordings/
```

#### Step 2: Generate Inputs from Recording

```bash
fluxloop generate inputs \
  --config setting.yaml \
  --from-recording recordings/pluto_args.jsonl \
  --limit 50
```

This creates `inputs/generated.yaml` with variations based on the recorded base content.

#### Step 3: Configure Replay

```yaml
# setting.yaml
name: pluto_duck_simulation

runner:
  target: "examples.pluto_duck.message_handler:MessageHandler.handle_message"
  working_directory: "."

# 🎬 Argument Replay
replay_args:
  enabled: true
  recording_file: "recordings/pluto_args.jsonl"
  callable_providers:
    send_message_callback: "builtin:collector.send"
    send_error_callback: "builtin:collector.error"
  override_param_path: "data.content"

inputs_file: "inputs/generated.yaml"
iterations: 50
parallel_runs: 4
```

#### Step 4: Run Simulation

```bash
fluxloop run experiment --config setting.yaml
```

> 💡 **Iteration 필드 다루기**
>
> SDK `0.1.x`는 `fluxloop.record_call_args()` 호출 시 iteration 값을 지정하지 않으면 타깃별로 자동 증가합니다. CLI에서 iteration을 고정하고 싶다면
>
> ```python
> fluxloop.set_recording_options(iteration_auto_increment=False)
> fluxloop.record_call_args(..., iteration=current_iteration)
> ```
>
> 형태로 녹화 코드를 조정하면 됩니다.

---

## 📋 Commands Reference

### `fluxloop init`

Create new projects and agents:

```bash
# Create a new project
fluxloop init project --name my-agent

# Create an agent from template
fluxloop init agent my_agent --template simple
```

### `fluxloop generate`

Generate input variations:

```bash
# Standard generation (from base_inputs)
fluxloop generate inputs --config setting.yaml --limit 20

# From recording (argument replay mode)
fluxloop generate inputs \
  --config setting.yaml \
  --from-recording recordings/args.jsonl \
  --limit 50

# Override strategies
fluxloop generate inputs \
  --config setting.yaml \
  --strategy rephrase \
  --strategy verbose
```

### `fluxloop run`

Execute experiments:

```bash
# Run full experiment
fluxloop run experiment --config setting.yaml

# Without collector
fluxloop run experiment --config setting.yaml --no-collector

# Override iterations
fluxloop run experiment --config setting.yaml --iterations 5

# Single execution for testing
fluxloop run single examples.simple_agent:run "Test input"
```

### `fluxloop status`

Check experiment status:

```bash
fluxloop status check --project my-agent
fluxloop status experiments --project my-agent
fluxloop status traces --project my-agent
```

### `fluxloop config`

Manage configuration:

```bash
# Show current config
fluxloop config show --project my-agent

# Validate config file
fluxloop config validate --config setting.yaml

# Set LLM credentials
fluxloop config set-llm openai sk-xxxx --model gpt-4o-mini

# View environment
fluxloop config env --show-values
```

---

## 📁 Output Structure

After running an experiment:

```
fluxloop/my-agent/
└── experiments/
    └── my_experiment_20250930_150000/
        ├── summary.json       # Statistics and metrics
        ├── traces.jsonl       # Individual trace data (one per line)
        ├── errors.json        # Failure details
        └── artifacts/         # Offline trace cache
```

**summary.json:**
```json
{
  "name": "my_experiment",
  "date": "2025-09-30T15:00:00",
  "results": {
    "total_runs": 100,
    "successful": 98,
    "failed": 2,
    "success_rate": 0.98,
    "avg_duration_ms": 1234.5
  }
}
```

---

## 🎯 Configuration Reference

### Runner Configuration

```yaml
runner:
  # New format (recommended)
  target: "module.path:ClassName.method_name"
  
  # Legacy format (still supported)
  module_path: "module.path"
  function_name: "function_name"
  
  # Environment
  working_directory: "."
  python_path: "/usr/bin/python3"
  environment_vars:
    DATABASE_URL: "postgresql://..."
  
  # Execution
  timeout_seconds: 300
  max_retries: 3
  retry_delay: 5
```

### Replay Args Configuration

```yaml
replay_args:
  enabled: true
  recording_file: "recordings/args.jsonl"
  
  # Map callable parameters to builtin providers
  callable_providers:
    send_message_callback: "builtin:collector.send"
    send_error_callback: "builtin:collector.error"
  
  # Path to override with runtime input (dot notation)
  override_param_path: "data.content"
```

### Input Generation

```yaml
input_generation:
  mode: llm  # or "deterministic"
  llm:
    enabled: true
    provider: openai
    model: gpt-4o-mini
    temperature: 0.7
    max_tokens: 1024
```

---

## 🔍 Environment Variables

```bash
# Core FluxLoop
FLUXLOOP_ENABLED=true
FLUXLOOP_DEBUG=false
FLUXLOOP_COLLECTOR_URL=http://localhost:8000
FLUXLOOP_API_KEY=your-api-key

# Recording
FLUXLOOP_RECORD_ARGS=false
FLUXLOOP_RECORDING_FILE=/tmp/fluxloop_args.jsonl

# Sampling
FLUXLOOP_SAMPLE_RATE=1.0

# Performance
FLUXLOOP_BATCH_SIZE=10
FLUXLOOP_FLUSH_INTERVAL=5.0

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
FLUXLOOP_LLM_API_KEY=sk-...  # Universal fallback
```

---

## 🧪 Testing Your Setup

### Quick Test (No Recording)

```bash
# 1. Create test config
cat > test.yaml << EOF
name: quick_test
runner:
  target: "examples.simple_agent:run"
base_inputs:
  - input: "Hello"
iterations: 1
output_directory: /tmp/test_output
EOF

# 2. Run
fluxloop run experiment --config test.yaml --no-collector

# 3. Check output
cat /tmp/test_output/quick_test_*/summary.json
```

### Test with Recording

```bash
# 1. Create mock recording
cat > /tmp/test_recording.jsonl << EOF
{"_version": "1", "iteration": 0, "target": "examples.simple_agent:run", "kwargs": {"data": {"content": "test"}}, "timestamp": "2025-09-30T00:00:00"}
EOF

# 2. Generate inputs
fluxloop generate inputs \
  --config setting.yaml \
  --from-recording /tmp/test_recording.jsonl \
  --limit 3

# 3. Run
fluxloop run experiment --config setting.yaml --iterations 1 --no-collector
```

---

## 🚨 Troubleshooting

### "Module not found"

**Problem:**
```
ImportError: No module named 'examples.simple_agent'
```

**Solution:**
Set `working_directory` in your config:
```yaml
runner:
  target: "examples.simple_agent:run"
  working_directory: "."  # Or path to your project root
```

### "Recording file not found"

**Problem:**
```
FileNotFoundError: Recording file not found: recordings/args.jsonl
```

**Solution:**
```bash
# Check relative paths are from config file location
ls -lh recordings/args.jsonl

# Use absolute path if needed
replay_args:
  recording_file: "/absolute/path/to/recordings/args.jsonl"
```

### "Missing callable providers"

**Problem:**
```
ValueError: Missing callable providers for recorded parameters: custom_callback
```

**Solution:**
Check your recording and add missing providers:
```bash
# See what callables were recorded
cat recordings/args.jsonl | jq .kwargs | grep '<builtin:'

# Add to config
replay_args:
  callable_providers:
    custom_callback: "builtin:collector.send"
```

---

## 🔗 Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code Quality

```bash
# Linting
ruff check fluxloop_cli

# Formatting
ruff format fluxloop_cli

# Type checking
mypy fluxloop_cli
```

---

## 📚 Documentation

- [SDK Documentation](../sdk/README.md)
- [Pluto Duck Integration](../../docs/guides/pluto-duck-fluxloop-integration.md)
- [Simulation Workflow Guide](../../docs/guides/simulation-workflow-ko.md)
- [Argument Replay PRD](../../docs/prd/argument-replay-system.md)

## License

MIT