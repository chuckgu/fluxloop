# FluxLoop CLI

Command-line interface for running agent simulations.

## Installation

```
pip install fluxloop-cli
```

## Configuration Overview (v0.2.0)

FluxLoop CLI now stores experiment settings in four files under `configs/`:

- `configs/project.yaml` – project metadata, collector defaults
- `configs/input.yaml` – personas, base inputs, input generation options
- `configs/simulation.yaml` – runtime parameters (iterations, runner, replay args)
- `configs/evaluation.yaml` – evaluator definitions (rule-based, LLM judge, etc.)

The legacy `setting.yaml` is still supported, but new projects created with
`fluxloop init project` will generate the structured layout above.

## Key Commands

- `fluxloop init project` – scaffold a new project (configs, `.env`, examples)
- `fluxloop generate inputs` – produce input variations for the active project
- `fluxloop run experiment` – execute an experiment using `configs/simulation.yaml`
- `fluxloop parse experiment` – convert experiment outputs into readable artifacts
- `fluxloop config set-llm` – update LLM provider/model in `configs/input.yaml`
- `fluxloop record enable|disable|status` – toggle recording mode across `.env` and simulation config

Run `fluxloop --help` or `fluxloop <command> --help` for more detail.

## Runner Integration Patterns

Configure how FluxLoop calls your code in `configs/simulation.yaml`:

- Module + function: `module_path`/`function_name` or `target: "module:function"`
- Class.method (zero-arg ctor): `target: "module:Class.method"`
- Module-scoped instance method: `target: "module:instance.method"`
- Class.method with factory: add `factory: "module:make_instance"` (+ `factory_kwargs`)
- Async generators: set `runner.stream_output_path` if your streamed event shape differs (default `message.delta`).

See full examples: `packages/website/docs-cli/configuration/runner-targets.md`.

## Developing

Install dependencies and run tests:

```
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

To package the CLI:

```
./build.sh
```

