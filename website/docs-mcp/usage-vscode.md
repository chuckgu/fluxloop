---
sidebar_position: 4
---

# Using with VSCode Extension

The FluxLoop VSCode extension provides a graphical interface for the MCP server, making it easy to use without manual CLI commands.

## Overview

Instead of running `fluxloop-mcp` commands manually, the VSCode extension:

- Automatically manages the MCP server process
- Provides visual status indicators
- Offers one-click knowledge search
- Integrates MCP analysis with Flux Agent for code suggestions

## Setup

### Install VSCode Extension

1. Open VSCode or Cursor
2. Search for "FluxLoop" in Extensions
3. Click Install

### Install MCP Server

The extension requires the MCP server package:

```bash
pip install fluxloop-mcp
```

### Build Index

```bash
fluxloop-mcp rebuild-index
```

## Using Integration View

Once installed, open the **FluxLoop** activity bar and navigate to the **Integration** view.

### Check Status

The **System Status** section shows:

- ✅ **fluxloop-mcp Package**: Installed and ready
- ✅ **MCP Index**: Knowledge base built
- ✅ **Python Environment**: Python 3.11+ detected

If any item shows ❌, click it for installation guidance.

### Knowledge Search

1. Click **Knowledge Search** button
2. Enter your question (e.g., "How do I trace FastAPI endpoints?")
3. View the answer in the FluxLoop output channel

The extension calls `fluxloop-mcp --once --query "<your question>"` behind the scenes.

### Flux Agent

For detailed integration suggestions:

1. Open a file you want to enhance
2. Click **Run Flux Agent**
3. Choose a mode (Integration, Base Input, Experiment, Insight) depending on whether you need code changes, base inputs, simulation updates, or insight analysis
4. The extension:
   - Runs `fluxloop-mcp` with `run_integration_workflow` tool
   - Combines analysis with LLM reasoning
   - Presents a detailed integration plan

## Features Powered by MCP

### Repository Analysis
- Automatic framework detection (Express, FastAPI, Next.js, etc.)
- Entry point identification
- Package manager detection

### Integration Planning
- Framework-specific code snippets
- Anchor-based insertion points
- Post-integration validation steps

### Documentation Search
- Citation-backed answers
- Context-aware suggestions
- Framework recipe lookup

## Workflow Comparison

### Manual MCP Usage (CLI)

```bash
# Step 1: Analyze
echo '{"type":"request","id":"1","tool":"analyze_repository","params":{"root":"."}}' | fluxloop-mcp

# Step 2: Parse JSON response manually
# Step 3: Run next tool based on results
# Step 4: Copy/paste code snippets
```

### VSCode Extension (Integrated)

1. Click **Run Flux Agent**
2. Review suggestion panel
3. Copy and apply changes

The extension handles all MCP communication, JSON parsing, and workflow orchestration automatically.

## Advanced: Direct MCP Access

If you need to call MCP tools directly (for scripting or debugging):

```bash
# Test FAQ
fluxloop-mcp --once --query "How do I configure runners?"

# Test workflow
echo '{"type":"request","id":"1","tool":"run_integration_workflow","params":{"root":"."}}' | fluxloop-mcp
```

But for daily use, the VSCode Integration view is recommended.

## Next Steps

- [VSCode Integration Assistant Overview](/vscode/integration-assistant/overview)
- [Using Flux Agent](/vscode/integration-assistant/flux-agent)
- [Knowledge Search Guide](/vscode/integration-assistant/knowledge-search)

