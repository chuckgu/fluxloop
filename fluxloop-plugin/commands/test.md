---
description: Run FluxLoop test (after sync pull)
allowed-tools: [Bash]
---

# FluxLoop Test

Run test (inputs must be pulled first)

## Prerequisites

1. Project selected: `fluxloop context show`
2. API Key configured: `fluxloop apikeys check`
3. **Inputs pulled**: `fluxloop sync pull --bundle-version-id <id>`

## Recommended Flow

```bash
# 1. Pull first
fluxloop sync pull --bundle-version-id <bundle_version_id>

# 2. Then test
fluxloop test --scenario <scenario_name>
```

> ⚠️ Always run `sync pull` and `test` separately

## Run

```bash
fluxloop test --scenario <scenario_name>
```

> `--scenario` is the folder name in `.fluxloop/scenarios/`

## Description

1. Load inputs from `inputs/` (must be pulled first)
2. Run agent and record results
3. Results are uploaded automatically when upload is enabled

## Options

| Option | Description |
|--------|-------------|
| `--scenario <name>` | Scenario folder name |
| `--skip-upload` | Skip upload |
| `--smoke` | Smoke test only |
| `--full` | Full test run |
| `--quiet` | Minimal output |

## Local Only (No API Key)

```bash
fluxloop test --scenario <name> --skip-upload
```

## Troubleshooting

**"Inputs file not found":**
```bash
# Check bundles
fluxloop bundles list --scenario-id <scenario_id>

# Pull first
fluxloop sync pull --bundle-version-id <bundle_version_id>

# Retry
fluxloop test --scenario <name>
```

**"Sync API key not set":**
```bash
fluxloop apikeys create
```
