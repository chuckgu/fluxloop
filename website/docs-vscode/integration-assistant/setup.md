---
sidebar_position: 2
---

# Setup Integration Assistant

This guide walks you through setting up the Integration Assistant feature in the FluxLoop VSCode extension.

## Prerequisites

### 1. Python Environment

Ensure you have Python 3.11 or newer:

```bash
python3 --version
# Should show: Python 3.11.0 or higher
```

### 2. Install fluxloop-mcp

Install the FluxLoop MCP server package:

```bash
pip install fluxloop-mcp
```

Verify installation:

```bash
fluxloop-mcp --version
# Should show: fluxloop-mcp 0.1.0 (or higher)
```

### 3. Build Knowledge Index

The MCP server requires a knowledge index built from FluxLoop documentation:

```bash
# If you cloned the fluxloop repository
cd packages/mcp
./scripts/rebuild_index.sh

# Or use the command directly
fluxloop-mcp rebuild-index
```

This creates an index at `~/.fluxloop/mcp/index/dev` containing:
- Indexed documentation chunks
- Framework recipes
- Search metadata

:::tip
The index only needs to be built once. It will be automatically updated when you upgrade `fluxloop-mcp`.
:::

### 4. Configure OpenAI API Key

The Flux Agent uses OpenAI's Chat Completions API for generating suggestions.

**Option 1: Store in VSCode Settings**

1. Open VSCode Settings (`Cmd+,` or `Ctrl+,`)
2. Search for "fluxloop openai"
3. Enter your API key in `Fluxloop: Openai Api Key`

**Option 2: Provide on First Use**

The extension will prompt for your API key when you first run Flux Agent. You can choose to:
- Enter the key and save it to Secret Storage (recommended)
- Enter the key for this session only
- Cancel and configure later

**Option 3: Manual Settings File**

Add to `.vscode/settings.json`:

```json
{
  "fluxloop.openaiApiKey": "sk-...",
  "fluxloop.openaiModel": "gpt-4o-mini"
}
```

:::warning
Never commit API keys to version control. Use workspace-local settings or Secret Storage.
:::

## Verify Setup

Open the **Integration** view in the FluxLoop activity bar:

1. Check **System Status** section:
   - ✅ **Python Environment** should show your Python version
   - ✅ **fluxloop-mcp Package** should show installed
   - ✅ **MCP Index** should show ready

2. Click **Connect MCP** to verify the connection

3. Try a knowledge search:
   - Click **Knowledge Search**
   - Enter: "How do I integrate FastAPI?"
   - Check the FluxLoop output channel for results

If all status indicators are green, you're ready to use Flux Agent!

## Configuration Options

### Model Selection

Choose the OpenAI model for suggestions (default: `gpt-4o-mini`):

```json
{
  "fluxloop.openaiModel": "gpt-4o"
}
```

Supported models:
- `gpt-4o-mini` (recommended, fast and cost-effective)
- `gpt-4o` (higher quality, slower)
- `gpt-4-turbo` (legacy)
- `gpt-3.5-turbo` (fastest, lower quality)

### MCP Index Path

Override the default index location:

```bash
export MCP_INDEX_PATH="/custom/path/to/index"
```

Or specify in VSCode settings:

```json
{
  "fluxloop.mcpIndexPath": "/custom/path/to/index"
}
```

## Next Steps

- [Knowledge Search Guide](./knowledge-search.md)
- [Using Flux Agent](./flux-agent.md)
- [Troubleshooting](./troubleshooting.md)

