# fluxloop apikeys

Manage API keys.

## Synopsis

```bash
fluxloop apikeys [command] [options]
```

## Description

The `apikeys` command manages FluxLoop API keys from the command line. API keys are used to authenticate CLI and programmatic access to the FluxLoop platform.

## Commands

### `fluxloop apikeys list`

List all API keys.

**Usage:**

```bash
fluxloop apikeys list [options]
```

**Options:**

- `--json`: Output in JSON format
- `--show-keys`: Show partial key values (last 4 characters)

**Examples:**

```bash
# List all API keys
fluxloop apikeys list

# List with partial key values
fluxloop apikeys list --show-keys

# Get keys in JSON format
fluxloop apikeys list --json
```

**Output:**

```
API Keys

┌──────────────────────────────────────────────────────────────────┐
│ My Development Key                                               │
│ Key: flux_dev_****...mno34                                       │
│ Created: Jan 15, 2024                                            │
│ Expires: Apr 15, 2024 (84 days remaining)                       │
│ Last used: 2 hours ago                                           │
│ Scope: customer-support-bot, sales-assistant                     │
│ Permissions: read_scenarios, upload_results, create_scenarios    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ CI/CD Pipeline                                                   │
│ Key: flux_ci_****...jkl                                          │
│ Created: Jan 10, 2024                                            │
│ Expires: Apr 10, 2024 (79 days remaining)                       │
│ Last used: 5 minutes ago                                         │
│ Scope: All Projects                                              │
│ Permissions: read_scenarios, upload_results                      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ Backup Key                                                       │
│ Key: flux_dev_****...tuv                                         │
│ Created: Dec 20, 2023                                            │
│ Expires: Never                                                   │
│ Last used: Never                                                 │
│ Scope: customer-support-bot                                      │
│ Permissions: read_scenarios                                      │
└──────────────────────────────────────────────────────────────────┘

Total: 3 API keys
```

### `fluxloop apikeys create`

Create a new API key.

**Usage:**

```bash
fluxloop apikeys create [options]
```

**Options:**

- `--name <name>`: Key name (required)
- `--description <desc>`: Key description
- `--scope <projects>`: Comma-separated list of projects (default: all)
- `--permissions <perms>`: Comma-separated list of permissions
- `--expires <duration>`: Expiration duration (30d, 90d, 1y, never)

**Examples:**

```bash
# Interactive key creation
fluxloop apikeys create

# Create key with specific permissions
fluxloop apikeys create \
  --name "Production Key" \
  --scope "customer-support-bot" \
  --permissions "read_scenarios,upload_results" \
  --expires 90d

# Create read-only key
fluxloop apikeys create \
  --name "Read Only" \
  --permissions "read_scenarios" \
  --expires never
```

**Interactive Flow:**

```
$ fluxloop apikeys create

Create New API Key

Key name: Production Deployment
Description: API key for production deployments

Scope:
1. All Projects
2. Specific Projects

Select (1-2): 2

Available projects:
  ☑ customer-support-bot
  ☑ sales-assistant
  ☐ analytics-agent

Permissions:
  ☑ Read scenarios
  ☑ Upload results
  ☑ Create scenarios
  ☐ Delete scenarios
  ☐ Manage projects

Expires:
1. 30 days
2. 90 days
3. 1 year
4. Never

Select (1-4): 2

✅ API key created successfully

┌─────────────────────────────────────────┐
│                                         │
│  flux_prod_abc123def456ghi789jkl012mno  │
│                                         │
│  ⚠️  Save this key now!                 │
│  You won't be able to see it again.    │
│                                         │
└─────────────────────────────────────────┘

Key details:
  Name: Production Deployment
  Scope: customer-support-bot, sales-assistant
  Expires: Apr 15, 2024 (90 days)

The key has been copied to your clipboard.
```

### `fluxloop apikeys show`

Display details for a specific API key.

**Usage:**

```bash
fluxloop apikeys show <key-id> [options]
```

**Options:**

- `--json`: Output in JSON format

**Examples:**

```bash
# Show key details
fluxloop apikeys show key_abc123

# Get details in JSON format
fluxloop apikeys show key_abc123 --json
```

**Output:**

```
API Key: Production Deployment

Key ID: key_abc123
Key: flux_prod_****...mno
Created: Jan 15, 2024
Expires: Apr 15, 2024 (84 days remaining)

Scope: 2 projects
  • customer-support-bot
  • sales-assistant

Permissions:
  ✅ Read scenarios
  ✅ Upload results
  ✅ Create scenarios
  ❌ Delete scenarios
  ❌ Manage projects

Usage (Last 30 days):
  Total requests: 1,234
  Avg per day: 41

  By operation:
    • Pull scenarios: 567 (46%)
    • Upload results: 432 (35%)
    • Create scenarios: 235 (19%)

  By project:
    • customer-support-bot: 987 (80%)
    • sales-assistant: 247 (20%)

Last used: 2 hours ago
  IP: 192.168.1.100
  Location: San Francisco, CA
  User Agent: fluxloop-cli/1.2.3
```

### `fluxloop apikeys update`

Update an existing API key.

**Usage:**

```bash
fluxloop apikeys update <key-id> [options]
```

**Options:**

- `--name <name>`: New key name
- `--description <desc>`: New description
- `--scope <projects>`: Update project scope
- `--permissions <perms>`: Update permissions
- `--expires <duration>`: Update expiration

**Examples:**

```bash
# Update key name
fluxloop apikeys update key_abc123 \
  --name "Production Key (Updated)"

# Update permissions
fluxloop apikeys update key_abc123 \
  --permissions "read_scenarios,upload_results,create_scenarios"

# Extend expiration
fluxloop apikeys update key_abc123 \
  --expires 1y
```

