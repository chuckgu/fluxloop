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

Manages the complete test cycle for AI agents — from initial setup to test execution.

## Role

**Agent-First Approach:** Understands user intent, automatically configures the environment, 
and executes the full workflow without requiring web visits (after initial login).

---

## Terminology

| Term | Description |
|------|-------------|
| **Web Project** | Remote project on FluxLoop cloud (has `project_id`) |
| **Web Scenario** | Remote scenario on FluxLoop cloud (has `scenario_id`) |
| **Local Scenario** | Local folder at `.fluxloop/scenarios/<name>/` |
| `--scenario <name>` | Local folder name (e.g., `order-bot`) |
| `--scenario-id <id>` | Remote scenario UUID |

---

## Quick Reference: Setup Flow

```
1. fluxloop auth login                                        # Login

# Project: Choose ONE
   fluxloop projects select <id>                              # Use existing (intent already set)
   fluxloop projects create --name "X" && fluxloop intent refine --intent "..."  # Create new + set intent

2. fluxloop init scenario X && cd .fluxloop/scenarios/X       # Create local folder

# Scenario: Choose ONE
   fluxloop scenarios select <id>                             # Use existing (goal already set)
   fluxloop scenarios create --name "X" --goal "..." --constraint "..."  # Create new with goal

3. fluxloop apikeys create                                    # API Key (for sync)
4. fluxloop personas suggest --scenario-id <id>               # Generate personas
5. fluxloop inputs synthesize --scenario-id <id>              # Generate test inputs
6. fluxloop test                                              # Run test
```

| Resource | New | Existing |
|----------|-----|----------|
| **Project** | `projects create` → `intent refine` | `projects select` |
| **Scenario** | `scenarios create --goal "..."` | `scenarios select` |

---

## Prerequisites (First-Time Only)

If `fluxloop` command is not found, install first:

```bash
# Check if installed
fluxloop --version

# If not installed:
uv tool install fluxloop-cli
# OR: pip install fluxloop-cli
```

> For detailed setup, run `/fluxloop:setup`

---

## Phase 0: Context Check

```bash
# Check login and context
fluxloop auth status
fluxloop context show

# Check local scenario folders (from workspace root)
ls .fluxloop/scenarios
```

| State | Action |
|-------|--------|
| **Not logged in** | → Phase 1 |
| **No Web Project** | → Phase 2 |
| **No Local Scenario folder** | → Phase 3 |
| **Ready** | → Phase 7 (Test Execution) |

---

## Phase 1: Authentication

```bash
# Check status
fluxloop auth status

# Login if needed
fluxloop auth login
```

After login:
```bash
# List available projects
fluxloop projects list
```

---

## Phase 2: Web Project Setup

```bash
# List projects
fluxloop projects list

# Select existing project (creates .fluxloop/project.json)
fluxloop projects select <project_id>

# Or create new project (new projects should set intent)
fluxloop projects create --name "my-agent"
fluxloop intent refine --intent "Order cancellation flows"
```

---

## Phase 3: Local Scenario Initialization

Create local scenario folder structure:

```bash
# Create scenario (from workspace root)
fluxloop init scenario order-bot

# Enter scenario directory
cd .fluxloop/scenarios/order-bot
```

This creates:
```
.fluxloop/scenarios/order-bot/
├── configs/
│   ├── scenario.yaml
│   ├── simulation.yaml
│   ├── input.yaml
│   └── evaluation.yaml
├── agents/
│   └── _template_wrapper.py
├── inputs/
└── experiments/
```

---

## Phase 4: Web Scenario Setup

```bash
# Create Web Scenario with inline options (recommended)
# Fill each option based on the user's request:
fluxloop scenarios create --name "Order Cancellation" \
  --description "Angry customer handling" \
  --goal "Test order cancellation handling for frustrated customers" \
  --constraint "Response must be polite and empathetic" \
  --constraint "Refund policy must be clearly explained" \
  --assumption "Customer has valid order in system" \
  --success-criteria "Customer receives cancellation confirmation"

# Options:
#   --goal: one sentence describing the test objective
#   --constraint: hard requirement (can be repeated)
#   --assumption: environment or data assumption (can be repeated)
#   --success-criteria: how to judge success (can be repeated)
#
# Minimal version (uses name as goal):
#   fluxloop scenarios create --name "Order Cancellation"
#
# Alternative: use config file instead of inline options
#   fluxloop scenarios create --name "X" --config-file configs/scenario_snapshot.json

# List scenarios
fluxloop scenarios list

# Select existing scenario
fluxloop scenarios select <scenario_id>
```

---

## Phase 5: API Key & Agent Setup

### 5.1 API Key

```bash
# Check if set
fluxloop apikeys check

# Create if needed (auto-saves to .env)
fluxloop apikeys create
```

### 5.2 Agent Loader

Check `configs/simulation.yaml` for `runner.module_path`:

```bash
grep -A5 "runner:" configs/simulation.yaml
```

If not configured, create wrapper:

```bash
cp agents/_template_wrapper.py agents/my_agent.py
```

Update `configs/simulation.yaml`:
```yaml
runner:
  module_path: "agents.my_agent"
  function_name: "run"
  target: "agents.my_agent:run"
  timeout_seconds: 300
```

---

## Phase 6: Test Data Synthesis (If Needed)

Check if inputs exist:
```bash
ls inputs/generated.yaml
```

If missing, synthesize:

