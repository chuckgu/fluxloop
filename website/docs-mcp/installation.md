---
id: installation
title: Installation & Setup
sidebar_position: 2
---

# Installation & Setup

## Prerequisites

- **Python 3.11 or higher** (required for MCP server)
- pip or pipx
- Cursor, Claude Desktop, VS Code with Flux extension, or another MCP-compatible client

:::info Python Version Requirement
The MCP server requires Python 3.11+ due to advanced type hints and protocol features. If you only need the CLI or SDK, those support Python 3.8+.
:::

## Install the MCP Server

### Option 1: Using pipx (Recommended)

```bash
pipx install fluxloop-mcp
```

**Benefits:**
- Isolated environment (no dependency conflicts)
- Global `fluxloop-mcp` command available
- Easy updates: `pipx upgrade fluxloop-mcp`

### Option 2: Using pip

```bash
pip install fluxloop-mcp
```

**Note:** Consider using a virtual environment to avoid conflicts.

### Option 3: From Source (Development)

```bash
cd /path/to/fluxloop/packages/mcp
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

## Verify Installation

```bash
# Check version
fluxloop-mcp --version

# Expected output:
# fluxloop-mcp 0.1.1
```

## Build the Knowledge Index

The MCP server requires a pre-built knowledge index to answer questions and provide integration guidance.

### Quick Build

```bash
# Build default index to ~/.fluxloop/mcp/index/dev
fluxloop-mcp rebuild-index
```

### Using the Build Script

```bash
# From Fluxloop repo root
packages/mcp/scripts/rebuild_index.sh

# Custom output directory
packages/mcp/scripts/rebuild_index.sh ~/.fluxloop/mcp/index/custom
```

**What gets indexed:**
- Fluxloop documentation from `docs/`
- CLI guides from `packages/website/docs-cli/`
- SDK guides from `packages/website/docs-sdk/`
- MCP guides from `packages/website/docs-mcp/`
- Sample code from `samples/` and `examples/`

**Index structure:**
```
~/.fluxloop/mcp/index/dev/
├── chunks.jsonl        # Document chunks with metadata
├── metadata.db         # SQLite index
├── faiss.index         # FAISS vector index
└── manifest.json       # Index metadata
```

**Index location:**
- **Default**: `~/.fluxloop/mcp/index/dev/`
- **Custom**: Set `MCP_INDEX_PATH` environment variable
- **Bundled**: Future releases will include pre-built indexes

## Test the Installation

Test that the MCP server can answer queries:

```bash
# Simple FAQ query
fluxloop-mcp --once --query "How to integrate FastAPI?"

# Expect JSON response with answer and citations
```

**Expected output:**
```json
{
  "type": "response",
  "result": {
    "answer": "To integrate FastAPI with Fluxloop:\n\n1. Install the SDK...",
    "citations": [
      "packages/website/docs-cli/configuration/runners/python-function.md"
    ],
    "score": 0.87
  }
}
```

## Configure MCP Client

### Cursor Users

Edit `~/.cursor/mcp.json`:

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

**Restart Cursor** after editing the configuration.

**Test in Cursor:**
1. Open a project
2. Use AI chat: "Ask Fluxloop MCP how to integrate FastAPI"
3. MCP server should respond with integration guidance

### Claude Desktop Users

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or equivalent on Windows/Linux:

```json
{
  "mcpServers": {
    "fluxloop": {
      "command": "fluxloop-mcp",
      "args": [],
      "env": {
        "MCP_VECTOR_BACKEND": "faiss"
      }
    }
  }
}
```

:::tip Use Absolute Path
If `fluxloop-mcp` is installed in a virtual environment, use the absolute path:
```json
{
  "command": "/Users/yourname/.local/pipx/venvs/fluxloop-mcp/bin/fluxloop-mcp"
}
```
:::

**Restart Claude Desktop** after configuration.

### VS Code with Flux Extension

The Fluxloop VS Code extension automatically detects and uses the MCP server if installed. No manual configuration needed.

**Verify:**
1. Install Flux extension from VS Code marketplace
2. Open Command Palette: `FluxLoop: Show Environment Info`
3. Check MCP server status

### Other MCP Clients

For other MCP clients, configure with:
- **Protocol**: stdio (JSON messages over stdin/stdout)
- **Command**: `fluxloop-mcp` (or full path)
- **Transport**: Standard input/output

## Environment Variables

Configure the MCP server behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_VECTOR_BACKEND` | `faiss` | Vector search: `faiss`, `qdrant`, `none` |
| `MCP_INDEX_MODE` | `bundled` | Index source: `bundled`, `download`, `remote` |
| `MCP_INDEX_PATH` | `~/.fluxloop/mcp/index/dev` | Custom index directory |
| `MCP_QDRANT_URL` | - | Qdrant server URL (if using remote) |
| `MCP_QDRANT_API_KEY` | - | Qdrant API key |
| `MCP_LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MCP_AUTO_UPDATE` | `false` | Auto-update index from releases |

