---
description: Execute synthesis workflow from scenario creation to bundle publication
allowed-tools: [Bash]
---

# FluxLoop Synthesis

Execute synthesis workflow from scenario creation to bundle publication (excludes testing).

## Run

Run 8 CLI commands sequentially (synthesis only, no testing):
1. `fluxloop scenarios create`
2. `fluxloop intent refine`
3. `fluxloop scenarios refine`
4. `fluxloop personas suggest`
5. `fluxloop inputs synthesize`
6. `fluxloop inputs qc`
7. (if needed) `fluxloop inputs refine`
8. `fluxloop bundles publish`

## Notes

- `fluxloop scenarios create` requires a `config_snapshot` payload (use `--config-file` or `--file`).
- `fluxloop intent refine` saves to project context by default (use `--no-apply` for preview).
- `fluxloop scenarios refine` saves to scenario snapshot by default (use `--no-apply` for preview).
- `fluxloop inputs synthesize` auto-uses the latest suggested `persona_ids` if `--persona-ids` is omitted.

## Description

Proceeds **only to bundle publication**, without testing.
- Use when you want to prepare data and test later
- For full test cycle, use the Skill instead

## Options

- `--add-inputs --bundle-id <ID>`: Add inputs to existing bundle
- `--dry-run`: Preview plan without actual synthesis
