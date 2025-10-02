<p align="center">
  <img src="fluxloop_logo_tr.png" alt="FluxLoop Logo" width="400"/>
</p>

# FluxLoop OSS

<p align="center">
  <a href="https://github.com/chuckgu/fluxloop"><img src="https://img.shields.io/badge/Status-Active-green" alt="Status"/></a>
  <a href="https://github.com/chuckgu/fluxloop/blob/main/packages/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"/></a>
  <a href="https://discord.gg/your-discord-link"><img src="https://img.shields.io/discord/your-server-id?logo=discord" alt="Discord"/></a>
  <a href="https://twitter.com/your-twitter-handle"><img src="https://img.shields.io/twitter/follow/your-twitter-handle?style=social&label=Follow" alt="Twitter"/></a>
</p>

## Simulate, Evaluate, and Trust Your AI Agents

**FluxLoop is an open-source toolkit for running reproducible, offline-first simulations of AI agents against dynamic scenarios.** It empowers developers to rigorously test agent behavior, evaluate performance against custom criteria, and build confidence before shipping to production.

### Core Philosophy

- **Local-first simulation**: Run experiments on your machine with full control
- **Framework-agnostic**: Works with any agent framework (LangGraph, LangChain, custom)
- **Argument replay**: Record complex function calls once, replay them hundreds of times
- **Structured artifacts**: Auditable JSON/JSONL outputs following a documented [contract](docs/api/json-contract.md)

Stop guessing, start simulating.

---

## Key Features

### 🎯 Simple Decorator-Based Setup
Instrument existing agent code with minimal changes—just add `@fluxloop.agent()` and you're tracing.

### 🔄 Argument Replay System
Record complex function arguments (WebSocket callbacks, session data, etc.) from staging, then replay them locally with different content. No manual mocking required.

### 🧪 Offline-First Simulation
Run experiments on your machine without cloud dependencies. Generate structured artifacts that work with any evaluation backend.

### 📊 Structured JSON Output
Every simulation produces reproducible, auditable artifacts:
- `summary.json`: Aggregate statistics
- `traces.jsonl`: Detailed execution traces
- `errors.json`: Failure analysis

### 🚀 CLI Orchestration
Define complex experiments in YAML, generate input variations with LLM, and run batch simulations—all from the command line.

### 🔌 VSCode Extension
Manage experiments, monitor runs, and explore results directly in your IDE.

---

## Getting Started

### 1. Install Packages

```bash
pip install fluxloop-cli fluxloop
```

### 2. Initialize Project

```bash
fluxloop init project --name my-agent
cd fluxloop/my-agent
```

**Generated structure:**
```
fluxloop/
├── .env                      # Global environment variables
└── my-agent/
    ├── setting.yaml          # Experiment configuration
    ├── .env                  # Project-specific overrides
    ├── examples/
    │   └── simple_agent.py   # Sample instrumented agent
    ├── experiments/          # Results output
    ├── inputs/               # Generated input datasets
    └── recordings/           # Recorded arguments (optional)
```

### 3. Instrument Your Agent

Add the `@fluxloop.agent` decorator to your agent's entry point:

```python
# examples/simple_agent.py
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    return f"Response to: {input_text}"
```

### 4. Configure Credentials

```bash
# Add to .env
FLUXLOOP_COLLECTOR_URL=http://localhost:8000
OPENAI_API_KEY=sk-...

# Or use CLI helper
fluxloop config set-llm openai sk-xxxx --model gpt-4o-mini
```

### 5. Generate Inputs

```bash
fluxloop generate inputs --config setting.yaml --limit 20
```

### 6. Run Experiment

```bash
fluxloop run experiment --config setting.yaml
```

**Results** → `experiments/my_agent_experiment_YYYYMMDD_HHMMSS/`

---

## 🎬 Argument Replay Workflow

For complex agents with many parameters (e.g., WebSocket handlers, class methods):

### Step 1: Record (Staging)

```python
import fluxloop

# Enable recording
fluxloop.configure(record_args=True, recording_file="/tmp/args.jsonl")

class MessageHandler:
    async def handle_message(
        self,
        connection_id: str,
        data: Dict[str, Any],
        user_connection: Dict[str, Any],
        send_callback: Callable,
        error_callback: Callable
    ):
        # Record arguments
        fluxloop.record_call_args(
            target="app.handler:MessageHandler.handle_message",
            connection_id=connection_id,
            data=data,
            user_connection=user_connection,
            send_callback=send_callback,
            error_callback=error_callback,
        )
        # ... existing logic
```

