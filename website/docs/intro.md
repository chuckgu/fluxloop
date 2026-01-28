---
sidebar_position: 1
slug: /
---

# Welcome to FluxLoop

## Build, Test, and Ship AI Agents with Confidence

FluxLoop is a cloud-powered platform for testing AI agents at scale with synthetic data. From rapid prototyping in Claude Code to team-wide testing in the cloud, FluxLoop helps you validate agent behavior before shipping to production.

---

## 🚀 Three Ways to Use FluxLoop

### 1. Claude Code Plugin
**Test agents directly in your IDE**

```bash
# Install the plugin
claude code plugin install fluxloop

# Run a quick test
/fluxloop test
```

Perfect for: Rapid iteration during development

### 2. CLI Tool
**Local testing and automation**

```bash
# Install
pip install fluxloop-cli

# Initialize and test
fluxloop init scenario --name my-agent
fluxloop test
```

Perfect for: CI/CD pipelines, local workflows

### 3. Web Platform
**Cloud-powered analysis and collaboration**

Visit [app.fluxloop.ai](https://app.fluxloop.ai) to:
- View test results and metrics
- Share scenarios with your team
- Track agent performance over time

Perfect for: Team collaboration, production monitoring

---

## Why FluxLoop?

### 🎭 Test with Synthetic Data
Generate realistic test scenarios using personas and synthetic inputs. Find edge cases before your users do.

### ⚡ Test at Scale
Run hundreds of scenarios in parallel. Validate behavior across diverse user types and situations.

### 🔗 Seamless Workflow
Test in Claude Code, deploy with the CLI, analyze in the cloud. One platform, multiple entry points.

### 📊 Framework Agnostic
Works with any Python agent framework: LangGraph, LangChain, custom solutions. Just add a decorator.

---

## Quick Start

### For Claude Code Users

1. **Install FluxLoop plugin**: `claude code plugin install fluxloop`
2. **Set up your project**: `/fluxloop setup`
3. **Run your first test**: `/fluxloop test`

### For CLI Users

1. **Install package**: `pip install fluxloop-cli`
2. **Initialize project**: `fluxloop init scenario --name my-agent`
3. **Authenticate**: `fluxloop auth login`
4. **Run test**: `fluxloop test`
5. **Upload results**: `fluxloop sync upload`

---

## How It Works

### 1. **Instrument Your Agent**
Add a simple decorator to your agent function:

```python
import fluxloop

@fluxloop.agent()
def my_agent(user_message: str) -> str:
    # Your agent logic here
    return response
```

### 2. **Define Test Scenarios**
Create personas and test inputs (or pull them from the Web Platform):

```yaml
# fluxloop.yaml
personas:
  - name: novice_user
    description: New user, unfamiliar with the product
  - name: expert_user
    description: Power user, knows advanced features

base_inputs:
  - input: "How do I get started?"
  - input: "What are the advanced settings?"
```

### 3. **Generate Variations**
Create diverse test cases automatically:

```bash
fluxloop generate --limit 100
```

FluxLoop generates realistic variations based on your personas and base inputs.

### 4. **Run Tests**
Execute your test suite locally:

```bash
fluxloop test
# or in Claude Code
/fluxloop test
```

### 5. **Analyze Results**
Open results in [results.fluxloop.ai](https://results.fluxloop.ai) to visualize conversations, performance, and costs.

---

## Core Concepts

### Agents
Any function that processes user input and returns output. Mark entry points with `@fluxloop.agent()`.

### Personas
Synthetic user archetypes that shape test input generation (e.g., "novice user", "expert user").

### Scenarios
Test cases combining personas and inputs to simulate real user interactions.

### Test Runs
Complete execution records capturing inputs, outputs, LLM calls, tool usage, timing, and costs.

---

## Documentation Structure

### 🎯 **Getting Started**
New to FluxLoop? Start here:
- [Installation](/docs/getting-started/installation) - Set up FluxLoop
- [Quick Start](/docs/getting-started/quick-start) - Your first test
- [Core Concepts](/docs/getting-started/core-concepts) - Key concepts

### 📚 **Workflows**
Step-by-step tutorials:
- [Local Testing Workflow](/docs/guides/local-testing-workflow) - Complete walkthrough
- [Environment Setup](/docs/guides/virtual-environment-setup) - Virtual environments

### 🛠️ **Reference**
Detailed documentation:
- [Python SDK](/sdk/) - Decorator API and configuration
- [CLI Tool](/cli/) - Command-line interface
- [Claude Code](/claude-code/) - Claude Code integration
- [Web Platform](/docs/platform/platform-overview) - Cloud features

---

## Next Steps

Choose your path:

- **New to FluxLoop?** → [Installation](/docs/getting-started/installation)
- **Using Claude Code?** → [Claude Code Guide](/claude-code/)
- **CLI User?** → [CLI First Test](/cli/getting-started/first-test)
- **Need API reference?** → [SDK](/sdk/) | [CLI](/cli/)

---

**Ready to build trustworthy AI agents?** Let's get started! 🚀
