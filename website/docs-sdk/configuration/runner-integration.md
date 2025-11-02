---
title: Runner Integration
sidebar_position: 15
---

The SDK works with the CLI runner by instrumenting your functions/classes. To connect code to simulations, set the `runner` in `configs/simulation.yaml`.

Common patterns (details in CLI docs → configuration/runner-targets):

- Module + function: `runner.target: "app.agent:run"`
- Class.method (zero-arg ctor): `runner.target: "app.agent:Handler.handle"`
- Module-scoped instance method: `runner.target: "app.main:support_server.respond"`
- Factory-backed class.method: add `runner.factory` (returns instance)
- Async generators: CLI consumes streamed events via `runner.stream_output_path` (default `message.delta`).

Recording/replay can be combined using `replay_args` for complex kwargs.


