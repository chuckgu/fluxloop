<p align="center">
  <img src="fluxloop_logo.png" alt="FluxLoop Logo" width="400"/>
</p>

# FluxLoop OSS

<p align="center">
  <a href="https://github.com/chuckgu/fluxloop"><img src="https://img.shields.io/badge/Status-Active-green" alt="Status"/></a>
  <a href="https://github.com/chuckgu/fluxloop/blob/main/packages/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"/></a>
  <a href="https://pypi.org/project/fluxloop/"><img src="https://img.shields.io/pypi/v/fluxloop?label=SDK" alt="SDK PyPI"/></a>
  <a href="https://pypi.org/project/fluxloop-cli/"><img src="https://img.shields.io/pypi/v/fluxloop-cli?label=CLI" alt="CLI PyPI"/></a>
  <a href="https://pypi.org/project/fluxloop-mcp/"><img src="https://img.shields.io/pypi/v/fluxloop-mcp?label=MCP" alt="MCP PyPI"/></a>
  <a href="https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop"><img src="https://img.shields.io/visual-studio-marketplace/v/fluxloop.fluxloop?label=VS%20Code&logo=visualstudiocode" alt="VS Code Marketplace"/></a>
  <a href="https://open-vsx.org/extension/fluxloop/fluxloop"><img src="https://img.shields.io/open-vsx/v/fluxloop/fluxloop?label=Open%20VSX&logo=eclipseide" alt="Open VSX"/></a>
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

### 🔌 VSCode/Cursor Extension ⭐

<p align="center">
  <img src="cursor.png" alt="FluxLoop Extension in Cursor" width="800"/>
</p>

Manage projects, generate inputs, run experiments, parse results, and explore outputs—all from your IDE with visual project management and configuration editing.

**Key Features:**
- **Parse Results**: Convert experiment traces into human-readable Markdown timelines with one click
- **Execution Wrapper Support**: Seamless integration with `uv run`, `pipx`, and other Python wrappers via `fluxloop.executionWrapper` setting
- **Organized Results**: Browse experiment outputs in a structured tree with timestamps and success rates
- **Multi-environment Support**: Run experiments locally, in Dev Containers, or Docker (coming soon)

**✨ Now Available in Extension Marketplaces!**

