# fluxloop projects

Manage FluxLoop projects.

## Synopsis

```bash
fluxloop projects [command] [options]
```

## Description

The `projects` command manages FluxLoop projects. Projects are the top-level organizational unit that contains scenarios, test runs, and results.

## Commands

### `fluxloop projects list`

List all available projects.

**Usage:**

```bash
fluxloop projects list [options]
```

**Options:**

- `--org <name>`: Filter by organization
- `--json`: Output in JSON format
- `--limit <n>`: Limit number of results (default: 100)

**Examples:**

```bash
# List all projects
fluxloop projects list

# List projects in specific organization
fluxloop projects list --org "Acme Inc"

# Get projects in JSON format
fluxloop projects list --json
```

**Output:**

```
Projects

┌──────────────────────────────────────────────────────────────────┐
│ customer-support-bot                                             │
│ Customer support agent for e-commerce                            │
│ Organization: Acme Inc                                           │
│ Scenarios: 12 | Last run: 2 hours ago                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ sales-assistant                                                  │
│ AI sales assistant for lead qualification                        │
│ Organization: Acme Inc                                           │
│ Scenarios: 8 | Last run: 1 day ago                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ analytics-agent                                                  │
│ Data analysis and reporting agent                               │
│ Organization: Personal                                           │
│ Scenarios: 5 | Last run: 3 days ago                             │
└──────────────────────────────────────────────────────────────────┘

Total: 3 projects
```

### `fluxloop projects create`

Create a new project.

**Usage:**

```bash
fluxloop projects create [options]
```

**Options:**

- `--name <name>`: Project name (required)
- `--description <desc>`: Project description
- `--org <name>`: Organization to create project in
- `--tags <tags>`: Comma-separated list of tags
- `--connect`: Connect this local directory to the new project

**Examples:**

```bash
# Interactive project creation
fluxloop projects create

# Create project with name and description
fluxloop projects create \
  --name "email-assistant" \
  --description "AI email assistant for customer support"

# Create and connect to local directory
fluxloop projects create \
  --name "chatbot" \
  --description "Customer chatbot" \
  --connect
```

**Interactive Flow:**

```
$ fluxloop projects create

Create New Project

Project name: email-assistant
Description: AI email assistant for customer support
Organization: Acme Inc
Tags (comma-separated): email, support, customer

✅ Project created successfully!

Project ID: proj_abc123
Name: email-assistant
URL: https://app.fluxloop.ai/projects/email-assistant

Would you like to connect this directory to the project? (y/n): y

✅ Connected to project: email-assistant

Configuration saved to .fluxloop/config.yaml
```

### `fluxloop projects select`

Select (link) a project to the current directory.

**Usage:**

```bash
fluxloop projects select [options]
```

**Options:**

- `--project <name>`: Project name or ID
- `--org <name>`: Organization name

**Examples:**

```bash
# Interactive project selection
fluxloop projects select

# Select specific project
fluxloop projects select --project customer-support-bot
```

**Interactive Flow:**

```
$ fluxloop projects select

Select a Project

Available projects:
  1. customer-support-bot (Acme Inc)
  2. sales-assistant (Acme Inc)
  3. analytics-agent (Personal)
  4. Create new project

Select a project (1-4): 1

✅ Connected to project: customer-support-bot

Project: customer-support-bot
Organization: Acme Inc
Scenarios: 12
Last sync: Never

Configuration saved to .fluxloop/config.yaml

Next steps:
• Run 'fluxloop pull' to fetch scenarios from the cloud
• Run 'fluxloop test' to start testing
```

### `fluxloop projects info`

Display information about the current or specified project.

**Usage:**

```bash
fluxloop projects info [options]
```

**Options:**

- `--project <name>`: Project name or ID (default: current project)
- `--json`: Output in JSON format

**Examples:**

```bash
# Show info for current project
fluxloop projects info

# Show info for specific project
fluxloop projects info --project sales-assistant

# Get info in JSON format
fluxloop projects info --json
```

**Output:**

```
Project: customer-support-bot

Description: Customer support agent for e-commerce
Organization: Acme Inc
Created: 2023-11-15
Updated: 2024-01-15

Scenarios: 12
  • password-reset (5 runs)
  • account-creation (8 runs)
  • order-tracking (12 runs)
  • refund-request (3 runs)
  • product-inquiry (15 runs)
  ... and 7 more

Test Runs: 156 total
  • Last 30 days: 45 runs
  • Success rate: 87%
  • Avg duration: 4.2s

Team Members: 5
  • john@acme.com (Owner)
  • sarah@acme.com (Editor)
  • mike@acme.com (Editor)
  • emma@acme.com (Viewer)
  • alex@acme.com (Viewer)

Tags: customer-support, e-commerce, chatbot

URLs:
  • Web: https://app.fluxloop.ai/projects/customer-support-bot
  • Results: https://results.fluxloop.ai/projects/customer-support-bot
```

