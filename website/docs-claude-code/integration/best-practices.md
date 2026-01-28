---
sidebar_position: 2
---

# Best Practices

Tips for using FluxLoop effectively with the Agent Test Skill.

## Let the Skill Guide You

### ✅ Do This

```
"test my agent with difficult customers"
"generate more test data"
"what went wrong in the last test?"
```

### ❌ Avoid This

```
/fluxloop:synthesis --count 50  (manual, misses context)
fluxloop test --scenario x      (raw CLI, no guidance)
```

**The skill is context-aware.** It knows your state and adapts.

---

## Be Specific About Goals

### ✅ Good Requests

```
"test my order cancellation flow"
"generate edge cases for payment failures"
"run stress tests with impatient users"
```

### ❌ Vague Requests

```
"test it"
"make some data"
"run tests"
```

The more context you give, the better the results.

---

## Use Incremental Testing

### Development Loop

```
1. Make small change
2. "quick smoke test"           → 5-10 inputs, fast feedback
3. Iterate until smoke passes
4. "run full test suite"        → Complete validation
5. Commit
```

### Don't Skip Smoke Tests

```
✗ Change code → Full test (slow, frustrating)
✓ Change code → Smoke test → Full test (fast iteration)
```

---

## Ask for Analysis

After tests run, ask:

```
"why did test #3 fail?"
"what patterns do you see in the failures?"
"how can I improve my agent's responses?"
"compare this run to yesterday's"
```

The skill can provide insights, not just results.

---

## Maintain Test Data Quality

### Regenerate Periodically

```
"generate fresh test data with current personas"
```

Old test data may not cover new edge cases.

### Use Targeted Personas

```
"add a persona for users who speak broken English"
"create edge cases for timezone issues"
```

### Version Your Bundles

```
"save this as bundle v4 with tag 'pre-launch'"
```

---

## Team Collaboration

### Share Bundles

```
"use the team's latest bundle"
"what bundles are available?"
```

### Document Scenarios

In FluxLoop Web, add descriptions to scenarios so team members understand what each tests.

### Review Together

```
"show me the test results from today"
"compare my results with the team average"
```

---

## Performance Tips

### For Large Test Sets

```
"run tests in batches of 10"
"test only the payment scenarios"
```

### For Slow Agents

```
"increase timeout to 60 seconds"
"run async tests"
```

### For Quick Feedback

```
"just run 3 random tests"
"smoke test only"
```

---

## Troubleshooting

### Tests Failing Unexpectedly?

```
"show me the test configuration"
"what changed since the last successful run?"
```

### Skill Not Understanding?

Be more explicit:

```
✗ "check it"
✓ "run fluxloop tests on my agent"
```

### Need Manual Control?

Fall back to commands:

```
/fluxloop:status
/fluxloop:test --scenario specific-scenario
```

---

## Summary

| Do | Don't |
|----|----|
| Use natural language | Memorize commands |
| Be specific about goals | Make vague requests |
| Run smoke tests first | Jump to full tests |
| Ask for analysis | Just look at pass/fail |
| Regenerate test data | Use stale data forever |

---

## Next Steps

- **[Agent Test Skill](/claude-code/skills/agent-test)** ⭐ - Complete skill reference
- **[Workflow Guide](./workflow)** - Development workflow
