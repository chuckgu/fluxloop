---
sidebar_position: 3
---

# First Experiment

Run your first FluxLoop experiment end-to-end.

## Prerequisites

- FluxLoop CLI installed (`pip install fluxloop-cli`)
- Python 3.8+ environment
- OpenAI or Anthropic API key (for input generation)

## Step 1: Create Your Project

```bash
# Create a new FluxLoop project
fluxloop init project --name my-first-agent

# Navigate to project directory
cd fluxloop/my-first-agent
```

**What you get:**

```
fluxloop/my-first-agent/
├── configs/
│   ├── project.yaml       # Project metadata
│   ├── input.yaml         # Personas and base inputs
│   ├── simulation.yaml    # Runner configuration
│   └── evaluation.yaml    # Evaluators
├── .env                   # Environment variables
├── examples/
│   └── simple_agent.py    # Sample agent code
└── experiments/           # Results will go here
```

## Step 2: Configure LLM Provider

Set up your API key for input generation:

```bash
# For OpenAI
fluxloop config set-llm openai sk-your-api-key-here --model gpt-4o-mini

# Or for Anthropic
fluxloop config set-llm anthropic sk-ant-your-key --model claude-3-5-sonnet-20241022
```

This updates:
- `.env` file with your API key
- `configs/input.yaml` with provider settings

## Step 3: Review Sample Agent

Open `examples/simple_agent.py` to see a basic agent:

```python
import fluxloop

@fluxloop.agent(name="SimpleAgent")
def run(input_text: str) -> str:
    """A simple echo agent that responds to user input."""
    return f"Echo: {input_text}"
```

**For this tutorial, we'll use the provided example as-is.**

The agent is already configured in `configs/simulation.yaml`:

```yaml
runner:
  target: "examples.simple_agent:run"
```

## Step 4: Verify Setup

Run diagnostics to ensure everything is ready:

```bash
fluxloop doctor
```

**Expected output:**

```
╭──────────────────────────────────╮
│ FluxLoop Environment Doctor      │
╰──────────────────────────────────╯

Component       Status  Details
Python          ✓       3.11.5
FluxLoop CLI    ✓       0.2.30
FluxLoop SDK    ✓       Installed
Project Config  ✓       configs/project.yaml

╭──────────────────╮
│ Doctor completed │
╰──────────────────╯
```

## Step 5: Generate Test Inputs

Create variations of base inputs for testing:

```bash
# Generate 10 input variations
fluxloop generate inputs --limit 10 --mode llm
```

**Output:**

```
Generating inputs with LLM mode...

✓ Generated 10 input variations
  - Base inputs: 2
  - Personas: 2
  - Strategies: rephrase, verbose
  - Saved to: inputs/generated.yaml

Total inputs ready: 10
```

**View generated inputs:**

```bash
cat inputs/generated.yaml
```

You'll see variations like:

```yaml
- input: "Hey, how would I get started with this?"
  persona: novice_user
  metadata:
    base_input: "How do I get started?"
    variation_strategy: rephrase

- input: "Hello, I'm new here and wondering how to begin..."
  persona: novice_user
  metadata:
    base_input: "How do I get started?"
    variation_strategy: verbose
```

## Step 6: Run Your First Experiment

Execute the experiment with all generated inputs:

```bash
fluxloop run experiment --iterations 1
```

**What happens:**

1. Loads 10 inputs from `inputs/generated.yaml`
2. Calls your agent function for each input
3. Captures traces and observations
4. Saves results to `experiments/my_first_agent_experiment_<timestamp>/`

**Output:**

```
╭─ Experiment: my_first_agent_experiment ───────────╮
│ Iterations: 1                                     │
│ Input Source: inputs/generated.yaml               │
│ Total Runs: 10                                    │
╰───────────────────────────────────────────────────╯

Running experiments...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 10/10 [00:05]

✓ Experiment completed!

Results saved to: experiments/my_first_agent_experiment_20250117_143022/
  - trace_summary.jsonl (10 traces)
  - observations.jsonl (30 observations)
  - summary.json
```

## Step 7: View Results

Check the experiment summary:

```bash
# View summary JSON
cat experiments/my_first_agent_*/summary.json | jq

# Or use fluxloop status
fluxloop status experiments
```

**Summary output:**

