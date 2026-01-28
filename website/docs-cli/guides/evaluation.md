---
sidebar_position: 3
---

# Evaluation Guide

Understanding and interpreting FluxLoop test evaluation results.

## Overview

FluxLoop evaluates agent test results using:
- Automated criteria scoring
- LLM-based evaluation
- Performance metrics
- Behavioral analysis

## Evaluation Process

### 1. Run Tests

```bash
fluxloop test --scenario production --upload
```

### 2. Automatic Evaluation

Results are evaluated against criteria:

```yaml
# Evaluation criteria
criteria:
  - accuracy: "Factual correctness"
  - helpfulness: "User helpfulness"
  - safety: "No harmful content"
```

### 3. View Results

```bash
# View locally
fluxloop results show

# View on Web Platform
# https://results.fluxloop.ai/run/run_123
```

## Evaluation Criteria

### LLM Judge

LLM evaluates subjective qualities:

```yaml
criteria:
  - id: accuracy
    type: "llm_judge"
    weight: 0.4
    rubric: |
      1.0: Completely accurate
      0.7: Mostly accurate, minor errors
      0.4: Significant inaccuracies
      0.0: Incorrect information
```

### Metrics

Automated performance measurements:

```yaml
criteria:
  - id: response_time
    type: "metric"
    weight: 0.2
    thresholds:
      excellent: 500   # < 500ms
      good: 1000       # < 1s
      acceptable: 2000 # < 2s
```

### Classifiers

Binary pass/fail checks:

```yaml
criteria:
  - id: safety
    type: "classifier"
    weight: 0.4
    required: true  # Must pass
```

## Scoring

### Individual Scores

Each criterion scored 0.0 - 1.0:

```json
{
  "input_id": "input_001",
  "scores": {
    "accuracy": 0.9,
    "helpfulness": 0.8,
    "safety": 1.0
  }
}
```

### Overall Score

Weighted average:

```
overall_score = (accuracy * 0.4) + (helpfulness * 0.4) + (safety * 0.2)
              = (0.9 * 0.4) + (0.8 * 0.4) + (1.0 * 0.2)
              = 0.88
```

### Pass/Fail

Based on threshold:

```yaml
evaluation:
  pass_threshold: 0.75

# Score 0.88 >= 0.75 → PASS ✅
```

## Interpreting Results

### High Score (0.9+)

✅ Excellent performance
- Agent meets or exceeds expectations
- Ready for production

### Good Score (0.75-0.9)

✅ Good performance
- Acceptable for production
- Minor improvements possible

### Marginal Score (0.6-0.75)

⚠️ Needs improvement
- Some issues present
- Review failures
- Iterate on prompts

### Poor Score (< 0.6)

❌ Significant issues
- Not ready for production
- Major revisions needed

## Common Patterns

### High Accuracy, Low Helpfulness

```
accuracy: 0.9
helpfulness: 0.5
```

Agent provides correct but unhelpful responses.

**Fix**: Improve response formatting, add examples.

### High Helpfulness, Low Accuracy

```
accuracy: 0.6
helpfulness: 0.9
```

Agent is friendly but provides wrong information.

**Fix**: Improve knowledge base, add fact-checking.

### Inconsistent Scores

```
input_001: 0.9
input_002: 0.4
input_003: 0.9
```

Agent handles some cases well, others poorly.

**Fix**: Identify failure patterns, add specific training.

## Best Practices

### 1. Define Clear Criteria

```yaml
✅ Good:
  - id: accuracy
    description: "Provides factually correct information"

❌ Vague:
  - id: quality
    description: "Good response"
```

### 2. Use Multiple Criteria

Don't rely on single metric:

```yaml
criteria:
  - accuracy
  - helpfulness
  - safety
  - response_time
```

### 3. Regular Evaluation

Evaluate frequently:

```bash
# Daily in CI
fluxloop test --scenario regression --upload
```

### 4. Track Trends

Compare results over time:

```bash
fluxloop results compare --baseline last-week
```

## Related

- [Criteria Command](../commands/criteria) - View evaluation criteria
- [Test Command](../commands/test) - Run evaluated tests
- [Viewing Results](/platform/viewing-results) - Web Platform analysis

## Next Steps

- Define evaluation criteria for your agent
- Run tests and review scores
- Iterate based on results
- Set up continuous evaluation
