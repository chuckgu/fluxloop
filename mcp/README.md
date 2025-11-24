# Fluxloop MCP Server

**Model Context Protocol server providing AI-assisted integration guidance for Fluxloop SDK.**

This package exposes tools for documentation Q&A, repository analysis, framework detection, and integration planning. It helps developers integrate Fluxloop into their projects by analyzing code structure and recommending appropriate setup steps.

## Requirements

- Python 3.11+
- macOS or Linux (Windows users can use WSL2)
- Git (for local development)

## Features

### Implemented (M0-M2)
- **FAQ Tool**: RAG-based documentation search with citations from indexed Fluxloop guides
- **Repository Analysis**: Scans languages, package managers, entry points, LOC, and risk flags
- **Framework Detection**: Identifies Express, FastAPI, Next.js, NestJS with confidence scoring
- **Integration Steps**: Generates framework-specific checklists with package manager awareness
- **Edit Plan Proposal**: Creates structured edit plans with anchors, payload, post-checks, and rollback
- **Plan Validation**: Verifies file existence, anchor patterns, and duplicate code detection
- **End-to-End Workflow**: `analyze → detect → steps → plan → validate` pipeline in one call
- **Multi-Mode Context APIs**: `fetch_integration_context`, `fetch_base_input_context`, `fetch_experiment_context`, `fetch_insight_context` provide mode-specific payloads for the VS Code Flux Agent (Integration, Base Input, Experiment, Insight)

### Indexing & Knowledge Base
- Document ingestion from `docs/`, `packages/website/docs-{cli,sdk}`, `samples/`
- Chunk-based storage (JSONL + SQLite metadata)
- BM25 + embedding hybrid retrieval (local FAISS or remote Qdrant)
- Recipe registry for framework-specific integration patterns

### MCP Protocol
- stdio-based server with structured `type: response/error` format
- Handshake capability discovery
- Supports `id`-based request/response correlation

## Installation

### From Source (Development)
```bash
cd packages/mcp
pip install -e .
```

### From PyPI (Planned)
```bash
pip install fluxloop-mcp
```

## Quick Start

### 1. Install
```bash
pip install fluxloop-mcp
```

### 2. Build the Knowledge Index
```bash
# Default output: ~/.fluxloop/mcp/index/dev
packages/mcp/scripts/rebuild_index.sh
```

### 3. Test FAQ Query
```bash
python -m fluxloop_mcp.server --once --query "How to integrate FastAPI?"
```

### 4. Run as MCP Server (stdio)
Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "fluxloop": {
      "command": "fluxloop-mcp",
      "args": [],
      "env": {
        "MCP_VECTOR_BACKEND": "faiss",
        "MCP_INDEX_MODE": "bundled"
      }
    }
  }
}
```

Restart Cursor/Claude Desktop. The MCP server will be available for queries.

### 5. Analyze a Repository
```python
from fluxloop_mcp.tools import AnalyzeRepositoryTool, DetectFrameworksTool

profile = AnalyzeRepositoryTool().analyze({"root": "."})
print(profile)

frameworks = DetectFrameworksTool().detect({"repository_profile": profile})
print(frameworks)
```

### 6. Run Full Integration Workflow
```python
from fluxloop_mcp.tools import RunIntegrationWorkflowTool

