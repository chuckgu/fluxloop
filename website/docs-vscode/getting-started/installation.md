---
sidebar_position: 1
---

# Installation

Set up the FluxLoop VSCode extension and required dependencies.

## 1. Install the Extension

FluxLoop ships on both VS Code Marketplace and Open VSX. We recommend installing from the marketplace inside your editor.

### 🎯 Marketplace (Recommended)

**Cursor**

1. Open **Extensions** (`Cmd+Shift+X`)
2. Search for **“FluxLoop”**
3. Click **Install**
4. Restart Cursor

> Cursor pulls the package from [Open VSX](https://open-vsx.org/extension/fluxloop/fluxloop) automatically.

**VS Code**

1. Open **Extensions** (`Cmd+Shift+X` / `Ctrl+Shift+X`)
2. Search for **“FluxLoop”**
3. Click **Install**
4. Restart VS Code

Or run from Command Palette:
```
ext install fluxloop.fluxloop
```

### 📦 Install from VSIX (Offline)

1. Download the latest `fluxloop-0.1.5.vsix` from [GitHub Releases](https://github.com/chuckgu/fluxloop/releases)
2. Command Palette → **“Extensions: Install from VSIX…”**
3. Select the downloaded file
4. Restart the editor

> Verify install: the FluxLoop activity bar icon appears with **Projects / Inputs / Experiments / Results / Integration / Status** views.

## 2. Install Required Python Packages

FluxLoop extension relies on three Python packages:

| Package | Purpose | Python Requirement |
|---------|---------|--------------------|
| `fluxloop-cli` | CLI used for project scaffolding, input generation, experiments | Python **3.8+** |
| `fluxloop` | SDK used by your agents | Python **3.11+** (due to type features) |
| `fluxloop-mcp` | MCP server powering Integration Assistant | Python **3.11+** |

We recommend installing everything inside your project virtual environment.

```bash
# Create venv (recommended)
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install FluxLoop toolchain
pip install --upgrade pip
pip install fluxloop-cli fluxloop fluxloop-mcp
```

### Alternative Install Options

- **uv**
  ```bash
  uv venv
  source .venv/bin/activate
  uv pip install fluxloop-cli fluxloop fluxloop-mcp
  ```

- **pipx (global CLI)**
  ```bash
  pipx install fluxloop-cli
  pipx install fluxloop-mcp
  # still install fluxloop SDK inside project venv
  pip install fluxloop
  ```

## 3. Build the MCP Knowledge Index

Flux Agent requires a local documentation index.

```bash
# From repo root
packages/mcp/scripts/rebuild_index.sh
```

Defaults to `~/.fluxloop/mcp/index/dev`. The extension warns in the Integration view if the index is missing.

## 4. Verify Installation

### From VS Code / Cursor

Open Command Palette and run:

- `FluxLoop: Show Environment Info` – quick summary of detected Python, CLI, SDK, MCP paths
- `FluxLoop: Run Doctor` – full diagnostics (Python, CLI, SDK, MCP, index, configs)

### From Terminal

```bash
# CLI version
fluxloop --version

# SDK version
python -c "import fluxloop; print(fluxloop.__version__)"

# MCP server health
fluxloop-mcp --help

# Comprehensive check
fluxloop doctor
```

Doctor output includes JSON guidance when run with `--json`.

## 5. Configure Project Environment

Once the extension is installed:

1. Create/activate your environment (`.venv`, Poetry, Conda, uv, etc.)
2. Install FluxLoop packages (step 2)
3. Run `FluxLoop: Select Environment` to choose one of the four modes:

| Mode | Description | Use When |
|------|-------------|----------|
| `auto` (default) | Detect `.venv`, Poetry, Conda, pyenv in workspace; fall back to PATH | Most projects |
| `workspace` | Require project-local env | Teams enforcing per-project venv |
| `global` | Always use global PATH executables (e.g., pipx) | Quick prototyping |
| `custom` | Manually specify Python + fluxloop-mcp paths | Complex Conda/pyenv setups |

4. (Optional) Set `Target Source Root…` from the Projects view so the Integration Assistant analyzes the correct codebase.

## System Requirements

- **Editor**: Cursor (latest) or VS Code ≥ 1.74.0
- **Python**:
  - CLI: 3.8+
  - SDK & MCP: 3.11+
- **OS**: macOS, Linux, Windows
- **OpenAI API key** for Flux Agent (prompted on first run, stored securely if approved)

## Troubleshooting

### Extension Not Activating

- Ensure FluxLoop icon appears after restart
- Open **View → Output → FluxLoop** for logs
- Check Developer Tools console for missing dependency errors
- Install required Python packages (step 2)

### CLI / SDK / MCP Not Found

1. Run `FluxLoop: Show Environment Info` to see detected paths
2. Confirm packages are installed inside the active environment
3. If using pipx/global installs, switch execution mode to **global** or set `fluxloop.executionWrapper`
4. Re-run `FluxLoop: Run Doctor`

### Missing MCP Index

- Build index: `packages/mcp/scripts/rebuild_index.sh`
- Verify location in **Integration → System Status**
- Set custom index path via `MCP_INDEX_PATH` if needed

### Extension Not Discoverable in Cursor

- Ensure you are online and Extensions tab fully loaded
- Search for **FluxLoop** (no spaces/case sensitive)
- Update Cursor to latest build
- Fallback: download VSIX from Open VSX and install manually

## Updating the Extension

| Source | Update Method |
|--------|---------------|
| Marketplace install | Auto-updates; check Extensions tab for pending updates |
| VSIX install | Download new VSIX → uninstall old → reinstall via “Install from VSIX…” |

After updating, re-run `FluxLoop: Run Doctor` to ensure dependencies are still detected.

## Next Steps

- [Create Your First Project](creating-first-project)
- [Environment Configuration](environment-configuration)
- [Running Experiments](running-experiments)
- [Integration Assistant Setup](/vscode/integration-assistant/setup)
*** End Patch
