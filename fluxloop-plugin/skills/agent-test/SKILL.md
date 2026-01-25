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

**Flow:** Intent parsing → Local context check → Auto-configuration → Test execution → Result analysis

---

## Phase 0: Local Context Check

First, check local context state:

```bash
# Check if logged in
fluxloop auth status

# Check local context
fluxloop context show
```

**Based on results:**

| Context State | Action |
|---------------|--------|
| **Has project & scenario** | "Use existing settings (order-bot / order-cancel)?" |
| **Has project only** | "Would you like to create a scenario?" |
| **No context** | "No project found. Would you like to create one?" |
| **Not logged in** | → Phase 1 (Login) |

---

## Phase 1: Authentication (If Needed)

```bash
# Check login status
fluxloop auth status

# If not logged in:
fluxloop login
# Browser opens for code entry only (no project selection)
# Wait for user to complete

# After login, show next steps
fluxloop projects list
```

**After login message:**
```
✅ Login successful: user@example.com

Please select or create a project:
  - fluxloop projects list    - View your projects
  - fluxloop projects create --name <name>  - Create new project
```

---

## Phase 2: Resource Setup (Auto-Configuration)

### 2.1 Project Setup

**If no project in context:**
```
No project found. What would you like to test?
→ Parse intent and create project
```

```bash
# Create project (auto-selects after creation)
fluxloop projects create --name "order-bot"
# → context.json updated with project_id

# Note: If user has multiple workspaces, --workspace-id is required
# fluxloop projects create --name "order-bot" --workspace-id <workspace_id>

# Or select existing
fluxloop projects list
fluxloop context set-project <id>
```

### 2.2 Scenario Setup

**If no scenario in context:**
```
What scenario would you like to test?
→ Create scenario based on intent
```

```bash
# Create scenario based on intent
fluxloop scenarios create --name "Order cancellation" --description "Angry customer handling"
# → context.json updated with scenario_id

# Or select existing
fluxloop scenarios list
fluxloop context set-scenario <id>
```

### 2.3 API Key Setup (For Sync Operations)

Before sync pull/upload, ensure API Key is set:

```bash
# Check if API Key is configured
fluxloop apikeys check
```

**If not set:**
```bash
# Create API Key using current project context
fluxloop apikeys create
# → Automatically saved to .env as FLUXLOOP_SYNC_API_KEY
```

**Success message:**
```
✓ API Key created: flx_sk_****1234
✓ Saved to .env as FLUXLOOP_SYNC_API_KEY

You can now use:
  fluxloop sync pull
  fluxloop sync upload
  fluxloop test
```

---

### 2.4 Agent Loader Setup (If Needed)

Check if `runner.module_path` is configured in `configs/simulation.yaml`:

```bash
grep -A5 "runner:" configs/simulation.yaml
```

**If not configured, ask:**
```
Agent loader setup is required for testing.

Where is your agent located?
1) In this project (I'll scan for entry points)
2) External location (please provide path)
```

#### Option 1: In-project Agent

Scan codebase for potential entry points:
- Functions with signatures like `def run(`, `async def handle(`
- Classes with `invoke`, `run`, `respond` methods

Present candidates and let user choose, then update `configs/simulation.yaml`.

#### Option 2: External Agent (Recommended Pattern)

**Use the built-in wrapper template:**

1. Read the template file: `agents/_template_wrapper.py`
2. Copy it to create a new wrapper:
   ```bash
   cp agents/_template_wrapper.py agents/<name>_agent.py
   ```

3. Help user modify the wrapper:
   - Set `ORIGINAL_AGENT_PATH` to point to their agent
   - Update the import statement
   - Implement `_call_original_agent()` function

4. Update `configs/simulation.yaml`:
   ```yaml
   runner:
     module_path: "agents.<name>_agent"
     function_name: "run"
     target: "agents.<name>_agent:run"
     working_directory: .
     python_path:
       - .
     timeout_seconds: 300
   ```

