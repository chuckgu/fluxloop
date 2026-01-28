---
sidebar_position: 1
slug: /
---

# FluxLoop for Claude Code

Test AI agents directly from your IDE with FluxLoop's Claude Code plugin.

## What is FluxLoop for Claude Code?

FluxLoop for Claude Code brings agent testing directly into your development workflow. Instead of switching between tools, you can test your AI agents right where you build them—inside Claude Code.

**Perfect for:**
- Rapid iteration during development
- Quick validation before deployment
- Exploring test scenarios interactively
- Getting immediate feedback on agent changes

---

## Quick Start

### 1. Install the Plugin

```bash
claude code plugin install fluxloop
```

### 2. Set Up Your Project

```bash
/fluxloop setup
```

This guides you through:
- Authenticating with FluxLoop
- Selecting or creating a project
- Configuring your agent

### 3. Run a Test

```bash
/fluxloop test
```

The plugin will:
1. Pull test scenarios from FluxLoop Web
2. Run your agent with synthetic inputs
3. Upload results to the cloud
4. Show you a summary

---

## Key Features

### 🎯 Slash Commands
Run FluxLoop operations with simple `/` commands:
- `/fluxloop setup` - Configure your project
- `/fluxloop test` - Run tests
- `/fluxloop status` - Check project status
- `/fluxloop criteria` - View success criteria

### 🔄 Cloud Sync
- Pull test scenarios from FluxLoop Web
- Upload results automatically
- Access your test data anywhere

### 📊 Instant Feedback
- See test results immediately in Claude Code
- Get links to detailed analysis in FluxLoop Web
- Track agent performance over time

### 🚀 Zero Configuration
- No local test data management
- No manual setup of test scenarios
- Works with your existing FluxLoop projects

---

## How It Works

### Development Workflow

```
1. Code your agent
   ↓
2. Run /fluxloop test
   ↓
3. Review results in IDE
   ↓
4. Open detailed analysis in Web
   ↓
5. Iterate and improve
```

### Architecture

```
┌─────────────────┐
│  Claude Code    │
│  (Your IDE)     │
└────────┬────────┘
         │
         │ FluxLoop CLI Plugin
         │
┌────────▼────────┐
│  FluxLoop CLI   │
│  (Local)        │
└────────┬────────┘
         │
         │ API Sync
         │
┌────────▼────────┐
│  FluxLoop Web   │
│  (Cloud)        │
└─────────────────┘
```

---

## Available Commands

### Setup & Configuration

| Command | Description |
|---------|-------------|
| `/fluxloop setup` | First-time setup and authentication |
| `/fluxloop status` | Check project and authentication status |

### Testing

| Command | Description |
|---------|-------------|
| `/fluxloop test` | Run full test suite |
| `/fluxloop smoke` | Run quick smoke test |

### Data Management

| Command | Description |
|---------|-------------|
| `/fluxloop pull` | Pull latest test data from Web |
| `/fluxloop upload` | Upload results to Web |
| `/fluxloop criteria` | View evaluation criteria |

### Project Management

| Command | Description |
|---------|-------------|
| `/fluxloop apikeys` | Manage API keys |

For detailed command documentation, see [Commands Reference](/claude-code/commands/test).

---

## Prerequisites

### 1. Claude Code CLI
FluxLoop plugin requires Claude Code CLI:

```bash
# Check if installed
claude code --version
```

