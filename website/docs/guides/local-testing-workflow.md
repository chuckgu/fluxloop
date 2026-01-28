---
sidebar_position: 1
---

# Local Testing Workflow

Learn the complete end-to-end workflow for testing agents locally using the FluxLoop CLI.

## Workflow Overview

The FluxLoop workflow follows these four main steps:

1. **Instrument**: Add decorators to your agent code.
2. **Define**: Set up personas and test inputs.
3. **Test**: Run simulations and capture traces.
4. **Analyze**: Upload results to the cloud for inspection.

---

## 1. Instrument Your Agent

The first step is to mark your agent's entry point using the FluxLoop SDK. This allows FluxLoop to intercept inputs and outputs automatically.

```python
# src/agent.py
import fluxloop

@fluxloop.agent(name="CustomerSupportAgent")
def my_agent(user_input: str) -> str:
    # Your agent logic (e.g., using LangChain, OpenAI, etc.)
    response = "Hello! How can I help you today?"
    return response
```

---

## 2. Define Test Scenarios

FluxLoop uses a `fluxloop.yaml` file to manage test configurations. You can define **Personas** (who is testing) and **Base Inputs** (what they are asking).

```yaml
# fluxloop.yaml
project:
  name: my-first-agent

runner:
  target: "src.agent:my_agent"
  type: python-function

personas:
  - name: novice_user
    description: A user new to the system, asks basic questions.
  - name: expert_user
    description: A power user who uses technical terminology.

base_inputs:
  - input: "How do I reset my password?"
    persona: novice_user
  - input: "What is the rate limit for the GraphQL API?"
    persona: expert_user
```

---

## 3. Generate Test Inputs

Instead of testing only your base inputs, use FluxLoop's generation capabilities to create diverse variations. This helps surface edge cases in how your agent handles different phrasing.

```bash
# Generate 20 variations for each base input
fluxloop generate --limit 20
```

FluxLoop will use an LLM (configured in your `.env` or via `fluxloop auth login`) to create realistic test data.

---

## 4. Run Local Tests

Execute your agent against the generated inputs:

```bash
fluxloop test
```

### Options:
- `--iterations 5`: Run each input 5 times to test for non-determinism.
- `--parallel 4`: Run 4 tests in parallel to speed up execution.
- `--skip-upload`: Skip automatic upload after the test completes.

---

## 5. Analyze Results

While results are saved locally in the `results/` directory, the most effective way to analyze them is using the Web Platform.

```bash
# Upload the latest results (if you skipped auto upload)
fluxloop sync upload
```

Open the generated link to [results.fluxloop.ai](https://results.fluxloop.ai) to:
- **Inspect Traces**: View the step-by-step execution of your agent.
- **Compare Runs**: See if your changes improved or degraded performance.
- **Collaborate**: Share specific failure cases with your team.

---

## 6. Sync with the Cloud

FluxLoop enables a "Cloud-First" workflow where scenarios are managed centrally.

```bash
# Pull team scenarios from the Web Platform
fluxloop sync pull

# Test against team scenarios
fluxloop test --scenario team-regression-v1
```

---

## Next Steps

- **[Installation Guide](../getting-started/installation)** - Get the CLI set up
- **[CLI Reference](/cli/)** - Explore all commands
- **[Web Platform Guide](../platform/platform-overview)** - Learn about cloud features
- **[Claude Code Integration](/claude-code/)** - Test agents directly in your IDE