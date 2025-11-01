---
sidebar_position: 1
---

# Installation

Get FluxLoop installed and ready to use in minutes.

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Virtual environment** (recommended)

## Install FluxLoop Packages

Install both the CLI and SDK:

```bash
pip install fluxloop-cli fluxloop
```

Or install them separately:

```bash
# CLI only
pip install fluxloop-cli

# SDK only
pip install fluxloop
```

## Verify Installation

Check that the CLI is installed:

```bash
fluxloop --version
```

You should see output like:

```
FluxLoop CLI version 0.2.1
```

## Optional: VSCode Extension

If you use Visual Studio Code, install the FluxLoop extension for enhanced workflow:

1. Open VSCode
2. Go to Extensions (Cmd+Shift+X / Ctrl+Shift+X)
3. Search for "FluxLoop"
4. Click Install

Or install from command line:

```bash
code --install-extension fluxloop
```

## Virtual Environment Setup

We recommend using a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install FluxLoop
pip install fluxloop-cli fluxloop
```

For more details, see [Virtual Environment Setup](../guides/virtual-environment-setup).

## Next Steps

Now that you have FluxLoop installed:

- **[Quick Start](./quick-start)** - Create your first project
- **[Core Concepts](./core-concepts)** - Understand the fundamentals
- **[End-to-End Guide](../guides/end-to-end-workflow)** - Complete walkthrough

