---
sidebar_position: 6
---

# Scenario Configuration

Configure test scenarios for your AI agent.

## Overview

Scenarios are curated test suites that define:
- Test inputs and expected behaviors
- Evaluation criteria
- Context and metadata
- Persona distributions

## Scenario Structure

### Basic Scenario

```yaml
# scenarios/my-scenario/config.yaml
scenario_id: basic-onboarding
name: "Basic Onboarding Flow"
description: "Tests for first-time user onboarding"
version: "1.0"

inputs:
  - id: input_001
    text: "How do I get started?"
    persona: novice_user
    expected_behavior:
      - "Provides clear first steps"
      - "Includes links to documentation"

  - id: input_002
    text: "What features are available?"
    persona: novice_user
    expected_behavior:
      - "Lists key features"
      - "Explains use cases"
```

### Full Scenario Configuration

```yaml
scenario_id: production-regression
name: "Production Regression Tests"
description: |
  Critical production paths that must pass before deployment.
  Covers authentication, user management, and billing flows.

version: "2.1.0"
created_at: "2024-11-01T10:00:00Z"
updated_at: "2024-11-01T14:30:00Z"
created_by: "team@company.com"

tags:
  - production
  - regression
  - critical

# Test inputs
inputs:
  - id: input_001
    text: "How do I reset my password?"
    persona: novice_user
    context:
      user_state: "logged_out"
      urgency: "high"
    expected_behavior:
      - "Provides password reset link"
      - "Explains reset process"
      - "Mentions security measures"
    weight: 1.0

  - id: input_002
    text: "What's the API rate limit for /auth/token?"
    persona: expert_user
    context:
      user_state: "authenticated"
      technical_level: "high"
    expected_behavior:
      - "States exact rate limit"
      - "Explains rate limit headers"
      - "Describes retry strategy"
    weight: 2.0  # Higher importance

# Evaluation criteria
evaluation:
  criteria:
    - id: accuracy
      name: "Response Accuracy"
      weight: 0.4
      description: "Correctness of information provided"

    - id: helpfulness
      name: "User Helpfulness"
      weight: 0.3
      description: "How well it helps the user"

    - id: safety
      name: "Safety & Compliance"
      weight: 0.3
      description: "Avoids harmful content"

  pass_threshold: 0.75  # Must score >= 0.75 to pass

# Persona distribution
personas:
  - id: novice_user
    weight: 0.40  # 40% of inputs
  - id: intermediate_user
    weight: 0.35
  - id: expert_user
    weight: 0.25

# Runtime configuration
runtime:
  iterations: 3  # Run each input 3 times
  timeout: 30  # 30 second timeout per input
  parallel: 4  # Run 4 tests in parallel

# Metadata
metadata:
  owner: "backend-team"
  reviewers:
    - "alice@company.com"
    - "bob@company.com"
  last_reviewed: "2024-11-01"
  review_frequency: "weekly"

  links:
    documentation: "https://docs.company.com/agent"
    issue_tracker: "https://github.com/company/agent/issues"
```

## Input Configuration

### Basic Input

```yaml
inputs:
  - id: input_001
    text: "How do I start?"
    persona: novice_user
```

### Input with Context

```yaml
inputs:
  - id: input_002
    text: "What's the pricing?"
    persona: potential_customer
    context:
      user_type: "enterprise"
      company_size: "500+"
      budget: "flexible"
      decision_stage: "evaluation"
```

Context helps generate more realistic agent responses.

### Input with Expected Behavior

```yaml
inputs:
  - id: input_003
    text: "How do I integrate the API?"
    persona: developer
    expected_behavior:
      - "Provides API documentation link"
      - "Shows code example"
      - "Explains authentication"
      - "Mentions rate limits"
```

Expected behaviors guide evaluation.

### Input Weighting

Assign importance to inputs:

```yaml
inputs:
  - id: critical_path
    text: "How do I purchase?"
    weight: 3.0  # 3x importance

  - id: edge_case
    text: "What if I have 10M users?"
    weight: 0.5  # Lower importance
```

### Multi-Turn Inputs

Define conversation flows:

```yaml
inputs:
  - id: conversation_001
    turns:
      - turn: 1
        text: "How do I reset password?"
        persona: novice_user

      - turn: 2
        text: "I didn't receive the email"
        persona: novice_user
        context:
          previous_action: "password_reset_sent"

      - turn: 3
        text: "Checked spam, still nothing"
        persona: novice_user
        emotional_state: "frustrated"
```

## Evaluation Configuration

### Criteria Definition

```yaml
evaluation:
  criteria:
    - id: accuracy
      name: "Factual Accuracy"
      description: "Information is correct"
      weight: 0.40
      type: "llm_judge"  # LLM evaluates

      rubric: |
        Score 1.0: All information is factually correct
        Score 0.7: Minor inaccuracies
        Score 0.4: Some incorrect information
        Score 0.0: Mostly incorrect

    - id: helpfulness
      name: "User Helpfulness"
      description: "Response helps the user"
      weight: 0.30
      type: "llm_judge"

    - id: response_time
      name: "Response Time"
      description: "Speed of response"
      weight: 0.10
      type: "metric"  # Measured automatically

      thresholds:
        excellent: 500  # < 500ms = 1.0
        good: 1000      # < 1000ms = 0.7
        acceptable: 2000 # < 2000ms = 0.4
        poor: 5000      # > 5000ms = 0.0

    - id: safety
      name: "Safety Check"
      description: "No harmful content"
      weight: 0.20
      type: "classifier"  # Binary classifier

      required: true  # Must pass to pass overall
```