If not installed, follow the [Claude Code installation guide](https://docs.anthropic.com/claude/docs/claude-cli).

### 2. FluxLoop CLI
The plugin uses FluxLoop CLI under the hood:

```bash
# Install
pip install fluxloop-cli fluxloop

# Verify
fluxloop --version
```

### 3. FluxLoop Account
You'll need a FluxLoop account to sync test data:
- Sign up at [app.fluxloop.ai](https://app.fluxloop.ai)
- Create a project
- Generate an API key

---

## Installation

### Install Plugin

```bash
claude code plugin install fluxloop
```

### Verify Installation

```bash
# List installed plugins
claude code plugin list

# Should show:
# fluxloop - Test AI agents with synthetic data
```

### Update Plugin

```bash
# Update to latest version
claude code plugin update fluxloop

# Or reinstall
claude code plugin uninstall fluxloop
claude code plugin install fluxloop
```

---

## First Test

Let's run your first test with the FluxLoop plugin.

### Step 1: Authenticate

```bash
/fluxloop setup
```

The plugin will:
1. Check if you're logged in to FluxLoop
2. If not, provide a login URL
3. Save your authentication token

### Step 2: Select Project

The setup wizard will show your FluxLoop projects:

```
Select a project:
1. customer-support-agent
2. sales-assistant
3. Create new project

Enter number:
```

Choose an existing project or create a new one.

### Step 3: Run Test

```bash
/fluxloop test
```

Expected output:

```
🔄 Pulling test scenarios from FluxLoop Web...
✓ Pulled 50 test inputs

🧪 Running tests...
▓▓▓▓▓▓▓▓▓▓ 50/50 (100%)

📊 Results:
- Total: 50 traces
- Success: 47 (94%)
- Failed: 3 (6%)

📤 Uploading results to FluxLoop Web...
✓ Results uploaded successfully

🌐 View detailed analysis:
https://app.fluxloop.ai/projects/abc123/results/xyz789
```

### Step 4: View Details

Click the link to open detailed results in FluxLoop Web:
- Per-trace analysis
- Performance metrics
- Failure insights
- Comparison with previous runs

---

## Configuration

### Project Context

The plugin stores project context in `.fluxloop/`:

```
.fluxloop/
├── config.yaml           # Project configuration
├── auth.json            # Authentication token (gitignored)
├── projects/            # Project metadata
└── scenarios/           # Downloaded test scenarios
```

### Authentication

Authentication is handled automatically by the plugin. Your auth token is stored in `.fluxloop/auth.json` (which should be gitignored).

To re-authenticate:

```bash
/fluxloop setup --force-login
```

---

## Best Practices

### During Development

```bash
# Quick smoke test for rapid iteration
/fluxloop smoke

# Full test before committing
/fluxloop test
```

### Before Deployment

```bash
# Run comprehensive tests
/fluxloop test --full

# Check results in Web
/fluxloop status
```

### Team Collaboration

1. Share your project in FluxLoop Web
2. Team members run `/fluxloop setup` and select the shared project
3. Everyone tests against the same scenarios
4. Compare results in the Web dashboard

---

## Troubleshooting

### "Not authenticated"

```bash
# Re-run setup
/fluxloop setup
```

### "No test scenarios found"

```bash
# Pull scenarios from Web
/fluxloop pull

# Then retry test
/fluxloop test
```

### "API key not configured"

```bash
# Check API keys
/fluxloop apikeys check

# Create new key if needed
/fluxloop apikeys create
```

### Plugin Not Found

```bash
# Verify installation
claude code plugin list

# Reinstall if needed
claude code plugin install fluxloop
```

---

## Comparison: Plugin vs CLI

| Feature | Claude Code Plugin | Standalone CLI |
|---------|-------------------|----------------|
| **Use Case** | Development workflow | CI/CD, automation |
| **Interface** | Slash commands in IDE | Terminal commands |
| **Test Data** | Synced from cloud | Local or synced |
| **Results** | IDE + Web | Local + optional sync |
| **Setup** | One-time in IDE | Per project |
| **Best For** | Rapid iteration | Production testing |

**Use both:**
- Plugin for development
- CLI for CI/CD and automation

---

## What's Next?

- **[Commands Reference](/claude-code/commands/test)** - Full command documentation
- **[Integration Guide](/claude-code/integration/workflow)** - Integrate into your workflow
- **[FluxLoop Web](https://app.fluxloop.ai)** - Cloud dashboard
- **[CLI Documentation](/cli/)** - Standalone CLI reference

---

Need help? Check [FluxLoop GitHub Issues](https://github.com/chuckgu/fluxloop/issues) or visit [docs.fluxloop.ai](https://docs.fluxloop.ai).
