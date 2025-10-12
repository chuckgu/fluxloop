# FluxLoop Virtual Environment Setup Guide

This guide explains how to install the FluxLoop CLI and SDK in an isolated environment. We recommend using virtual environments or `pipx` so that FluxLoop never conflicts with system Python packages.

## Prerequisites

- Python 3.9 or newer (macOS, Linux, or Windows)
- Basic shell access (Terminal, PowerShell, or git-bash)
- The FluxLoop distribution artifacts located at:
  - `packages/cli/dist/fluxloop_cli-0.1.0-py3-none-any.whl`
  - `packages/sdk/dist/fluxloop-0.1.0-py3-none-any.whl`

> **Note:** Replace the version numbers in the examples below if you build newer wheels.

---

## Option 1 — Install with `pipx` (Recommended for CLI users)

`pipx` creates and manages a dedicated virtual environment per application. It keeps the CLI isolated while making the `fluxloop` command available everywhere.

### 1. Install `pipx`

- **macOS (Homebrew):**
  ```bash
  brew install pipx
  pipx ensurepath
  ```
  After running `ensurepath`, open a new terminal so the PATH update takes effect.

- **Windows / Linux:**
  ```bash
  python3 -m pip install --user pipx
  python3 -m pipx ensurepath
  ```
  On Windows PowerShell, run the commands without the `3` (i.e., `python -m pip ...`).

### 2. Install the FluxLoop CLI

```bash
pipx install /Users/user/Documents/fluxloop/packages/cli/dist/fluxloop_cli-0.1.0-py3-none-any.whl
```

### 3. Inject the FluxLoop SDK (Optional)

If you also need the Python SDK inside the same `pipx` environment:

```bash
pipx inject fluxloop-cli /Users/user/Documents/fluxloop/packages/sdk/dist/fluxloop-0.1.0-py3-none-any.whl
```

### 4. Verify the Installation

```bash
fluxloop --version
python3 -c "import fluxloop; print(fluxloop.__version__)"
```

If both commands return version numbers, the installation succeeded.

### 5. Update or Remove

```bash
pipx reinstall fluxloop-cli   # Replace with the latest wheel
pipx uninstall fluxloop-cli   # Remove the CLI entirely
```

---

## Option 2 — Project-Specific Virtual Environment (Recommended for SDK development)

Use `venv` when you want to keep the CLI or SDK tied to a specific project directory.

### 1. Create and Activate the Environment

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .\.venv\Scripts\activate
```

### 2. Install the CLI or SDK

```bash
pip install /Users/user/Documents/fluxloop/packages/cli/dist/fluxloop_cli-0.1.0-py3-none-any.whl
pip install /Users/user/Documents/fluxloop/packages/sdk/dist/fluxloop-0.1.0-py3-none-any.whl
```

### 3. Configure VSCode (Optional)

- Select the virtual environment interpreter (`Ctrl+Shift+P` → `Python: Select Interpreter`).
- The FluxLoop VSCode extension will now detect the CLI inside this environment.

### 4. Deactivate or Remove

```bash
deactivate                # Leave the venv session
rm -rf .venv              # Remove the environment entirely
```

---

## Frequently Asked Questions

**Q: Why not install globally with `pip install`?**  
macOS 14+ and many Linux distributions protect system Python, preventing global installs (`externally-managed-environment`). Even when it works, global installs can conflict with other tools.

**Q: Do I have to install both CLI and SDK?**  
- Install the **CLI** if you run experiments or use the VSCode extension.
- Install the **SDK** if you write Python code that imports `fluxloop`.
- You can install both inside the same virtual environment.

**Q: Does the VSCode extension install the CLI automatically?**  
No. The extension checks whether `fluxloop` is available. If not, it prompts you to install it (typically by opening a terminal). Following this guide ensures the extension detects the CLI immediately.

**Q: How do I update to a new release?**  
Download or build the new wheels, then run `pipx reinstall fluxloop-cli` or `pip install --upgrade` inside your venv.

---

## Quick Reference

| Action                     | Command                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| Install CLI via pipx      | `pipx install path/to/fluxloop_cli-*.whl`                                |
| Inject SDK into pipx env  | `pipx inject fluxloop-cli path/to/fluxloop-*.whl`                        |
| Create venv               | `python3 -m venv .venv`                                                  |
| Activate venv             | `source .venv/bin/activate` *(Windows: `.\.venv\Scripts\activate`)*    |
| Install CLI/SDK in venv   | `pip install path/to/fluxloop_cli-*.whl fluxloop-*.whl`                  |
| Remove venv               | `rm -rf .venv`                                                           |

By following the steps above, you can keep FluxLoop isolated from system-wide Python packages and maintain reproducible environments across different machines or teammates.
