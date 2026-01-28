# API Keys

Learn how to create and manage API keys on the FluxLoop Web Platform.

## What are API Keys?

API keys are authentication tokens for securely accessing the FluxLoop Web Platform from your local CLI or Claude Code plugin.

### Use Cases

- **Local Development**: Access web platform from CLI
- **Claude Code**: Pull scenarios and upload results from the plugin
- **CI/CD**: Automated testing in GitHub Actions, GitLab CI, etc.
- **Programmatic Access**: API calls from custom scripts or tools

### Key Features

- **Scoped Permissions**: Control access per project
- **Expiration**: Set key expiration period
- **Audit Trail**: Track key usage history
- **Revocation**: Deactivate keys anytime

## Creating API Keys

### Via Web Platform

1. Log in to [app.fluxloop.ai](https://app.fluxloop.ai)
2. Navigate to **Settings** → **API Keys**
3. Click **"Create New API Key"**

4. Enter key information:

```
┌─────────────────────────────────────────┐
│ Create API Key                          │
├─────────────────────────────────────────┤
│                                         │
│ Name: *                                 │
│ ┌─────────────────────────────────┐    │
│ │ My Development Key               │    │
│ └─────────────────────────────────┘    │
│                                         │
│ Description: (optional)                 │
│ ┌─────────────────────────────────┐    │
│ │ For local development on MacBook │    │
│ └─────────────────────────────────┘    │
│                                         │
│ Scope:                                  │
│ ○ All Projects                          │
│ ● Specific Projects                     │
│   ☑ customer-support-bot                │
│   ☑ sales-assistant                     │
│   □ analytics-agent                     │
│                                         │
│ Permissions:                            │
│ ☑ Read scenarios                        │
│ ☑ Upload results                        │
│ ☑ Create scenarios                      │
│ □ Delete scenarios                      │
│ □ Manage projects                       │
│                                         │
│ Expires:                                │
│ ○ Never                                 │
│ ○ 30 days                               │
│ ● 90 days                               │
│ ○ 1 year                                │
│ ○ Custom: [____]                        │
│                                         │
│        [Cancel]  [Create Key]           │
└─────────────────────────────────────────┘
```

5. Copy the generated key to a secure location:

```
✅ API Key Created Successfully

┌─────────────────────────────────────────┐
│                                         │
│  flux_dev_abc123def456ghi789jkl012mno34 │
│                                         │
│  ⚠️  Save this key now!                 │
│  You won't be able to see it again.    │
│                                         │
│  [Copy to Clipboard]  [Download .env]  │
│                                         │
└─────────────────────────────────────────┘
```

⚠️ **Important**: The key is only displayed once at creation. Store it securely.

### Via CLI

You can also create API keys via CLI (requires authentication with an existing key):

```bash
fluxloop apikeys create \
  --name "CI/CD Pipeline" \
  --scope customer-support-bot \
  --expires 90d
```

Result:

```
✅ API key created successfully

Name: CI/CD Pipeline
Key: flux_ci_xyz789abc123def456ghi789jkl
Scope: customer-support-bot
Expires: 2024-04-15

⚠️  Save this key securely. You won't see it again.
```

## Using API Keys

### In CLI

Set the API key as an environment variable:

#### Option 1: Environment Variable

```bash
export FLUXLOOP_API_KEY="flux_dev_abc123def456ghi789jkl012mno34"
fluxloop test
```

#### Option 2: .env File

```bash
# .fluxloop/.env
FLUXLOOP_API_KEY=flux_dev_abc123def456ghi789jkl012mno34
```

Add `.env` to `.gitignore`:

```gitignore
# .gitignore
.fluxloop/.env
```

#### Option 3: Config File

```bash
# .fluxloop/config.yaml
api_key: flux_dev_abc123def456ghi789jkl012mno34
```

#### Option 4: Interactive Login

```bash
fluxloop auth login
# Enter API key interactively
```

### In Claude Code

The Claude Code plugin automatically manages API keys:

```
/fluxloop setup

> Please enter your FluxLoop API key:
flux_dev_abc123def456ghi789jkl012mno34

✅ API key saved securely
```

The key is stored securely in Claude Code's secure storage.

### In CI/CD

#### GitHub Actions

```yaml
# .github/workflows/fluxloop-test.yml
name: FluxLoop Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install FluxLoop
        run: pip install fluxloop

      - name: Run Tests
        env:
          FLUXLOOP_API_KEY: ${{ secrets.FLUXLOOP_API_KEY }}
        run: |
          fluxloop sync pull
          fluxloop test
          fluxloop sync upload
```

**Setting the Secret:**
1. GitHub repository → Settings → Secrets → Actions
2. Click "New repository secret"
3. Name: `FLUXLOOP_API_KEY`
4. Value: Your generated API key
5. Click "Add secret"

#### GitLab CI

```yaml
# .gitlab-ci.yml
fluxloop-test:
  stage: test
  image: python:3.11
  script:
    - pip install fluxloop
    - fluxloop sync pull
    - fluxloop test
    - fluxloop sync upload
  variables:
    FLUXLOOP_API_KEY: $FLUXLOOP_API_KEY
```

**Setting the Variable:**
1. GitLab project → Settings → CI/CD → Variables
2. Click "Add variable"
3. Key: `FLUXLOOP_API_KEY`
4. Value: Your generated API key
5. ☑ Masked
6. ☑ Protected (optional)

#### CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  test:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Install FluxLoop
          command: pip install fluxloop
      - run:
          name: Run Tests
          command: |
            fluxloop sync pull
            fluxloop test
            fluxloop sync upload
          environment:
            FLUXLOOP_API_KEY: ${FLUXLOOP_API_KEY}
```

## Managing API Keys

### Viewing Keys

View key list on the web platform:

```
┌──────────────────────────────────────────────────────────┐
│ API Keys                                                  │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ Name: My Development Key                                 │
│ Key: flux_dev_abc1...mno34 (last used: 2 hours ago)     │
│ Created: Jan 15, 2024                                    │
│ Expires: Apr 15, 2024                                    │
│ Scope: customer-support-bot, sales-assistant             │
│ [View Usage] [Regenerate] [Delete]                       │
│                                                           │
│ Name: CI/CD Pipeline                                     │
│ Key: flux_ci_xyz7...jkl (last used: 5 minutes ago)      │
│ Created: Jan 10, 2024                                    │
│ Expires: Apr 10, 2024                                    │
│ Scope: All Projects                                      │
│ [View Usage] [Regenerate] [Delete]                       │
│                                                           │
│ Name: Backup Key                                         │
│ Key: flux_dev_qrs4...tuv (never used)                   │
│ Created: Dec 20, 2023                                    │
│ Expires: Never                                           │
│ Scope: customer-support-bot                              │
│ [View Usage] [Regenerate] [Delete]                       │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

View in CLI as well:

```bash
fluxloop apikeys list
```

### Viewing Usage

View usage history for a specific key:

```
┌─────────────────────────────────────────┐
│ API Key Usage: My Development Key       │
├─────────────────────────────────────────┤
│                                         │
│ Last 7 Days:                            │
│                                         │
│ Jan 15: ████████████ 245 requests       │
│ Jan 14: ██████ 123 requests             │
│ Jan 13: ████ 89 requests                │
│ Jan 12: ██████████ 201 requests         │
│ Jan 11: ████████ 167 requests           │
│ Jan 10: ███ 56 requests                 │
│ Jan 9:  █ 23 requests                   │
│                                         │
│ Total Requests: 904                     │
│ Avg per Day: 129                        │
│                                         │
│ By Operation:                           │
│ • Pull scenarios: 456 (50%)             │
│ • Upload results: 301 (33%)             │
│ • Create scenarios: 147 (16%)           │
│                                         │
│ By Project:                             │
│ • customer-support-bot: 687 (76%)       │
│ • sales-assistant: 217 (24%)            │
│                                         │
└─────────────────────────────────────────┘
```

### Regenerating Keys

If a key is compromised or needs renewal:

1. Click **"Regenerate"** next to the key
2. Click **"Confirm"** in the confirmation popup
3. Copy the new key

⚠️ **Warning**: The old key is immediately deactivated. You must update to the new key.

```bash
# Update with new key in local environment
export FLUXLOOP_API_KEY="flux_dev_new123new456new789"

# CI/CD secrets also need updating
```

### Revoking Keys

Delete keys that are no longer in use:

1. Click **"Delete"** next to the key
2. Enter the key name in the confirmation popup
3. Click **"Delete"**

```
┌─────────────────────────────────────────┐
│ Delete API Key                          │
├─────────────────────────────────────────┤
│                                         │
│ ⚠️  This action cannot be undone.       │
│                                         │
│ Key: flux_dev_abc1...mno34              │
│ Name: My Development Key                │
│                                         │
│ Type the key name to confirm:           │
│ ┌─────────────────────────────────┐    │
│ │ My Development Key               │    │
│ └─────────────────────────────────┘    │
│                                         │
│        [Cancel]  [Delete]               │
└─────────────────────────────────────────┘
```

## Security Best Practices

### 1. Key Rotation

Rotate keys regularly:

```bash
# Rotate keys every 3 months (can be automated)
fluxloop apikeys rotate --key-id abc123
```

### 2. Minimal Scope

Grant only necessary permissions:

```
❌ Bad: All Projects + All Permissions
✅ Good: Specific Project + Read-only
```

### 3. Environment-Specific Keys

Use different keys per environment:

```
Development:   flux_dev_...
Staging:       flux_stg_...
Production:    flux_prod_...
CI/CD:         flux_ci_...
```

### 4. Never Commit Keys

Don't commit keys to Git:

```gitignore
# .gitignore
.env
.fluxloop/.env
*.key
secrets.yaml
```

If accidentally committed to Git:

```bash
# 1. Delete key immediately
fluxloop apikeys delete --key-id abc123

# 2. Create new key
fluxloop apikeys create --name "New Key"

# 3. Remove from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

### 5. Monitor Usage

Monitor for abnormal activity:

- Access from unexpected locations
- Unusually high request volumes
- Failed authentication attempts

## Troubleshooting

### Invalid API Key

```
❌ Error: Invalid API key

Possible causes:
1. Key was regenerated or deleted
2. Key expired
3. Typo in key value

Solution:
- Check key in web platform
- Regenerate if needed
- Update environment variable
```

### Insufficient Permissions

```
❌ Error: Permission denied

You don't have permission to access this resource.

Current permissions:
✅ Read scenarios
❌ Upload results (required)

Solution:
- Update key permissions in web platform
- Or create a new key with required permissions
```

### Rate Limiting

```
⚠️  Warning: Rate limit exceeded

Current rate: 1000 requests/hour
Your usage: 1,234 requests/hour

Retry after: 15 minutes

Solution:
- Wait for rate limit to reset
- Contact support for higher limits
```

## Next Steps

- [Platform Overview](./platform-overview.md): Web platform overview
- [Projects and Scenarios](./projects-and-scenarios.md): Manage projects and scenarios
- [CLI Authentication](/cli/commands/auth): CLI authentication methods
