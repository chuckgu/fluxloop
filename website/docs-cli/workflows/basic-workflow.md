---
sidebar_position: 1
---

# Basic Workflow

Complete guide to the standard FluxLoop CLI workflow from setup to evaluation.

## Overview

The FluxLoop workflow consists of five main phases:

1. **Initialize** - Create project structure and configuration
2. **Generate** - Create input variations for testing
3. **Run** - Execute experiments and collect traces
4. **Parse** - Convert raw outputs into readable formats
5. **Evaluate** - Score results and generate reports

This guide walks through each phase with practical examples.

---

## Phase 1: Initialize Project

### Create New Project

```bash
# Initialize a new FluxLoop project
fluxloop init scenario --name my-agent

# Navigate to project directory
cd fluxloop/my-agent
```

**What Gets Created:**

```
fluxloop/my-agent/
├── configs/
│   ├── project.yaml       # Project metadata
│   ├── input.yaml         # Personas and input settings
│   ├── simulation.yaml    # Runner and experiment config
│   └── evaluation.yaml    # Evaluators and success criteria
├── .env                   # Environment variables (gitignored)
├── .gitignore
├── examples/
│   └── simple_agent.py    # Sample agent implementation
├── inputs/                # Generated inputs stored here
├── recordings/            # Recorded arguments (if using recording mode)
└── results/           # Experiment outputs
```

### Verify Installation

```bash
# Check system status
fluxloop doctor

# Verify configuration
fluxloop config validate
```

**Expected Output:**

```
╭──────────────────────────────────╮
│ FluxLoop Environment Doctor      │
╰──────────────────────────────────╯

Component       Status  Details
Python          ✓       3.11.5
FluxLoop CLI    ✓       0.2.30
FluxLoop SDK    ✓       0.1.6
FluxLoop MCP    ✓       /path/to/fluxloop-mcp
MCP Index       ✓       ~/.fluxloop/mcp/index/dev
Project Config  ✓       configs/project.yaml

╭──────────────────╮
│ Doctor completed │
╰──────────────────╯
```

---

## Phase 2: Configure Your Agent

### Set Up LLM Provider

```bash
# Configure OpenAI (for input generation)
fluxloop config set-llm openai sk-your-api-key --model gpt-4o

# Or Anthropic
fluxloop config set-llm anthropic sk-ant-your-key --model claude-3-5-sonnet-20241022
```

### Point to Your Agent Code

Edit `configs/simulation.yaml`:

```yaml
runner:
  target: "my_agent:run"              # Point to your agent entry point
  working_directory: .                # Project root
  timeout_seconds: 120
  max_retries: 3
```

**Agent Entry Point Example:**

```python
# my_agent.py
import fluxloop

@fluxloop.agent(name="MyAgent")
def run(input_text: str) -> str:
    """Main agent entry point."""
    # Your agent logic here
    return f"Response to: {input_text}"
```

### Configure Personas

Edit `configs/input.yaml` to define user personas:

```yaml
personas:
  - name: novice_user
    description: A user new to the system
    characteristics:
      - Asks basic questions
      - May use incorrect terminology
      - Needs detailed explanations
    language: en
    expertise_level: novice
    goals:
      - Understand system capabilities
      - Complete basic tasks

  - name: expert_user
    description: An experienced power user
    characteristics:
      - Uses technical terminology
      - Asks complex questions
      - Expects efficient responses
    language: en
    expertise_level: expert
    goals:
      - Optimize workflows
      - Access advanced features
```

### Define Base Inputs

Still in `configs/input.yaml`:

```yaml
base_inputs:
  - input: "How do I get started?"
    expected_intent: help
    metadata:
      category: onboarding
      
  - input: "What are the advanced features?"
    expected_intent: capabilities
    metadata:
      category: features

  - input: "Can you help me with error code 404?"
    expected_intent: troubleshooting
    metadata:
      category: support
```

---

## Phase 3: Generate Inputs

### Generate Input Variations

```bash
# Generate variations using LLM
fluxloop generate inputs --limit 50 --mode llm

# Or deterministic variations
fluxloop generate inputs --limit 30 --mode deterministic
```

**What Happens:**

1. FluxLoop reads `configs/input.yaml`
2. For each base input × persona combination
3. Generates variations using specified strategies
4. Saves to `inputs/generated.yaml`

**Output:**

```
Generating inputs with LLM mode...

✓ Generated 50 input variations
  - Base inputs: 3
  - Personas: 2
  - Strategies: rephrase, verbose, error_prone
  - Saved to: inputs/generated.yaml

Total inputs ready: 50
```

