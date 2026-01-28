---
sidebar_position: 1
---

# Development Workflow

Integrate FluxLoop into your development workflow using the Agent Test Skill.

## Recommended: Skill-Driven Workflow

### Daily Development

```
1. Write code
2. Say: "test my agent with a quick smoke test"
3. Review results
4. Iterate
```

### Before Commit

```
"run full tests on my agent"
```

### Before Deployment

```
"test my agent with stress scenarios"
```

---

## Example Development Session

```
You: [Make changes to agent code]

You: "quick test"

Claude: Running smoke test...
✓ 5/5 passed

You: [Make more changes]

You: "test with edge cases"

Claude: I'll generate edge case scenarios...
[Creates personas, synthesizes inputs]
Running tests...

📊 Results: 18/20 passed
⚠️ 2 failures on timeout scenarios

Would you like me to show the failures?

You: "yes, and suggest fixes"

Claude: Here are the failures:
1. [impatient_user] - Response took 5.2s (limit: 3s)
2. [rapid_fire_user] - Rate limited

Suggestions:
- Add response caching for common queries
- Implement graceful degradation for rate limits

You: [Implement fixes]

You: "test again"

Claude: Running tests...
✓ 20/20 passed!

Ready to commit?
```

---

## Manual Workflow (Alternative)

If you prefer explicit commands:

```bash
# During development
/fluxloop:test --smoke

# Before commit  
/fluxloop:test

# Full test with all scenarios
/fluxloop:test --full
```

---

## Team Collaboration

### Shared Testing

1. Share project in FluxLoop Web
2. Team members install the plugin
3. Everyone says: "set up fluxloop" → selects shared project
4. All test against same scenarios
5. Compare results in Web dashboard

### Consistent Personas

Use the same generated personas across team:

```
"use the existing test data from bundle v3"
```

---

## CI/CD Integration

For automated pipelines, use the CLI directly:

```yaml
# GitHub Actions
- name: Run FluxLoop Tests
  run: |
    fluxloop test --scenario main
```

The plugin is for development; CLI is for automation.

---

## Next Steps

- **[Agent Test Skill](/claude-code/skills/agent-test)** ⭐ - Full skill guide
- **[Best Practices](./best-practices)** - Tips for effective testing
