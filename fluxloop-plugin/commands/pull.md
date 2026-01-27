---
description: Pull bundle data from Web (requires API Key)
allowed-tools: [Bash]
---

# FluxLoop Pull

Pull bundle data (criteria/inputs) from Web

## Prerequisites

1. Check API Key:
```bash
fluxloop apikeys check
```

2. Create if not set:
```bash
fluxloop apikeys create
```

## Run

```bash
# Specify bundle-version-id (recommended)
fluxloop sync pull --bundle-version-id <bundle_version_id>
```

> Get `bundle_version_id` from `fluxloop bundles list --scenario-id <id>`

## Pre-check

Check existing bundles before pulling:
```bash
fluxloop bundles list --scenario-id <scenario_id>
```

## Troubleshooting

**"Sync API key is not set" error:**
```bash
fluxloop apikeys create
fluxloop sync pull --bundle-version-id <id>
```
