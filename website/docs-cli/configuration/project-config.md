---
sidebar_position: 1
---

# Project Configuration

Configure project metadata and global defaults in `configs/project.yaml`.

## Overview

The project configuration file describes global metadata and defaults shared across the entire FluxLoop project. It defines:

- Project identity (name, version, description)
- Source code location for VSCode extension
- Collector service settings (optional)
- Tags and metadata for categorization

## File Location

```
fluxloop/my-agent/
└── configs/
    └── project.yaml    # ← This file
```

## Complete Example

```yaml
# FluxLoop Project Configuration
# ------------------------------------------------------------
# Describes global metadata and defaults shared across the project.
# Update name/description/tags to suit your workspace.
name: my_agent
description: AI agent simulation project
version: 1.0.0

# FluxLoop VSCode extension will prompt to set this path
source_root: ""

# Optional collector settings (leave null if using offline mode only)
collector_url: null
collector_api_key: null

# Tags and metadata help downstream tooling categorize experiments
tags:
  - simulation
  - testing

metadata:
  team: development
  environment: local
  service_context: ""
  # Describe the overall service scenario (used by multi-turn supervisor)
  # Add any custom fields used by dashboards or automation tools.
```

## Configuration Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Project identifier (used in experiment names) |
| `description` | `string` | Human-readable project description |
| `version` | `string` | Project version (semantic versioning recommended) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source_root` | `string` | `""` | Absolute path to agent source code root (for VSCode extension) |
| `collector_url` | `string \| null` | `null` | Remote collector service URL |
| `collector_api_key` | `string \| null` | `null` | API key for collector authentication |
| `tags` | `list[string]` | `[]` | Tags for categorizing experiments |
| `metadata` | `object` | `{}` | Custom metadata fields |

---

## Field Details

### name

**Type:** `string`  
**Required:** Yes  
**Example:** `my_agent`, `customer_support_bot`, `production_agent_v2`

Project identifier used throughout FluxLoop:
- Stored in experiment metadata and dashboards
- Referenced by VSCode extension

**Best Practices:**
- Use snake_case for consistency
- Keep it concise (under 30 characters)
- Make it descriptive but not overly specific
- Don't include version numbers (use `version` field instead)

---

### description

**Type:** `string`  
**Required:** Yes  
**Example:** `Customer support chatbot for e-commerce platform`

Human-readable description of the project purpose.

**Best Practices:**
- One sentence summary
- Explain what the agent does
- Mention primary use case or domain
- Keep under 100 characters for dashboard display

---

### version

**Type:** `string`  
**Required:** Yes  
**Example:** `1.0.0`, `2.1.3`, `0.5.0-beta`

Project version for tracking changes and comparing experiments across versions.

**Best Practices:**
- Follow semantic versioning (`MAJOR.MINOR.PATCH`)
- Increment when agent behavior changes
- Use in baseline comparisons
- Tag git commits with same version

**Versioning Strategy:**
- **MAJOR**: Breaking changes to agent interface or behavior
- **MINOR**: New features or significant improvements
- **PATCH**: Bug fixes or minor tweaks

---

### source_root

**Type:** `string`  
**Default:** `""`  
**Example:** `/Users/me/projects/my-agent/src`

Absolute path to the root directory containing agent source code.

**Used By:**
- VSCode extension for navigating to code
- Integration assistant for repository analysis
- Debugging tools

**How to Set:**

**Via VSCode Extension:**
1. Open FluxLoop Activity Bar
2. Go to Projects view
3. Click "Set Target Source Root…"
4. Select your source directory

**Via CLI:**
```bash
fluxloop config set source_root "/path/to/source" --file configs/project.yaml
```

**Notes:**
- Must be absolute path
- Should point to root, not specific files
- VSCode extension can auto-detect from workspace

---

### collector_url

**Type:** `string | null`  
**Default:** `null`  
**Example:** `http://localhost:8000`, `https://collector.example.com`

URL of remote FluxLoop collector service for centralized trace storage.

**When to Use:**
- Running a shared collector service
- Centralizing traces from multiple agents
- Team dashboard and analytics

**Offline Mode:**
- Set to `null` to use offline/local-only mode
- Traces saved to `results/` directory
- No network calls made

**Configuration:**
```yaml
# Remote collector
collector_url: "https://collector.example.com"
collector_api_key: "your-api-key"

# Offline mode (default)
collector_url: null
collector_api_key: null
```

---

### collector_api_key

**Type:** `string | null`  
**Default:** `null`  
**Example:** `fl_sk_abc123...`

API key for authenticating with remote collector service.

**Security Best Practices:**
- **Don't commit API keys to git!**
- Store in `.env` file (gitignored)
- Use environment variables in CI/CD

**Recommended Setup:**

**1. Store in .env:**
```bash
# .env
FLUXLOOP_API_KEY=fl_sk_abc123xyz789
```

**2. Reference in config:**
```yaml
# configs/project.yaml
collector_api_key: null  # Will use FLUXLOOP_API_KEY from env
```

**3. Or use environment variable directly:**
```bash
export FLUXLOOP_API_KEY="fl_sk_abc123xyz789"
```

---

### tags

**Type:** `list[string]`  
**Default:** `["simulation", "testing"]`  
**Example:** `["production", "customer-support", "v2"]`

Tags for categorizing and filtering experiments.

