# FluxLoop CLI

Command-line interface for running AI agent simulations and experiments.

## Installation

```bash
pip install fluxloop-cli
```

## Quick Start

### 1. Initialize a Project

```bash
fluxloop init project my-agent-project
cd my-agent-project
```

This creates:
- `fluxloop.yaml` - Experiment configuration
- `.env` - Environment variables
- `examples/` - Sample agent code

### 2. Configure Your Experiment

Edit `fluxloop.yaml` to define:
- Number of iterations
- User personas
- Input variations
- Evaluation criteria

### 3. Run an Experiment

```bash
fluxloop run experiment
```

## Commands

### `fluxloop init`

Initialize FluxLoop projects and agents.

```bash
# Create a new project
fluxloop init project [PATH]

# Create an agent from template
fluxloop init agent my_agent --template langchain
```

### `fluxloop run`

Run experiments and simulations.

```bash
# Run full experiment from config
fluxloop run experiment --config fluxloop.yaml

# Run single agent execution
fluxloop run single my_agent.main "Test input"

# Override configuration
fluxloop run experiment --iterations 20 --personas expert_user
```

### `fluxloop status`

Check system status and view results.

```bash
# Check system status
fluxloop status check

# List recent experiments
fluxloop status experiments

# View traces
fluxloop status traces
```

### `fluxloop config`

Manage configuration.

```bash
# Show current configuration
fluxloop config show

# Set configuration value
fluxloop config set iterations 20

# Show environment variables
fluxloop config env

# Validate configuration
fluxloop config validate
```

## Configuration

### Experiment Configuration (fluxloop.yaml)

```yaml
name: my_experiment
iterations: 10

personas:
  - name: novice_user
    description: New to the system
    expertise_level: novice

variation_strategies:
  - rephrase
  - verbose
variation_count: 2

runner:
  module_path: my_agent.main
  function_name: run
  timeout_seconds: 30

evaluators:
  - name: success_checker
    type: rule_based
    enabled: true
```

### Environment Variables

```bash
# Collector configuration
export FLUXLOOP_COLLECTOR_URL=http://localhost:8000
export FLUXLOOP_API_KEY=your-api-key

# SDK configuration
export FLUXLOOP_ENABLED=true
export FLUXLOOP_DEBUG=false
export FLUXLOOP_SAMPLE_RATE=1.0

# LLM API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Writing Agents

### Simple Agent

```python
import fluxloop_sdk as fluxloop

@fluxloop.agent(name="MyAgent")
def run(input_text: str) -> str:
    # Your agent logic
    response = process_input(input_text)
    return response

@fluxloop.prompt(model="gpt-3.5-turbo")
def process_input(text: str) -> str:
    # LLM call
    return llm.complete(text)
```

### Async Agent

```python
import asyncio
import fluxloop_sdk as fluxloop

@fluxloop.agent()
async def run(input_text: str) -> str:
    result = await async_process(input_text)
    return result
```

## Output Structure

Experiments create the following output structure:

```
experiments/
└── my_experiment_20240101_120000/
    ├── summary.json       # Experiment summary and metrics
    ├── traces.jsonl       # Individual trace data
    └── errors.json        # Any errors encountered
```

## Advanced Usage

### Custom Evaluators

```python
# In your configuration
evaluators:
  - name: custom_evaluator
    type: custom
    module_path: my_evaluators.quality_checker
    class_name: QualityEvaluator
```

### Parallel Execution

```bash
# Run multiple iterations in parallel
fluxloop run experiment --parallel-runs 4
```

### Docker Execution

```bash
# Run in Docker container
fluxloop run experiment --docker
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Building

```bash
python -m build
```

## Troubleshooting

### Common Issues

1. **Module not found**: Ensure your agent module is in the Python path
2. **Collector connection failed**: Check FLUXLOOP_COLLECTOR_URL
3. **API key errors**: Verify your LLM API keys are set

### Debug Mode

```bash
# Enable debug output
fluxloop --debug run experiment
```

## License

MIT