```bash
# 1. Get scenario_id
fluxloop scenarios list

# 2. Refine intent/context (auto-saves to project context)
fluxloop intent refine --intent "Order cancellation flows"

# 3. Refine scenario (auto-saves to scenario snapshot)
fluxloop scenarios refine --scenario-id <scenario_id>

# 4. Generate personas (REQUIRED)
fluxloop personas suggest --scenario-id <scenario_id>

# 5. Synthesize inputs (auto-uses suggested personas if --persona-ids not provided)
fluxloop inputs synthesize --scenario-id <scenario_id> --total-count 10

# 6. (Optional) Pull to local
# `fluxloop test` already runs sync pull by default.
fluxloop sync pull --scenario <scenario_name>
```

> ⚠️ **Important:**
> - Web Project must be selected (`fluxloop projects select`)
> - Personas must exist before synthesis. Without personas, `inputs synthesize` returns empty results.

---

## Phase 7: Test Execution (includes sync pull)

From workspace root:
```bash
fluxloop test --scenario <scenario_name>
```

Or from scenario directory:
```bash
cd .fluxloop/scenarios/<scenario_name>
fluxloop test
```

---

## Phase 8: Result Analysis

```bash
# From scenario directory
cat .state/latest_result.md

# Or specify scenario
cat .fluxloop/scenarios/<scenario_name>/.state/latest_result.md
```

**Summary format:**
```
✅ Test Complete!

📋 Summary:
  - Total: 10, Passed: 8 (80%), Warnings: 2

⚠️ Issues:
  - Input #3: [analysis]
  - Input #7: [analysis]

🚀 Next:
  - "show details" - view turns
  - "test again" - rerun
  - "add inputs" - more cases
```

---

## Flow Diagram

```
"Test my agent"
       │
       ▼
[fluxloop auth status]
       │
       ├─ Not logged in ──→ fluxloop auth login
       │
       ▼
[fluxloop context show]
       │
       ├─ No Web Project ──→ fluxloop projects select <id>
       │
       ├─ No Local Scenario ──→ fluxloop init scenario X
       │                        cd .fluxloop/scenarios/X
       │
       ├─ No Web Scenario ──→ fluxloop scenarios create --name X
       │
       ├─ No API Key ──→ fluxloop apikeys create
       │
       ├─ No Agent Loader ──→ Setup wrapper
       │
       ├─ No Inputs ──→ Synthesis workflow
       │
       ▼
┌──────────────────────────────────┐
│  fluxloop test --scenario X      │
│  → Result Summary                │
│  → Web Dashboard Link            │
└──────────────────────────────────┘
```

---

## Command Reference

### Authentication
```bash
fluxloop auth login      # Login
fluxloop auth logout     # Logout
fluxloop auth status     # Check status
```

### Projects
```bash
fluxloop projects list              # List projects
fluxloop projects select <id>       # Select project
fluxloop projects create --name X   # Create project
```

### Scenarios
```bash
fluxloop scenarios list                    # List scenarios
fluxloop scenarios select <id>             # Select scenario
fluxloop scenarios create --name X         # Create scenario
fluxloop scenarios refine --scenario-id X  # Refine with AI
```

### Local
```bash
fluxloop init scenario X           # Create local folder
fluxloop context show              # Show context
fluxloop context clear             # Clear context
```

### Sync & Test
```bash
fluxloop apikeys check                    # Check API key
fluxloop apikeys create                   # Create API key
fluxloop sync pull --scenario X           # Pull data
fluxloop sync upload --scenario X         # Upload results
fluxloop test --scenario X                # Run test
```

### Synthesis
```bash
fluxloop intent refine --intent "..." --apply      # Refine project intent
fluxloop personas suggest --scenario-id X  # Generate personas
fluxloop inputs synthesize --scenario-id X --total-count N # Synthesize inputs
fluxloop inputs qc --scenario-id X         # Quality check
```

---

## Error Handling

**Not Logged In:**
```
❌ Login required.
→ fluxloop auth login
```

**No Web Project:**
```
❌ No Web Project selected.
→ fluxloop projects list
→ fluxloop projects select <id>
```

**API Key Missing:**
```
❌ Sync API key is not set.
→ fluxloop apikeys create
```

**No Personas (Synthesis Empty):**
```
❌ No personas found.
→ fluxloop personas suggest --scenario-id <id>
→ Then retry: fluxloop inputs synthesize --scenario-id <id>
```

**Agent Loader Failed:**
```
❌ ModuleNotFoundError
→ Check module_path in configs/simulation.yaml
→ Verify python_path includes agent directory
```

---

## Usage Examples

### First-time User

```
User: "Test my agent"

Agent: Checking environment...
       ❌ Not logged in
       
       Running: fluxloop auth login
       [Browser opens]

User: "Done"

Agent: ✅ Logged in: user@example.com
       
       No Web Project. What are you testing?

User: "My order chatbot"

Agent: Creating setup:
       - Web Project: order-chatbot
       - Local Scenario: order-test
       - Web Scenario: Order handling
       
       Proceed? (Y/n)

User: "Yes"

Agent: [1/5] Creating Web Project... ✓
       [2/5] Local scenario... ✓ .fluxloop/scenarios/order-test
       [3/5] Web Scenario... ✓
       [4/5] API Key... ✓
       [5/5] Agent wrapper... ✓
       
       Where is your agent?

User: "../chatbot/bot.py"

Agent: Created agents/chatbot_agent.py ✓
       
       🚀 Running test...
       ✅ 8/10 passed (80%)
```

### Returning User

```
User: "Run test"

Agent: Current settings:
       - Project: order-chatbot
       - Scenario: order-test (10 inputs)
       
       Proceed? (Y/n)

User: "Yes"

Agent: 🚀 Running...
       ✅ 9/10 passed (90%)
       
       [Improved from last run!]
```
