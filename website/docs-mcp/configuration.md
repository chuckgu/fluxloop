---
id: configuration
title: Advanced Configuration
sidebar_position: 5
---

# Advanced Configuration

## Environment Variables

### Vector Backend Configuration

Control how the MCP server stores and searches document embeddings.

#### Local FAISS (Default)
```bash
export MCP_VECTOR_BACKEND=faiss
export MCP_INDEX_PATH=~/.fluxloop/mcp/index/dev
```

**Best for:**
- Single-user local development
- Offline usage
- Fast startup with no external dependencies

#### Remote Qdrant
```bash
export MCP_VECTOR_BACKEND=qdrant
export MCP_QDRANT_URL=https://your-qdrant-instance.example.com
export MCP_QDRANT_API_KEY=your-api-key
```

**Best for:**
- Team-shared knowledge base
- Large document collections (>10k chunks)
- Advanced filtering and multi-user concurrency

#### No Vector Search
```bash
export MCP_VECTOR_BACKEND=none
```

Uses keyword-only (BM25) search. Faster but less accurate for semantic queries.

### Index Management

#### Index Mode
```bash
# Bundled with package (default)
export MCP_INDEX_MODE=bundled

# Download on first run
export MCP_INDEX_MODE=download

# Use remote index service
export MCP_INDEX_MODE=remote
```

#### Auto-Update
```bash
# Check for updates daily
export MCP_AUTO_UPDATE=true
export MCP_UPDATE_CHECK_INTERVAL=86400  # seconds
```

#### Custom Index Path
```bash
export MCP_INDEX_PATH=/custom/path/to/index
```

## MCP Client Configuration

### Cursor

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "fluxloop": {
      "command": "fluxloop-mcp",
      "args": [],
      "env": {
        "MCP_VECTOR_BACKEND": "faiss",
        "MCP_INDEX_MODE": "bundled",
        "MCP_INDEX_PATH": "/Users/yourname/.fluxloop/mcp/index/dev"
      }
    }
  }
}
```

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fluxloop": {
      "command": "/path/to/venv/bin/fluxloop-mcp",
      "env": {
        "MCP_VECTOR_BACKEND": "faiss"
      }
    }
  }
}
```

:::tip
Use absolute path to `fluxloop-mcp` if installed in a virtual environment.
:::

### Custom MCP Client

For other MCP clients, use:
- **Protocol**: stdio
- **Command**: `fluxloop-mcp` (or full path)
- **Transport**: Standard input/output with JSON-RPC-like messages

## Recipe Customization

### Adding Custom Recipes

Recipes define framework-specific integration patterns. To add a custom recipe:

1. Create `~/.fluxloop/mcp/recipes/custom.json`:

```json
{
  "framework": "my-framework",
  "pkgManager": "npm",
  "packages": ["@fluxloop/sdk"],
  "runner_pattern": "http-rest",
  "doc_url": "https://example.com/docs",
  "steps": [
    {
      "id": "install",
      "title": "Install SDK",
      "details": "npm install @fluxloop/sdk"
    }
  ],
  "anchors": [
    {"name": "app_init", "pattern": "const app = MyFramework()"}
  ]
}
```

2. Set environment variable:
```bash
export MCP_CUSTOM_RECIPES_DIR=~/.fluxloop/mcp/recipes
```

3. Restart MCP server

### Recipe Schema

See `packages/mcp/fluxloop_mcp/schemas/runner_pattern_metadata.json` for the complete schema.

## Logging

### Enable Debug Logging

```bash
export MCP_LOG_LEVEL=DEBUG
fluxloop-mcp
```

Logs are written to stderr (visible in MCP client output channels).

### Log File
```bash
export MCP_LOG_FILE=~/.fluxloop/mcp/server.log
fluxloop-mcp
```

## Performance Tuning

### Chunk Size
Control document chunking granularity during indexing:

```bash
python -m fluxloop_mcp.index.ingestor \
  --output ~/.fluxloop/mcp/index/dev \
  --chunk-size 512
```

Larger chunks = better context, slower search.

### Cache Configuration
```bash
export MCP_CACHE_DIR=~/.fluxloop/mcp/cache
export MCP_CACHE_TTL=3600  # seconds
```

### Retrieval Parameters
```bash
export MCP_RETRIEVAL_TOP_K=5
export MCP_RETRIEVAL_MIN_SCORE=0.5
```

## Security & Privacy

### Read-Only Mode (Default)
The MCP server operates in read-only mode by default:
- Analyzes files without modification
- Proposes plans but doesn't apply them
- No git operations

### Sensitive Data Handling
```bash
# Mask API keys and secrets in logs
export MCP_MASK_SECRETS=true

# Limit path exposure in citations
export MCP_RELATIVE_PATHS_ONLY=true
```

### Network Isolation
For air-gapped environments:
```bash
export MCP_VECTOR_BACKEND=faiss
export MCP_INDEX_MODE=bundled
export MCP_AUTO_UPDATE=false
```

## Multi-User Setup

For teams sharing a centralized knowledge base:

### Shared Qdrant Instance
```bash
# Deploy Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Build index once
MCP_VECTOR_BACKEND=qdrant \
MCP_QDRANT_URL=http://localhost:6333 \
  packages/mcp/scripts/rebuild_index.sh

# Each user configures
export MCP_VECTOR_BACKEND=qdrant
export MCP_QDRANT_URL=http://shared-qdrant.company.com:6333
```

### Shared Index Repository
Use git or cloud storage to distribute pre-built indexes:

```bash
# Build once
packages/mcp/scripts/rebuild_index.sh

# Package index
cd ~/.fluxloop/mcp/index/dev
tar czf fluxloop_mcp_index_v0.1.0.tar.gz *

# Distribute to team
# Users extract to ~/.fluxloop/mcp/index/dev/
```

## Troubleshooting

### Index Out of Date

```bash
# Manual rebuild
fluxloop-mcp rebuild-index

# Or
packages/mcp/scripts/rebuild_index.sh
```

### Slow Queries

- Reduce `MCP_RETRIEVAL_TOP_K`
- Increase `chunk-size` during indexing
- Enable caching with `MCP_CACHE_DIR`

### Memory Usage

For large indexes, use remote Qdrant instead of local FAISS:
```bash
export MCP_VECTOR_BACKEND=qdrant
```

## Advanced Use Cases

### Custom Document Sources

Add your own documentation to the index:

```bash
python -m fluxloop_mcp.index.ingestor \
  --output ~/.fluxloop/mcp/index/custom \
  --source /path/to/your/docs/**/*.md
```

### Programmatic Access

Use MCP tools directly in Python:

```python
from fluxloop_mcp.tools import RunIntegrationWorkflowTool

workflow = RunIntegrationWorkflowTool()
result = workflow.run({"root": "/path/to/project"})

print(result["edit_plan"]["summary"])
print(result["validation"]["warnings"])
```

### CI Integration

Validate index quality in CI:

```bash
# In .github/workflows/ci.yml
- name: Validate MCP Index
  run: |
    packages/mcp/scripts/rebuild_index.sh
    python -m fluxloop_mcp.index.validator --index-dir ~/.fluxloop/mcp/index/dev
```

## Next Steps

- [Examples](./examples.md)
- [Tool Reference](./tools-reference.md)

