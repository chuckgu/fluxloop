---
sidebar_position: 6
---

# Integration View

The **Integration** view provides a centralized dashboard for the Integration Assistant feature, combining system monitoring, console tools, MCP connection management, and suggestion history.

## Overview

The Integration view is located in the FluxLoop activity bar and contains:

- **System Status**: Real-time checks for dependencies and environment
- **System Console**: Tools for environment management and diagnostics
- **Search in Documents**: Knowledge search via MCP
- **Recent Suggestions**: History of knowledge searches and agent runs

## View Components

### System Status

Expandable section showing dependency checks:

| Item | Description | States |
|------|-------------|--------|
| **FluxLoop CLI** | CLI installation status | ✅ Installed / ❌ Not found |
| **Python Environment** | Python 3.11+ availability | ✅ Ready / ❌ Missing |
| **fluxloop-mcp Package** | MCP server package | ✅ Installed / ❌ Not installed |
| **MCP Index** | Knowledge base status | ✅ Ready / ⚠️ Missing / ❌ Error |
| **Refresh Status** | Manual refresh button | - |

**Auto-refresh**:
- Status updates when project changes
- Manual refresh via **Refresh Status** button

### System Console

Tools for environment configuration and diagnostics:

| Item | Description |
|------|-------------|
| **Show Installation Guide** | Opens comprehensive setup documentation |
| **Select Environment** | Choose Python environment (Auto/Workspace/Global/Custom) |
| **Show Environment** | Display current environment details |
| **Connect MCP** | Check MCP status and install if needed |
| **Run Doctor** | Run diagnostic checks on FluxLoop installation |

#### Show Installation Guide

Opens a detailed guide covering:
- FluxLoop CLI installation steps
- Python environment setup
- MCP server configuration
- Explanation of System Console tools

### Search in Documents

Launch button for querying documentation via MCP FAQ:
- Click to open search input
- Results appear in FluxLoop output channel
- Recent queries saved to **Recent Suggestions**

### Recent Suggestions

Lists the 5 most recent knowledge searches and Flux Agent runs.

**Display format**: `[timestamp] • [query or file name]`

**Actions**:
- **Click** to view full suggestion in output channel or panel
- **Right-click** → **Clear History** to remove all entries

## Status Indicators

### Connection States

- ✅ **OK**: Component is ready and functional
- ⚠️ **Warning**: Component works but has issues (e.g., index missing)
- ❌ **Error**: Component is unavailable or broken
- ❓ **Unknown**: Status not yet determined

### Common Status Combinations

| Python | fluxloop-mcp | MCP Index | Action |
|--------|--------------|-----------|--------|
| ✅ | ✅ | ✅ | Ready to use |
| ✅ | ✅ | ⚠️ | Run `rebuild_index.sh` |
| ✅ | ❌ | ❌ | Run `pip install fluxloop-mcp` |
| ❌ | - | - | Install Python 3.11+ |

## Using the View

### First-Time Setup

1. Open **Integration** view
2. Expand **System Status** to check dependencies
3. If any items show ❌:
   - Click **Show Installation Guide** in System Console
   - Follow the setup instructions
4. Once all items show ✅, you're ready to use integration features

### Daily Workflow

1. Check **System Status** for any issues
2. Use **Search in Documents** for quick documentation lookups
3. Review **Recent Suggestions** for past queries

### Knowledge Search

1. Click **Search in Documents**
2. Enter your question
3. Review answer in FluxLoop output channel
4. Find the entry in **Recent Suggestions** for later reference

## Keyboard Shortcuts

No default keyboard shortcuts are assigned. You can add custom shortcuts via:

1. Open Keyboard Shortcuts (`Cmd+K Cmd+S` or `Ctrl+K Ctrl+S`)
2. Search for "FluxLoop Integration"
3. Assign your preferred shortcuts:
   - `FluxLoop: Open Knowledge Search`
   - `FluxLoop: Connect MCP`

## Integration with Other Views

### Projects View
- Switching active project triggers Integration status refresh
- Project-specific MCP index paths (if configured)

### Results View
- Flux Agent suggestions can reference experiment results
- Cross-link between integration plans and test outcomes

## Next Steps

- [Integration Assistant Overview](../integration-assistant/overview.md)
- [Using Flux Agent](../integration-assistant/flux-agent.md)
- [Knowledge Search](../integration-assistant/knowledge-search.md)
