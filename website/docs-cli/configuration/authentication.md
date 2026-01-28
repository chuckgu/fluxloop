---
sidebar_position: 5
---

# Authentication

Configure authentication with FluxLoop Web Platform.

## Overview

Authentication is required to:
- Pull scenarios from Web Platform
- Upload test results
- Sync data with your team
- Access project resources

## Authentication Methods

### 1. Interactive Login (Recommended for Development)

Login via browser:

```bash
fluxloop auth login
```

This opens your browser to authenticate:

```
1. Browser opens: https://app.fluxloop.ai/login
2. Login with your account
3. Authorize CLI access
4. Return to terminal
✅ Successfully authenticated
```

Credentials stored in `~/.fluxloop/credentials`:

```json
{
  "access_token": "flx_...",
  "refresh_token": "flx_refresh_...",
  "expires_at": "2024-11-02T10:00:00Z",
  "user_email": "user@example.com"
}
```

### 2. API Key (Recommended for CI/CD)

Create and use API key:

```bash
# Create API key on Web Platform
# app.fluxloop.ai/settings/api-keys

# Set environment variable
export FLUXLOOP_API_KEY=flx_api_...

# CLI automatically uses API key
fluxloop test --upload
```

### 3. Service Account (Team Automation)

For shared automation:

```bash
# Admin creates service account
fluxloop apikeys create \
  --name "ci-bot" \
  --type service-account \
  --scope read-write

# Use in CI
export FLUXLOOP_API_KEY=flx_sa_...
```

## Configuration

### Credentials File

Located at `~/.fluxloop/credentials`:

```json
{
  "default_profile": "production",
  "profiles": {
    "production": {
      "access_token": "flx_...",
      "refresh_token": "flx_refresh_...",
      "expires_at": "2024-11-02T10:00:00Z",
      "api_endpoint": "https://api.fluxloop.ai"
    },
    "staging": {
      "access_token": "flx_...",
      "api_endpoint": "https://api-staging.fluxloop.ai"
    }
  }
}
```

### Multiple Profiles

Use different profiles for different environments:

```bash
# Login to production
fluxloop auth login --profile production

# Login to staging
fluxloop auth login --profile staging

# Use specific profile
fluxloop test --profile staging --upload

# Set default profile
fluxloop config set profile staging
```

## API Keys

### Create API Key

Via Web Platform:

```
1. Go to app.fluxloop.ai/settings/api-keys
2. Click "Create API Key"
3. Name: "my-cli-key"
4. Scope: Select permissions
5. Click "Create"
6. Copy key (shown once!)
```

Via CLI:

```bash
fluxloop apikeys create --name "my-cli-key"
```

### API Key Scopes

| Scope | Description |
|-------|-------------|
| `read` | View scenarios, criteria, results |
| `write` | Upload results, create scenarios |
| `read-write` | Full access |
| `admin` | Manage project settings |

### Use API Key

**Environment Variable (Recommended):**

```bash
export FLUXLOOP_API_KEY=flx_api_...
fluxloop test --upload
```

**Config File:**

```yaml
# fluxloop.yaml
api:
  key_file: ~/.fluxloop/api_key.txt
```

**Command Line:**

```bash
fluxloop test --api-key flx_api_... --upload
```

### Rotate API Keys

Regularly rotate keys for security:

```bash
# Create new key
fluxloop apikeys create --name "new-key"

# Update environment
export FLUXLOOP_API_KEY=flx_new_key...

# Revoke old key
fluxloop apikeys revoke flx_old_key...
```

## Security Best Practices

### 1. Protect Credentials

❌ Don't commit credentials:
```bash
# .gitignore
.fluxloop/credentials
api_key.txt
```

✅ Use environment variables:
```bash
export FLUXLOOP_API_KEY=...
```

### 2. Use Minimal Scopes

❌ Don't use admin keys for CI:
```bash
fluxloop apikeys create --scope admin  # Too broad
```

✅ Use least privilege:
```bash
fluxloop apikeys create --scope read-write  # Sufficient
```

### 3. Rotate Keys Regularly

```bash
# Monthly rotation
fluxloop apikeys create --name "ci-bot-$(date +%Y%m)"
# Update CI environment
# Revoke old key after grace period
```

### 4. Monitor Key Usage

Check key usage on Web Platform:

```
app.fluxloop.ai/settings/api-keys
- Last used: 2024-11-01 14:30:00
- Usage count: 1,234 requests
```

### 5. Revoke Compromised Keys

If key is compromised:

```bash
# Immediately revoke
fluxloop apikeys revoke flx_compromised_key

# Create new key
fluxloop apikeys create --name "replacement-key"

# Update all services
```

## Troubleshooting

### Authentication Failed

**Problem**: Login fails

**Solution**: Check browser and network

```bash
$ fluxloop auth login
[ERROR] Authentication failed
Check:
1. Browser opened?
2. Network connection?
3. Ad blockers disabled?
```

### Token Expired

**Problem**: "Authentication token expired"

**Solution**: Refresh token

```bash
$ fluxloop test --upload
[ERROR] Token expired

# Refresh automatically
fluxloop auth refresh

# Or login again
fluxloop auth login
```

### Invalid API Key

**Problem**: "Invalid API key"

**Solution**: Check key format and revocation

```bash
$ fluxloop test --upload
[ERROR] Invalid API key

# Check key
echo $FLUXLOOP_API_KEY
# Should start with: flx_api_...

# Verify on Web Platform
# app.fluxloop.ai/settings/api-keys
```

### Permission Denied

**Problem**: "Permission denied"

**Solution**: Check API key scope

```bash
$ fluxloop sync upload
[ERROR] Permission denied

# Check scope
fluxloop apikeys info $FLUXLOOP_API_KEY

# Create key with correct scope
fluxloop apikeys create --scope read-write
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FLUXLOOP_API_KEY` | API key for authentication |
| `FLUXLOOP_API_ENDPOINT` | API endpoint URL |
| `FLUXLOOP_PROFILE` | Authentication profile |
| `FLUXLOOP_TOKEN` | Direct access token |

## CI/CD Examples

### GitHub Actions

```yaml
# .github/workflows/test.yml
- name: Run Tests
  env:
    FLUXLOOP_API_KEY: ${{ secrets.FLUXLOOP_API_KEY }}
  run: |
    fluxloop sync pull --yes
    fluxloop test --upload --yes
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  script:
    - export FLUXLOOP_API_KEY=$FLUXLOOP_API_KEY
    - fluxloop sync pull --yes
    - fluxloop test --upload --yes
  variables:
    FLUXLOOP_API_KEY: $FLUXLOOP_API_KEY_SECRET
```

### Jenkins

```groovy
// Jenkinsfile
withCredentials([string(credentialsId: 'fluxloop-api-key', variable: 'FLUXLOOP_API_KEY')]) {
    sh 'fluxloop sync pull --yes'
    sh 'fluxloop test --upload --yes'
}
```

## Related

- [Auth Command](../commands/auth) - Authentication commands
- [API Keys Command](../commands/apikeys) - Manage API keys
- [Security Guide](../guides/security) - Security best practices
- [CI/CD Integration](../workflows/ci-cd-integration) - Automation

## Next Steps

- Login to FluxLoop Web Platform
- Create an API key
- Configure your CI/CD pipeline
- Set up team authentication
