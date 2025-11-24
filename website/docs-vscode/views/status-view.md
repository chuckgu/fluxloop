---
sidebar_position: 5
---

# Status View

Status indicators now live inside the **Integration** view under the **System Status** section. This page summarizes the checks surfaced there.

## Where to Find It

1. Open the FluxLoop activity bar
2. Select **Integration**
3. Expand **System Status**

All environment and dependency checks that were previously shown in a standalone Status view are consolidated here.

## What’s Displayed

| Item | Description | Typical Fix |
|------|-------------|-------------|
| **FluxLoop CLI** | Detects `fluxloop` binary | Install via `pip install fluxloop-cli` |
| **Python Environment** | Ensures Python 3.11+ is available | Point to correct interpreter / upgrade Python |
| **fluxloop-mcp** | MCP server package status | `pip install fluxloop-mcp` |
| **MCP Index** | Knowledge base presence/version | `packages/mcp/scripts/rebuild_index.sh` |
| **Source Root** | `configs/project.yaml → source_root` | Set via Projects view → **Target Source Root…** |

Each item shows ✅ (ready), ⚠️ (warning), or ❌ (error). Hover over a row to see the detected path or error message.

## Actions

- **Select Environment** – Opens `FluxLoop: Select Environment` to switch Auto / Workspace / Global / Custom modes.
- **Run Doctor** – Launches `fluxloop doctor` and renders the output inline (also available via Command Palette).
- **Connect MCP** – Installs missing packages, rebuilds index, or opens documentation if something is broken.
- **Refresh** – Re-runs every check (equivalent to `FluxLoop: Refresh Integration View`).

## Recommended Workflow

1. After creating or switching projects, open System Status to confirm everything is green.
2. If the Flux Agent warns about missing components, click **Run Doctor** from the same panel.
3. Use the provided links (Install / Rebuild / Open Docs) to resolve issues without leaving VS Code.

## Related Docs

- [Integration View](./integration-view.md)
- [Environment Setup](../user-guide/environment-setup.md)
- [Integration Assistant Overview](../integration-assistant/overview.md)
