# fluxloop auth

Authenticate with the FluxLoop Web Platform.

## Synopsis

```bash
fluxloop auth <command> [options]
```

## Description

The `auth` command manages authentication with the FluxLoop Web Platform. It handles login, logout, and viewing current authentication status.

## Commands

### `fluxloop auth login`

Log in to the FluxLoop Web Platform using an API key.

**Usage:**

```bash
fluxloop auth login [options]
```

**Options:**

- `--api-key <key>`: API key to use for authentication (optional, will prompt if not provided)
- `--save`: Save the API key to local configuration (default: true)
- `--profile <name>`: Profile name to save credentials under (default: "default")

**Examples:**

```bash
# Interactive login (prompts for API key)
fluxloop auth login

# Login with API key provided
fluxloop auth login --api-key flux_dev_abc123...

# Login and save to a specific profile
fluxloop auth login --profile production
```

**Interactive Flow:**

```
$ fluxloop auth login

Welcome to FluxLoop!

Please enter your API key:
> flux_dev_abc123def456ghi789jkl012mno34

✅ Successfully authenticated!
✅ Credentials saved to ~/.fluxloop/credentials

Your account: john@example.com
Organizations: Acme Inc, Personal
```

### `fluxloop auth logout`

Log out from the FluxLoop Web Platform.

**Usage:**

```bash
fluxloop auth logout [options]
```

**Options:**

- `--profile <name>`: Profile to log out from (default: "default")
- `--all`: Log out from all profiles

**Examples:**

```bash
# Logout from default profile
fluxloop auth logout

# Logout from specific profile
fluxloop auth logout --profile production

# Logout from all profiles
fluxloop auth logout --all
```

### `fluxloop auth status`

Display current authentication status.

**Usage:**

```bash
fluxloop auth status [options]
```

**Options:**

- `--profile <name>`: Profile to check status for (default: "default")
- `--json`: Output in JSON format

**Examples:**

```bash
# Check authentication status
fluxloop auth status

# Check specific profile
fluxloop auth status --profile production

# Get status in JSON format
fluxloop auth status --json
```

**Output:**

```
✅ Authenticated

Profile: default
Account: john@example.com
Organizations:
  • Acme Inc (owner)
  • Personal (member)

API Key: flux_dev_abc1...mno34
Expires: 2024-04-15 (84 days remaining)
Scopes: All Projects
Permissions:
  ✅ Read scenarios
  ✅ Upload results
  ✅ Create scenarios
  ❌ Delete scenarios
  ❌ Manage projects
```

### `fluxloop auth whoami`

Display information about the currently authenticated user.

**Usage:**

```bash
fluxloop auth whoami [options]
```

**Options:**

- `--profile <name>`: Profile to check (default: "default")
- `--json`: Output in JSON format

**Examples:**

```bash
# Display current user info
fluxloop auth whoami

# Get user info in JSON format
fluxloop auth whoami --json
```

**Output:**

```
john@example.com

Organizations:
  • Acme Inc (owner)
  • Personal (member)

Projects:
  • customer-support-bot
  • sales-assistant
  • analytics-agent

API Access: Enabled
Plan: Team (1,000 runs/month)
Usage this month: 234 / 1,000 runs
```

## Configuration

### Credential Storage

Credentials are stored in `~/.fluxloop/credentials` by default. This file contains:

```yaml
profiles:
  default:
    api_key: flux_dev_abc123...
    account: john@example.com
    expires: "2024-04-15"

  production:
    api_key: flux_prod_xyz789...
    account: john@example.com
    expires: "2024-06-01"
```

### Environment Variables

You can also authenticate using environment variables:

```bash
export FLUXLOOP_API_KEY="flux_dev_abc123..."
fluxloop auth status
```

Environment variables take precedence over saved credentials.

### Multiple Profiles

Use profiles to manage multiple accounts or environments:

```bash
# Development
fluxloop auth login --profile dev
fluxloop test --profile dev

# Production
fluxloop auth login --profile prod
fluxloop test --profile prod
```

## Security

### Protecting Your API Key

1. **Never commit credentials**: Add `~/.fluxloop/credentials` to `.gitignore`
2. **Use environment variables in CI/CD**: Set `FLUXLOOP_API_KEY` as a secret
3. **Rotate keys regularly**: Generate new API keys every 90 days
4. **Use scoped keys**: Limit permissions to only what's needed

### Revoking Access

If your API key is compromised:

1. Log in to [app.fluxloop.ai](https://app.fluxloop.ai)
2. Go to Settings → API Keys
3. Delete the compromised key
4. Generate a new key
5. Update your local credentials:

```bash
fluxloop auth login --api-key <new-key>
```

## Troubleshooting

### Invalid API Key

```
❌ Error: Invalid API key

Please check that:
1. The API key is correct (no typos)
2. The key hasn't been revoked or expired
3. You have network connectivity

Generate a new key at: https://app.fluxloop.ai/settings/api-keys
```

**Solution:**

```bash
# Check your API key in the web platform
# Generate a new key if needed
fluxloop auth login --api-key <new-key>
```

### Permission Denied

```
❌ Error: Permission denied

Your API key doesn't have permission to perform this action.

Required permission: upload_results
Your permissions: read_scenarios
```

**Solution:**

Update your API key permissions in the web platform, or create a new key with the required permissions.

### Network Issues

```
❌ Error: Unable to connect to FluxLoop API

Failed to connect to api.fluxloop.ai

Please check your internet connection and try again.
```

**Solution:**

```bash
# Check network connectivity
ping api.fluxloop.ai

# If behind a proxy, set proxy environment variables
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## Related Commands

- [`fluxloop projects`](./projects): Manage projects
- [`fluxloop apikeys`](./apikeys): Manage API keys
- [`fluxloop status`](./status): View project status

## See Also

- [Web Platform - API Keys](/platform/api-keys): Managing API keys in the web platform
- [Authentication Guide](../configuration/authentication): Detailed authentication guide
- [CI/CD Integration](../workflows/ci-cd-integration): Using FluxLoop in CI/CD