**Example configuration:**

```bash
# Use remote Qdrant for team-shared knowledge base
export MCP_VECTOR_BACKEND=qdrant
export MCP_QDRANT_URL=https://your-qdrant.example.com
export MCP_QDRANT_API_KEY=your-api-key

# Enable debug logging
export MCP_LOG_LEVEL=DEBUG

# Custom index path
export MCP_INDEX_PATH=~/.fluxloop/mcp/index/production
```

## Troubleshooting

### "Command not found: fluxloop-mcp"

**Cause:** Package not installed or not in PATH.

**Solution:**
```bash
# Verify installation
pip list | grep fluxloop-mcp

# Check command location
which fluxloop-mcp

# Reinstall if missing
pip install --force-reinstall fluxloop-mcp

# Or use pipx
pipx install fluxloop-mcp
```

### "Index directory does not exist"

**Cause:** Knowledge index not built.

**Solution:**
```bash
# Build index
fluxloop-mcp rebuild-index

# Or use script
packages/mcp/scripts/rebuild_index.sh

# Verify index exists
ls -la ~/.fluxloop/mcp/index/dev/
```

### "No matching documents found"

**Cause:** Index is empty or outdated.

**Solution:**
```bash
# Rebuild index
fluxloop-mcp rebuild-index

# Verify index size
du -sh ~/.fluxloop/mcp/index/dev/

# Check chunk count
wc -l ~/.fluxloop/mcp/index/dev/chunks.jsonl
```

### MCP Server Not Responding in Cursor

**Cause:** Configuration error or server crash.

**Solution:**

1. **Check configuration syntax:**
   ```bash
   cat ~/.cursor/mcp.json | python -m json.tool
   ```

2. **Test server manually:**
   ```bash
   fluxloop-mcp --once --query "test"
   ```

3. **Check Cursor logs:**
   - View → Output → Select "MCP" channel
   - Look for error messages

4. **Verify Python version:**
   ```bash
   python --version
   # Must be 3.11+
   ```

5. **Restart Cursor completely** (not just reload window)

### "Python version 3.11 required"

**Cause:** MCP server requires Python 3.11+.

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.11+ if needed
# macOS (Homebrew):
brew install python@3.11

# Ubuntu/Debian:
sudo apt install python3.11

# Then reinstall MCP server with correct Python
python3.11 -m pip install fluxloop-mcp
```

### Index Build Fails

**Cause:** Missing source files or permissions.

**Solution:**
```bash
# Check repository structure
ls -la packages/website/docs-cli/
ls -la packages/website/docs-sdk/

# Ensure you're in Fluxloop repo root
cd /path/to/fluxloop

# Rebuild with verbose output
MCP_LOG_LEVEL=DEBUG packages/mcp/scripts/rebuild_index.sh

# Check permissions
chmod -R u+w ~/.fluxloop/mcp/index/
```

## Updating the MCP Server

### Upgrade via pip/pipx

```bash
# pipx
pipx upgrade fluxloop-mcp

# pip
pip install --upgrade fluxloop-mcp
```

### Rebuild Index After Upgrade

```bash
# Rebuild to include new documentation
fluxloop-mcp rebuild-index

# Or use force flag to clear old index
fluxloop-mcp rebuild-index --force
```

## Next Steps

- **[Using with Cursor](./usage-cursor.md)** - Cursor IDE integration guide
- **[Using with VS Code](./usage-vscode.md)** - VS Code Flux extension guide
- **[Tool Reference](./tools-reference.md)** - Available MCP tools
- **[Configuration](./configuration.md)** - Advanced configuration options