5. Verify setup:
   ```bash
   python agents/<name>_agent.py
   ```

**Alternative: Use CLI command:**
```bash
fluxloop init agent <name> --template wrapper
```

---

## Phase 3: Test Data Synthesis (If Needed)

Check if test inputs exist:

```bash
ls inputs/generated.yaml
```

**If synthesis needed:**
```
Execute /fluxloop:synthesis
```

Or manually:
```bash
# Ensure API Key is set first (if not done in Phase 2.3)
fluxloop apikeys check
# If not set: fluxloop apikeys create

# Uses current project/scenario from context
fluxloop inputs synthesize --total-count 10
fluxloop sync pull
```

---

## Phase 4: Test Execution

```bash
fluxloop test
```

---

## Phase 5: Result Analysis

Read and summarize results:

```bash
cat .fluxloop/latest_result.md
```

**Present summary:**
```
✅ Test Complete!

📋 Summary:
  - Total tests: 10
  - Passed: 8 (80%)
  - Warnings: 2 (20%)

⚠️ Warning Analysis:
  - Input #3: [root cause analysis]
  - Input #7: [root cause analysis]

💡 Improvement Suggestions:
  - [specific recommendations based on failures]

🚀 Next Steps:
  - "show detailed results" - check individual turns
  - "test again" - retest with same bundle
  - "add more inputs" - generate additional cases

🌐 Web Dashboard:
  - https://app.fluxloop.ai/runs/...
```

---

## Complete Flow Diagram

```
"Test my agent"
    │
    ▼
[Local Context Check] .fluxloop/context.json
    │
    ├─ Context exists (project + scenario)
    │   └─ "Current settings: order-bot / order-cancel
    │       Proceed with these?" (Y/n)
    │       │
    │       ├─ Y → [Check API Key] → [Phase 4: Test]
    │       └─ n → "Create new or select different?"
    │
    └─ No context
        │
        ├─ Logged in? ──❌──→ fluxloop login (browser)
        │   ✅                 → no project selection
        │   │
        │   ▼
        ├─ Create project? ──Y──→ fluxloop projects create --name <name>
        │   │                      (auto-select)
        │   ▼
        ├─ Create scenario? ──Y──→ fluxloop scenarios create --name <name>
        │   │                       (auto-select)
        │   ▼
        ├─ API Key set? ──❌──→ fluxloop apikeys create
        │   ✅                   (auto-save to .env)
        │   │
        │   ▼
        ├─ Agent loader? ──❌──→ [Create wrapper from template]
        │   ✅
        │   ▼
        └─ Test inputs? ──❌──→ /fluxloop:synthesis
            ✅
            │
            ▼
┌─────────────────────────────────────┐
│  fluxloop test                      │
│  + Result Summary                   │
│  + Web Dashboard Link (optional)    │
└─────────────────────────────────────┘
```

---

## State-Based Branching

```
"Run test"
    │
    ▼
[Check context.json]
    │
    ├─ Has project & scenario
    │   └─ "Current settings: order-bot / order-cancel
    │       Proceed with these?" (Y/n)
    │       │
    │       ├─ Y → [Check API Key] → Run test immediately
    │       │       └─ If missing: fluxloop apikeys create
    │       └─ n → "Create new or select different?"
    │
    ├─ Has project only
    │   └─ "No scenario found. Would you like to create one?"
    │       → Intent-based scenario creation
    │       → [Check API Key] → fluxloop apikeys create (if needed)
    │
    └─ No context
        └─ "No project found. Would you like to create one?"
            │
            ├─ Y → Intent-based project/scenario creation
            │      → [Check API Key] → fluxloop apikeys create (if needed)
            └─ n → "Show existing projects?"
                   → fluxloop projects list
```

---

## Context Commands Reference

