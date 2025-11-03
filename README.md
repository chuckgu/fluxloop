<p align="center">
  <img src="fluxloop_logo_tr.png" alt="FluxLoop Logo" width="400"/>
</p>

# FluxLoop OSS

<p align="center">
  <a href="https://github.com/chuckgu/fluxloop"><img src="https://img.shields.io/badge/Status-Active-green" alt="Status"/></a>
  <a href="https://github.com/chuckgu/fluxloop/blob/main/packages/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"/></a>
  <a href="https://pypi.org/project/fluxloop/"><img src="https://img.shields.io/pypi/v/fluxloop" alt="PyPI"/></a>
  <a href="https://github.com/chuckgu/fluxloop/releases"><img src="https://img.shields.io/badge/VSCode-Download_VSIX-007ACC?logo=visualstudiocode" alt="VSCode Extension"/></a>
</p>

## Simulate, Evaluate, and Trust Your AI Agents

**FluxLoop is an open-source toolkit for running reproducible, offline-first simulations of AI agents against dynamic scenarios.** It empowers developers to rigorously test agent behavior, evaluate performance against custom criteria, and build confidence before shipping to production.

### Core Philosophy

- **Local-first simulation**: Run experiments on your machine with full control
- **Framework-agnostic**: Works with any agent framework (LangGraph, LangChain, custom)
- **Argument replay**: Record complex function calls once, replay them hundreds of times
- **Structured artifacts**: Auditable JSON/JSONL outputs following a documented [contract](https://github.com/chuckgu/fluxloop/blob/main/docs/api/json-contract.md)

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
- `trace_summary.jsonl`: Per-trace summary records
- `observations.jsonl`: Observation stream
- `traces.jsonl`: Detailed execution traces

### 🚀 CLI Orchestration
Define complex experiments in YAML, generate input variations with LLM, and run batch simulations—all from the command line.

### 🔌 VSCode Extension
Manage projects, generate inputs, run experiments, and explore results—all from your IDE with visual project management and configuration editing.

**Installation:**
- **Cursor Users**: Download VSIX from [GitHub Releases](https://github.com/chuckgu/fluxloop/releases) and install manually
- **VS Code Users**: Search "FluxLoop" in Extensions Marketplace or install VSIX

---

## 🧭 End-to-End Flow

```
Init → Input Generation → Experiment → Parse → Evaluate (TBD)
                         ↑ (Optional: Record Mode for complex args)
```

This is the canonical workflow. Recording is an optional advanced feature for complex argument structures.

### Runner Integration Patterns (simulation.yaml)

For the final simulation hookup, set `runner` to point at your code. Supported patterns:

1) Module + function
   - module_path/function_name or `target: "module:function"`
2) Class.method (zero-arg constructor)
   - `target: "module:Class.method"`
3) Module-scoped instance method (bound)
   - `target: "module:instance.method"`
4) Class.method with factory (constructor needs dependencies)
   - `target: "module:Class.method"` + `factory: "module:make_instance"` (+ `factory_kwargs`)
5) Async generator targets (streamed responses)
   - Any above can be async generators; CLI will consume stream with `runner.stream_output_path` (default `message.delta`).

See detailed examples: `packages/website/docs-cli/configuration/runner-targets.md`.

## Getting Started

### 1. Install Packages

**Python SDK & CLI:**
```bash
pip install fluxloop-cli fluxloop
```

**VSCode Extension (Optional but Recommended):**

