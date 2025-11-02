---
title: Runner Targets (simulation.yaml)
sidebar_position: 20
---

## Runner Integration Patterns

You connect your code to FluxLoop by configuring the `runner` in `configs/simulation.yaml`. These patterns are supported:

1) Module + function (sync/async)
```yaml
runner:
  module_path: "app.agent"
  function_name: "run"
  working_directory: .
```
or
```yaml
runner:
  target: "app.agent:run"
  working_directory: .
```

2) Class.method (zero-arg constructor)
```yaml
runner:
  target: "app.agent:Handler.handle"
```

3) Module-scoped instance method (bound)
```yaml
runner:
  target: "app.main:support_server.respond"
```

4) Class.method with factory (constructor needs dependencies)
```yaml
runner:
  target: "app.main:CustomerSupportServer.respond"
  factory: "app.main:get_server"       # get_server() -> CustomerSupportServer
  factory_kwargs: {}                     # optional
```

5) Async generator targets (streamed responses)
```yaml
runner:
  target: "app.main:support_server.respond"
  stream_output_path: "message.delta"   # default
```
FluxLoop consumes the async stream and joins text found at `stream_output_path` into a single result.

6) Async iterable returned from coroutine
If your function returns an async generator/iterable, it will also be consumed with the same `stream_output_path`.

## Argument Replay (optional)

Replay recorded kwargs and override only the runtime input.
```yaml
replay_args:
  enabled: true
  recording_file: recordings/args_recording.jsonl
  # override_param_path: "item.content.0.text"   # if you need to replace nested text
```

## Tips
- Use `working_directory` if the module is not importable from the current CWD.
- Use `factory` when your class requires constructor args or external dependencies.
- Default `stream_output_path` is `message.delta`. Adjust if your streamed event shape differs.


