# FluxLoop OSS

<p align="center">
  <a href="https://github.com/chuckgu/fluxloop"><img src="https://img.shields.io/badge/Status-Active-green" alt="Status"/></a>
  <a href="https://github.com/chuckgu/fluxloop/blob/main/packages/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"/></a>
  <a href="https://discord.gg/your-discord-link"><img src="https://img.shields.io/discord/your-server-id?logo=discord" alt="Discord"/></a>
  <a href="https://twitter.com/your-twitter-handle"><img src="https://img.shields.io/twitter/follow/your-twitter-handle?style=social&label=Follow" alt="Twitter"/></a>
</p>

## Simulate, Evaluate, and Trust Your AI Agents

**FluxLoop is an open-source toolkit for running reproducible, offline-first simulations of AI agents against dynamic scenarios.** It empowers developers to rigorously test agent behavior, evaluate performance against custom criteria, and build confidence before shipping to production. Stop guessing, start simulating.

Our core philosophy is **local-first, framework-agnostic evaluation**. FluxLoop runs on your machine, integrating with your existing agent code via simple decorators. It produces structured, auditable JSON artifacts that describe every step of a simulation, from prompt variations to tool calls and final outputs. These artifacts are your ground truth for performance, and can be consumed by any evaluation backend—including our own upcoming FluxLoop Service for advanced analytics.

## Key Features

- **Simple, decorator-based setup:** Instrument your existing agent code with minimal changes.
- **Framework-agnostic:** Works with any agent framework.
- **Local-first simulation:** Run experiments on your machine with full control. No cloud dependency required.
- **Structured JSON output:** Generate reproducible, auditable artifacts that follow a documented [JSON contract](docs/api/json-contract.md).
- **Extensible evaluation:** Use the generated artifacts with any evaluation tool.
- **Orchestration CLI:** Define and run complex simulation experiments from the command line.
- **VSCode extension:** Manage and monitor your experiments from within your IDE.

This repository contains the core OSS packages: the **SDK**, **CLI**, and **VSCode Extension**.

## Getting Started

1. **Install the CLI and SDK:**
   ```bash
   pip install fluxloop-cli fluxloop-sdk
   ```
2. **Initialize a FluxLoop project:**
   ```bash
   fluxloop init project my-agent-project
   cd my-agent-project
   ```
3. **Instrument your agent:**
   Add the `@fluxloop.agent` decorator to your agent's entry point function.
   ```python
   # examples/simple_agent.py
   import fluxloop_sdk as fluxloop
   
   @fluxloop.agent
   def my_agent(prompt: str) -> str:
     return f"Response to: {prompt}"
   ```
4. **Run an experiment:**
   Configure `fluxloop.yaml` and run your first simulation.
   ```bash
   fluxloop run experiment
   ```

Check out our full documentation and examples to learn more.

## Why Contribute?

Building trustworthy AI requires a community dedicated to rigorous, transparent evaluation. FluxLoop provides the foundational tooling for this task, but there is much more to do. We invite you to join us in building the future of AI agent simulation.

- **Shape the standard:** Help define the open contract for AI agent simulation data.
- **Build new integrations:** Create adapters for popular agent frameworks like LangChain, LlamaIndex, and more.
- **Improve the developer experience:** Enhance the CLI, SDK, and VSCode extension.
- **Develop novel evaluation methods:** Use the structured output to create new ways of measuring agent performance.

We are an early-stage project with an ambitious roadmap. Your contributions can have a massive impact. Check out our [contribution guide](CONTRIBUTING.md) and open issues to get started.

## Community & Support

- Join our community on [Discord](https://discord.gg/your-discord-link) to ask questions, share your projects, and connect with other developers.
- Follow us on [Twitter](https://twitter.com/your-twitter-handle) for project updates.
- Open an issue to report bugs or suggest new features.

## License
FluxLoop is licensed under the [Apache License 2.0](LICENSE).

### Generating Input Sets

Use the CLI to scaffold inputs for review before running an experiment:

```bash
fluxloop generate inputs --config fluxloop.yaml --output inputs/generated.yaml
```

Open the generated file, review or edit the inputs, then point your experiment
configuration at it via the `inputs_file` field.

### Running an Experiment

This will:
