---
sidebar_position: 2
---

# Input Configuration

Configure `configs/input.yaml` for input generation.

## Example

```yaml
personas:
  - name: user
    description: Regular user

base_inputs:
  - input: "Hello"
    persona: user

input_generation:
  mode: llm
  llm:
    provider: openai
    model: gpt-4o-mini
```

## Next Steps

- [Simulation Config](./simulation-config)
