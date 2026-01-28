---
sidebar_position: 2
---

# Quick Start

Get up and running with FluxLoop in 5 minutes.

## Step 1: Create a Project

Initialize a new FluxLoop project:

```bash
fluxloop init scenario --name my-agent
cd my-agent
```

This creates:

```
my-agent/
├── fluxloop.yaml          # Main configuration file
├── .env                   # Environment variables
├── src/
│   └── agent.py           # Sample agent code
└── scenarios/             # Test scenarios
```

## Step 2: Instrument Your Agent

Add the `@fluxloop.agent()` decorator to your agent function in `src/agent.py`:

```python
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    """Your agent logic"""
    # Process the input
    result = process_input(input_text)
    return result
```

## Step 3: Authenticate

Log in to the Web Platform:

```bash
fluxloop auth login
# Enter your API key from app.fluxloop.ai
```

## Step 4: Define Scenarios

Edit `fluxloop.yaml` to define your test personas and base inputs:

```yaml
# fluxloop.yaml
personas:
  - name: novice_user
    description: A user new to the system
    
base_inputs:
  - input: "How do I get started?"
    expected_intent: help
```

## Step 5: Generate Inputs

Create diverse test case variations:

```bash
fluxloop generate --limit 50
```

This creates a local test bundle with 50 variations based on your personas.

## Step 6: Run Test

Execute your agent with the generated inputs:

```bash
fluxloop test
```

Results are saved locally in the `results/` directory.

## Step 7: View Results in the Cloud

Upload and analyze your results on the Web Platform:

```bash
fluxloop sync upload
```

Open the provided link to [results.fluxloop.ai](https://results.fluxloop.ai) to see:
- Visual conversation traces
- Performance metrics (latency, tokens, cost)
- Success rate analysis

## What You Get

After running a test and uploading, you'll have:

- **Local Results** - Structured JSONL data in `./results/`
- **Cloud Dashboard** - Interactive visualization and team collaboration
- **Performance Insights** - Automatic analysis of agent behavior

## Next Steps

- **[Core Concepts](./core-concepts)** - Understand the FluxLoop philosophy
- **[CLI Reference](/cli/)** - Explore all commands
- **[Claude Code Integration](/claude-code/)** - Test agents directly in your IDE
- **[Web Platform Guide](../platform/platform-overview)** - Learn about cloud features

---

**Congratulations!** 🎉 You've run your first FluxLoop test.
