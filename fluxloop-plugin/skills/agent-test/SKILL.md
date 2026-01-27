---
name: fluxloop-agent-test
description: |
  Use for AI agent testing, simulation, and test data generation requests.
  Keywords: test, simulation, input synthesis, scenario, agent evaluation

  Auto-activates on requests like:
  - "test this agent", "create test"
  - "run simulation"
  - "generate test data"
  - "evaluate agent"
---

# FluxLoop Agent Test Skill

Manages the complete test cycle for AI agents.

## Core Principle

**Context-First:** Always read context first → understand state → ask user → execute after confirmation

```
1. Check context (fluxloop context show)
2. Summarize current state
3. Present options (NO auto-execution)
4. Execute after user confirmation
5. Save results to context
```

---

## Terminology

| Term | Description |
|------|-------------|
| **Web Project** | Remote project on FluxLoop cloud (`project_id`) |
| **Web Scenario** | Remote scenario on FluxLoop cloud (`scenario_id`) |
| **Local Scenario** | Local folder at `.fluxloop/scenarios/<name>/` |
| **Input Set** | Generated test inputs (`input_set_id`) |
| **Bundle** | Published snapshot of inputs + personas (`bundle_version_id`) |

---

## Phase 0: Context Check (Always First!)

```bash
fluxloop context show    # Check current state
fluxloop auth status     # Check login status
ls .fluxloop/scenarios   # Check local scenario folders (from workspace root)
```

### State-Based Actions

| Context State | Next Action |
|---------------|-------------|
| None (no context.json) | → Phase 1: Setup |
| Project only | → Phase 2: Create Scenario |
| Scenario exists, no data | → Phase 3: Generate Data |
| Bundle exists | → Phase 4: Run Test |

---

## Phase 1: Setup (One-time)

```bash
# 0. Check if installed
fluxloop --version

# If not installed:
uv tool install fluxloop-cli
# OR: pip install fluxloop-cli

# 1. Login
fluxloop auth login

# 2. Select or create project
fluxloop projects list
fluxloop projects select <project_id>
# OR
fluxloop projects create --name "my-agent"
fluxloop intent refine --intent "..."
```

> For detailed setup instructions, run `/fluxloop:setup`

---

## Phase 2: Create Scenario (Once per scenario)

> ⚠️ **Important:** Run from workspace root (where `.fluxloop/` should be created).  
> Phase 1 (`projects select`) must be done first to establish the workspace.

```bash
# 0. Ensure you're in workspace root (not home directory!)
pwd  # Should be your project directory, NOT ~

# 1. Initialize local folder (creates .fluxloop/scenarios/<name>/)
fluxloop init scenario order-bot
cd .fluxloop/scenarios/order-bot

# 2. Create and refine web scenario
fluxloop scenarios create --name "Order Bot" --goal "..."
fluxloop scenarios refine --scenario-id <id>

# 3. Create API key
fluxloop apikeys create
```

**Common mistake:** Running `init scenario` from home directory creates in `~/.fluxloop/` instead of workspace.

---

## Phase 3: Generate Data (Decision Tree)

**Always check existing data with list commands, then ask user:**

```
bundles list --scenario-id <id>
  │
  ├─ Multiple bundles found → Show list with details, ask "Which bundle?"
  │   │
  │   └─ User selects → Go to Phase 4 (2 commands)
  │
  ├─ One bundle found → "Use existing or create new?"
  │   │
  │   ├─ Use existing → Go to Phase 4 (2 commands)
  │   │
  │   └─ Create new → Check inputs list
  │
  └─ No bundle → inputs list --scenario-id <id>
                   │
                   ├─ Multiple input sets → Show list with details, ask "Which one?"
                   │   │
                   │   └─ User selects → Publish bundle only (3 commands)
                   │
                   ├─ One input set found → "Use existing or create new?"
                   │   │
                   │   ├─ Use existing → Publish bundle only (3 commands)
                   │   │
                   │   └─ Create new → Full generation (5 commands)
                   │
                   └─ No input set → Full generation
```

### When Multiple Resources Exist

Show identifying information to help user choose:

```
Agent: Found 3 existing bundles:
       1. v3 (stress-test, 20 inputs, 1 day ago)
       2. v2 (happy-path, 5 inputs, 3 days ago)
       3. v1 (edge-cases, 10 inputs, 7 days ago)
       
       Which bundle to use? Or create new?
```

Key info to display: **version/name, tag/description, count, created date**

### Commands by Path

**Use existing bundle (2 commands):**
```bash
fluxloop sync pull --bundle-version-id <id>
fluxloop test --scenario <name>
```

**Use existing input set (3 commands):**
```bash
fluxloop bundles publish --scenario-id <id> --input-set-id <id>
fluxloop sync pull --bundle-version-id <id>
fluxloop test --scenario <name>
```

