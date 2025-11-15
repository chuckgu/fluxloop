---
sidebar_position: 3
---

# Simulation Configuration

Configure `configs/simulation.yaml` to control how experiments execute.

## Example

```yaml
name: my_experiment
iterations: 10

runner:
  target: "examples.agent:run"
  working_directory: .
  timeout_seconds: 120

multi_turn:
  enabled: false
  max_turns: 8
  auto_approve_tools: true
  supervisor:
    provider: openai
    model: gpt-5-mini
    temperature: 0.2

output_directory: experiments
save_traces: true
```

## Multi-Turn Conversations

Enable multi-turn mode to automatically extend single-input experiments into dynamic conversations. When `multi_turn.enabled` is `true`, FluxLoop:

1. Starts with the initial user message from your input file
2. Calls your agent to generate a response
3. Consults an AI supervisor to decide if the conversation should continue
4. If continuing, the supervisor generates the next user message based on:
   - Conversation history
   - Persona characteristics (from input metadata)
   - Service context (from project.yaml)
5. Repeats until the supervisor detects natural completion or `max_turns` is reached

### Configuration Options

```yaml
multi_turn:
  enabled: true                    # Enable multi-turn mode
  max_turns: 12                    # Maximum conversation turns
  auto_approve_tools: true         # Auto-approve tool calls (no human prompt)
  persona_override: null           # Override persona from input (optional)
  
  supervisor:
    provider: openai               # LLM provider (openai, mock)
    model: gpt-5-mini             # Model for conversation supervision
    temperature: 0.2               # Lower = more deterministic
    api_key: null                  # Override API key (defaults to env)
    system_prompt: null            # Custom supervisor prompt (optional)
```

### CLI Overrides

Override multi-turn settings from the command line:

```bash
fluxloop run experiment --multi-turn --max-turns 15 --auto-approve
```

Available flags:
- `--multi-turn` / `--no-multi-turn` – enable/disable multi-turn mode
- `--max-turns N` – set maximum conversation turns
- `--auto-approve` / `--no-auto-approve` – control tool approval
- `--persona NAME` – override persona from input metadata
- `--supervisor-model MODEL` – change supervisor LLM model
- `--supervisor-temperature TEMP` – adjust supervisor creativity

### Service Context

The supervisor uses service context from `configs/project.yaml`:

```yaml
metadata:
  service_context: >
    SWISS Airlines customer support – handles flight changes, 
    cancellations, seat upgrades, and baggage inquiries
```

This helps the supervisor generate realistic user messages that match your domain.

## Next Steps

- [Runner Targets](./runner-targets) – detailed runner integration patterns
- [Run Command](../commands/run) – command-line reference
- [Multi-Turn Tutorial](../workflows/multi-turn-workflow) – end-to-end example
