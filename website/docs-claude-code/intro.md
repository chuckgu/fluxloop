---
sidebar_position: 1
slug: /
---

# FluxLoop for Claude Code

Test AI agents directly from your IDE. **Just talk naturally—FluxLoop handles the rest.**

---

## ⭐ The Core: Agent Test Skill

**Forget commands. Just ask Claude.**

```
"test my agent"
"generate test data"
"run a simulation"
"set up fluxloop"
```

The **Agent Test Skill** automatically:
- ✅ Checks your setup state
- ✅ Guides you through installation
- ✅ Generates test data and personas
- ✅ Runs tests against your agent
- ✅ Uploads results to the cloud
- ✅ Shows you what to fix

**No commands to memorize. No manual steps.**

---

## Quick Start

### 1. Install the Plugin

```
/plugin install Fluxloop-AI/fluxloop-claude-plugin
```

### 2. Just Talk

```
You: "I want to test my customer support agent"
```

That's it. The skill takes over and guides you through everything.

---

## How the Skill Works

### Context-First Workflow

```
You: "test my agent"
      ↓
[Skill checks your state]
      ↓
Claude: "Here's your current setup:
         - CLI: ✓ Installed
         - Auth: ✓ Logged in
         - Project: customer-support
         - Bundle: v3 (50 inputs)
         
         Would you like to run tests now?"
      ↓
You: "yes"
      ↓
[Skill runs tests, shows results]
```

**You're always in control.** Nothing runs without your approval.

### Auto-Activation Keywords

The skill activates when you mention:

| What You Say | What Happens |
|--------------|--------------|
| "test my agent" | Run tests |
| "generate test data" | Create synthetic inputs |
| "run simulation" | Execute agent simulation |
| "set up fluxloop" | Full installation guide |
| "evaluate responses" | Analyze agent quality |

---

## Example Conversation

```
You: "test my chatbot with difficult customers"

Claude: I'll help you test your agent.

📊 Current State:
- Project: customer-support
- Scenario: support-bot  
- Available bundles:
  1. v3 (stress-test, 50 inputs)
  2. v2 (basic, 10 inputs)

Which bundle would you like to use, or should I generate new test data 
with difficult customer personas?

You: "generate new with difficult customers"

Claude: Creating personas focused on difficult customers...

[Executes: fluxloop personas suggest]

✓ Generated 5 personas:
- angry_customer
- confused_user
- demanding_professional
- impatient_caller
- skeptical_buyer

Now synthesizing test inputs...

[Executes: fluxloop inputs synthesize]

✓ 30 test inputs created!
✓ Published as bundle v4

Running tests...

[Executes: fluxloop sync pull + fluxloop test]

📊 Results: 25/30 passed (83%)
⚠️ 5 failures detected

Would you like me to analyze the failures?
```

---

## Why Skill > Commands?

| Approach | Experience |
|----------|------------|
| **Skill** | "test my agent" → Everything automatic |
| Commands | `/fluxloop:pull` → `/fluxloop:test` → manual steps |

The skill is:
- **Smarter**: Knows your context, adapts to your state
- **Safer**: Always asks before executing
- **Simpler**: No syntax to remember

---

## Slash Commands (Manual Alternative)

For when you need direct control:

| Command | Description |
|---------|-------------|
| `/fluxloop:setup` | First-time setup |
| `/fluxloop:test` | Run tests |
| `/fluxloop:smoke` | Quick smoke test |
| `/fluxloop:pull` | Pull test data |
| `/fluxloop:status` | Check status |

> 💡 **Recommendation**: Use natural language instead. The skill handles edge cases automatically.

---

## Requirements

- **FluxLoop CLI**: `pip install fluxloop-cli`
- **FluxLoop Account**: [fluxloop.app](https://fluxloop.app)

> 💡 **Tip**: Just say "set up fluxloop" and the skill guides you through everything!

---

## Architecture

```
┌─────────────────────────────────────┐
│  You: "test my agent"               │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  Agent Test Skill                   │
│  (Context-aware, guides workflow)   │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  FluxLoop CLI                       │
│  (Executes commands)                │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  FluxLoop Web                       │
│  (Cloud storage & analysis)         │
└─────────────────────────────────────┘
```

---

## Best Practices

### Let the Skill Guide You

```
Good: "I want to test edge cases"
Less helpful: "/fluxloop:synthesis" (manual)
```

### Be Specific About Goals

```
Good: "test my order cancellation flow with angry customers"
Less helpful: "test it"
```

### Ask for Analysis

```
"Why did these tests fail?"
"What patterns do you see?"
"How can I improve my agent?"
```

---

## Troubleshooting

### Skill Not Activating?

Include activation keywords:

```
✗ "check this"
✓ "test this agent"
```

### Need Manual Control?

Use slash commands:

```
/fluxloop:status
/fluxloop:test --smoke
```

---

## What's Next?

- **[Agent Test Skill](/claude-code/skills/agent-test)** ⭐ - Full skill documentation
- **[Commands Reference](/claude-code/commands/test)** - Manual commands
- **[Installation](/claude-code/getting-started/installation)** - Setup details
- **[FluxLoop Web](https://fluxloop.app)** - Cloud dashboard

---

Need help? Just ask: "help me with fluxloop" — the skill will guide you!