### `fluxloop projects update`

Update project settings.

**Usage:**

```bash
fluxloop projects update [options]
```

**Options:**

- `--project <name>`: Project name or ID (default: current project)
- `--name <name>`: New project name
- `--description <desc>`: New description
- `--tags <tags>`: New comma-separated list of tags

**Examples:**

```bash
# Update current project description
fluxloop projects update \
  --description "Enhanced customer support agent with GPT-4"

# Update specific project
fluxloop projects update \
  --project sales-assistant \
  --tags "sales, leads, qualification, automation"
```

### `fluxloop projects delete`

Delete a project.

**Usage:**

```bash
fluxloop projects delete [options]
```

**Options:**

- `--project <name>`: Project name or ID (required)
- `--force`: Skip confirmation prompt

**Examples:**

```bash
# Delete project (with confirmation)
fluxloop projects delete --project old-project

# Delete without confirmation
fluxloop projects delete --project old-project --force
```

**Warning:**

```
⚠️  Warning: This action cannot be undone!

Delete project: old-project

This will permanently delete:
  • All scenarios (15)
  • All test runs (234)
  • All results and data

Type the project name to confirm: old-project

✅ Project deleted successfully
```

### `fluxloop projects disconnect`

Disconnect the current directory from its project.

**Usage:**

```bash
fluxloop projects disconnect
```

**Examples:**

```bash
# Disconnect from current project
fluxloop projects disconnect
```

## Configuration

### Project Configuration File

When you connect a directory to a project, FluxLoop creates `.fluxloop/config.yaml`:

```yaml
# .fluxloop/config.yaml
project_id: proj_abc123
project_name: customer-support-bot
organization: Acme Inc

# Last sync timestamp
last_sync: "2024-01-15T14:30:00Z"

# Default settings
defaults:
  scenario_dir: scenarios
  results_dir: results
```

### Local vs. Cloud Projects

- **Local Project**: Created with `fluxloop init`, exists only on your machine
- **Cloud Project**: Created with `fluxloop projects create`, synced to the web platform
- **Connected Project**: Local project linked to a cloud project

```bash
# Create local-only project
fluxloop init

# Connect to cloud project
fluxloop projects select

# Create new cloud project and connect
fluxloop projects create --connect
```

## Best Practices

### Naming Conventions

Use descriptive, kebab-case names:

```bash
✅ Good:
  • customer-support-bot
  • sales-lead-qualifier
  • data-analysis-agent

❌ Bad:
  • bot1
  • project_test
  • My Project
```

### Project Organization

Organize projects by:

- **Product**: `acme-shop-chatbot`, `acme-crm-assistant`
- **Team**: `sales-team-agents`, `support-team-bots`
- **Environment**: `chatbot-dev`, `chatbot-staging`, `chatbot-prod`

### Team Collaboration

1. **Create shared projects** in your organization
2. **Invite team members** via the web platform
3. **Use consistent naming** for scenarios and tests
4. **Document project purpose** in the description

## Troubleshooting

### Project Not Found

```
❌ Error: Project 'my-project' not found

Available projects:
  • customer-support-bot
  • sales-assistant

Run 'fluxloop projects list' to see all projects.
```

**Solution:**

```bash
# List all projects
fluxloop projects list

# Select the correct project
fluxloop projects select --project customer-support-bot
```

### Permission Denied

```
❌ Error: Permission denied

You don't have permission to modify this project.

Required role: Editor or Owner
Your role: Viewer
```

**Solution:**

Contact the project owner to grant you the appropriate permissions.

### Already Connected

```
⚠️  Warning: This directory is already connected to a project

Current project: customer-support-bot

Do you want to switch to a different project? (y/n):
```

**Solution:**

```bash
# Disconnect first
fluxloop projects disconnect

# Then connect to new project
fluxloop projects select
```

## Related Commands

- [`fluxloop init`](./init): Initialize a local project
- [`fluxloop scenarios`](./scenarios): Manage scenarios
- [`fluxloop sync pull`](/cli/commands/sync): Pull scenarios from cloud
- [`fluxloop auth`](./auth): Authenticate with FluxLoop

## See Also

- [Projects and Scenarios](/platform/projects-and-scenarios): Managing projects on the web platform
- [Project Configuration](../configuration/project-config): Configuring project settings
- [Team Collaboration](../workflows/team-collaboration): Working with teams
