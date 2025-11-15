---
sidebar_position: 4
---

# Multi-Turn Workflow

Run multi-turn conversational experiments with AI-supervised dialogues.

## Overview

Multi-turn mode extends single-input experiments into dynamic conversations. Instead of running one agent call per input, FluxLoop:

1. Feeds the initial user message to your agent
2. Captures the agent's response
3. Consults an AI supervisor to decide if the conversation is complete
4. Generates the next user message (if continuing) based on persona and service context
5. Repeats until natural completion or maximum turns

This enables realistic testing of conversational agents without manual scripting.

## Quick Start

### 1. Enable Multi-Turn in Configuration

Edit `configs/simulation.yaml`:

```yaml
multi_turn:
  enabled: true
  max_turns: 12
  auto_approve_tools: true
  
  supervisor:
    provider: openai
    model: gpt-5-mini
    temperature: 0.2
```

### 2. Set Service Context

Add service description to `configs/project.yaml`:

```yaml
metadata:
  team: development
  environment: local
  service_context: >
    Customer support assistant for SWISS Airlines.
    Handles flight changes, cancellations, seat upgrades, and baggage inquiries.
```

### 3. Ensure Input Has Persona

Your `inputs/generated.yaml` should include persona metadata:

```yaml
inputs:
  - input: "Hi, I need to change my flight"
    metadata:
      persona: business_traveler
      persona_description: "Frequent business traveler who values efficiency"
```

### 4. Run Experiment

```bash
fluxloop run experiment
```

FluxLoop will now run multi-turn conversations automatically.

## How It Works

### Conversation Flow

```
[Initial Input] → [Agent Response] → [Supervisor Decision]
                                           ↓
                        ┌──────────────────┴──────────────────┐
                        ↓                                     ↓
               [Continue: Generate Next User Msg]    [Terminate: Save & Exit]
                        ↓
               [Agent Response] → [Supervisor Decision] → ...
```

### Supervisor Decision Format

The supervisor LLM returns JSON:

```json
{
  "decision": "continue",
  "next_user_message": "Thanks! Can you also help me upgrade my seat?",
  "termination_reason": null,
  "closing_user_message": null
}
```

Or when complete:

```json
{
  "decision": "terminate",
  "next_user_message": null,
  "termination_reason": "user_satisfied",
  "closing_user_message": "Perfect, thank you for your help!"
}
```

## Configuration Reference

### Multi-Turn Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable multi-turn mode |
| `max_turns` | integer | `8` | Maximum conversation turns |
| `auto_approve_tools` | boolean | `true` | Auto-approve agent tool calls |
| `persona_override` | string | `null` | Override persona from input |

### Supervisor Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `provider` | string | `"openai"` | LLM provider (openai, mock) |
| `model` | string | `"gpt-5-mini"` | Model for supervision |
| `temperature` | float | `0.2` | Sampling temperature |
| `api_key` | string | `null` | API key override (uses env by default) |
| `system_prompt` | string | `null` | Custom supervisor prompt |

## CLI Overrides

Override multi-turn settings from the command line:

```bash
# Enable multi-turn with custom settings
fluxloop run experiment \
  --multi-turn \
  --max-turns 15 \
  --auto-approve \
  --supervisor-model gpt-4o-mini

# Disable multi-turn for single-turn testing
fluxloop run experiment --no-multi-turn

# Override persona
fluxloop run experiment --multi-turn --persona expert_user
```

## Advanced Usage

### Custom Supervisor Prompt

Provide a custom system prompt for the supervisor:

```yaml
multi_turn:
  supervisor:
    system_prompt: |
      You supervise a technical support bot for SaaS products.
      Generate concise, technical user messages.
      End the conversation when the issue is resolved or escalated.
```

### Mock Supervisor for Testing

Use deterministic mock responses during development:

```yaml
multi_turn:
  supervisor:
    provider: mock
    metadata:
      mock_decision: terminate
      mock_reason: "Mock conversation complete"
```

