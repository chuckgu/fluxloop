---
sidebar_position: 2
---

# Quick Start

Get up and running with FluxLoop in 5 minutes.

## Step 1: Create a Project

Initialize a new FluxLoop project:

```bash
fluxloop init project --name my-agent
cd fluxloop/my-agent
```

This creates:

```
fluxloop/my-agent/
├── configs/
│   ├── project.yaml          # Project metadata
│   ├── input.yaml            # Input generation settings
│   ├── simulation.yaml       # Experiment configuration
│   └── evaluation.yaml       # Evaluation rules
├── .env                      # Environment variables
├── examples/
│   └── simple_agent.py       # Sample agent
├── experiments/              # Results output
├── inputs/                   # Generated inputs
└── recordings/               # Recorded arguments
```

## Step 2: Instrument Your Agent

Edit your agent code and add the `@fluxloop.agent()` decorator:

```python
# examples/my_agent.py
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    """Your agent logic"""
    # Process the input
    result = process_input(input_text)
    return result
```

## Step 3: Configure LLM Provider (Optional)

If you want to generate inputs using LLM:

```bash
# Set OpenAI API key
fluxloop config set-llm openai sk-your-api-key --model gpt-4o-mini

# Or set in .env file
echo "OPENAI_API_KEY=sk-your-api-key" >> .env
```

Edit `configs/input.yaml` to define personas and base inputs:

```yaml
personas:
  - name: novice_user
    description: A user new to the system
    
base_inputs:
  - input: "How do I get started?"
    expected_intent: help
```

## Step 4: Generate Inputs

Create input variations:

```bash
fluxloop generate inputs --limit 50
```

This produces `inputs/generated.yaml` with 50 variations.

## Step 5: Run Experiment

Execute your agent with all generated inputs:

```bash
fluxloop run experiment
```

Results are saved to `experiments/exp_YYYYMMDD_HHMMSS/`.

## Step 6: View Results

Parse the results into human-readable format:

```bash
fluxloop parse experiment experiments/exp_*/
```

This creates Markdown timelines under `per_trace_analysis/`.

## What You Get

After running an experiment, you'll have:

- **summary.json** - Aggregate statistics
- **trace_summary.jsonl** - Per-trace summaries
- **traces.jsonl** - Detailed execution traces
- **observations.jsonl** - Observation stream
- **per_trace_analysis/** - Human-readable timelines

## Next Steps

- **[Core Concepts](./core-concepts)** - Understand key concepts
- **[End-to-End Workflow](../guides/end-to-end-workflow)** - Detailed guide
- **[Configuration](../reference/configuration)** - Config file reference
- **[CLI Commands](/cli/commands/init)** - Full command reference

---

**Congratulations!** 🎉 You've run your first FluxLoop experiment.

