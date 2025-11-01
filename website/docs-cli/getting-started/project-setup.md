---
sidebar_position: 2
---

# Project Setup

Create and configure your first FluxLoop project.

## Initialize a New Project

Create a new project with the CLI:

```bash
fluxloop init project --name my-agent
cd fluxloop/my-agent
```

This generates a complete project structure:

```
fluxloop/my-agent/
├── configs/
│   ├── project.yaml          # Project metadata
│   ├── input.yaml            # Input generation settings
│   ├── simulation.yaml       # Experiment configuration
│   └── evaluation.yaml       # Evaluation rules
├── .env                      # Environment variables
├── examples/
│   └── simple_agent.py       # Sample instrumented agent
├── experiments/              # Results output directory
├── inputs/                   # Generated inputs directory
└── recordings/               # Recorded arguments (optional)
```

## Project Configuration Files

###  `configs/project.yaml`

Project-level metadata and collector settings:

```yaml
project:
  name: my-agent
  version: "1.0.0"
  description: "My AI agent simulation project"

collector:
  enabled: false
  url: "http://localhost:8000"
  api_key: ""
```

### `configs/input.yaml`

Personas, base inputs, and input generation settings:

```yaml
personas:
  - name: novice_user
    description: A user new to the system
    traits:
      - Asks basic questions
      - May not know terminology
  
  - name: expert_user
    description: An experienced power user
    traits:
      - Uses technical jargon
      - Expects advanced features

base_inputs:
  - input: "How do I get started?"
    expected_intent: help
    persona: novice_user
  
  - input: "What are the advanced configuration options?"
    expected_intent: configuration
    persona: expert_user

input_generation:
  mode: llm                    # or "deterministic"
  llm:
    provider: openai           # or "anthropic"
    model: gpt-4o-mini
    temperature: 0.7
  strategies:
    - rephrase
    - verbose
    - concise
    - error_prone
```

### `configs/simulation.yaml`

Experiment runtime configuration:

```yaml
runner:
  target: "examples.simple_agent:run"   # Your agent function
  iterations: 10                         # Runs per input

replay_args:
  enabled: false
  recording_file: "recordings/args.jsonl"
  callable_providers: {}
  override_param_path: ""

output:
  directory: "experiments"
  format: jsonl
```

### `configs/evaluation.yaml`

Evaluator definitions (optional):

```yaml
evaluators:
  - name: response_quality
    type: rule_based
    rules:
      - check: response_length_min
        value: 10
      - check: no_errors
        value: true

  - name: llm_judge
    type: llm
    model: gpt-4o-mini
    prompt: "Rate this response quality from 1-10"
```

## Environment Variables

The `.env` file stores sensitive configuration:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Collector Configuration
FLUXLOOP_COLLECTOR_URL=http://localhost:8000
FLUXLOOP_COLLECTOR_API_KEY=your-api-key

# Recording Mode
FLUXLOOP_RECORD_ARGS=false

# Project Settings
FLUXLOOP_PROJECT_NAME=my-agent
```

## Configure LLM Provider

Set your API key for input generation:

```bash
# Using CLI helper
fluxloop config set-llm openai sk-your-api-key --model gpt-4o-mini

# Or manually edit .env
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

## Add Your Agent Code

Replace the example agent with your actual agent:

```python
# examples/my_agent.py
import fluxloop

@fluxloop.agent()
def run(input_text: str) -> str:
    """Your agent logic here"""
    # Process the input
    response = process_input(input_text)
    return response
```

Update `configs/simulation.yaml` to point to your agent:

```yaml
runner:
  target: "examples.my_agent:run"
  iterations: 10
```

## Define Personas and Base Inputs

Edit `configs/input.yaml` to match your use case:

```yaml
personas:
  - name: customer_support
    description: A customer seeking help
    traits:
      - Polite but frustrated
      - Wants quick resolution
  
  - name: technical_user
    description: A developer using the API
    traits:
      - Technical language
      - Needs documentation

base_inputs:
  - input: "My order hasn't arrived yet"
    expected_intent: order_status
    persona: customer_support
  
  - input: "What's the rate limit for the API?"
    expected_intent: api_docs
    persona: technical_user
```

## Verify Configuration

Check your project status:

```bash
fluxloop status
```

This shows:
- ✅ CLI version
- ✅ SDK installation
- ✅ Project configuration
- ✅ Environment variables
- ✅ Recording mode status

## Multiple Projects

FluxLoop supports multiple projects:

```bash
# Create another project
fluxloop init project --name chatbot-v2
cd fluxloop/chatbot-v2

# Switch between projects
cd ../my-agent
```

Each project has independent configuration and results.

## Best Practices

1. **Version control your configs**
   ```bash
   git add configs/
   git commit -m "Add project configuration"
   ```

2. **Keep .env out of version control**
   ```bash
   echo ".env" >> .gitignore
   ```

3. **Use descriptive base inputs**
   - Cover different personas
   - Include edge cases
   - Add expected outcomes

4. **Start small**
   - Begin with 5-10 base inputs
   - Generate 50-100 variations
   - Run 10 iterations per input

5. **Iterate on configuration**
   - Review results
   - Adjust personas
   - Refine generation strategies

## Next Steps

- [First Experiment](./first-experiment) - Run your first experiment
- [Command Reference](/cli/commands/init) - Detailed command docs
- [Configuration Reference](/cli/configuration/project-config) - Full config specs
