---
sidebar_position: 1
---

# Projects View

Use the **Projects** view (first icon in the FluxLoop activity bar) to create, register, and configure FluxLoop projects without leaving VS Code.

## Layout Overview

```
FluxLoop
└─ Projects
   ├─ + Create New Project…
   ├─ + Add Existing Project…
   ├─ my-chatbot (Active)
   │   ├─ Configure Project
   │   ├─ Target Source Root…
   │   ├─ Show Environment Info
   │   └─ Remove Project
   └─ …
```

### Active Project
- The project highlighted in **bold** is the one used by Inputs / Experiments / Results / Integration views.
- Clicking another project switches context immediately and triggers environment re-detection.
- The VS Code status bar shows the current selection (`FluxLoop: my-chatbot`).

### Project Actions

| Action | Description |
|--------|-------------|
| **Create New Project…** | Launches the default/custom project wizard (runs `fluxloop init project`). |
| **Add Existing Project…** | Registers an on-disk project (folder containing `configs/`). |
| **Configure Project** | Opens `configs/project.yaml` plus quick links to input/simulation/evaluation configs. |
| **Target Source Root…** | Sets the source root used for environment detection and Integration Assistant analysis. |
| **Show Environment Info** | Displays Python/CLI/MCP paths for the selected project. |
| **Remove Project** | Removes the project from the list (files remain untouched). |

### Status Indicators

Each project displays an icon to highlight configuration health:

- ✅ **Green check** – Required configs found and environment detected
- ⚠️ **Yellow warning** – Missing files or packages; hover for details
- ❌ **Red error** – Environment unreadable or configs missing entirely

Clicking the icon opens a tooltip with remediation steps (e.g., install packages, set target source root).

### Environment At a Glance

Selecting a project expands a summary node showing:

- Execution mode (Auto / Workspace / Global / Custom)
- Source root path
- Detected Python / `fluxloop` / `fluxloop-mcp` executables
- Recording status (Enabled/Disabled)
- Shortcuts to `FluxLoop: Select Environment` and `FluxLoop: Run Doctor`

### Shared Project Root

The default project wizard stores new projects under `fluxloop.projectRoot` (default `~/FluxLoopProjects`). Change it via:

- Settings → FluxLoop → **Project Root**
- `settings.json`:
  ```json
  {
    "fluxloop.projectRoot": "/Users/me/FluxLoopWorkspaces"
  }
  ```

## Tips

- Use the context menu on each project to access commands quickly (Configure, Target Source Root, Show Environment, Remove).
- The view refreshes automatically when you switch branches or edit `configs/`.
- Projects are stored per workspace—open another folder to maintain a separate list.
