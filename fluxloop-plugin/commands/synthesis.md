---
description: Generate test data (personas → inputs → bundle)
allowed-tools: [Bash]
---

# FluxLoop Synthesis

Generate test data (personas → inputs → bundle)

## Pre-check (First!)

Check existing data before proceeding:
```bash
fluxloop bundles list --scenario-id <scenario_id>
fluxloop inputs list --scenario-id <scenario_id>
```

## Decision Logic

| Situation | Action |
|-----------|--------|
| Existing bundle | `sync pull` → `test` (2 commands) |
| Existing input set | `bundles publish` → `sync pull` → `test` (3 commands) |
| None | Full generation (see below) |

## Full Generation (5 commands)

```bash
# 1. Generate personas
fluxloop personas suggest --scenario-id <id>

# 2. Synthesize inputs
fluxloop inputs synthesize --scenario-id <id>

# 3. Publish bundle
fluxloop bundles publish --scenario-id <id> --input-set-id <input_set_id>

# 4. Pull
fluxloop sync pull --bundle-version-id <bundle_version_id>

# 5. Test
fluxloop test --scenario <name>
```

## Notes

- `personas suggest`: Generate personas for scenario (required before synthesize)
- `inputs synthesize`: Generate inputs based on personas → outputs `input_set_id`
- `bundles publish`: Publish input set as bundle → outputs `bundle_version_id`
- Use output IDs from each command in subsequent commands

## Options

| Option | Description |
|--------|-------------|
| `--total-count N` | Number of inputs to generate |
| `--scenario-id` | Target scenario ID |
