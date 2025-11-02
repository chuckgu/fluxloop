---
sidebar_position: 3
---

# Running Experiments

Run experiments from VSCode.

## Steps

1. Generate inputs
2. Click "Run Experiment"
3. View results

## Configure the Runner

Open `Projects → Configure Experiment` to edit `configs/simulation.yaml`. Set `runner` to your code:

```yaml
runner:
  target: "app.main:support_server.respond"
  working_directory: .
  # stream_output_path: "message.delta"   # optional for async generators
```

More patterns (class.method, factory, etc.): see CLI docs → `configuration/runner-targets`.
