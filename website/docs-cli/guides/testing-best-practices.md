---
sidebar_position: 4
---

# Testing Best Practices

Best practices for testing AI agents with FluxLoop.

## Core Principles

### 1. Test Early, Test Often

Start testing from day one:

```bash
# Don't wait until "ready"
fluxloop test
```

Benefits:
- Catch issues early
- Build confidence incrementally
- Establish baseline performance

### 2. Use Realistic Inputs

Test with realistic, diverse inputs:

```bash
✅ fluxloop inputs generate --persona novice_user,expert_user
❌ Manual inputs: ["test1", "test2", "test3"]
```

### 3. Automate Everything

Integrate testing into your workflow:

```bash
# CI/CD pipeline
fluxloop test --yes --no-skip-upload
```

### 4. Track Changes Over Time

Compare results across versions:

```bash
fluxloop results compare --baseline production
```

## Input Design

### Diverse Personas

Cover different user types:

```yaml
personas:
  - novice_user       # 40%
  - intermediate_user # 35%
  - expert_user       # 25%
```

### Edge Cases

Include unusual scenarios:

```yaml
inputs:
  - ""                          # Empty input
  - "A" * 1000                  # Very long input
  - "!@#$%^&*()"               # Special characters
  - "混合语言 mixed language"  # Mixed languages
```

### Realistic Distribution

Match production traffic:

```bash
# Analyze production logs
analyze_logs.py --output distribution.yaml

# Generate matching test inputs
fluxloop inputs generate --distribution distribution.yaml
```

## Test Coverage

### Feature Coverage

Test all major features:

```yaml
scenarios:
  - authentication
  - user_management
  - billing
  - api_integration
  - error_handling
```

### Behavioral Coverage

Test different behaviors:

```yaml
behaviors:
  - happy_path          # Normal usage
  - error_conditions    # Failures
  - edge_cases          # Unusual inputs
  - multi_turn          # Conversations
  - time_sensitive      # Timeouts, etc.
```

### Persona Coverage

Test all user types:

```yaml
personas:
  - novice_user
  - expert_user
  - frustrated_user
  - mobile_user
  - non_native_english
```

## Test Organization

### Scenario Structure

```
scenarios/
├── smoke/            # Quick sanity checks
├── regression/       # Core functionality
├── performance/      # Speed tests
└── edge-cases/       # Unusual scenarios
```

### Naming Conventions

```bash
✅ auth_password_reset_flow
✅ billing_subscription_upgrade
✅ api_rate_limit_exceeded

❌ test1
❌ scenario_final_v2
❌ my_test
```

## Iteration Strategy

### Multiple Iterations

Run each input multiple times:

```bash
fluxloop test --iterations 10
```

Why:
- Measure consistency
- Account for LLM randomness
- Statistical significance

### Recommended Iterations

| Test Type | Iterations | Reason |
|-----------|------------|--------|
| Smoke | 1 | Quick feedback |
| Regression | 3-5 | Balance speed/confidence |
| Performance | 10-20 | Statistical validity |
| Critical Path | 10-20 | High confidence |

## Evaluation Criteria

### Define Clear Criteria

```yaml
criteria:
  - id: accuracy
    description: "Provides factually correct information"
    weight: 0.4

  - id: helpfulness
    description: "Helps user achieve their goal"
    weight: 0.3

  - id: safety
    description: "No harmful or inappropriate content"
    weight: 0.3
```

### Set Appropriate Thresholds

```yaml
evaluation:
  pass_threshold: 0.75  # Adjust based on use case

  # Critical features: Higher threshold
  critical:
    pass_threshold: 0.90

  # Experimental features: Lower threshold
  experimental:
    pass_threshold: 0.60
```

## CI/CD Integration

### Pre-Deployment Testing

```yaml
# .github/workflows/deploy.yml
- name: Run Tests
  run: fluxloop test --scenario production --yes

- name: Check Pass Rate
  run: fluxloop results check --fail-on-regression

- name: Deploy
  if: success()
  run: deploy.sh
```

### Continuous Testing

