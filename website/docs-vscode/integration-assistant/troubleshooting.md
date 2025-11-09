---
sidebar_position: 5
---

# Integration Assistant Troubleshooting

Common issues and solutions for the Integration Assistant feature.

## MCP Connection Issues

### "fluxloop-mcp package is not installed"

**Cause**: The `fluxloop-mcp` Python package is missing.

**Solution**:

```bash
pip install fluxloop-mcp
```

Then click **Refresh Integration View** or restart VSCode.

### "MCP Index not found"

**Cause**: Knowledge index hasn't been built yet.

**Solution**:

```bash
# Option 1: Use the MCP command
fluxloop-mcp rebuild-index

# Option 2: Run the script (if you have the repo)
cd packages/mcp
./scripts/rebuild_index.sh
```

The index will be created at `~/.fluxloop/mcp/index/dev`.

### "Python Environment not available"

**Cause**: Python 3.11+ is not installed or not in PATH.

**Solution**:

1. Install Python 3.11 or newer
2. Verify: `python3 --version`
3. Restart VSCode
4. Click **Refresh Integration View**

### MCP Process Fails to Start

**Cause**: Python environment issues or corrupted installation.

**Solution**:

```bash
# Reinstall fluxloop-mcp
pip uninstall fluxloop-mcp
pip install fluxloop-mcp

# Verify installation
fluxloop-mcp --version
```

Check the **FluxLoop** output channel for detailed error messages.

## OpenAI API Issues

### "OpenAI API key is required"

**Cause**: No API key configured.

**Solution**:

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Store in VSCode settings:
   ```json
   {
     "fluxloop.openaiApiKey": "sk-..."
   }
   ```
3. Or enter when prompted (can be saved to Secret Storage)

### "Invalid API key" or "Unauthorized"

**Cause**: API key is incorrect or expired.

**Solution**:

1. Verify your key at [OpenAI Platform](https://platform.openai.com/api-keys)
2. Update in VSCode settings or Secret Storage
3. Try again

### "Rate limit exceeded"

**Cause**: Too many API requests.

**Solution**:

- Wait a few minutes before retrying
- Use a different model (e.g., `gpt-4o-mini` instead of `gpt-4o`)
- Check your OpenAI usage limits

### API Call Timeout

**Cause**: Network issues or slow model response.

**Solution**:

- Check your internet connection
- Switch to a faster model (`gpt-4o-mini`)
- Try again in a few moments

## Flux Agent Issues

### "Open a file and place the cursor where you need guidance"

**Cause**: No file is open in the editor.

**Solution**:

1. Open a source file (e.g., `src/server.ts`, `app/main.py`)
2. Optionally select a code block
3. Run Flux Agent again

### "Open a FluxLoop project workspace"

**Cause**: No workspace folder is open.

**Solution**:

1. Open a folder containing your FluxLoop project
2. Ensure `configs/` directory exists
3. Run Flux Agent again

### Suggestions Are Too Generic

**Cause**: Insufficient context or selection.

**Solution**:

1. **Select specific code**: Highlight the exact function/class you want to enhance
2. **Open main files**: Open entry points like `server.ts` or `main.py`
3. **Add project context**: Ensure `package.json`/`requirements.txt` exist
4. **Try Knowledge Search first**: Get framework-specific info before running agent

### Suggestions Don't Match My Framework

**Cause**: MCP analysis incorrectly detected framework.

**Solution**:

1. Check **System Status** → **MCP Index** is ready
2. Verify your project has clear framework indicators:
   - Express: `package.json` with `"express": "..."`
   - FastAPI: `requirements.txt` with `fastapi`
   - Next.js: `package.json` with `"next": "..."`
3. Rebuild index if recipes were recently updated:
   ```bash
   fluxloop-mcp rebuild-index
   ```

## Performance Issues

### Slow Response Times

**Cause**: Large files or complex analysis.

**Solutions**:

- **Select smaller code blocks** instead of entire files
- **Use faster models**: Switch to `gpt-4o-mini`
- **Check MCP index**: Ensure it's not rebuilding in the background

### Extension Becomes Unresponsive

**Cause**: Background process stuck.

**Solution**:

1. Check **FluxLoop** output channel for errors
2. Restart VSCode
3. Verify Python processes:
   ```bash
   ps aux | grep fluxloop-mcp
   ```
4. Kill any stuck processes if needed

## Data and Privacy

### Where is Data Stored?

- **MCP Index**: `~/.fluxloop/mcp/index/dev` (local only)
- **Suggestions**: VSCode workspace state (local only)
- **API Keys**: VSCode Secret Storage (encrypted) or workspace settings

### What Data is Sent to OpenAI?

When you run Flux Agent, the following is sent to OpenAI API:
- Selected code snippet or file content (truncated to ~4000 chars)
- MCP analysis results (framework detection, file paths)
- Your structured prompt

**Not sent:**
- Full codebase
- Environment variables or secrets
- Private repository metadata

## Getting Help

If you encounter issues not covered here:

1. Check the **FluxLoop** output channel for detailed logs
2. Review [VSCode Extension Troubleshooting](../troubleshooting.md)
3. Visit [GitHub Issues](https://github.com/chuckgu/fluxloop/issues)
4. Check [MCP Server Docs](/mcp) for protocol-level debugging

## Next Steps

- [Knowledge Search](./knowledge-search.md) - Learn about documentation queries
- [Integration View](../views/integration-view.md) - View reference
- [Setup Guide](./setup.md) - Installation and configuration

