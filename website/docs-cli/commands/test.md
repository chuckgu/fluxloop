---
sidebar_position: 10
---

# test Command

Run agent tests with synthetic inputs from bundles or scenarios.

## Usage

```bash
fluxloop test [OPTIONS]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--bundle`, `-b` | Bundle ID or path to use | Latest bundle |
| `--scenario`, `-s` | Scenario ID to test against | None |
| `--iterations`, `-i` | Number of runs per input | 1 |
| `--config`, `-c` | Path to configuration file | `fluxloop.yaml` |
| `--output-dir` | Output directory for results | `./fluxloop/results` |
| `--yes`, `-y` | Skip confirmation prompt | `false` |
| `--upload` | Upload results to Web Platform | `false` |

## Examples

### Basic Test

Run test with the latest local bundle:

```bash
fluxloop test
```

### Test Specific Scenario

Run against a scenario from the Web Platform:

```bash
fluxloop test --scenario prod-regression-v2
```

### Multiple Iterations

Run each input multiple times to test consistency:

```bash
fluxloop test --iterations 10
```

### Test and Upload Results

Run tests and automatically upload results to Web Platform (default behavior unless disabled in config):

```bash
fluxloop test
```

To explicitly ensure upload or override a config that skips it:

```bash
fluxloop test --no-skip-upload
```

### CI/CD Mode

Skip confirmation prompts for automation:

```bash
fluxloop test --yes --upload
```

## How It Works

### 1. Load Test Bundle

The command loads synthetic inputs from:
- **Local bundle**: Generated with `fluxloop bundles create`
- **Scenario**: Pulled from Web Platform with `fluxloop scenarios pull`

```yaml
# Example bundle structure
bundle_id: bundle_20241101_143022
inputs:
  - id: input_001
    text: "How do I get started?"
    persona: novice_user
    context:
      user_type: beginner
      goal: onboarding
  - id: input_002
    text: "What are the advanced features?"
    persona: expert_user
```

### 2. Execute Agent

For each input, runs your agent according to the runner configuration:

```yaml
# fluxloop.yaml
runner:
  target: "src.agent:run"
  type: python-function

test:
  iterations: 1
  timeout: 30
```

### 3. Collect Results

Captures execution data:
- Input/output pairs
- Execution time
- Trace data (if using FluxLoop SDK)
- Errors and exceptions

### 4. Save Results

Outputs to `./fluxloop/results/run_YYYYMMDD_HHMMSS/`:

```
results/run_20241101_143022/
├── summary.json           # Aggregate statistics
├── results.jsonl          # Per-input results
├── traces.jsonl           # Detailed traces (if SDK used)
└── config.yaml            # Test configuration snapshot
```

## Output Files

### summary.json

Aggregate test statistics:

```json
{
  "test_id": "run_20241101_143022",
  "bundle_id": "bundle_20241101_140000",
  "total_inputs": 50,
  "total_runs": 500,
  "successful": 495,
  "failed": 5,
  "avg_duration_ms": 245.5,
  "started_at": "2024-11-01T14:30:22Z",
  "completed_at": "2024-11-01T14:35:10Z"
}
```

### results.jsonl

One line per test run:

```jsonl
{"input_id": "input_001", "iteration": 0, "persona": "novice_user", "input": "How do I start?", "output": "...", "duration_ms": 245, "success": true}
{"input_id": "input_002", "iteration": 0, "persona": "expert_user", "input": "What are options?", "output": "...", "duration_ms": 267, "success": true}
```

## Testing Against Scenarios

Scenarios are curated test suites managed on the Web Platform. They include:
- Predefined synthetic inputs
- Expected behavior criteria
- Regression test cases
- Production edge cases

### Pull and Test Scenario

```bash
# Pull scenario from Web Platform
fluxloop sync pull --scenario prod-regression-v2

# Run tests against it
fluxloop test --scenario prod-regression-v2
```

### Automatic Evaluation

When testing against scenarios with evaluation criteria:

```bash
# Run test and evaluate against criteria
fluxloop test --scenario prod-regression-v2
```

Results are automatically evaluated on the Web Platform.
## Integration with Web Platform

### Upload Results

Upload test results to view on the Web Platform:

```bash
fluxloop test --upload
```

This enables:
- Visual result analysis
- Team collaboration
- Historical tracking
- Automated evaluation

### View Results

After uploading, you'll get a URL to view results:

```
[INFO] Test completed successfully
[INFO] Results uploaded to Web Platform
[INFO] View results at: https://results.fluxloop.ai/run/run_20241101_143022
```

See [Viewing Results](/docs/platform/viewing-results) for details.

## Error Handling

### Graceful Failures

If an agent run fails:
- Error is captured in the result
- Test continues with next input
- Summary shows failure count

### Critical Failures

If configuration is invalid:
- Test stops immediately
- Error message shows what to fix

Example:

```bash
$ fluxloop test
[ERROR] Runner target not found: src.agent:run
[ERROR] Please check your fluxloop.yaml configuration
```

## Performance Tips

### Parallel Execution

Configure parallel execution in your config:

```yaml
test:
  parallel: 4  # Run 4 tests in parallel
```

### Batch Testing

For large test suites, consider batching:

```bash
# Test specific subset
fluxloop test --bundle bundle_batch1 --output-dir results/batch1
fluxloop test --bundle bundle_batch2 --output-dir results/batch2
```

## Best Practices

### 1. Use Multiple Iterations

Test consistency by running multiple iterations:

```bash
fluxloop test --iterations 10
```

This helps identify:
- Non-deterministic behavior
- Edge case failures
- Performance variance

### 2. Regular Scenario Testing

Pull and test against scenarios regularly:

```bash
# In CI/CD pipeline
fluxloop scenarios pull production
fluxloop test --scenario production --yes --upload
```

### 3. Automatic Upload

Results are automatically uploaded for team visibility and historical tracking.

```bash
fluxloop test
```

## Related Commands

- [`bundles`](./bundles) - Create and manage test bundles
- [`scenarios`](./scenarios) - Pull scenarios from Web Platform
- [`criteria`](./criteria) - View evaluation criteria
- [`sync`](./sync) - Sync results with Web Platform

## Next Steps

- [Basic Workflow](../workflows/basic-workflow) - End-to-end testing guide
- [Testing Best Practices](../guides/testing-best-practices) - Tips and patterns
- [Evaluation Guide](../guides/evaluation) - Understanding test results