**For Cursor Users:**
1. Download the latest VSIX from [GitHub Releases](https://github.com/chuckgu/fluxloop/releases)
2. Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
3. Type and select **"Extensions: Install from VSIX..."**
4. Select the downloaded `.vsix` file and restart Cursor

**For VS Code Users:**
- Search "FluxLoop" in Extensions Marketplace, or
- Download VSIX and install manually (same as Cursor)

### 2. Initialize Project

```bash
fluxloop init project --name my-agent
cd fluxloop/my-agent
```

**Generated structure (v0.2.0):**
```
fluxloop/
├── .env                      # Global environment variables
└── my-agent/
    ├── configs/              # Separated configuration files
    │   ├── project.yaml      # Project metadata, collector settings
    │   ├── input.yaml        # Personas, base inputs, generation settings
    │   ├── simulation.yaml   # Runner, iterations, replay args
    │   └── evaluation.yaml   # Evaluator definitions
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

### 4. Review Configuration

Edit `configs/input.yaml` to set up personas, base inputs, and LLM provider:

```yaml
# configs/input.yaml
personas:
  - name: novice_user
    description: A user new to the system
    ...

base_inputs:
  - input: "How do I get started?"
    expected_intent: help

input_generation:
  mode: llm
  llm:
    provider: openai
    model: gpt-4o-mini
```

Configure credentials in `.env` or using CLI:

```bash
# Add to .env
OPENAI_API_KEY=sk-...

# Or use CLI helper
fluxloop config set-llm openai sk-xxxx --model gpt-4o-mini
```

### 5. Generate Inputs

```bash
fluxloop generate inputs --limit 50
```

This reads from `configs/input.yaml` and produces `inputs/generated.yaml` with LLM-generated variations.

### 6. Run Experiment

```bash
fluxloop run experiment
```

This loads merged configuration from `configs/` and runs the experiment.

**Results** → `experiments/my_agent_experiment_YYYYMMDD_HHMMSS/`

### 7. Parse Results (Human-Readable)

Convert raw JSONL artifacts into per-trace Markdown timelines:

```bash
fluxloop parse experiment experiments/<your_experiment_dir>
```

Each trace gets a timeline file under `per_trace_analysis/` showing step-by-step inputs/outputs.

---

## 🎬 Argument Replay Workflow (Advanced/Optional)

For agents with complex call signatures (e.g., WebSocket handlers with callbacks), you can record actual arguments and replay them during experiments. **Most projects won't need this feature.**

### Step 1: Enable Recording Mode

```bash
fluxloop record enable
```

This updates `.env` and `configs/simulation.yaml` to enable argument recording.

### Step 2: Execute Your Service

Run your application with recording hooks enabled. Arguments will be saved to `recordings/args_recording.jsonl`.

### Step 3: Disable Recording

```bash
fluxloop record disable
```

Verify recorded data:
```bash
fluxloop record status
```

### Step 4: Configure Replay

Edit `configs/simulation.yaml`:
```yaml
# configs/simulation.yaml
runner:
  target: "app.handler:MessageHandler.handle_message"

replay_args:
  enabled: true
  recording_file: "recordings/args.jsonl"
  callable_providers:
    send_callback: "builtin:collector.send"
    error_callback: "builtin:collector.error"
  override_param_path: "data.content"
```

### Step 5: Run Experiment

```bash
fluxloop run experiment
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
│   ├── sdk/              # Python SDK (decorators, recording, instrumentation)
│   ├── cli/              # CLI tool (init, generate, run, record, parse, status)
│   ├── vscode/           # VSCode/Cursor extension (download VSIX from Releases)
│   ├── website/          # Documentation website (Docusaurus)
│   └── docs/             # Additional guides and references
├── services/
│   └── collector/        # Trace collection service (optional)
└── examples/
    ├── simple-agent/     # Basic agent examples
    └── pluto_duck/       # Complex multi-agent example
```

---

## 📚 Documentation

### Quick Links
- **📖 Full Documentation**: [https://docs.fluxloop.io](https://docs.fluxloop.io) (or see `packages/website/`)
- **CLI Reference**: [packages/cli/README.md](cli/README.md)
- **SDK Reference**: [packages/sdk/README.md](sdk/README.md)
- **VSCode Extension**: [packages/vscode/README.md](vscode/README.md)
  - **Download VSIX**: [GitHub Releases](https://github.com/chuckgu/fluxloop/releases) (for Cursor/VS Code)

### Design Docs
- **v0.2.0 Settings & Recording**: [docs/prd/fluxloop_v0.2.0_settings_recording.md](docs/prd/fluxloop_v0.2.0_settings_recording.md)
- **VSCode Extension Design**: [docs/prd/codex_vscode_extention.md](docs/prd/codex_vscode_extention.md)

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
fluxloop generate inputs --limit 50
fluxloop run experiment
# → Tests function with 50 input variations
```

### Use Case 2: Advanced Recording Workflow

Enable recording, run service to capture args, then use in experiments:
```python
# In your agent code
fluxloop.record_call_args(target="app:Handler.handle", **kwargs)
```

```bash
fluxloop record enable
# ... run your service ...
fluxloop record disable
fluxloop run experiment
# → Replays recorded args with different inputs
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

- **Issues**: Report bugs or suggest features on [GitHub](https://github.com/chuckgu/fluxloop/issues)

---

## 📄 License

FluxLoop is licensed under the [Apache License 2.0](LICENSE).

---

## 🚀 What's Next?

1. **Read the End-to-End Workflow**: [Follow the full pipeline](docs/guides/end-to-end-workflow.md)
2. **Initialize and Run**: Create a project and run an experiment
3. **Parse Results**: Generate human-readable timelines from artifacts
4. **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md) and open an [issue](https://github.com/chuckgu/fluxloop/issues)

**Start simulating your agents today!** 🎯