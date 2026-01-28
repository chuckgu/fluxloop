---
sidebar_position: 1
---

# /fluxloop:test

Run agent tests with scenarios from FluxLoop Web.

## Overview

The `/fluxloop:test` command:
1. Pulls test scenarios from FluxLoop Web (if needed)
2. Runs your instrumented agent with synthetic inputs
3. Captures traces and results
4. Uploads results to FluxLoop Web
5. Displays summary and analysis link

## Basic Usage

```bash
/fluxloop:test
```

This runs the full test suite for the current scenario.

## Options

### --scenario

Specify which scenario to test:

```bash
/fluxloop:test --scenario customer-onboarding
```

### --skip-upload

Run tests locally without uploading results:

```bash
/fluxloop:test --skip-upload
```

Useful for:
- Quick local validation
- Testing without internet connection
- Development without FluxLoop account

### --smoke

Run a quick smoke test (subset of inputs):

```bash
/fluxloop:test --smoke
```

Typically tests 5-10 inputs for rapid feedback.

### --full

Run comprehensive test with all iterations:

```bash
/fluxloop:test --full
```

### --quiet

Minimize output for CI/CD:

```bash
/fluxloop:test --quiet
```

## Prerequisites

Before running tests, ensure:

1. **Authenticated**: Run `/fluxloop:setup` first
2. **Project selected**: Current project configured
3. **Inputs available**: Scenarios pulled from Web

Check status:

```bash
/fluxloop:status
```

## How It Works

### Step 1: Pull Scenarios

If scenarios aren't already local, the command automatically pulls them:

```
🔄 Pulling test scenarios from FluxLoop Web...
✓ Pulled 50 test inputs for scenario: customer-support
```

### Step 2: Run Tests

Executes your agent with each test input:

```
🧪 Running tests...
▓▓▓▓▓▓░░░░ 25/50 (50%) - ETA: 1m 30s
```

### Step 3: Upload Results

Sends traces and metrics to FluxLoop Web:

```
📤 Uploading results to FluxLoop Web...
✓ Results uploaded successfully
```

### Step 4: Show Summary

Displays test summary and link to detailed analysis:

```
📊 Results:
- Total: 50 traces
- Success: 47 (94%)
- Failed: 3 (6%)
- Avg Duration: 2.3s

🌐 View detailed analysis:
https://alpha.app.fluxloop.ai/projects/abc123/results/xyz789
```

## Examples

### Quick Development Test

```bash
# Fast feedback during development
/fluxloop:test --smoke
```

### Pre-Commit Validation

```bash
# Full test before committing
/fluxloop:test
```

### Local Testing Only

```bash
# Test without uploading
/fluxloop:test --skip-upload
```

### Specific Scenario

```bash
# Test specific workflow
/fluxloop:test --scenario error-handling
```

## Workflow Integration

### Development Loop

```
1. Make changes to agent code
   ↓
2. Run: /fluxloop:test --smoke
   ↓
3. Review results
   ↓
4. Iterate
   ↓
5. Before commit: /fluxloop:test
```

### Before Deployment

```bash
# Comprehensive testing
/fluxloop:test --full

# Review in Web
# Check all scenarios passed
# Verify performance metrics
```

## Output Details

### Success Summary

```
📊 Test Results:
✓ Passed: 47/50 (94%)
✗ Failed: 3/50 (6%)

⚡ Performance:
- Avg Duration: 2.3s
- Max Duration: 5.1s
- Total Time: 2m 15s

🎯 Coverage:
- Personas: 5/5 tested
- Scenarios: customer-support

🔗 Details: https://alpha.app.fluxloop.ai/projects/.../results/...
```

### Failure Details

```
✗ Failed Traces (3):
1. [novice_user] "How do I reset my password?"
   Error: Timeout after 30s

2. [expert_user] "What's the API rate limit?"
   Error: Agent returned null

3. [frustrated_user] "This doesn't work!"
   Error: Exception in tool call

🔍 View full details: [link to Web]
```

## Troubleshooting

### "Scenario not found"

```bash
# List available scenarios
/fluxloop:status

# Pull specific scenario
/fluxloop:pull --scenario <name>

# Retry test
/fluxloop:test --scenario <name>
```

### "No inputs found"

Scenarios haven't been pulled yet:

```bash
# Pull from Web
/fluxloop:pull

# Then test
/fluxloop:test
```

### "Authentication error"

Re-authenticate:

```bash
# Re-authenticate
/fluxloop:setup --force-login
```

### "Agent not instrumented"

Ensure your agent function has the `@fluxloop.agent()` decorator:

```python
import fluxloop

@fluxloop.agent()
def my_agent(input: str) -> str:
    # Your logic
    return response
```

### Slow Tests

For faster iteration:

```bash
# Use smoke test
/fluxloop test --smoke

# Or reduce inputs in FluxLoop Web
```

## Advanced Usage

### Custom Configuration

Override simulation config:

```bash
# Specify custom runner
/fluxloop:test --runner custom_module:custom_function

# Increase timeout
/fluxloop:test --timeout 60
```

### Multiple Scenarios

Test all scenarios in a project:

```bash
# List scenarios
/fluxloop:status

# Test each one
/fluxloop:test --scenario scenario1
/fluxloop:test --scenario scenario2
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | Some tests failed |
| 2 | Configuration error |
| 3 | Authentication error |

## Related Commands

- [`/fluxloop:pull`](./pull) - Pull test scenarios
- [`/fluxloop:upload`](./status) - Upload results manually
- [`/fluxloop:status`](./status) - Check project status
- [`/fluxloop:criteria`](./criteria) - View success criteria

## See Also

- [Setup Guide](../getting-started/installation) - Initial configuration
- [Integration Workflow](../integration/workflow) - Full development workflow
- [CLI test command](/cli/commands/test) - Standalone CLI equivalent
