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

- **Easy to Use**: Get started quickly with MCP integration and Flux Agent (TBD) for automated setup
- **Local-first**: Run experiments on your machine with full control and reproducibility
- **Framework-agnostic**: Works with any agent framework (LangGraph, LangChain, custom)
- **Evaluation-first**: Solve the AI evaluation problem properly with rigorous, offline-first testing

Stop guessing, start evaluating.

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

## 📦 Packages

FluxLoop consists of multiple integrated packages that work together to provide a complete AI agent testing solution:

### 1. SDK (Python 3.11+)
**Core instrumentation library** for tracing and recording agent execution.

Add `@fluxloop.agent()` decorator to your code to automatically capture traces, observations, and execution context. Supports async, streaming, and complex agent frameworks.

📖 **Documentation**: [https://fluxloop.io/sdk/](https://fluxloop.io/sdk/)  
📦 **PyPI**: [fluxloop](https://pypi.org/project/fluxloop/)

### 2. CLI
**Command-line orchestration tool** for managing experiments end-to-end.

Initialize projects, generate test inputs with LLM, run batch simulations, and parse results into human-readable formats—all from your terminal.

📖 **Documentation**: [https://fluxloop.io/cli/](https://fluxloop.io/cli/)  
📦 **PyPI**: [fluxloop-cli](https://pypi.org/project/fluxloop-cli/)

### 3. VSCode Extension
**Visual project management** for Cursor and VS Code.

Browse projects, run experiments with one click, parse results into Markdown timelines, and explore outputs in a structured tree view—all without leaving your IDE.

📖 **Documentation**: [https://fluxloop.io/vscode/](https://fluxloop.io/vscode/)  
🛒 **Marketplaces**: [VS Code](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop) | [Open VSX (Cursor)](https://open-vsx.org/extension/fluxloop/fluxloop)

### 4. MCP Server (Python 3.11+)
**AI-assisted integration guidance** via Model Context Protocol.

Automatically detect your agent framework, suggest integration patterns, and provide context-aware help for setting up FluxLoop in your codebase.

📖 **Documentation**: [https://fluxloop.io/mcp/](https://fluxloop.io/mcp/)  
📦 **PyPI**: [fluxloop-mcp](https://pypi.org/project/fluxloop-mcp/)

### 5. Flux Agent (TBD)
**Autonomous setup and evaluation agent** (coming soon).

An intelligent agent that automatically instruments your code, generates test scenarios, runs experiments, and provides evaluation insights—fully automated.

🔜 **Status**: In development

---

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

## 🤝 Why Contribute?

Building trustworthy AI requires a community dedicated to rigorous, transparent evaluation. FluxLoop provides the foundational tooling, but there's much more to do:

- **Shape the standard**: Define the open contract for AI agent simulation data
- **Build integrations**: Create adapters for popular frameworks (LangChain, LlamaIndex, CrewAI)
- **Enhance developer experience**: Improve CLI, SDK, and VSCode extension
- **Develop evaluation methods**: Create novel ways of measuring agent performance

We're an early-stage project with an ambitious roadmap. Your contributions can have massive impact.

Check out our [contribution guide](CONTRIBUTING.md) and open issues to get started.

---

## 🚨 Community & Support

- **Issues**: Report bugs or suggest features on [GitHub](https://github.com/chuckgu/fluxloop/issues)

---

## 📄 License

FluxLoop is licensed under the [Apache License 2.0](LICENSE).
