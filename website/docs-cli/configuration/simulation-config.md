---
sidebar_position: 3
---

# Simulation Configuration

Configure `configs/simulation.yaml`.

## Example

```yaml
runner:
  target: "examples.agent:run"
  iterations: 10

output:
  directory: "experiments"
```

## Next Steps

- [Runner Targets](./runner-targets) – detailed runner integration patterns
- [Run Command](../commands/run)
