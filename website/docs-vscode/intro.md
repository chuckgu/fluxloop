---
sidebar_position: 1
slug: /
---

# FluxLoop VSCode Extension

Visual Studio Code extension for managing FluxLoop AI agent simulation projects directly from your IDE.

## Installation

### Recommended: Install from Extension Marketplace

**Cursor Users:**
- Open Extensions (`Cmd+Shift+X`)
- Search for **"FluxLoop"**
- Click **Install** (auto-downloads from [Open VSX](https://open-vsx.org/extension/fluxloop/fluxloop))

**VS Code Users:**
- Open Extensions (`Cmd+Shift+X`)
- Search for **"FluxLoop"**
- Click **Install** (from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop))

### Alternative: Manual Installation

Download VSIX from [GitHub Releases](https://github.com/chuckgu/fluxloop/releases):
```bash
# Via command line
code --install-extension fluxloop-0.1.1.vsix
```

Or via Command Palette: **"Extensions: Install from VSIX..."**

## Version

Current version: **0.1.1**

## Features

### 🎯 Project-Centric Workflow
- Create and manage multiple FluxLoop projects from the Activity Bar
- Switch between projects with a single click
- Automatic project discovery and configuration validation

### 📝 Input Management
- View and edit base inputs from `configs/input.yaml`
- Generate input variations using LLM or deterministic strategies
- Browse generated inputs and recordings in dedicated views

### 🧪 Experiment Execution
- Run experiments directly from VSCode
- Monitor execution progress with real-time feedback
- View runner configuration and iteration settings at a glance

### 📊 Results Exploration
- Browse experiment outputs organized by run timestamp under **Experiments** folder
- Open traces, summaries, observations, and artifacts with one click
- Parse results into human-readable Markdown timelines with **Parse Results** action
- View parsed analysis outputs in `per_trace_analysis/` folder

### 🔴 Recording Mode (Advanced)
- Toggle argument recording for complex function signatures
- Enable/disable recording mode from Command Palette or Experiments view
- Status panel shows current recording state and target file

### 🤖 Integration Assistant
- AI-powered integration guidance using MCP server and LLM
- Knowledge search backed by FluxLoop documentation index
- Flux Agent generates contextualized code suggestions
- Manual review and application workflow (no automatic changes)

### ℹ️ System Status
- Real-time CLI and SDK installation checks
- Configuration validation for `configs/` structure
- Recording mode and environment status at a glance

## Quick Start

### 1. Create a Project

Open the **FluxLoop** Activity Bar and click **"Create New Project…"** or use Command Palette:

```
FluxLoop: Create FluxLoop Project
```

### 2. Generate Inputs

From the **Inputs** view, click **"Generate New Inputs…"** to launch the wizard.

### 3. Run Experiment

From the **Experiments** view, click **"Run Experiment"** and select execution environment.

### 4. View Results

Browse experiment outputs in the **Results** view.

## Prerequisites

Install FluxLoop CLI and SDK:

```bash
pip install fluxloop-cli fluxloop
```

## Available Commands

Access via Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):

**Project Management:**
- `FluxLoop: Create FluxLoop Project`
- `FluxLoop: Add Existing FluxLoop Project`
- `FluxLoop: Switch FluxLoop Project`
- `FluxLoop: Remove FluxLoop Project`

**Workflow:**
- `FluxLoop: Generate Inputs`
- `FluxLoop: Run Experiment`
- `FluxLoop: Run Single Execution`
- `FluxLoop: Show Status`

**Integration:**
- `FluxLoop: Connect MCP`
- `FluxLoop: Open Knowledge Search`
- `FluxLoop: Run Flux Agent`

**Recording:**
- `FluxLoop: Enable Recording Mode`
- `FluxLoop: Disable Recording Mode`
- `FluxLoop: Show Recording Status`

**Configuration:**
- `FluxLoop: Open Configuration`
- `FluxLoop: Select Execution Environment`
- `FluxLoop: Configure Execution Wrapper`

**Results:**
- `FluxLoop: Parse Experiment` - Convert experiment traces to Markdown

## What's Next?

- **[Installation](/vscode/getting-started/installation)** - Detailed setup guide
- **[Integration Assistant](/vscode/integration-assistant/overview)** - AI-powered integration guidance
- **[User Guide](/vscode/user-guide/creating-projects)** - Step-by-step tutorials
- **[Commands](/vscode/commands/project-commands)** - All available commands
- **[API Reference](/vscode/api)** - TypeScript API documentation (auto-generated)

---

Need help? Check [Troubleshooting](/vscode/troubleshooting) or [GitHub Issues](https://github.com/chuckgu/fluxloop/issues).

