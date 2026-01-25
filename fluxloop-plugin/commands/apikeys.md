---
description: Create API Key for sync operations (pull/upload)
allowed-tools: [Bash]
---

# FluxLoop API Keys

Create and manage API Keys for sync operations

## Check if API Key is Set
```bash
fluxloop apikeys check
```

## Create API Key
```bash
# Create for current project (auto-saved to .env)
fluxloop apikeys create

# Specify project explicitly
fluxloop apikeys create --project-id <id>

# Custom key name
fluxloop apikeys create --name "ci-key"

# Don't auto-save (print key instead)
fluxloop apikeys create --no-save
```

## When Needed

API Key is required for:
- `fluxloop sync pull` - Pull bundle from Web
- `fluxloop sync upload` - Upload results to Web
- `fluxloop test` - Full test workflow (includes sync)

## Output Example
```
Creating API Key for project: my-agent...
✓ API Key created: flx_sk_****1234
✓ Saved to .env as FLUXLOOP_SYNC_API_KEY

You can now use:
  fluxloop sync pull
  fluxloop sync upload
  fluxloop test
```

## Notes

- Requires login first (`fluxloop auth login`)
- Requires project selected (`fluxloop context set-project <id>`)
- Key is automatically saved to `.env` for immediate use
- Use `--overwrite-env` to replace existing key
