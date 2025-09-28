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

Init scaffolds a ready-to-run workspace:
```
my-agent-project/
├── setting.yaml        # Experiment template (personas, inputs, runner)
├── .env                # Collector + LLM credentials (fill these in)
├── examples/
│   └── simple_agent.py # Sample agent instrumented with fluxloop
└── experiments/        # Outputs land here once you run
```

### 2. Configure Credentials and Environment

- Open `.env`, set values like:
  ```bash
  FLUXLOOP_COLLECTOR_URL=http://localhost:8000
  FLUXLOOP_API_KEY=your-collector-key
  OPENAI_API_KEY=sk-...
  ANTHROPIC_API_KEY=sk-ant-...
  ```
- Or write them through the CLI (updates `.env` automatically):
  ```bash
  fluxloop config set-llm openai sk-xxxx --model gpt-4o-mini
  ```
- To check what’s loaded, run:
  ```bash
  fluxloop config env --show-values
  ```

### 3. Configure Your Experiment

Edit `setting.yaml` to define:
- Number of iterations & parallelism
- User personas and variation strategies
- Base inputs or external input files
- Runner module/function pointing at your agent
- Evaluators and collector settings

### 4. Run an Experiment

```bash
fluxloop run experiment --config setting.yaml
```
Add flags such as `--no-collector`, `--dry-run`, or overrides like `--iterations 20` as needed.

## Folder Structure (after first run)
```
my-agent-project/
├── setting.yaml
├── .env
├── examples/
├── experiments/
│   ├── my_experiment_YYYYMMDD_HHMMSS/
│   │   ├── summary.json
│   │   ├── traces.jsonl
│   │   └── errors.json
│   └── artifacts/        # offline trace cache (SDK-managed)
└── inputs/               # (optional) generated inputs
```

## Commands

### `fluxloop init`
```bash
# Create a new project scaffold
fluxloop init project [PATH]

# Create an agent from template
fluxloop init agent my_agent --template simple
```

### `fluxloop run`
```bash
# Run full experiment
fluxloop run experiment --config setting.yaml

# Single agent execution
fluxloop run single examples.simple_agent "Test input"

# Override parameters
fluxloop run experiment --config setting.yaml --iterations 20
```

### `fluxloop status`
```bash
fluxloop status check
fluxloop status experiments
fluxloop status traces
```

### `fluxloop config`
```bash
fluxloop config show
fluxloop config set iterations 20
fluxloop config env
fluxloop config validate
fluxloop config set-llm openai sk-xxxx
```

## Environment Variables Reference
```bash
# Collector
export FLUXLOOP_COLLECTOR_URL=http://localhost:8000
export FLUXLOOP_API_KEY=your-api-key

# CLI/SDK behavior
export FLUXLOOP_ENABLED=true
export FLUXLOOP_DEBUG=false
export FLUXLOOP_SAMPLE_RATE=1.0

# LLM providers
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export FLUXLOOP_LLM_API_KEY=sk-...  # universal fallback
```

If values are set in `.env`, `fluxloop init` and `fluxloop run` will automatically load them (thanks to `python-dotenv`).

## Writing Agents

```python
import fluxloop

@fluxloop.agent(name="MyAgent")
def run(input_text: str) -> str:
    return process_input(input_text)

@fluxloop.prompt(model="gpt-3.5-turbo")
def process_input(text: str) -> str:
    # LLM call
    return llm.complete(text)
```

## Output Structure

```
experiments/
└── my_experiment_YYYYMMDD_HHMMSS/
    ├── summary.json       # Experiment summary and metrics
    ├── traces.jsonl       # Individual trace data
    └── errors.json        # Any errors encountered
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Troubleshooting
1. **Module not found**: Ensure your agent module is on `PYTHONPATH`.
2. **Collector connection failed**: Verify `FLUXLOOP_COLLECTOR_URL` and network access.
3. **API key errors**: Ensure `.env` has the right LLM/collector keys (`fluxloop config env`).

```bash
# Enable verbose logging
fluxloop --debug run experiment
```

## License
MIT
