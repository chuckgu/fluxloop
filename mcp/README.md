# Fluxloop MCP Server

**Model Context Protocol server providing AI-assisted integration guidance for Fluxloop SDK.**

This package exposes tools for documentation Q&A, repository analysis, framework detection, and integration planning. It helps developers integrate Fluxloop into their projects by analyzing code structure and recommending appropriate setup steps.

## Features

### Implemented (M0-M2)
- **FAQ Tool**: RAG-based documentation search with citations from indexed Fluxloop guides
- **Repository Analysis**: Scans languages, package managers, entry points, LOC, and risk flags
- **Framework Detection**: Identifies Express, FastAPI, Next.js, NestJS with confidence scoring
- **Integration Steps**: Generates framework-specific checklists with package manager awareness
- **Edit Plan Proposal**: Creates structured edit plans with anchors, payload, post-checks, and rollback
- **Plan Validation**: Verifies file existence, anchor patterns, and duplicate code detection
- **End-to-End Workflow**: `analyze → detect → steps → plan → validate` pipeline in one call

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

### 1. Build the Knowledge Index
```bash
# Default output: ~/.fluxloop/mcp/index/dev
packages/mcp/scripts/rebuild_index.sh
```

### 2. Test FAQ Query
```bash
python -m fluxloop_mcp.server --once --query "How to integrate FastAPI?"
```

### 3. Run as MCP Server (stdio)
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

### 4. Analyze a Repository
```python
from fluxloop_mcp.tools import AnalyzeRepositoryTool, DetectFrameworksTool

profile = AnalyzeRepositoryTool().analyze({"root": "."})
print(profile)

frameworks = DetectFrameworksTool().detect({"repository_profile": profile})
print(frameworks)
```

### 5. Run Full Integration Workflow
```python
from fluxloop_mcp.tools import RunIntegrationWorkflowTool

result = RunIntegrationWorkflowTool().run({"root": "."})
print(result.keys())  # profile, detection, integration_steps, edit_plan, validation
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

## Configuration

### Environment Variables
- `MCP_VECTOR_BACKEND`: `faiss` (default) | `qdrant` | `none`
- `MCP_QDRANT_URL`: Qdrant server URL (if using remote backend)
- `MCP_QDRANT_API_KEY`: Qdrant API key
- `MCP_INDEX_MODE`: `bundled` | `download` | `remote`
- `MCP_INDEX_PATH`: Custom index directory (default: `~/.fluxloop/mcp/index/dev`)

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

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.

## License

Apache 2.0 - See [LICENSE](../../LICENSE)