**View Generated Inputs:**

```bash
# Check generated inputs
cat inputs/generated.yaml

# Or view in editor
code inputs/generated.yaml
```

**Example Generated Input:**

```yaml
- input: "Hey, how would I go about getting started with this thing?"
  persona: novice_user
  metadata:
    base_input: "How do I get started?"
    variation_strategy: rephrase
    variation_index: 0
```

---

## Phase 4: Run Experiment

### Execute Simulation

```bash
# Run experiment with default settings
fluxloop test

# Run with custom iterations
fluxloop test --iterations 5

# Run with multi-turn enabled
fluxloop test --multi-turn --max-turns 10
```

**What Happens:**

1. Loads configuration from `configs/simulation.yaml`
2. Loads inputs from `inputs/generated.yaml`
3. For each input × iteration:
   - Calls your agent function
   - Captures traces via FluxLoop SDK
   - Records observations
4. Saves results to `results/exp_<timestamp>/`

**Output:**

```
╭─ Experiment: my_agent_experiment ─────────────────────╮
│ Iterations: 1                                         │
│ Input Source: inputs/generated.yaml                   │
│ Total Runs: 50                                        │
╰───────────────────────────────────────────────────────╯

Running experiments...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 50/50 [00:45]

✓ Experiment completed!

Results saved to: results/exp_20250117_143022/
  - traces.jsonl (50 traces)
  - observations.jsonl (150 observations)
  - summary.json
  - metadata.json
```

### Check Results Immediately

```bash
# View summary
cat results/exp_*/summary.json | jq

# List recent experiments
fluxloop status experiments
```

---

## Phase 5: Parse Results

### Convert to Human-Readable Format

```bash
# Parse experiment outputs
fluxloop parse experiment results/exp_20250117_143022/

# Or use glob pattern for latest
fluxloop parse experiment results/exp_*/
```

**What Happens:**

1. Reads `traces.jsonl` and `observations.jsonl`
2. Reconstructs conversation flow for each trace
3. Generates Markdown timeline for each trace
4. Creates `per_trace.jsonl` with structured data

**Output:**

```
Parsing experiment: results/exp_20250117_143022/

✓ Parsed 50 traces
  - Total observations: 150
  - Average trace length: 3 observations
  - Saved to: results/.../per_trace_analysis/

Generated Files:
  - per_trace_analysis/00_<trace_id>.md (50 files)
  - per_trace_analysis/per_trace.jsonl
```

**View Parsed Trace:**

```bash
# Open first trace in editor
code results/exp_*/per_trace_analysis/00_*.md
```

**Example Parsed Trace (Markdown):**

```markdown
# Trace Analysis: 00_7f39c11-1eac-423b-96b9-09aa8a8f588a

**Experiment**: my_agent_experiment
**Persona**: novice_user
**Input**: "Hey, how would I go about getting started with this thing?"
**Status**: SUCCESS
**Duration**: 234ms

## Timeline

### 1. AGENT: SimpleAgent
**Start**: 14:30:22.123
**Duration**: 234ms

**Input:**
```json
{
  "input_text": "Hey, how would I go about getting started with this thing?"
}
```

**Output:**
```json
{
  "response": "Hello! To get started, first visit our documentation..."
}
```

### 2. TOOL: process_input
**Start**: 14:30:22.145
**Duration**: 12ms

**Input:**
```json
{
  "text": "Hey, how would I go about getting started with this thing?"
}
```

**Output:**
```json
{
  "intent": "help",
  "word_count": 11,
  "has_question": true
}
```
```

---

## Phase 6: Evaluate Results

### Generate the Interactive Report

```bash
# Run evaluation
fluxloop evaluate experiment results/exp_20250117_143022/

# With custom config
fluxloop evaluate experiment results/exp_*/ \
  --config configs/evaluation.yaml
```

**What Happens:**

1. Loads `per_trace_analysis/per_trace.jsonl` generated by `fluxloop parse`.
2. Runs the 5단계 파이프라인:
   - **LLM-PT**: LLM judges each trace on 7 metrics (task completion, hallucination, relevance, tool usage, satisfaction, clarity, persona)
   - **Rule aggregation**: 통계, 메트릭 패스율, 성능 카드, 케이스 분류
   - **LLM-OV**: LLM이 전반적인 인사이트·추천을 작성
   - **Data preparation + HTML 렌더링**: `evaluation_report/report.html` 생성
3. Outputs progress logs plus a final path to the generated dashboard.

**Output:**

