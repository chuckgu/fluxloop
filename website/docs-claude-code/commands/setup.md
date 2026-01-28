---
sidebar_position: 2
---

# /fluxloop setup

Initial configuration and authentication for FluxLoop.

## Overview

The `/fluxloop setup` command guides you through:
1. Authentication with FluxLoop Web
2. Project selection or creation
3. Local configuration

Run this once per project to get started.

## Basic Usage

```bash
/fluxloop setup
```

## What It Does

### Step 1: Authentication

Checks if you're logged in:

```
🔐 Checking authentication...
✗ Not authenticated

Please visit: https://app.fluxloop.ai/cli-login?token=abc123
After login, press Enter to continue...
```

Opens browser for authentication, then saves your token locally.

### Step 2: Project Selection

Shows available projects:

```
📋 Select a project:

1. customer-support-agent (ID: proj_abc)
   Last updated: 2 days ago
   3 scenarios

2. sales-assistant (ID: proj_def)
   Last updated: 1 week ago
   2 scenarios

3. [Create new project]

Enter number (1-3):
```

### Step 3: Configuration

Creates local configuration:

```
✓ Project selected: customer-support-agent
✓ Configuration saved to .fluxloop/config.yaml
✓ Created .fluxloop/auth.json

🎉 Setup complete! Ready to test.

Next steps:
  Run tests: /fluxloop test
  Check status: /fluxloop status
```

## Options

### --force-login

Force re-authentication even if already logged in:

```bash
/fluxloop setup --force-login
```

Useful when:
- Switching accounts
- Token expired
- Authentication issues

### --project

Skip project selection and specify project:

```bash
/fluxloop setup --project customer-support-agent
```

Or using project ID:

```bash
/fluxloop setup --project proj_abc123
```

### --non-interactive

For CI/CD environments:

```bash
# Set via environment variables
export FLUXLOOP_API_KEY=your-api-key
export FLUXLOOP_PROJECT_ID=proj_abc123

/fluxloop setup --non-interactive
```

## Generated Files

Setup creates these files in your project:

```
.fluxloop/
├── config.yaml          # Project configuration
├── auth.json           # Authentication token (gitignored)
├── projects/           # Project metadata
│   └── customer-support-agent/
│       ├── project.yaml
│       └── scenarios/
└── .gitignore         # Ignores auth.json
```

### .fluxloop/config.yaml

```yaml
current_project:
  id: proj_abc123
  name: customer-support-agent

auth:
  token_path: .fluxloop/auth.json

defaults:
  scenario: main
  upload_results: true
```

### .fluxloop/auth.json

```json
{
  "access_token": "fluxloop_...",
  "refresh_token": "...",
  "expires_at": "2024-02-01T12:00:00Z"
}
```

**⚠️ Important**: Never commit `auth.json` to version control!

## First Time Setup

### Complete Walkthrough

```bash
# 1. Run setup
/fluxloop setup

# Output:
# 🔐 Checking authentication...
# ✗ Not authenticated
#
# Please visit: https://app.fluxloop.ai/cli-login
# After login, press Enter to continue...

# (Browser opens, you log in)

# ✓ Authentication successful
#
# 📋 Select a project:
# 1. customer-support-agent
# 2. [Create new project]
#
# Enter number: 1

# ✓ Project selected: customer-support-agent
# ✓ Configuration saved
#
# 🎉 Setup complete!

# 2. Verify setup
/fluxloop status

# Output:
# ✓ Authenticated
# ✓ Project: customer-support-agent
# ✓ Scenarios: 3 available

# 3. Run first test
/fluxloop test
```

## Team Setup

When joining a team project:

```bash
# 1. Setup with team's project
/fluxloop setup

# 2. Select the team project
# (Choose from list)

# 3. Pull team's test scenarios
/fluxloop pull

# 4. Run tests
/fluxloop test
```

Everyone on the team:
- Uses the same project
- Tests against the same scenarios
- Sees results in shared dashboard

## Troubleshooting

### "Browser didn't open"

Manually visit the URL shown:

```bash
/fluxloop setup

# Copy the URL from output:
# https://app.fluxloop.ai/cli-login?token=abc123

# Paste in browser, log in
# Press Enter in terminal
```

### "Project not found"

Ensure you have access:
- Check project name spelling
- Verify account has access
- Ask project owner for access

### "Configuration invalid"

Reset configuration:

```bash
# Remove old config
rm -rf .fluxloop/

# Re-run setup
/fluxloop setup
```

### Multiple Projects

Switch between projects:

```bash
# Setup for different project
/fluxloop setup --project other-project

# Or re-run setup and select different project
/fluxloop setup
```

## CI/CD Setup

For automated environments:

### GitHub Actions

```yaml
# .github/workflows/test.yml
- name: Setup FluxLoop
  env:
    FLUXLOOP_API_KEY: ${{ secrets.FLUXLOOP_API_KEY }}
    FLUXLOOP_PROJECT_ID: proj_abc123
  run: |
    pip install fluxloop-cli fluxloop
    fluxloop setup --non-interactive

- name: Run tests
  run: fluxloop test
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  script:
    - export FLUXLOOP_API_KEY=$FLUXLOOP_API_KEY
    - export FLUXLOOP_PROJECT_ID=proj_abc123
    - fluxloop setup --non-interactive
    - fluxloop test
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `FLUXLOOP_API_KEY` | API key for authentication |
| `FLUXLOOP_PROJECT_ID` | Project ID |
| `FLUXLOOP_SCENARIO` | Default scenario |

## Updating Configuration

### Change Project

```bash
# Re-run setup
/fluxloop setup

# Select different project
```

### Update API Key

```bash
# Force new login
/fluxloop setup --force-login
```

### View Current Configuration

```bash
# Check status
/fluxloop status

# View config file
cat .fluxloop/config.yaml
```

## Security Best Practices

### .gitignore

Always ignore authentication files:

```gitignore
# .gitignore
.fluxloop/auth.json
.fluxloop/*.token
```

The setup command automatically creates this.

### API Key Management

- **Never** commit API keys
- Use environment variables in CI/CD
- Rotate keys periodically
- Use different keys for dev/prod

### Team Sharing

Share safely:
- Commit `.fluxloop/config.yaml` (no secrets)
- Don't commit `.fluxloop/auth.json`
- Each team member runs `/fluxloop setup`
- Each gets their own auth token

## Related Commands

- [`/fluxloop status`](./status) - Check setup status
- [`/fluxloop test`](./test) - Run tests
- [`/fluxloop apikeys`](./apikeys) - Manage API keys

## See Also

- [Installation Guide](../getting-started/installation) - Install FluxLoop plugin
- [Integration Workflow](../integration/workflow) - Full workflow