### `fluxloop apikeys regenerate`

Regenerate (rotate) an API key.

**Usage:**

```bash
fluxloop apikeys regenerate <key-id> [options]
```

**Options:**

- `--force`: Skip confirmation prompt

**Examples:**

```bash
# Regenerate key (with confirmation)
fluxloop apikeys regenerate key_abc123

# Regenerate without confirmation
fluxloop apikeys regenerate key_abc123 --force
```

**Warning:**

```
⚠️  Warning: The old key will be immediately revoked

Key: Production Deployment (flux_prod_****...mno)
Last used: 2 hours ago

After regeneration:
• The old key will stop working immediately
• You'll need to update the key in all systems using it
• A new key will be generated with the same permissions

Continue? (y/n): y

✅ API key regenerated successfully

┌─────────────────────────────────────────┐
│                                         │
│  flux_prod_xyz789abc123def456ghi789jkl  │
│                                         │
│  ⚠️  Save this key now!                 │
│  You won't be able to see it again.    │
│                                         │
└─────────────────────────────────────────┘

⚠️  Action required:
Update the API key in the following locations:
  • CI/CD environment variables
  • Local .env files
  • Any scripts or applications using this key
```

### `fluxloop apikeys delete`

Delete an API key.

**Usage:**

```bash
fluxloop apikeys delete <key-id> [options]
```

**Options:**

- `--force`: Skip confirmation prompt

**Examples:**

```bash
# Delete key (with confirmation)
fluxloop apikeys delete key_abc123

# Delete without confirmation
fluxloop apikeys delete key_abc123 --force
```

**Warning:**

```
⚠️  Warning: This action cannot be undone

Key: Old Development Key
Created: 6 months ago
Last used: 3 months ago

This key will be permanently revoked and cannot be recovered.

Type the key name to confirm: Old Development Key

✅ API key deleted successfully
```

## Permissions

API keys can have the following permissions:

| Permission | Description |
|-----------|-------------|
| `read_scenarios` | Pull scenarios from cloud |
| `create_scenarios` | Create new scenarios |
| `update_scenarios` | Modify existing scenarios |
| `delete_scenarios` | Delete scenarios |
| `upload_results` | Upload test results |
| `read_results` | View test results |
| `manage_projects` | Create and modify projects |
| `invite_members` | Invite team members |
| `manage_keys` | Create and manage API keys |

## Scope

API keys can be scoped to:

- **All Projects**: Access all projects in your organization
- **Specific Projects**: Access only specified projects

Example:

```bash
# All projects
fluxloop apikeys create \
  --name "Admin Key" \
  --scope "*"

# Specific projects
fluxloop apikeys create \
  --name "Bot Key" \
  --scope "customer-support-bot,sales-assistant"
```

## Expiration

API keys can have different expiration policies:

- **30 days**: Short-term testing
- **90 days**: Regular development (recommended)
- **1 year**: Long-term projects
- **Never**: Service accounts (use with caution)

## Security Best Practices

### 1. Use Minimal Permissions

Grant only the permissions needed:

```bash
# Good: Read-only for analysis
fluxloop apikeys create \
  --name "Analytics" \
  --permissions "read_scenarios,read_results"

# Bad: Full access when not needed
fluxloop apikeys create \
  --name "Analytics" \
  --permissions "*"
```

### 2. Set Expiration Dates

Always set expiration for non-service keys:

```bash
# Good: 90-day expiration
fluxloop apikeys create --expires 90d

# Bad: Never expires (unless for service accounts)
fluxloop apikeys create --expires never
```

### 3. Rotate Keys Regularly

Rotate keys every 90 days:

```bash
# Regenerate key
fluxloop apikeys regenerate key_abc123

# Update in all systems
export FLUXLOOP_API_KEY="<new-key>"
```

### 4. Use Environment-Specific Keys

Different keys for different environments:

```bash
# Development
fluxloop apikeys create \
  --name "Development" \
  --expires 90d

# Staging
fluxloop apikeys create \
  --name "Staging" \
  --expires 1y

# Production
fluxloop apikeys create \
  --name "Production" \
  --expires 1y \
  --permissions "read_scenarios,upload_results"
```

### 5. Monitor Usage

Regularly check key usage:

```bash
# List all keys and their last usage
fluxloop apikeys list

# Check specific key usage
fluxloop apikeys show key_abc123
```

### 6. Revoke Unused Keys

Delete keys that haven't been used:

```bash
# Check for unused keys
fluxloop apikeys list

# Delete unused keys
fluxloop apikeys delete key_xyz789
```

## Troubleshooting

### Invalid API Key

```
❌ Error: Invalid API key

The API key is invalid or has been revoked.

Possible causes:
  • Key was deleted
  • Key was regenerated
  • Key has expired
  • Typo in key value

Solution:
  • Check key in web platform
  • Regenerate if needed
  • Create new key if deleted
```

### Insufficient Permissions

```
❌ Error: Insufficient permissions

Your API key doesn't have permission to perform this action.

Required: create_scenarios
Current: read_scenarios, upload_results

Solution:
  • Update key permissions in web platform
  • Create new key with required permissions
```

### Key Expired

```
❌ Error: API key expired

Key: Production Key
Expired: Jan 15, 2024 (30 days ago)

Solution:
  • Create a new API key
  • Or update the expiration date in web platform
```

## Related Commands

- [`fluxloop auth`](./auth): Authenticate with API keys
- [`fluxloop projects`](./projects): Manage projects
- [`fluxloop status`](./status): Check authentication status

## See Also

- [API Keys (Web Platform)](/platform/api-keys): Managing API keys in the web platform
- [Authentication](../configuration/authentication): Authentication guide
- [Security Best Practices](../guides/security): Security guidelines