```bash
# Show current context
fluxloop context show

# Set project
fluxloop context set-project <project_id>
# Or shortcut:
fluxloop projects select <project_id>

# Set scenario
fluxloop context set-scenario <scenario_id>

# Clear context
fluxloop context clear

# List resources
fluxloop projects list
fluxloop scenarios list
```

## API Key Commands Reference

```bash
# Check if API Key is configured
fluxloop apikeys check

# Create API Key (auto-saved to .env)
fluxloop apikeys create

# Create with explicit project
fluxloop apikeys create --project-id <project_id>

# Don't auto-save (print key instead)
fluxloop apikeys create --no-save
```

---

## Error Handling

**Not Logged In:**
```
❌ Login required.

Running: fluxloop login
Browser will open for authentication.
Please complete login and let me know when done.
```

**No Project:**
```
❌ No project selected.

Options:
  1. Create new: fluxloop projects create --name <name>
  2. Select existing: fluxloop projects list
```

**Agent Loader Failed:**
```
❌ Agent loader verification failed.

Error: ModuleNotFoundError: No module named 'original_package'

Possible fixes:
1. Check the original agent path is correct
2. Verify python_path in simulation.yaml includes the right directories
3. Check if any dependencies are missing
```

**Synthesis Failed:**
```
❌ Input synthesis failed.

Recovery options:
  - Run /fluxloop:synthesis again
  - Or execute: fluxloop inputs synthesize
```

**API Key Not Set (Sync Failed):**
```
❌ Sync API key is not set.

Creating API Key for current project...

Running: fluxloop apikeys create
```

**After creation:**
```
✓ API Key created: flx_sk_****1234
✓ Saved to .env as FLUXLOOP_SYNC_API_KEY

Retrying sync...
```

---

## Usage Examples

### First-time User (Full Setup)

```
User: "Test my agent"

Skill: Checking environment...
       ❌ Not logged in → Running login...
       [Browser opens]
       
User: "I'm logged in"

Skill: ✅ Logged in: user@example.com
       
       No project found. What would you like to test?

User: "My chatbot. Order cancellation with angry customers."

Skill: Got it! Should I create this setup?
       
       📋 Creating:
       - Project: chatbot-test
       - Scenario: Order cancellation handling
       - Personas: Regular customer, Angry customer, VIP
       - Inputs: 10 (40% hard)
       
       Proceed? (Y/n)

User: "Yes"

Skill: ⏳ Setting up environment...
       
       [1/5] Creating project... ✓ proj-abc123
       [2/5] Creating scenario... ✓ scn-xyz789
       [3/5] Creating API Key... ✓ saved to .env
       [4/5] Creating personas... ✓ 3 created
       [5/5] Synthesizing inputs... ✓ 10 generated
       
       ❓ Where is your agent located?

User: "../chatbot/src/bot.py"

Skill: Creating agents/chatbot_agent.py... ✓
       
       🚀 Running test...
       
       ✅ Complete! 8/10 passed (80%)
       
       [Analysis...]
```

### Returning User (Quick Test)

```
User: "Run test"

Skill: [Checking context.json]
       
       Current settings:
       - Project: chatbot-test
       - Scenario: Order cancellation (10 inputs)
       
       Run test with these? (Y/n)

User: "Yes"

Skill: 🚀 Running test...
       
       ✅ Complete! 9/10 passed (90%)
       
       [Improved from last run!]
```

### Add New Scenario

```
User: "I want to test refund scenarios too"

Skill: Create a new scenario?
       
       Adding to current project (chatbot-test).
       
       📋 Creating:
       - Scenario: Refund request handling
       - Personas: Reusing existing 3
       - Inputs: 10
       
       Proceed? (Y/n)
```

### Switch Context

```
User: "Switch to a different project"

Skill: Your projects:
       
       1. chatbot-test (current)
       2. support-bot
       3. sales-assistant
       
       Which one?

User: "2"

Skill: ✅ Switched to support-bot.
       
       Scenarios:
       1. Customer inquiry handling
       2. Complaint processing
       
       Which scenario to test?
```
