---
id: installation
title: Installation & Setup
sidebar_position: 2
---

# Installation & Setup

## Prerequisites

- Python 3.8 or higher
- pip or pipx
- Cursor, Claude Desktop, or another MCP-compatible client

## Install the MCP Server

### Option 1: Using pipx (Recommended)

```bash
pipx install fluxloop-mcp
```

**Benefits:**
- Isolated environment (no dependency conflicts)
- Global `fluxloop-mcp` command available

### Option 2: Using pip

```bash
pip install fluxloop-mcp
```

### Option 3: From Source (Development)

```bash
cd /path/to/fluxloop/packages/mcp
pip install -e .
```

## Build the Knowledge Index

The MCP server requires a pre-built knowledge index to answer questions and provide integration guidance.

```bash
# Build default index to ~/.fluxloop/mcp/index/dev
fluxloop-mcp rebuild-index

# Or use the script directly
packages/mcp/scripts/rebuild_index.sh
```

**What gets indexed:**
- Fluxloop documentation from `docs/`
- CLI guides from `packages/website/docs-cli/`
- SDK guides from `packages/website/docs-sdk/`
- Sample code from `examples/`

**Index location:**
- Default: `~/.fluxloop/mcp/index/dev/`
- Custom: Set `MCP_INDEX_PATH` environment variable

## Verify Installation

```bash
# Check version
fluxloop-mcp --version

# Test FAQ query
fluxloop-mcp --once --query "How to integrate FastAPI?"
```

**Expected output:**
```json
{
  "type": "response",
  "result": {
    "answer": "...",
    "citations": [...]
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

Restart Cursor.

### Claude Desktop Users

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fluxloop": {
      "command": "fluxloop-mcp",
      "args": []
    }
  }
}
```

Restart Claude Desktop.

### Other MCP Clients

Refer to your client's documentation for MCP server configuration. Use:
- **Command**: `fluxloop-mcp`
- **Protocol**: stdio (default)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_VECTOR_BACKEND` | `faiss` | Vector search backend: `faiss`, `qdrant`, `none` |
| `MCP_INDEX_MODE` | `bundled` | Index source: `bundled`, `download`, `remote` |
| `MCP_INDEX_PATH` | `~/.fluxloop/mcp/index/dev` | Custom index directory |
| `MCP_QDRANT_URL` | - | Qdrant server URL (if using remote backend) |
| `MCP_QDRANT_API_KEY` | - | Qdrant API key |

## Troubleshooting

### "Command not found: fluxloop-mcp"

**Cause:** Package not installed or not in PATH.

**Solution:**
```bash
# Verify installation
pip list | grep fluxloop-mcp

# Reinstall if missing
pip install --force-reinstall fluxloop-mcp
```

### "Index directory does not exist"

**Cause:** Knowledge index not built.

**Solution:**
```bash
fluxloop-mcp rebuild-index
```

### "No matching documents found"

**Cause:** Index is empty or outdated.

**Solution:**
```bash
# Rebuild index
fluxloop-mcp rebuild-index

# Verify index
python -m fluxloop_mcp.index.validator --index-dir ~/.fluxloop/mcp/index/dev
```

### MCP Server Not Responding in Cursor

**Cause:** Configuration error or server crash.

**Solution:**
1. Check `~/.cursor/mcp.json` syntax (valid JSON)
2. Test server manually: `fluxloop-mcp --once --query test`
3. Check Cursor logs: View → Output → Select "MCP" channel

## Next Steps

- [Using with Cursor/Claude](./usage-cursor.md)
- [Tool Reference](./tools-reference.md)
- [Advanced Configuration](./configuration.md)