result = RunIntegrationWorkflowTool().run({"root": "."})
print(result.keys())  # profile, detection, integration_steps, edit_plan, validation
```

### 7. Local Development Environment
```bash
git clone https://github.com/chuckgu/fluxloop.git
cd fluxloop/packages/mcp
pip install -e ".[dev]"
pytest
```

## Available Tools

| Tool | Description |
|------|-------------|
| `handshake` | Returns server name, version, and capabilities |
| `faq` | Searches indexed documentation and returns answer + citations |
| `analyze_repository` | Scans project structure, languages, package managers, entry points |
| `detect_frameworks` | Identifies frameworks with confidence scores and recommended patterns |
| `generate_integration_steps` | Creates framework-specific integration checklist |
| `propose_edit_plan` | Generates structured edit plan with anchors and validation |
| `validate_edit_plan` | Verifies plan structure and checks file/anchor existence |
| `run_integration_workflow` | Executes full pipeline from analysis to validated plan |
| `fetch_integration_context` | Returns repo profile + integration workflow payloads for VS Code planner |
| `fetch_base_input_context` | Packages base input samples/service settings + RAG topics |
| `fetch_experiment_context` | Summarizes past experiments, runner configs, simulation templates |
| `fetch_insight_context` | Collects evaluation reports and aggregated metrics for Insight mode |

### Multi-Mode Planner Support

Flux Agent in VS Code currently operates in **Integration** mode only:

| Mode | MCP Tool | Data Provided |
| --- | --- | --- |
| Integration | `fetch_integration_context` | Repository profile, integration workflow, structure context, RAG topics |

Future releases will add:
- **Base Input** mode using `fetch_base_input_context`: Existing `inputs/` samples, `setting.yaml` preview, suggested RAG topics
- **Experiment** mode using `fetch_experiment_context`: `experiments/` summaries, runner configs, simulation templates
- **Insight** mode using `fetch_insight_context`: Evaluation reports (`summary.json`, `traces.jsonl`) and aggregated success metrics

The VS Code extension uses these APIs alongside the local planner to route LLM prompts per mode. Run the regression suite to ensure MCP changes don't break planners:

```bash
. .venv/bin/activate
python3 -m pytest packages/mcp -k multi_mode_regression
```

## Protocol (stdio)

Fluxloop MCP server follows the [Model Context Protocol](https://modelcontextprotocol.io/) over standard input/output. Each message is a single JSON object terminated by a newline.

### Message Envelope

| Field | Description |
|-------|-------------|
| `type` | `"handshake"`, `"request"`, `"response"`, or `"error"` |
| `id` | Client-supplied identifier used to correlate requests and responses |
| `tool` | Name of the tool to invoke (`request` messages only) |
| `params` | JSON payload passed to the tool (`request` messages only) |
| `result` | Successful tool output (`response` messages only) |
| `error` | Error metadata (`error` messages only) |

### Handshake

Clients must initiate a handshake before sending tool requests.

```json
{"type":"handshake","id":"1"}
```

Handshake response exposes server metadata and supported tools.

```json
{
  "type": "response",
  "id": "1",
  "result": {
    "name": "fluxloop-mcp",
    "version": "0.1.0",
    "capabilities": {
      "tools": [
        "handshake",
        "faq",
        "analyze_repository",
        "detect_frameworks",
        "generate_integration_steps",
        "propose_edit_plan",
        "validate_edit_plan",
        "run_integration_workflow"
      ]
    }
  }
}
```

### Tool Invocation

Request payloads are validated against the tool schema. Successful responses return structured JSON in the `result` field.

```json
{"type":"request","id":"42","tool":"faq","params":{"query":"How do I integrate FastAPI?"}}
```

```json
{
  "type": "response",
  "id": "42",
  "result": {
    "answer": "- Install fluxloop SDK...\n- Configure `simulation.yaml`...",
    "citations": [
      {
        "path": "packages/website/docs-sdk/integration/fastapi.md",
        "section": "Installation"
      }
    ]
  }
}
```

### Error Response

Errors maintain the same `id` and include a machine-readable `code`.

```json
{
  "type": "error",
  "id": "42",
  "error": {
    "code": "tool_not_found",
    "message": "Unknown tool: faqz",
    "details": {"availableTools": ["faq","analyze_repository", "..."]}
  }
}
```

Clients should fall back to the next strategy or surface the error to users.

## Configuration

### Environment Variables
- `MCP_VECTOR_BACKEND`: `faiss` (default) | `qdrant` | `none`
- `MCP_QDRANT_URL`: Qdrant server URL (if using remote backend)
- `MCP_QDRANT_API_KEY`: Qdrant API key
- `MCP_INDEX_MODE`: `bundled` | `download` | `remote`
- `MCP_INDEX_PATH`: Custom index directory (default: `~/.fluxloop/mcp/index/dev`)
- `MCP_AUTO_UPDATE`: `true` to allow automatic index download when newer releases are detected

## Architecture

```
fluxloop_mcp/
├── server.py           # stdio MCP server entry point
├── tools/              # Tool implementations
│   ├── faq.py
│   ├── analyze_repository.py
│   ├── detect_frameworks.py
│   ├── generate_integration_steps.py
│   ├── propose_edit_plan.py
│   ├── validate_edit_plan.py
│   └── run_integration_workflow.py
├── index/              # Document indexing & retrieval
│   ├── ingestor.py
│   ├── store.py
│   ├── retriever.py
│   ├── embedder.py
│   └── validator.py
├── recipes/            # Framework integration recipes
│   └── registry.py
└── schemas/            # JSON schemas for validation
    ├── repository_profile.json
    ├── edit_plan.json
    └── runner_pattern_metadata.json
```

## Roadmap

### M3: Quality & Stabilization (Next)
- [ ] pytest test suite for all tools with golden fixtures
- [ ] CI integration for index validation
- [ ] Comprehensive MCP protocol documentation
- [ ] Structured logging and error code standardization
- [ ] Performance benchmarks and caching improvements

### Future Enhancements
- [ ] Expand recipe coverage (Django, Flask, Svelte, etc.)
- [ ] AST-based code modification (beyond pattern matching)
- [ ] Streaming progress events for long-running workflows
- [ ] LLM-enhanced answer synthesis for FAQ
- [ ] Direct file editing with approval workflow
- [ ] Integration with VS Code extension for UI-based workflow

## Release Checklist

When publishing to PyPI:

1. Bump the version in `pyproject.toml` and update this README if necessary.
2. Run the quality checks:
   ```bash
   pip install -e ".[dev]"
   pytest
   ruff check fluxloop_mcp
   mypy fluxloop_mcp
   ```
3. Verify index rebuild succeeds:
   ```bash
   scripts/rebuild_index.sh
   ```
4. Build distribution artifacts:
   ```bash
   scripts/build.sh
   ```
5. Upload to PyPI (optionally via TestPyPI first):
   ```bash
   twine upload --repository testpypi dist/*
   twine upload dist/*
   ```
6. Tag the release and push:
   ```bash
   git tag mcp-v0.1.0
   git push origin mcp-v0.1.0
   ```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.

## License

Apache 2.0 - See [LICENSE](../../LICENSE)