### Pass Thresholds

```yaml
evaluation:
  pass_threshold: 0.75  # Overall score >= 0.75 to pass

  criteria:
    - id: accuracy
      weight: 0.5
      min_score: 0.8  # Must score >= 0.8 on accuracy

    - id: safety
      weight: 0.5
      min_score: 1.0  # Must score 1.0 (perfect) on safety
```

### Evaluation Models

Specify LLM for evaluation:

```yaml
evaluation:
  model:
    provider: "openai"
    name: "gpt-4o"
    temperature: 0.0  # Deterministic evaluation

  criteria:
    - id: accuracy
      type: "llm_judge"
```

## Persona Distribution

### Weighted Personas

```yaml
personas:
  - id: novice_user
    weight: 0.50  # 50% of inputs

  - id: intermediate_user
    weight: 0.30  # 30% of inputs

  - id: expert_user
    weight: 0.20  # 20% of inputs
```

### Conditional Personas

Use different personas based on context:

```yaml
personas:
  onboarding_phase:
    - id: novice_user
      weight: 0.80
    - id: intermediate_user
      weight: 0.20

  power_user_phase:
    - id: expert_user
      weight: 0.70
    - id: intermediate_user
      weight: 0.30
```

## Runtime Configuration

### Execution Settings

```yaml
runtime:
  # Iterations per input
  iterations: 3

  # Timeout per input (seconds)
  timeout: 30

  # Parallel execution
  parallel: 4

  # Retry on failure
  retry:
    enabled: true
    max_attempts: 3
    backoff: "exponential"

  # Resource limits
  limits:
    max_memory: "1GB"
    max_cpu: "2"
```

### Environment Variables

```yaml
runtime:
  environment:
    AGENT_MODE: "production"
    LOG_LEVEL: "info"
    API_TIMEOUT: "30"
```

## Scenario Variants

### Base Scenario

```yaml
# scenarios/base/config.yaml
scenario_id: base-tests
name: "Base Test Suite"

inputs:
  - id: input_001
    text: "How do I start?"
```

### Scenario Variants

```yaml
# scenarios/mobile/config.yaml
scenario_id: mobile-tests
name: "Mobile Test Suite"
extends: base-tests  # Inherit from base

# Override persona
personas:
  - id: mobile_user
    weight: 1.0

# Add mobile-specific inputs
inputs:
  - id: mobile_001
    text: "quick q: pricing?"
    persona: mobile_user
```

## Scenario Templates

### Regression Template

```yaml
scenario_id: regression-template
name: "Regression Test Template"
type: regression

evaluation:
  criteria:
    - id: no_regressions
      type: "comparison"
      compare_with: "baseline"
      threshold: 0.95  # Must be >= 95% as good as baseline

  baseline:
    run_id: "run_20241001_100000"  # Compare against this run
```

### Performance Template

```yaml
scenario_id: performance-template
name: "Performance Test Template"
type: performance

runtime:
  iterations: 100  # Many iterations for statistics
  parallel: 10

evaluation:
  criteria:
    - id: latency
      type: "metric"
      thresholds:
        p50: 500   # 50th percentile < 500ms
        p95: 1000  # 95th percentile < 1000ms
        p99: 2000  # 99th percentile < 2000ms
```

### Smoke Test Template

```yaml
scenario_id: smoke-template
name: "Smoke Test Template"
type: smoke

# Quick, critical paths only
inputs:
  - id: health_check
    text: "Are you working?"
    expected_behavior:
      - "Responds within 1 second"
      - "Returns success status"

runtime:
  iterations: 1
  timeout: 5
  fail_fast: true  # Stop on first failure
```

## Best Practices

### 1. Version Scenarios

```yaml
scenario_id: production-regression
version: "2.1.0"

changelog:
  - version: "2.1.0"
    date: "2024-11-01"
    changes:
      - "Added API authentication tests"
      - "Updated evaluation criteria"

  - version: "2.0.0"
    date: "2024-10-15"
    changes:
      - "Major refactor: new input structure"
```

### 2. Document Expected Behaviors

```yaml
inputs:
  - id: password_reset
    text: "How do I reset my password?"
    expected_behavior:
      - "Provides password reset link"  # ✅ Specific
      - "Responds helpfully"  # ❌ Vague
```

### 3. Use Meaningful IDs

```yaml
# ✅ Good
inputs:
  - id: auth_password_reset
  - id: auth_login_failed
  - id: auth_logout

# ❌ Bad
inputs:
  - id: input_001
  - id: test_2
  - id: scenario_1_input_3
```

### 4. Regular Reviews

```yaml
metadata:
  last_reviewed: "2024-11-01"
  review_frequency: "monthly"
  next_review: "2024-12-01"
```

## Related

- [Scenarios Command](../commands/scenarios) - Manage scenarios
- [Test Command](../commands/test) - Run scenario tests
- [Sync Command](/cli/commands/sync) - Pull scenarios from Web Platform
- [Team Collaboration](../workflows/team-collaboration) - Share scenarios

## Examples

See [FluxLoop Examples](https://github.com/chuckgu/fluxloop/tree/main/examples/scenarios) for:
- Complete scenario examples
- Domain-specific scenarios
- Evaluation configurations
- Best practices
