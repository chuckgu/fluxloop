# FluxLoop Claude Code Plugin

A Claude Code plugin for automated AI agent testing and evaluation.

## 🚀 Installation

### Install via Claude Code

```
/plugin install Fluxloop-AI/fluxloop-claude-plugin
```

Or add to marketplace:

```
/plugin marketplace add Fluxloop-AI/fluxloop-claude-plugin
```

### Local Installation (Development)

```
/plugin install ./path/to/fluxloop-plugin
```

## 📋 Requirements

- **FluxLoop CLI**: `pip install fluxloop-cli` or `uv tool install fluxloop-cli`
- **FluxLoop Account**: [https://fluxloop.app](https://fluxloop.app)
- **Python 3.8+**

## ✨ Features

### Slash Commands

| Command | Description |
|---------|-------------|
| `/fluxloop:setup` | First-time installation and setup guide |
| `/fluxloop:test` | Run full test cycle (pull → run → upload) |
| `/fluxloop:smoke` | Quick smoke test |
| `/fluxloop:pull` | Pull scenarios and test inputs from Web |
| `/fluxloop:upload` | Upload test results |
| `/fluxloop:criteria` | Display evaluation criteria |
| `/fluxloop:status` | Check current status |
| `/fluxloop:apikeys` | Manage API keys |
| `/fluxloop:synthesis` | Generate test data automatically |

### Skills

| Skill | Description |
|-------|-------------|
| `fluxloop-agent-test` | Manages the complete AI agent test cycle |

Auto-activates on natural language requests like:
- "test my agent"
- "generate test data"
- "run simulation"

### Hooks (Optional)

Automatically run smoke tests after file modifications:

```json
{
  "hooks": [
    {
      "type": "PostToolUse",
      "matcher": "Write|Edit",
      "command": "fluxloop test --smoke --quiet"
    }
  ]
}
```

## 🔧 Quick Start

### 1. Install CLI and Login

```bash
# Install CLI
uv tool install fluxloop-cli

# Login
fluxloop auth login
```

### 2. Project Setup

```bash
# Select or create project
fluxloop projects list
fluxloop projects select <project_id>

# Initialize scenario
fluxloop init scenario my-test

# Create API key
fluxloop apikeys create
```

### 3. Run Tests

```bash
# Pull test data
fluxloop sync pull --bundle-version-id <id>

# Run test
fluxloop test --scenario my-test
```

## 📁 Project Structure

```
your-project/
├── .fluxloop/
│   ├── project.json          # Project connection info
│   ├── context.json          # Current scenario pointer
│   ├── .env                  # API key
│   └── scenarios/
│       └── my-test/
│           ├── agents/       # Agent wrappers
│           ├── configs/      # Configuration files
│           ├── inputs/       # Test inputs
│           └── experiments/  # Test results
└── fluxloop.yaml             # Project settings
```

## 📖 Workflow

```
[Claude Code] "run tests"
      ↓
[FluxLoop Plugin] /fluxloop:test
      ↓
[FluxLoop CLI] fluxloop test
      ├─ (1) sync pull (fetch data from Web)
      ├─ (2) run (execute tests)
      ├─ (3) sync upload (upload results)
      └─ (4) output results + evaluation criteria
      ↓
[Claude Code] Review results and make decisions
```

## 🔗 Links

- **FluxLoop Web**: [https://fluxloop.app](https://fluxloop.app)
- **FluxLoop CLI Docs**: [https://fluxloop.app/docs/cli](https://fluxloop.app/docs/cli)
- **FluxLoop SDK**: [https://fluxloop.app/docs/sdk](https://fluxloop.app/docs/sdk)

## 📄 License

MIT License

## 🤝 Contributing

Issues and PRs are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
