---
sidebar_position: 2
---

# Authentication

Connect your local environment to the FluxLoop Web Platform.

## Why Authenticate?

Authenticating the CLI enables cloud-powered features:

- **Sync Scenarios**: Pull test cases managed on the web platform.
- **Upload Results**: Visualize and share test results on the interactive dashboard.
- **Team Collaboration**: Share project data and results with team members.
- **Evaluation**: Use cloud-based LLM evaluators to analyze agent behavior.

## Obtaining an API Key

1. Log in to [app.fluxloop.ai](https://app.fluxloop.ai).
2. Navigate to **Settings** → **API Keys**.
3. Click **"Create New API Key"**.
4. Enter a name (e.g., "MacBook Pro") and copy the generated key.

⚠️ **Important**: The key is only displayed once. Store it securely in a password manager.

## Login via CLI

The easiest way to authenticate is using the `auth login` command:

```bash
fluxloop auth login
```

When prompted, paste your API key. The CLI will verify the key and save it securely in your local configuration.

## Environment Variables

In CI/CD environments (like GitHub Actions) or for local development, you can use the `FLUXLOOP_API_KEY` environment variable:

```bash
export FLUXLOOP_API_KEY="flux_dev_abc123..."
fluxloop test
```

## .env File

You can also store your key in a `.env` file in your project root:

```bash
# .env
FLUXLOOP_API_KEY=flux_dev_abc123...
```

Make sure to add `.env` to your `.gitignore` to avoid leaking your key:

```bash
echo ".env" >> .gitignore
```

## Verify Authentication

Check your current authentication status:

```bash
fluxloop auth status
```

**Output:**

```
Authenticated as: user@company.com
Default Project: customer-support-bot
API Key: flux_dev_abc1... (Expires in 85 days)
```

## Next Steps

- [First Test](./first-test)
- [Project Configuration](../configuration/project-config)
