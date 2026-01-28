---
sidebar_position: 1
slug: /
---

# FluxLoop CLI

Command-line interface for managing FluxLoop projects, generating test inputs, and running agent simulations with Web Platform integration.

## Installation

```bash
pip install fluxloop-cli
```

## Features

- 🎯 **Project Management**: Initialize and configure agent testing projects
- 📝 **Input Generation**: Create test input variations using LLMs
- 🧪 **Agent Testing**: Run batch simulations locally and capture traces
- ☁️ **Cloud Integration**: Sync scenarios and upload results to [app.fluxloop.ai](https://app.fluxloop.ai)
- ⚙️ **Flexible Configuration**: Simple YAML-based configuration for runners and targets
- 🤝 **Team Collaboration**: Share test results and scenarios with your team

## Quick Start

```bash
# 1. Initialize a new project
fluxloop init scenario --name my-agent
cd my-agent

# 2. Authenticate with Web Platform
fluxloop auth login

# 3. Generate test inputs
fluxloop generate --limit 20

# 4. Run tests
fluxloop test

# 5. Upload results
fluxloop sync upload
```

## Key Command Groups

### Project Initialization
`fluxloop init` - Create new projects or initialize existing ones.

### Authentication & Sync
`fluxloop auth` - Manage authentication with the Web Platform.
`fluxloop pull` - Download scenarios, criteria, and bundles from the cloud.
`fluxloop upload` - Upload results, local scenarios, and bundles to the cloud.

### Testing Workflow
`fluxloop generate` - Generate synthetic test inputs.
`fluxloop test` - Execute agent tests locally.
`fluxloop status` - Check project and test status.

### Input Management
`fluxloop personas` - Manage test personas.
`fluxloop inputs` - Manage base and generated inputs.
`fluxloop bundles` - Manage test input bundles.

## Configuration

FluxLoop CLI uses `fluxloop.yaml` for project configuration:

```yaml
# fluxloop.yaml
project:
  name: my-agent
  version: "1.0.0"

runner:
  target: "src.agent:run"
  type: python-function

test:
  iterations: 1
  parallel: 4
```

## What's Next?

- **[Installation](/cli/getting-started/installation)** - Get set up in minutes
- **[Authentication](/cli/getting-started/authentication)** - Connect to the Web Platform
- **[First Test](/cli/getting-started/first-test)** - Run your first test end-to-end
- **[Command Reference](/cli/commands/test)** - Complete documentation of all commands
- **[Configuration Guide](/cli/configuration/project-config)** - Fine-tune your testing environment

---

Need help? Run `fluxloop --help` or visit the [GitHub Repository](https://github.com/chuckgu/fluxloop).