**Full generation (5 commands):**
```bash
fluxloop personas suggest --scenario-id <id>
fluxloop inputs synthesize --scenario-id <id>
fluxloop bundles publish --scenario-id <id> --input-set-id <id>
fluxloop sync pull --bundle-version-id <id>
fluxloop test --scenario <name>
```

---

## Phase 4: Run Test

```bash
# Always run sync pull and test separately
fluxloop sync pull --bundle-version-id <id>
fluxloop test --scenario <name>
```

> ⚠️ Do NOT use `test --pull`. Always run `sync pull` + `test` separately.

### View Results
```bash
cat .fluxloop/scenarios/<name>/.state/latest_result.md
```

---

## Example Conversations

### Example 1: "Run test"

```
User: "Run test"

Agent: [Check context]
       
       📋 Current state:
       - Project: order-bot
       - Scenario: order-cancel
       - Existing bundle: v2 (10 inputs, created 3 days ago)
       
       What would you like to do?
       1. Run test with existing bundle (v2)
       2. Generate new inputs and test
       3. Select different scenario

User: "1"

Agent: [Execute]
       → fluxloop sync pull --bundle-version-id <v2_id>
       → fluxloop test --scenario order-cancel
       
       ✅ 8/10 passed (80%)
```

### Example 2: "Test with new inputs"

```
User: "Test with new inputs"

Agent: [Check context - scenario exists, new generation requested]
       
       Generating new inputs and running test.
       
       [Execute]
       → fluxloop personas suggest --scenario-id <id>
       → fluxloop inputs synthesize --scenario-id <id>
       → fluxloop bundles publish --scenario-id <id> --input-set-id <id>
       → fluxloop sync pull --bundle-version-id <id>
       → fluxloop test --scenario <name>
       
       ✅ 9/10 passed (90%)
```

### Example 3: First-time User

```
User: "I want to test my agent"

Agent: [Check context - none]
       
       This is your first time! Let's set up first.
       
       Are you logged in?
       
User: "No"

Agent: → fluxloop auth login
       (Browser opens)
       
       Let me know when you're done.

User: "Done"

Agent: What agent are you testing?

User: "Order cancellation chatbot"

Agent: [Create project + scenario]
       → fluxloop projects create --name "order-cancel-bot"
       → fluxloop intent refine --intent "Order cancellation handling test"
       → fluxloop init scenario order-cancel
       → fluxloop scenarios create --name "Order Cancel" --goal "..."
       → fluxloop scenarios refine --scenario-id <id>
       → fluxloop apikeys create
       
       ✓ Setup complete
       
       Would you like to generate test data?

User: "Yes"

Agent: [Generate data + test]
       ...
```

---

## Command Reference

### Context
```bash
fluxloop context show     # Current state
fluxloop context clear    # Reset
```

### Auth
```bash
fluxloop auth login
fluxloop auth status
```

### Projects
```bash
fluxloop projects list
fluxloop projects select <id>
fluxloop projects create --name X
fluxloop intent refine --intent "..."
```

### Scenarios
```bash
fluxloop scenarios list
fluxloop scenarios select <id>
fluxloop scenarios create --name X --goal "..."
fluxloop scenarios refine --scenario-id <id>
fluxloop init scenario <name>
```

### Data (Always check with list first!)
```bash
fluxloop bundles list --scenario-id <id>
fluxloop inputs list --scenario-id <id>
fluxloop personas suggest --scenario-id <id>
fluxloop inputs synthesize --scenario-id <id>
fluxloop bundles publish --scenario-id <id> --input-set-id <id>
```

### Sync & Test (Always separate!)
```bash
fluxloop sync pull --bundle-version-id <id>
fluxloop test --scenario <name>
```

### API Keys
```bash
fluxloop apikeys check
fluxloop apikeys create
```

---

## Error Handling

| Error | Solution |
|-------|----------|
| `Login required` | `fluxloop auth login` |
| `No project selected` | `fluxloop projects select <id>` |
| `Sync API key not set` | `fluxloop apikeys create` |
| `Inputs file not found` | `fluxloop sync pull --bundle-version-id <id>` |
| `No personas found` | `fluxloop personas suggest --scenario-id <id>` first |
| Scenario created in `~/.fluxloop/` | Run from workspace root, not home. Do `projects select` first. |

---

## Key Takeaways

1. **Always check context first** (`fluxloop context show`)
2. **Check existing data with list** (`bundles list`, `inputs list`)
3. **Ask user before executing** (NO auto-execution)
4. **Run sync pull + test separately** (Do NOT use `--pull`)
5. **Use explicit IDs** (`--bundle-version-id`, `--scenario-id`)
