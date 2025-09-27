# FluxLoop OSS Release Notes

## 0.0.1 — Initial Toolkit Preview

_Release date: YYYY-MM-DD_

### New
- Added `fluxloop generate inputs` to scaffold reviewed input sets before experiments.
- Introduced deterministic input generator utilities and persisted input counts in configuration objects.
- Enabled `ExperimentRunner` to consume external input files, resolve relative paths, and update metadata.
- Enhanced CLI summaries and progress indicators to reflect actual run counts derived from resolved inputs.

### Documentation
- Updated `packages/README.md`, CLI README, and `test-project/fluxloop.yaml` to describe the pre-generated input workflow.

### Testing
- Added unit tests covering input generation utilities, relative path handling, and resolved input count logic.

### Known Gaps
- LLM-backed input variation generation remains unimplemented; current generator produces deterministic entries.
- Additional end-to-end tests for large experiments and collector integration are planned for a future release.