```
📊 Evaluating experiment at results/exp_20250117_143022
🧵 Per-trace data: results/.../per_trace_analysis/per_trace.jsonl
📁 Output: results/.../evaluation_report

Stage 1: LLM-PT (10 traces) ...
Stage 2: Aggregation ...
Stage 3: LLM-OV ...
Stage 4 & 5: Rendering HTML report...

✅ Report ready: results/.../evaluation_report/report.html
```

### View Evaluation Reports

```bash
# Open HTML report in browser
open results/exp_*/evaluation_report/report.html

# Check the structured traces (input to the pipeline)
cat results/exp_*/per_trace_analysis/per_trace.jsonl | jq
```

---

## Complete Workflow Script

Put it all together in one script:

```bash
#!/bin/bash
# run_full_workflow.sh

set -e  # Exit on error

PROJECT="my-agent"
ITERATIONS=5

echo "=== FluxLoop Complete Workflow ==="

# 1. Initialize (if needed)
if [ ! -d "fluxloop/$PROJECT" ]; then
    echo "1. Initializing project..."
    fluxloop init scenario --name "$PROJECT"
fi

cd "fluxloop/$PROJECT"

# 2. Verify setup
echo "2. Verifying setup..."
fluxloop doctor
fluxloop config validate

# 3. Generate inputs
echo "3. Generating inputs..."
fluxloop generate inputs --limit 50 --mode llm

# 4. Run experiment
echo "4. Running experiment..."
fluxloop test --iterations "$ITERATIONS"

# 5. Find latest experiment
LATEST_EXP=$(ls -td results/*/ | head -1)

# 6. Parse results
echo "5. Parsing results..."
fluxloop parse experiment "$LATEST_EXP"

# 7. Evaluate
echo "6. Evaluating..."
fluxloop evaluate experiment "$LATEST_EXP"

# 8. Summary
echo ""
echo "=== Workflow Complete ==="
echo "Results in: $LATEST_EXP"
echo ""
echo "View reports:"
echo "  HTML: open ${LATEST_EXP}evaluation_report/report.html"
```

Make it executable and run:

```bash
chmod +x run_full_workflow.sh
./run_full_workflow.sh
```

---

## Tips and Best Practices

### Start Small

Begin with a minimal setup to verify everything works:

```bash
# Generate just 10 inputs
fluxloop generate inputs --limit 10

# Run 1 iteration
fluxloop test --iterations 1

# Verify results
fluxloop status experiments
```

### Iterate on Configuration

Tune your setup incrementally:

```bash
# Try different variation strategies
fluxloop config set variation_strategies "[rephrase, verbose]" --file configs/input.yaml

# Adjust iteration count
fluxloop config set iterations 20 --file configs/simulation.yaml

# Re-run and compare
fluxloop test
```

### Sync Test Data

Link your workspace and sync with the cloud:

```bash
# 1. Select a web project
fluxloop projects select <project_id>

# 2. Pull scenarios
fluxloop sync pull

# 3. Test and upload
fluxloop test
```

### Use Multi-Turn for Deeper Testing

```bash
# Enable multi-turn conversations
fluxloop config set multi_turn.enabled true --file configs/simulation.yaml
fluxloop config set multi_turn.max_turns 10 --file configs/simulation.yaml

# Run with supervisor
fluxloop test --multi-turn --auto-approve
```

---

## Troubleshooting

### Agent Not Found

**Error:** `ModuleNotFoundError: No module named 'my_agent'`

**Solution:**
```bash
# Verify runner.target points to correct module
fluxloop config show --file configs/simulation.yaml | grep target

# Ensure module is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### No Inputs Generated

**Error:** `No inputs found in inputs/generated.yaml`

**Solution:**
```bash
# Check input config
fluxloop config show --file configs/input.yaml

# Verify LLM API key
fluxloop config env | grep API_KEY

# Re-generate
fluxloop generate inputs --limit 10 --mode deterministic
```

### Evaluation Fails

**Error:** `Missing per_trace.jsonl`

**Solution:**
```bash
# Must parse before evaluating
fluxloop parse experiment results/exp_*/
fluxloop evaluate experiment results/exp_*/
```

---

## Next Steps

- **[Multi-Turn Workflow](/cli/workflows/multi-turn-workflow)** - Dynamic conversations
- **[CI/CD Integration](/cli/workflows/ci-cd-integration)** - Automate in pipelines
- **[Commands Reference](/cli/commands/init)** - Detailed command documentation

---

## Quick Reference

```bash
# Setup
fluxloop projects select <id>
fluxloop init scenario my-agent
fluxloop auth login
fluxloop doctor

# Workflow
fluxloop sync pull
fluxloop test
fluxloop sync upload
```
