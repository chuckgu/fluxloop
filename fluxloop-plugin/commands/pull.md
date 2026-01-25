---
description: Pull criteria/inputs from Web (requires API Key)
allowed-tools: [Bash]
---

# FluxLoop Pull

Pull criteria/inputs from Web

## Prerequisites

API Key must be configured. Check with:
```bash
fluxloop apikeys check
```

If not set:
```bash
fluxloop apikeys create
```

## Run
```bash
fluxloop sync pull
```

## Troubleshooting

**"Sync API key is not set" error:**
```bash
# Create and save API Key
fluxloop apikeys create

# Then retry
fluxloop sync pull
```
