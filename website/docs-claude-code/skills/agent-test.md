---
sidebar_position: 1
---

# Agent Test Skill ⭐

**The most powerful way to use FluxLoop.** Just talk naturally—the skill handles everything.

## Why Use the Skill?

| Approach | Experience |
|----------|------------|
| **Skill (Recommended)** | "test my agent" → Everything happens automatically |
| Slash Commands | Manual: `/fluxloop:pull` → `/fluxloop:test` → check results |

**The skill is context-aware.** It:
- Knows your current setup state
- Guides you through missing steps
- Asks before executing anything
- Handles errors gracefully

---

## How to Use

Just ask Claude naturally:

```
"test my agent"
"generate test data"
"run a simulation"
"set up fluxloop"
"evaluate my chatbot"
```

That's it. The skill activates automatically.

---

## Activation Keywords

The skill activates when you mention:

| Category | Keywords |
|----------|----------|
| **Testing** | test, testing, test my agent, run test |
| **Simulation** | simulation, run simulation, simulate |
| **Data Generation** | generate test data, synthesize, create inputs |
| **Evaluation** | evaluate, evaluation, assess, check quality |
| **Setup** | set up fluxloop, configure, initialize |

---

## Skill Workflow

### Core Principle: Context-First

The skill always follows this pattern:

```
1. Check context (fluxloop context show)
      ↓
2. Summarize current state to you
      ↓
3. Present options (NO auto-execution)
      ↓
4. Execute after your confirmation
      ↓
5. Show results and next steps
```

**You're always in control.** Nothing runs without your approval.

---

## Example Conversations

### First-Time Setup

```
You: "I want to test my agent with fluxloop"

Claude: I'll help you set up FluxLoop for agent testing.

Let me check your current state...

📊 Current State:
- FluxLoop CLI: ✗ Not installed
- Authentication: -
- Project: -

To get started, I need to:
1. Install FluxLoop CLI
2. Log you in
3. Create or select a project

Should I proceed with the installation?

You: "yes"

Claude: Installing FluxLoop CLI...
[Executes: pip install fluxloop-cli]

✓ FluxLoop CLI installed!

Now let's log you in. Run this command and follow the browser prompt:

[Executes: fluxloop auth login]

...
```

### Generate Test Data

```
You: "generate test data for my customer support bot"

Claude: I'll generate test data for your agent.

📊 Current State:
- Project: customer-support (proj_abc)
- Scenario: support-bot (scn_123)
- Existing bundles: 2 found
  - v2 (stress-test, 50 inputs, 1 day ago)
  - v1 (basic, 10 inputs, 1 week ago)

Would you like to:
1. Use existing bundle v2 (50 inputs)
2. Use existing bundle v1 (10 inputs)  
3. Generate new test data

You: "3"

Claude: I'll generate new test data. First, let me create personas...

[Executes: fluxloop personas suggest --scenario-id scn_123]

✓ 5 personas generated:
- frustrated_customer
- new_user
- power_user
- confused_elderly
- impatient_professional

Now synthesizing test inputs...

[Executes: fluxloop inputs synthesize --scenario-id scn_123]

✓ 30 test inputs generated!

Publishing as bundle v3...

[Executes: fluxloop bundles publish ...]

✓ Bundle v3 published! Ready to test.

Run tests now?
```

### Run Tests

```
You: "run the tests"

Claude: Running tests with bundle v3...

[Executes: fluxloop sync pull --bundle-version-id bv_xyz]
[Executes: fluxloop test --scenario support-bot]

📊 Test Results:
✓ Passed: 27/30 (90%)
⚠️ Warnings: 3

Failed cases:
1. [frustrated_customer] "This is ridiculous!" 
   → Agent used "sorry" (forbidden word)
   
2. [power_user] "What's the API rate limit?"
   → Response too long (2500 chars > 2000 limit)
   
3. [impatient_professional] "Just fix it now"
   → Empty response

🔗 Detailed analysis: https://app.fluxloop.ai/runs/...

Would you like me to analyze these failures and suggest fixes?
```

---

## State-Based Guidance

The skill adapts to your current state:

| Your State | Skill Response |
|------------|----------------|
| No CLI installed | **Installs CLI automatically** |
| Not logged in | Helps with authentication |
| No project | Lists projects or creates new |
| No scenario | Creates local scenario folder |
| No test data | Generates personas and inputs |
| Ready to test | Runs tests immediately |

---

## Decision Tree

When you ask to test, the skill follows this logic:

```
Check bundles list
  │
  ├─ Multiple bundles → "Which bundle?" (shows list)
  │
  ├─ One bundle → "Use existing or create new?"
  │
  └─ No bundles → Check inputs
                    │
                    ├─ Has inputs → "Publish as bundle?"
                    │
                    └─ No inputs → "Generate new data?"
```

---

## Key Commands Used by Skill

The skill orchestrates these CLI commands for you:

| Phase | Commands |
|-------|----------|
| **Setup** | `fluxloop auth login`, `fluxloop projects select` |
| **Scenario** | `fluxloop init scenario`, `fluxloop scenarios create` |
| **Data Gen** | `fluxloop personas suggest`, `fluxloop inputs synthesize` |
| **Publish** | `fluxloop bundles publish` |
| **Test** | `fluxloop sync pull`, `fluxloop test` |
| **Results** | `fluxloop test results` |

You don't need to remember any of these. Just talk naturally.

---

## Best Practices

### 1. Be Specific About Your Agent

```
Good: "test my customer support chatbot"
Good: "generate edge cases for my order cancellation flow"

Less helpful: "test it"
```

### 2. Let the Skill Guide You

Don't try to run commands manually. Say what you want to achieve:

```
Good: "I want to test with more difficult scenarios"
Less helpful: "/fluxloop:synthesis" (manual command)
```

### 3. Ask for Analysis

After tests run, ask:

```
"Why did test #3 fail?"
"How can I fix these warnings?"
"What patterns do you see in the failures?"
```

---

## Troubleshooting

### Skill Not Activating?

Make sure your message includes activation keywords:

```
✗ "check this"
✓ "test this agent"

✗ "make some data"  
✓ "generate test data"
```

### Wrong Context?

If the skill is checking the wrong project:

```
"switch to project customer-support"
"use scenario order-bot"
```

### Need Manual Control?

For edge cases, you can use slash commands:

```
/fluxloop:status   → Check current state
/fluxloop:pull     → Pull specific bundle
/fluxloop:test     → Run with specific options
```

But 99% of the time, just talk naturally!

---

## Related

- [Installation](../getting-started/installation) - Plugin setup
- [Commands Reference](../commands/test) - Manual commands
- [Workflow Integration](../integration/workflow) - Development workflow
- [FluxLoop Web](https://alpha.app.fluxloop.ai) - Cloud dashboard