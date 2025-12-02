# FluxLoop System Console Guide

Use this guide to quickly review the **System Console** actions and installation steps required by the FluxLoop VS Code extension. For deeper walkthroughs, refer to the official docs (e.g., [CLI Quick Start](https://docs.fluxloop.io/cli/getting-started/quick-start), [Experiment Workflow](https://docs.fluxloop.io/cli/workflows/basic-workflow)).

---

## 1. Installation Checklist

| Component       | How to check              | Install / repair command                        |
|-----------------|---------------------------|-------------------------------------------------|
| FluxLoop CLI    | `fluxloop --version`      | `pip install -U fluxloop-cli`                   |
| Python 3.10+    | `python3 --version`       | Install from [python.org](https://www.python.org/downloads/) or your preferred toolchain |
| fluxloop-mcp    | `fluxloop-mcp --help`     | `pip install -U fluxloop-mcp`                   |
| MCP Index       | Check `~/.fluxloop/mcp/index/dev` | Run `scripts/rebuild_index.sh` from your project root |

> 📌 **Tip:** Run these commands from your project virtual environment (`.venv`) so the extension and CLI share the same interpreter.

---

## 2. System Console Actions

### Show Install Guide
Opens this markdown file inside VS Code so you can copy commands or follow the checklist without leaving the editor.

### Select Environment
Choose the Python environment FluxLoop should use (typically your project’s `.venv`). After creating a new virtual environment, rerun this action so `System Status` binds to the correct interpreter.

```
python3 -m venv .venv
source .venv/bin/activate
fluxloop doctor
```

### Show Environment
Displays the currently bound environment details—Python path, FluxLoop CLI location, MCP binaries, etc.—which is handy for debugging.

### Connect MCP
Verifies the `fluxloop-mcp` package and the MCP index. If the CLI is missing, you’ll be prompted to install it (`pip install fluxloop-mcp`) or open the PyPI instructions. If the index is missing, rebuild it with `scripts/rebuild_index.sh`.

### Run Doctor
Executes `fluxloop doctor` for a comprehensive health check (CLI, Python, MCP server, index). Check the FluxLoop Output channel if something fails; logs are appended there.

```
fluxloop doctor
```

---

## 3. Additional Resources
- [FluxLoop CLI Reference](https://docs.fluxloop.io/cli/intro)
- [Recording & Experiment Workflow](https://docs.fluxloop.io/cli/workflows/basic-workflow)
- [VS Code Extension Guide](https://docs.fluxloop.io/vscode/intro)

If issues persist, hit **System Status → Refresh Status** to rerun diagnostics, then capture the `Run Doctor` output for your team when requesting help.

