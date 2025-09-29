# FluxLoop CLI

Command-line interface for running AI agent simulations and experiments.

## Installation

```bash
pip install fluxloop-cli
```

## Quick Start

### 1. Initialize the FluxLoop workspace

```bash
fluxloop init project --name my-agent
# creates fluxloop/my-agent/
cd fluxloop/my-agent
```

Scaffold after init:
```
fluxloop/
├── .env                      # Global environment variables
└── my-agent/
    ├── setting.yaml          # Project experiment configuration
    ├── .env                  # (optional) project-specific overrides
    ├── examples/
    │   └── simple_agent.py
    ├── experiments/          # Run outputs will be created here
    └── inputs/               # Generated/curated input datasets
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
- User personas (입력 생성 시 참고용)
- Base inputs (LLM이 변주를 생성할 때 참조)
- `inputs_file` (필수) – `fluxloop generate inputs`로 생성한 파일 경로
- `input_generation` 블록 – LLM provider/model, 전략(`strategies`), 생성 횟수(`variation_count`) 등
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
# Create a new project under fluxloop/<name>
fluxloop init project --name my-agent

# Create an agent from template
fluxloop init agent my_agent --template simple
```

### `fluxloop generate`
```bash
# Generate LLM-based inputs (필수)
fluxloop generate inputs --project my-agent --output inputs/generated.yaml \
    --strategy rephrase --strategy verbose
```

### `fluxloop run`
```bash
# Run full experiment (auto-detects setting.yaml in current project)
fluxloop run experiment

# Or specify project and root explicitly
fluxloop run experiment --project my-agent

# Single agent execution
fluxloop run single examples.simple_agent "Test input"

# Override parameters
fluxloop run experiment --project my-agent --iterations 20
```

### `fluxloop status`
```bash
fluxloop status check --project my-agent
fluxloop status experiments --project my-agent
fluxloop status traces --project my-agent
```

### `fluxloop generate`
```bash
fluxloop generate inputs --project my-agent --output inputs/generated.yaml
```

### `fluxloop config`
```bash
fluxloop config show --project my-agent
fluxloop config set iterations 20 --project my-agent
fluxloop config env --project my-agent
fluxloop config validate --project my-agent
fluxloop config set-llm openai sk-xxxx --project my-agent
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

## Output & Artifacts

```
fluxloop/
└── my-agent/
    └── experiments/
        └── my_experiment_YYYYMMDD_HHMMSS/
            ├── summary.json       # Experiment summary and metrics
            ├── traces.jsonl       # Individual trace data
            ├── errors.json        # Any errors encountered
            └── artifacts/         # Offline store (trace cache)
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
