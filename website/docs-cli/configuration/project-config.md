---
sidebar_position: 1
---

# Project Configuration

Configure `configs/project.yaml`.

## Example

```yaml
project:
  name: my-agent
  version: "1.0.0"
  description: "My AI agent"

collector:
  enabled: false
  url: "http://localhost:8000"
```

## Fields

- `project.name`: Project identifier
- `project.version`: Project version
- `project.description`: Description
- `collector.enabled`: Enable remote collector
- `collector.url`: Collector URL

## Next Steps

- [Input Config](./input-config)
- [Simulation Config](./simulation-config)