**Use Cases:**
- Filter experiments by environment (`dev`, `staging`, `prod`)
- Categorize by feature (`authentication`, `payments`, `search`)
- Track versions (`v1`, `v2-beta`)
- Mark special runs (`baseline`, `regression`, `benchmark`)

**Example:**
```yaml
tags:
  - production
  - customer-support
  - gpt-4o
  - multi-turn
```

**Best Practices:**
- Use lowercase, kebab-case
- Keep tags concise (1-2 words)
- Establish tag taxonomy across team
- Use in dashboards and reports for filtering

---

### metadata

**Type:** `object`  
**Default:** `{}`  
**Example:**

```yaml
metadata:
  team: development
  environment: local
  service_context: "Customer support chatbot for e-commerce"
  owner: "alice@example.com"
  slack_channel: "#agent-alerts"
  jira_epic: "AGT-1234"
```

Custom key-value pairs for any project-specific metadata.

**Common Fields:**

| Field | Description |
|-------|-------------|
| `team` | Team responsible for the agent |
| `environment` | Deployment environment (`local`, `dev`, `staging`, `prod`) |
| `service_context` | Overall service scenario description (used by multi-turn supervisor) |
| `owner` | Person or email responsible |
| `repository` | Git repository URL |
| `slack_channel` | Team communication channel |
| `jira_epic` | Related ticket/epic |

**Service Context:**

The `service_context` field is special - it's used by the multi-turn supervisor to understand the overall purpose of the agent:

```yaml
metadata:
  service_context: |
    You are an AI assistant for a travel booking platform.
    Help users search flights, book hotels, and manage reservations.
```

This context helps the supervisor generate realistic follow-up questions.

---

## Usage Examples

### Minimal Configuration

```yaml
name: simple_agent
description: Basic agent for testing
version: 1.0.0
```

### Full Production Configuration

```yaml
name: customer_support_bot
description: AI-powered customer support chatbot for e-commerce platform
version: 2.3.1

source_root: "/Users/alice/projects/support-bot/src"

collector_url: "https://collector.example.com"
collector_api_key: null  # Set via FLUXLOOP_API_KEY env var

tags:
  - production
  - customer-support
  - gpt-4o
  - multi-turn

metadata:
  team: customer-success
  environment: production
  service_context: |
    AI customer support assistant for an e-commerce platform.
    Helps with orders, returns, product questions, and account issues.
  owner: "alice@example.com"
  repository: "https://github.com/company/support-bot"
  slack_channel: "#support-agent"
  deployment_region: "us-east-1"
  cost_center: "CS-001"
```

### Development Configuration

```yaml
name: support_bot_dev
description: Development instance of customer support bot
version: 2.4.0-dev

source_root: "/Users/bob/dev/support-bot"

# Offline mode for local development
collector_url: null
collector_api_key: null

tags:
  - development
  - experimental
  - local

metadata:
  team: development
  environment: local
  service_context: "Development instance for testing new features"
  owner: "bob@example.com"
  notes: "Testing GPT-4o integration"
```

---

## Updating Configuration

### Via Config Command

```bash
# Set simple values
fluxloop config set name "my_new_agent" --file configs/project.yaml
fluxloop config set version "2.0.0" --file configs/project.yaml

# Set nested metadata
fluxloop config set metadata.team "data-science" --file configs/project.yaml
fluxloop config set metadata.environment "production" --file configs/project.yaml
```

### Via Direct Edit

```bash
# Open in editor
code fluxloop/my-agent/configs/project.yaml

# Or use your preferred editor
vim fluxloop/my-agent/configs/project.yaml
```

### Validate After Changes

```bash
fluxloop config validate --file configs/project.yaml
```

---

## Environment Variables

These environment variables can override config values:

| Variable | Overrides | Example |
|----------|-----------|---------|
| `FLUXLOOP_API_KEY` | `collector_api_key` | `fl_sk_abc123...` |
| `FLUXLOOP_SERVICE_NAME` | `name` | `my_agent` |

**Precedence:**
1. Environment variables (highest priority)
2. Project `.env` file
3. `configs/project.yaml`
4. Defaults (lowest priority)

---

## Tips

### Version Management

Track project versions in git:

```bash
# Update version in config
fluxloop config set version "1.2.0" --file configs/project.yaml

# Commit with version tag
git add configs/project.yaml
git commit -m "Bump version to 1.2.0"
git tag v1.2.0
```

### Multiple Environments

Create environment-specific configs:

```bash
configs/
├── project.yaml            # Base config
├── project.dev.yaml        # Development overrides
├── project.staging.yaml    # Staging overrides
└── project.prod.yaml       # Production overrides
```

Use environment-specific config:

```bash
cp configs/project.prod.yaml configs/project.yaml
fluxloop test
```

### Team Conventions

Establish conventions for:
- Tag taxonomy (`environment:prod`, `feature:auth`)
- Metadata fields (required vs optional)
- Versioning strategy
- Naming patterns

Document in team wiki or `README.md`.

---

## See Also

- [Input Configuration](/cli/configuration/input-config) - Personas and input generation
- [Simulation Configuration](/cli/configuration/simulation-config) - Runner and experiment settings
- [config Command](/cli/commands/config) - Configuration management CLI
- [Basic Workflow](/cli/workflows/basic-workflow) - Complete workflow guide
