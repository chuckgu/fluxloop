---
sidebar_position: 1
---

# Installation

Installation guide for the FluxLoop VSCode Extension.

## Installation Methods

FluxLoop Extension can be **installed directly from the Extension Marketplace**!

### 🎯 Method 1: Install from Extension Marketplace (Recommended)

#### Cursor Users

1. **Open Extensions tab** (sidebar or `Cmd+Shift+X`)
2. **Search for "FluxLoop"**
3. **Click Install**
4. **Restart Cursor**

> ✨ Cursor automatically downloads the extension from [Open VSX Registry](https://open-vsx.org/extension/fluxloop/fluxloop)

#### VS Code Users

1. **Open Extensions** (`Cmd+Shift+X` / `Ctrl+Shift+X`)
2. **Search for "FluxLoop"**
3. **Click Install**
4. **Restart VS Code**

> Or install directly from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fluxloop.fluxloop)

**Or via Command Palette:**
```
ext install fluxloop.fluxloop
```

#### Verify Installation

After restart:
- **FluxLoop icon** appears in the left Activity Bar
- Clicking the icon displays Projects, Inputs, Experiments, Results, and Status panels

### 📦 Method 2: Manual Installation from VSIX (Alternative)

If you cannot access the Marketplace:

#### 1. Download VSIX File

Download the latest VSIX file from [GitHub Releases](https://github.com/chuckgu/fluxloop/releases).

- Example filename: `fluxloop-0.1.4.vsix`

#### 2. Install

1. **Open Command Palette** (`Cmd+Shift+P` or `Ctrl+Shift+P`)
2. **Type and select "Extensions: Install from VSIX..."**
3. **Select the downloaded VSIX file**
4. **Restart**

## Prerequisites

To use FluxLoop Extension, you need FluxLoop CLI, SDK, and MCP server installed.

### Recommended Installation

Install in a project-specific virtual environment (recommended):

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install FluxLoop packages
pip install fluxloop-cli fluxloop fluxloop-mcp
```

### Alternative Installation Methods

#### Using uv

```bash
uv venv
source .venv/bin/activate
uv pip install fluxloop-cli fluxloop fluxloop-mcp
```

#### Using pipx (Global Installation)

```bash
pipx install fluxloop-cli
pipx install fluxloop-mcp
pip install fluxloop  # SDK recommended in project venv
```

### Verify Installation

Automatic diagnostics from extension:
```
FluxLoop: Run Doctor
```

Or from terminal:
```bash
# Check CLI version
fluxloop --version

# Verify SDK
python -c "import fluxloop; print(fluxloop.__version__)"

# Check MCP server
fluxloop-mcp --help

# Full environment diagnostics
fluxloop doctor
```

## System Requirements

- **Cursor**: Latest version (based on VSCode 1.74.0+)
- **VS Code**: 1.74.0 or higher
- **Python**: 3.8 or higher (3.11+ recommended for SDK/MCP)
- **Operating System**: macOS, Linux, Windows

## Troubleshooting

### Extension Not Activating

**Symptom**: FluxLoop icon not visible, or panels are empty

**Solution**:
1. Restart Cursor/VS Code
2. Open Developer Tools (View → Toggle Developer Tools)
3. Check Console for errors
4. Usually caused by missing FluxLoop CLI:
   ```bash
   pip install fluxloop-cli fluxloop
   ```

### "Cannot find module 'yaml'" Error

**Symptom**: Error when activating extension

**Solution**:
- Download and reinstall latest VSIX file
- Older VSIX versions may have missing runtime dependencies

### CLI Not Recognized

**Symptom**: "FluxLoop CLI is not installed" message

**Solution**:
1. **Check environment:**
   ```
   FluxLoop: Show Environment Info
   ```

2. **Install in project venv:**
```bash
   source .venv/bin/activate
   pip install fluxloop-cli fluxloop fluxloop-mcp
   ```

3. **Or install globally:**
   ```bash
pipx install fluxloop-cli
   pipx install fluxloop-mcp
   ```

4. **Configure environment mode:**
   ```
   FluxLoop: Select Environment
   ```

5. **Verify PATH:**
   ```bash
   which fluxloop
   fluxloop doctor
```

### Extension Not Found in Cursor

**Symptom**: Searching for "FluxLoop" in Cursor Extensions returns no results

**Solution**:
1. Verify Extensions tab loaded properly
2. Search exactly for **"FluxLoop"**
3. Update Cursor to latest version
4. If still not visible, download VSIX directly from [Open VSX page](https://open-vsx.org/extension/fluxloop/fluxloop) and install manually

## Updates

### Automatic Updates (Cursor & VS Code)

**Auto-update is supported when installed from Marketplace:**

- **Cursor**: Auto-updates or shows notification when new version detected on Open VSX
- **VS Code**: Auto-updates or shows notification when new version detected on Marketplace

Check Extensions tab for FluxLoop and click **Update** button if available.

### Manual Update

If installed from VSIX:

1. Download latest VSIX from GitHub Releases
2. Uninstall existing extension: Extensions tab → FluxLoop → Uninstall
3. Restart
4. Command Palette (`Cmd+Shift+P`) → **"Extensions: Install from VSIX..."**
5. Select new VSIX file and restart

## Next Steps

After installing the extension:

- [Creating Your First Project](creating-first-project)
- [Running Experiments](running-experiments)
- [User Guide](../user-guide/creating-projects)