```json
{
  "experiment_name": "my_first_agent_experiment",
  "total_traces": 10,
  "successful": 10,
  "failed": 0,
  "avg_duration_ms": 42.3,
  "started_at": "2025-01-17T14:30:22Z",
  "completed_at": "2025-01-17T14:30:27Z"
}
```

## Step 8: Parse Results (Optional)

Convert raw outputs into human-readable format:

```bash
fluxloop parse experiment experiments/my_first_agent_experiment_*/
```

This creates:
- Markdown files for each trace
- `per_trace.jsonl` with structured data

**View parsed trace:**

```bash
# Open first trace
cat experiments/my_first_agent_*/per_trace_analysis/00_*.md
```

## Step 9: Evaluate Results (Optional)

Score your agent's performance:

```bash
fluxloop evaluate experiment experiments/my_first_agent_experiment_*/
```

**Output:**

```
╭─ Evaluation: my_first_agent_experiment ───────────╮
│ Traces: 10                                        │
│ Evaluators: 2                                     │
╰───────────────────────────────────────────────────╯

Running evaluations...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 10/10 [00:03]

✓ Evaluation completed!

╭─ Results Summary ─────────────────────────────────╮
│ Overall Score: 1.00 / 1.00 (100%)                │
│ Pass/Fail: PASS (threshold: 0.70)                │
│                                                   │
│ By Evaluator:                                     │
│   - output_not_empty: 1.00 (10/10 passed)        │
│   - success: 1.00 (10/10 passed)                 │
╰───────────────────────────────────────────────────╯

Reports saved to: experiments/.../evaluation/
  - report.md
  - report.html
```

## Congratulations! 🎉

You've successfully:

✅ Created a FluxLoop project  
✅ Configured LLM provider  
✅ Generated test inputs  
✅ Run an experiment  
✅ Viewed results  
✅ Parsed and evaluated outputs  

## What's Next?

### Customize Your Agent

Replace the example agent with your actual code:

```python
# my_agent.py
import fluxloop

@fluxloop.agent(name="MyCustomAgent")
def run(input_text: str) -> str:
    # Your agent logic here
    result = process_input(input_text)
    return result
```

Update `configs/simulation.yaml`:

```yaml
runner:
  target: "my_agent:run"
```

### Add More Personas

Edit `configs/input.yaml` to test different user types:

```yaml
personas:
  - name: expert_user
    description: Technical power user
    expertise_level: expert
  
  - name: frustrated_user
    description: User experiencing issues
    characteristics:
      - Expresses frustration
      - Wants quick resolution
```

### Try Multi-Turn Conversations

Enable multi-turn mode for dynamic dialogues:

```bash
fluxloop run experiment --multi-turn --max-turns 8
```

See [Multi-Turn Workflow](/cli/workflows/multi-turn-workflow) for details.

### Run in CI/CD

Add FluxLoop to your testing pipeline:

```yaml
# .github/workflows/test.yml
- name: Run FluxLoop Tests
  run: |
    fluxloop generate inputs --limit 20
    fluxloop run experiment --yes --iterations 3
    fluxloop evaluate experiment experiments/latest_*/
```

See [CI/CD Integration](/cli/workflows/ci-cd-integration) for examples.

## Troubleshooting

### "API key not found"

Set your LLM API key:

```bash
fluxloop config set-llm openai sk-your-key
```

### "Module not found"

Ensure your agent module is importable:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
fluxloop run experiment
```

### "No inputs generated"

Check input generation succeeded:

```bash
ls -la inputs/generated.yaml
cat inputs/generated.yaml
```

If empty, regenerate:

```bash
fluxloop generate inputs --limit 10 --overwrite
```

## Quick Reference

```bash
# Complete workflow
fluxloop init project --name my-agent
cd fluxloop/my-agent
fluxloop config set-llm openai sk-xxxxx
fluxloop generate inputs --limit 10
fluxloop run experiment
fluxloop parse experiment experiments/latest_*/
fluxloop evaluate experiment experiments/latest_*/

# Check status
fluxloop doctor
fluxloop status experiments
fluxloop config env
```

## Next Steps

- **[Basic Workflow](/cli/workflows/basic-workflow)** - Complete guide with more details
- **[Commands Reference](/cli/commands/init)** - Full command documentation
- **[Configuration](/cli/configuration/project-config)** - Detailed config reference
- **[Multi-Turn Workflow](/cli/workflows/multi-turn-workflow)** - Dynamic conversations
