---
sidebar_position: 1
---

# Installation

Install the FluxLoop plugin for Claude Code in one command.

## Install Plugin

```bash
/plugin install Fluxloop-AI/fluxloop-claude-plugin
```

**Done!** Now just talk to Claude naturally.

---

## What's Included

The plugin includes:

| Component | Description |
|-----------|-------------|
| **Agent Test Skill** ⭐ | Auto-activates on "test my agent", handles everything |
| Slash Commands | Manual commands like `/fluxloop:test` |
| Hooks | Optional auto-testing on file changes |

---

## After Installation

### Recommended: Use the Skill

Just say:

```
"set up fluxloop for my project"
```

or

```
"test my agent"
```

The skill will guide you through:
- Installing FluxLoop CLI (if needed)
- Authentication
- Project setup
- Running tests

### Alternative: Manual Setup

If you prefer to install manually:

```bash
# 1. Install CLI (the skill does this automatically)
pip install fluxloop-cli

# 2. Run setup command
/fluxloop:setup
```

---

## Verify Installation

```bash
/plugin list
```

Should show `fluxloop` in the list.

---

## Update Plugin

```bash
/plugin install Fluxloop-AI/fluxloop-claude-plugin
```

Reinstalling always gets the latest version.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| Claude Code | Must be installed |
| Python 3.8+ | For FluxLoop CLI |
| FluxLoop Account | Free at [alpha.app.fluxloop.ai](https://alpha.app.fluxloop.ai) |

> 💡 **The skill installs everything!** Just say "set up fluxloop" and it handles CLI installation, login, and project setup automatically.

---

## Next Steps

- **[Your First Test](./first-test)** - Run a test (just by talking!)
- **[Agent Test Skill](/claude-code/skills/agent-test)** ⭐ - Full skill documentation
