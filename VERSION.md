# FluxLoop OSS Versions

## 0.0.1 (Unreleased)

### Highlights
- Introduced pre-generated input workflow with `fluxloop generate inputs` CLI command.
- Added deterministic input generator scaffold and persisted input counts to configuration.
- Updated experiment runner to load external input files, resolve relative paths, and honor reviewed datasets.
- Improved CLI summaries and progress reporting by using resolved input counts per configuration.
- Expanded documentation (`packages/README.md`, CLI README, example config) to cover the new workflow.
- Added regression tests for input generation utilities, relative path handling, and resolved input counts.

### Notes
- LLM-backed variation generation is still pending; the new generator currently produces deterministic entries.
- Ensure experiments point to reviewed input files via `inputs_file` when running larger batches.
