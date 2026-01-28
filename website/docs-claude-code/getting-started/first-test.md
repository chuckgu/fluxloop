---
sidebar_position: 2
---

# Your First Test

Run your first FluxLoop test—just by talking to Claude.

## The Easy Way: Use the Skill ⭐

After installing the plugin, simply say:

```
"test my agent"
```

or

```
"set up fluxloop and run a test"
```

**That's it.** The Agent Test Skill will:

1. Check if FluxLoop CLI is installed (install if needed)
2. Guide you through authentication
3. Help you select or create a project
4. Generate test data if none exists
5. Run the test
6. Show you results

---

## Example First-Time Conversation

```
You: "I want to test my customer support agent with fluxloop"

Claude: I'll help you set up FluxLoop and test your agent.

Let me check your current state...

📊 Current State:
- FluxLoop CLI: ✗ Not installed

First, I'll install the FluxLoop CLI. Should I proceed?

You: "yes"

Claude: Installing FluxLoop CLI...
[Executes: pip install fluxloop-cli]
✓ Installed!

Now let's log you in. Please follow the browser prompt...
[Executes: fluxloop auth login]

✓ Authenticated!

📋 Your projects:
1. customer-support (3 scenarios)
2. sales-bot (1 scenario)
3. [Create new]

Which project?

You: "1"

Claude: Selected: customer-support

Available bundles:
- v2 (stress-test, 50 inputs)
- v1 (basic, 10 inputs)

Which bundle to test with, or generate new?

You: "v2"

Claude: Running tests with bundle v2...

[Executes: fluxloop sync pull]
[Executes: fluxloop test]

📊 Results:
✓ 47/50 passed (94%)
⚠️ 3 warnings

View details: https://app.fluxloop.ai/...

Would you like me to analyze the failures?
```

---

## Alternative: Manual Commands

If you prefer direct control:

### Step 1: Setup

```bash
/fluxloop:setup
```

### Step 2: Run Test

```bash
/fluxloop:test
```

### Step 3: View Results

Results appear in Claude Code and upload to FluxLoop Web.

---

## Next Steps

- **[Agent Test Skill](/claude-code/skills/agent-test)** ⭐ - Full skill documentation
- **[Commands Reference](/claude-code/commands/test)** - Manual commands
- **[Workflow Integration](/claude-code/integration/workflow)** - Development workflow
