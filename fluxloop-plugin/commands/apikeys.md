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
- `fluxloop sync pull --scenario <name>` - Pull bundle from Web
- `fluxloop sync upload --scenario <name>` - Upload results to Web
- `fluxloop test --scenario <name>` - Full test workflow (includes sync)

## Output Example
```
Creating API Key for project: my-agent...
✓ API Key created: flx_sk_****1234
✓ Saved to .env as FLUXLOOP_SYNC_API_KEY

You can now use:
  fluxloop sync pull --scenario <name>
  fluxloop sync upload --scenario <name>
  fluxloop test --scenario <name>
```

> `--scenario` specifies the folder name in `.fluxloop/scenarios/`.

## Notes

- Requires login first (`fluxloop auth login`)
- Requires Web Project selected (`fluxloop projects select <id>`)
- Key is automatically saved to `.env` for immediate use
- Use `--overwrite-env` to replace existing key
