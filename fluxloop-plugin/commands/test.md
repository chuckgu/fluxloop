---
description: Run the full FluxLoop test workflow (pull → run → upload)
allowed-tools: [Bash]
---

# FluxLoop Test

Run the full FluxLoop test workflow (pull → run → upload)

## Prerequisites

1. Project selected: `fluxloop context show`
2. API Key configured (for sync): `fluxloop apikeys check`

If API Key not set:
```bash
fluxloop apikeys create
```

## Run
```bash
fluxloop test --scenario <scenario_name>
```

> `--scenario` specifies the folder name in `.fluxloop/scenarios/`.

## Description
1. Pull criteria/inputs from Web (requires API Key)
2. Run the test (turn recording)
3. Upload results to Web (requires API Key)
4. Print summary + evaluation criteria

## Options
- `--scenario <name>`: Scenario folder name (in `.fluxloop/scenarios/`)
- `--skip-pull`: Skip pull (use local data only)
- `--skip-upload`: Skip upload
- `--smoke`: Smoke test only
- `--full`: Full test run
- `--quiet`: Minimal output (for hooks)

## No API Key Mode

If you only want to test locally without sync:
```bash
fluxloop test --scenario <scenario_name> --skip-pull --skip-upload
```

## Troubleshooting

**"Sync API key is not set" error:**
```bash
# Create and save API Key
fluxloop apikeys create

# Then retry
fluxloop test --scenario <scenario_name>
```
