---
sidebar_position: 6
---

# Integration View

The **Integration** view provides a centralized dashboard for the Integration Assistant feature, combining MCP connection management, system status monitoring, and suggestion history.

## Overview

The Integration view is located in the FluxLoop activity bar and contains:

- **MCP Connection**: Status and connection controls
- **Flux Agent**: Launch the AI-powered integration assistant
- **System Status**: Real-time checks for dependencies and environment
- **Recent Suggestions**: History of knowledge searches and agent runs

## View Components

### MCP Connection

Shows the current state of the MCP server connection:

- ✅ **Connected**: MCP server is ready
- ⚠️ **Warning**: Package installed but index missing
- ❌ **Error**: Package not installed or Python unavailable
- ❓ **Unknown**: Status check pending

**Actions**:
- **Click** to connect/reconnect MCP
- **Tooltip** shows installation path and last error (if any)

### Flux Agent

Launch button for running the integration assistant.

**Actions**:
- **Click** to run Flux Agent on the current file
- Requires an active file open in the editor

### System Status

Expandable section showing dependency checks:

| Item | Description | States |
|------|-------------|--------|
| **FluxLoop CLI** | CLI installation status | ✅ Installed / ❌ Not found |
| **Python Environment** | Python 3.11+ availability | ✅ Ready / ❌ Missing |
| **fluxloop-mcp Package** | MCP server package | ✅ Installed / ❌ Not installed |
| **MCP Index** | Knowledge base status | ✅ Ready / ⚠️ Missing / ❌ Error |

**Auto-refresh**:
- Status updates when project changes
- Manual refresh via **Refresh Integration View** button

### Recent Suggestions

Lists the 5 most recent knowledge searches and Flux Agent runs.

**Display format**: `[timestamp] • [query or file name]`

**Actions**:
- **Click** to view full suggestion in output channel or panel
- **Right-click** → **Clear History** to remove all entries

## Toolbar Actions

The view toolbar (top-right) provides quick actions:

| Button | Command | Description |
|--------|---------|-------------|
| 🔌 | Connect MCP | Check MCP status and install if needed |
| 🤖 | Run Flux Agent | Launch integration assistant |
| 🔍 | Knowledge Search | Query documentation with MCP FAQ |
| 🔄 | Refresh | Update all status indicators |
| 🗑️ | Clear History | Remove all suggestion history |

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
2. Check **System Status**
3. If any items show ❌:
   - Click **MCP Connection** for installation guide
   - Follow prompts to install missing components
4. Once all items show ✅, you're ready to use Flux Agent

### Daily Workflow

1. Open a file you want to enhance
2. (Optional) Select a specific code block
3. Click **Flux Agent** in Integration view
4. Review suggestion in the panel
5. Apply changes manually
6. Verify with validation checklist

### Knowledge Search

1. Click **Knowledge Search** button
2. Enter your question
3. Review answer in FluxLoop output channel
4. Find the entry in **Recent Suggestions** for later reference

## Keyboard Shortcuts

No default keyboard shortcuts are assigned. You can add custom shortcuts via:

1. Open Keyboard Shortcuts (`Cmd+K Cmd+S` or `Ctrl+K Ctrl+S`)
2. Search for "FluxLoop Integration"
3. Assign your preferred shortcuts:
   - `FluxLoop: Run Flux Agent`
   - `FluxLoop: Open Knowledge Search`
   - `FluxLoop: Connect MCP`

## Integration with Other Views

### Projects View
- Switching active project triggers Integration status refresh
- Project-specific MCP index paths (if configured)

### Results View
- Flux Agent suggestions can reference experiment results
- Cross-link between integration plans and test outcomes

### Status View (Merged)
- System Status section in Integration view replaces standalone Status view
- All dependency checks now centralized

## Customization

### Hide/Show Sections

Currently all sections are visible by default. Future versions may support:
- Collapsible root-level sections
- Customizable status item filters
- Suggestion history limits

## Next Steps

- [Integration Assistant Overview](../integration-assistant/overview.md)
- [Using Flux Agent](../integration-assistant/flux-agent.md)
- [Knowledge Search](../integration-assistant/knowledge-search.md)

