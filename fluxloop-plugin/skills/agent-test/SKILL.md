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

## Role

Receives user test requests, **assesses the situation**, and automatically executes the full workflow: **synthesis → test → result analysis** as needed.

## Workflow

### Step 1: Assess Situation

First, check current status:

```bash
fluxloop auth status
```

**Check for**:
- Login status (not logged in → guide to `fluxloop auth login`)
- Current project
- Existing bundle availability

### Step 2: Understand Intent

Analyze user's request:

| Request Type | Assessment | Action |
|--------------|------------|--------|
| "create test" (new) | No bundle | synthesis → test |
| "test again" | Bundle exists | test only |
| "add more inputs" | Bundle exists | synthesis (--add-inputs) → test |
| "add harder cases" | Bundle exists | synthesis (↑hard weight) → test |

### Step 3: Gather Context (for new test)

Collect information needed to create a new test:

**Required questions**:
1. What scenario do you want to test? (purpose)
2. What service/product is this for? (domain)

**Optional questions** (have defaults):
3. Difficulty distribution (default: even)
4. Number of inputs (default: 10)

### Step 4: Execute Workflow

**When synthesis is needed**:
```
Execute /fluxloop:synthesis
```

Run 8 CLI commands sequentially (synthesis only, excluding test):
1. scenarios create
2. context refine
3. scenarios refine
4. personas suggest
5. inputs synthesize
6. inputs qc
7. (if needed) inputs refine
8. bundles publish

**Run test**:
```
Execute /fluxloop:test
```

### Step 5: Analyze Results

Analyze and summarize test results:

```
✅ Test Complete!

📋 Summary:
  - Total tests: 10
  - Passed: 8 (80%)
  - Failed: 2 (20%)

⚠️ Failure Analysis:
  - Input #3: [root cause analysis]
  - Input #7: [root cause analysis]

💡 Improvement Suggestions:
  - [specific improvement recommendations]

🚀 Next Steps:
  - "show detailed results" - check individual turns
  - "test again" - retest with same bundle
  - "add more inputs" - generate additional cases
```

## Error Handling

**Login Required**:
```
❌ Login required.

Please login with:
  fluxloop auth login
```

**Synthesis Failed**:
```
❌ Input synthesis failed

Created resources:
  - Scenario: scn-abc123

Recovery options:
  Run /fluxloop:synthesis again, or
  Execute fluxloop inputs synthesize --scenario-id scn-abc123 directly
```

## Usage Examples

### Create New Test
```
User: "test the order cancellation agent"
Skill: [gather context] → [synthesis] → [test] → [analyze results]
```

### Retest with Existing Bundle
```
User: "test again"
Skill: [run test only] → [analyze results]
```

### Add More Inputs
```
User: "add harder test cases"
Skill: [synthesis --add-inputs, ↑hard weight] → [test] → [analyze results]
```