- **🎯 Cursor Users**: Search **"FluxLoop"** in Extensions (powered by [Open VSX](https://open-vsx.org/extension/fluxloop/fluxloop))
- **💻 VS Code Users**: Search **"FluxLoop"** in [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop)
- **📦 Manual Install**: Download [VSIX from GitHub Releases](https://github.com/chuckgu/fluxloop/releases) (alternative method)

**✅ Auto-update enabled** for Marketplace installations!

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

### Installation

```bash
# Install Python packages (SDK and MCP require Python 3.11+)
pip install fluxloop fluxloop-cli fluxloop-mcp

# Install VSCode/Cursor Extension
# Search "FluxLoop" in Extensions marketplace
```

📖 **Installation Guides**: [SDK](https://fluxloop.io/sdk/getting-started/sdk-installation) | [CLI](https://fluxloop.io/cli/getting-started/cli-installation) | [VSCode](https://fluxloop.io/vscode/getting-started/installation) | [MCP](https://fluxloop.io/mcp/installation)

### Quick Workflow

```bash
# 1. Create a project
fluxloop init project --name my-agent

# 2. Add @fluxloop.agent() decorator to your code

# 3. Generate test inputs
fluxloop generate inputs --limit 50

# 4. Run experiment
fluxloop run experiment

# 5. Parse results
fluxloop parse experiment experiments/<experiment_dir>
```

📖 **Complete Tutorial**: [End-to-End Workflow Guide](https://fluxloop.io/docs/guides/getting-started)

### What You Can Do

- **🎯 Instrument Agents**: Add decorators to trace execution
- **📝 Generate Inputs**: Create test scenarios with LLM or deterministic strategies
- **🧪 Run Simulations**: Execute batch experiments with different configurations
- **📊 Analyze Results**: Parse structured outputs into human-readable timelines
- **🔴 Record & Replay**: Capture complex arguments and replay them (advanced)
- **🧠 AI-Assisted Setup**: Use MCP server for framework detection and integration guidance

---

## 🎬 Advanced Features

### Argument Replay Workflow (Optional)

For agents with complex call signatures (WebSocket handlers, callbacks, etc.), FluxLoop supports recording and replaying actual arguments during experiments.

📖 **Full Guide**: [Argument Replay Documentation](https://fluxloop.io/cli/workflows#argument-replay)

**Quick Overview:**
```bash
fluxloop record enable   # Start recording
# Run your application
fluxloop record disable  # Stop recording
fluxloop run experiment  # Replay with variations
```

---

## 📦 Repository Structure

```
fluxloop/
├── packages/
│   ├── sdk/              # Python SDK (decorators, recording, instrumentation)
│   ├── cli/              # CLI tool (init, generate, run, record, parse, status)
│   ├── mcp/              # MCP Server (AI-assisted integration guidance)
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
- **📖 Full Documentation**: [https://fluxloop.io](https://fluxloop.io)
- **SDK Documentation**: [https://fluxloop.io/sdk](https://fluxloop.io/sdk) - Python 3.11+ (v0.1.3)
- **CLI Documentation**: [https://fluxloop.io/cli](https://fluxloop.io/cli) - (v0.2.1)
- **VSCode Extension**: [https://fluxloop.io/vscode](https://fluxloop.io/vscode) - (v0.1.1)
  - **VS Code Marketplace**: [Install from Marketplace](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop)
  - **Open VSX** (Cursor): [Install from Open VSX](https://open-vsx.org/extension/fluxloop/fluxloop)
  - **Manual**: [Download VSIX from Releases](https://github.com/chuckgu/fluxloop/releases)
- **MCP Server**: [https://fluxloop.io/mcp](https://fluxloop.io/mcp) - Python 3.11+ (v0.1.0)
  - **PyPI**: [fluxloop-mcp](https://pypi.org/project/fluxloop-mcp/)

### Design Docs
- **v0.2.0 Settings & Recording**: [docs/prd/fluxloop_v0.2.0_settings_recording.md](docs/prd/fluxloop_v0.2.0_settings_recording.md)
- **VSCode Extension Design**: [docs/prd/codex_vscode_extention.md](docs/prd/codex_vscode_extention.md)
- **MCP Server Plan**: [docs/prd/mcp_server_plan.md](docs/prd/mcp_server_plan.md)

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

📖 **Detailed Examples & Tutorials**: [FluxLoop Documentation](https://fluxloop.io/docs)

### Simple Agent Testing
```python
@fluxloop.agent()
def run(input_text: str) -> str:
    return process(input_text)
```

### Multi-Agent Orchestration
```python
@fluxloop.agent()
async def orchestrator(...):
    result = await planner_agent.plan(...)
    await executor_agent.execute(...)
    return result
```

**Learn More**:
- [SDK Quick Start](https://fluxloop.io/sdk/getting-started/basic-usage)
- [CLI Workflows](https://fluxloop.io/cli/workflows)
- [Framework Integration](https://fluxloop.io/sdk/framework-integration)

---

## 🚨 Community & Support

- **Issues**: Report bugs or suggest features on [GitHub](https://github.com/chuckgu/fluxloop/issues)

---

## 📄 License

FluxLoop is licensed under the [Apache License 2.0](LICENSE).

---

## 🚀 What's Next?

1. **📖 Read the Documentation**: [https://fluxloop.io](https://fluxloop.io)
2. **🎯 Quick Start**: [SDK Installation](https://fluxloop.io/sdk/getting-started/sdk-installation) & [CLI Setup](https://fluxloop.io/cli/getting-started/cli-installation)
3. **🧠 AI-Assisted Integration**: Try the [MCP Server](https://fluxloop.io/mcp) for automated setup guidance
4. **🤝 Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md) and open an [issue](https://github.com/chuckgu/fluxloop/issues)

**Start simulating your agents today!** 🎯