Deploy to staging, trigger a test request, then download:
```bash
scp staging:/tmp/args.jsonl ./recordings/
```

### Step 2: Generate (Local)

```bash
fluxloop generate inputs \
  --config setting.yaml \
  --from-recording recordings/args.jsonl \
  --limit 50
```

### Step 3: Configure (Local)

```yaml
# setting.yaml
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
```

### Step 4: Simulate (Local)

```bash
fluxloop run experiment --config setting.yaml
```

The CLI will:
1. Load recorded kwargs
2. Override `data.content` with each generated input
3. Restore callable objects
4. Execute real logic with actual code paths

**Benefits:**
- ✅ No manual mock construction
- ✅ Real code execution (not mocked)
- ✅ Different LLM responses every iteration
- ✅ Production-like argument structures

---

## 📦 Repository Structure

```
fluxloop/
├── packages/
│   ├── sdk/              # Python SDK (decorators, recording)
│   ├── cli/              # CLI tool (generate, run, status)
│   └── vscode/           # VSCode extension
├── services/
│   └── collector/        # Trace collection service
├── examples/
│   ├── simple-agent/     # Basic examples
│   └── pluto_duck/       # Complex multi-agent example
└── docs/
    ├── guides/           # Integration guides
    ├── prd/              # Product specs
    └── api/              # API contracts
```

---

## 📚 Documentation

- **Quick Start**: [5-Minute Guide](../docs/guides/fluxloop-quick-start.md)
- **SDK Reference**: [SDK README](sdk/README.md)
- **CLI Reference**: [CLI README](cli/README.md)
- **Pluto Duck Integration**: [Integration Guide](../docs/guides/pluto-duck-fluxloop-integration.md)
- **Argument Replay PRD**: [System Design](../docs/prd/argument-replay-system.md)
- **Simulation Workflow**: [Korean Guide](../docs/guides/simulation-workflow-ko.md)

---

## 🤝 Why Contribute?

Building trustworthy AI requires a community dedicated to rigorous, transparent evaluation. FluxLoop provides the foundational tooling, but there's much more to do:

- **Shape the standard**: Define the open contract for AI agent simulation data
- **Build integrations**: Create adapters for popular frameworks (LangChain, LlamaIndex, CrewAI)
- **Enhance developer experience**: Improve CLI, SDK, and VSCode extension
- **Develop evaluation methods**: Create novel ways of measuring agent performance

We're an early-stage project with an ambitious roadmap. Your contributions can have massive impact.

Check out our [contribution guide](CONTRIBUTING.md) and open issues to get started.

---

## 🌟 Example Use Cases

### Use Case 1: Simple Agent Testing

```python
@fluxloop.agent()
def run(input_text: str) -> str:
    return process(input_text)
```

```bash
fluxloop run experiment --config setting.yaml
# → Tests function with 50 input variations
```

### Use Case 2: Complex WebSocket Handler

Record from staging:
```python
fluxloop.record_call_args(target="app:Handler.handle", **all_args)
```

Replay locally:
```bash
fluxloop generate inputs --from-recording recordings/args.jsonl --limit 100
fluxloop run experiment --config setting.yaml
# → Simulates 100 realistic scenarios offline
```

### Use Case 3: Multi-Agent System

```python
@fluxloop.agent()
async def orchestrator(...):
    result = await planner_agent.plan(...)
    await executor_agent.execute(...)
    return result
```

Trace the entire flow with hierarchical observations.

---

## 🚨 Community & Support

- **Discord**: Join our [community](https://discord.gg/your-discord-link) for questions and discussions
- **Twitter**: Follow [@your-handle](https://twitter.com/your-twitter-handle) for updates
- **Issues**: Report bugs or suggest features on [GitHub](https://github.com/chuckgu/fluxloop/issues)

---

## 📄 License

FluxLoop is licensed under the [Apache License 2.0](LICENSE).

---

## 🚀 What's Next?

1. **Try the Quick Start**: [Get running in 5 minutes](../docs/guides/fluxloop-quick-start.md)
2. **Explore Examples**: Check out `examples/` for real-world patterns
3. **Read the Guides**: Deep-dive into [integration guides](../docs/guides/)
4. **Join the Community**: Connect with other FluxLoop users

**Start simulating your agents today!** 🎯