```yaml
# Daily regression tests
schedule:
  - cron: '0 2 * * *'
```

### Branch Testing

```yaml
# Test on every PR
on: [pull_request]

steps:
  - run: fluxloop test --scenario regression --no-skip-upload
```

## Performance Testing

### Response Time

Monitor latency:

```yaml
criteria:
  - id: response_time
    thresholds:
      excellent: 500
      good: 1000
      acceptable: 2000
```

### Throughput

Test concurrent requests:

```bash
fluxloop test --parallel 10 --iterations 100
```

### Resource Usage

Monitor memory and CPU:

```yaml
runtime:
  limits:
    max_memory: "1GB"
    max_cpu: "2"
```

## Debugging Failures

### Review Failed Tests

```bash
# List failures
fluxloop results list --status failed

# View specific failure
fluxloop results show input_001
```

### Reproduce Locally

```bash
# Reproduce specific failure
fluxloop test --input input_001 --iterations 1
```

### Analyze Patterns

```bash
# Group failures by type
fluxloop results analyze --group-by error_type
```

## Common Pitfalls

### ❌ Testing Too Late

Don't wait until "done":

```
❌ Build agent → Deploy → Test
✅ Test → Build → Test → Deploy → Test
```

### ❌ Insufficient Coverage

Don't test only happy paths:

```yaml
❌ Only novice_user persona
✅ Multiple personas + edge cases
```

### ❌ Ignoring Failures

Don't skip failures:

```
❌ "It's just one failure, ship it"
✅ Investigate all failures
```

### ❌ Manual Testing Only

Don't rely on manual testing:

```
❌ Manually test 10 cases
✅ Automated test 1000 cases
```

### ❌ No Baseline

Don't test without comparison:

```
❌ Test once, no context
✅ Compare to baseline, track trends
```

## Optimization

### Parallel Execution

Speed up tests:

```bash
fluxloop test --parallel 4
```

### Selective Testing

Test relevant scenarios:

```bash
# Changed authentication code?
fluxloop test --scenario auth --no-skip-upload

# Changed everything?
fluxloop test --all-scenarios --no-skip-upload
```

### Caching

Cache unchanged results:

```yaml
runtime:
  cache:
    enabled: true
    ttl: 3600  # 1 hour
```

## Monitoring

### Set Up Alerts

```yaml
# Alert on failures
alerts:
  - type: failure_rate
    threshold: 0.10  # Alert if > 10% fail
    channel: slack

  - type: score_drop
    threshold: 0.05  # Alert if score drops > 5%
    channel: email
```

### Track Metrics

Monitor key metrics:

```yaml
metrics:
  - pass_rate
  - avg_score
  - response_time_p95
  - failure_count
```

### Review Regularly

Schedule reviews:

```
Weekly: Review test results
Monthly: Update test scenarios
Quarterly: Revise evaluation criteria
```

## Team Practices

### Shared Scenarios

Use team scenarios:

```bash
# Pull team scenarios
fluxloop sync pull

# Test locally
fluxloop test --scenario team-regression
```

### Code Reviews

Include test results in PRs:

```markdown
## Test Results

- Scenario: auth-flows
- Pass Rate: 98% (49/50)
- Avg Score: 0.89
- Link: https://results.fluxloop.ai/run/run_123
```

### Documentation

Document test strategy:

```markdown
# Testing Strategy

## Scenarios
- smoke: Quick health checks
- regression: Core functionality
- performance: Speed tests

## Frequency
- smoke: Every commit
- regression: Every PR
- performance: Daily

## Criteria
- accuracy: 0.4 weight
- helpfulness: 0.3 weight
- safety: 0.3 weight
```

## Related

- [Basic Workflow](../workflows/basic-workflow) - End-to-end testing
- [Evaluation Guide](./evaluation) - Understanding results
- [CI/CD Integration](../workflows/ci-cd-integration) - Automation

## Examples

See [FluxLoop Examples](https://github.com/chuckgu/fluxloop/tree/main/examples/best-practices) for complete testing workflows.