The mock provider can operate in two modes:

**Simple fallback mode** (no scripted questions):
- Returns `terminate` by default with `mock_reason` and `mock_closing` from metadata
- Set `mock_decision: continue` + `mock_next_user_message` for simple test loops

**Scripted playback mode** (with question list):
```yaml
multi_turn:
  supervisor:
    provider: mock
    metadata:
      scripted_questions:
        - "Hi there, what time is my flight?"
        - "Am I allowed to update my flight to something sooner?"
        - "Update my flight to sometime next week then"
        - "What about lodging and transportation?"
        - "Yeah I think I'd like an affordable hotel for my week-long stay."
      mock_reason: "script_complete"
      mock_closing: "Thanks for your help. I have no further questions."
```

In scripted mode, the supervisor replays questions in order and terminates when the list is exhausted. This is ideal for regression testing, demos, and reproducible benchmarks.

### Access Conversation State in Agent

If your agent accepts `conversation_state`, you can inspect the full dialogue:

```python
@fluxloop.agent()
def my_agent(
    input_text: str,
    conversation_state: dict | None = None,
    auto_approve: bool = False,
) -> str:
    if conversation_state:
        turn_count = len(conversation_state.get("turns", []))
        print(f"Processing turn {turn_count}")
    
    # Your agent logic...
    return response
```

## Output Structure

Multi-turn runs produce enriched trace entries:

```json
{
  "trace_id": "...",
  "iteration": 0,
  "persona": "business_traveler",
  "input": "Hi, I need to change my flight",
  "output": "Perfect, thank you!",
  "duration_ms": 8432,
  "success": true,
  "multi_turn": {
    "enabled": true,
    "turn_count": 4,
    "termination_reason": "user_satisfied"
  },
  "conversation_state": {
    "turns": [
      {"role": "user", "content": "Hi, I need to change my flight"},
      {"role": "assistant", "content": "I can help with that..."},
      {"role": "user", "content": "Can you also upgrade my seat?"},
      {"role": "assistant", "content": "Sure, let me check availability..."},
      ...
    ],
    "metadata": { ... },
    "context": {
      "persona": "business_traveler",
      "service_context": "SWISS Airlines customer support..."
    }
  }
}
```

## Best Practices

### 1. Set Realistic Max Turns
- Customer support: 8-12 turns
- Technical troubleshooting: 10-15 turns
- Simple Q&A: 3-5 turns

### 2. Use Lower Temperature for Reproducibility
- `0.0-0.3`: More consistent, predictable conversations
- `0.4-0.7`: Balanced variety and coherence
- `0.8-1.0`: Higher variety, less reproducibility

### 3. Define Clear Service Context
A well-defined service context helps the supervisor generate realistic user messages:

```yaml
metadata:
  service_context: |
    E-commerce customer support chatbot.
    Handles: order tracking, returns, product questions, account issues.
    Cannot: process payments, change passwords, access private data.
```

### 4. Monitor Costs
Multi-turn mode makes additional LLM calls (supervisor decisions). Use:
- Mock provider for development
- Lower `max_turns` for cost control
- Track supervisor usage in traces

## Troubleshooting

### Conversations End Too Early
- Increase `max_turns`
- Review `service_context` – ensure it's clear and detailed
- Check supervisor temperature (try 0.3-0.5 for more variety)

### Conversations Don't Terminate
- Lower `max_turns` as safety limit
- Review supervisor prompt – ensure termination criteria are clear
- Check that agent responses indicate task completion

### Supervisor API Errors
- Verify API key is set (`OPENAI_API_KEY` env or `supervisor.api_key`)
- Check model name is valid for your provider
- Review error logs in trace output

## Next Steps

- [Runner Targets](./runner-targets) – detailed runner integration patterns
- [Run Command](../commands/run) – command-line reference
- [Project Configuration](../configuration/project-config) – metadata setup

