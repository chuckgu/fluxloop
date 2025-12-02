---
id: examples
title: Complete Examples
sidebar_position: 6
---

# Complete Integration Examples

## Example 1: FastAPI Project

### Scenario
You have a FastAPI service at `app/main.py` and want to add Fluxloop tracing.

### Step 1: Analyze Project

**Ask Cursor/Claude:**
```
Analyze my repository for Fluxloop integration
```

**MCP calls:** `analyze_repository`

**Response:**
```json
{
  "languages": ["python"],
  "packageManagers": ["pip"],
  "entryPoints": ["app/main.py"],
  "frameworkCandidates": ["fastapi"],
  "riskFlags": []
}
```

### Step 2: Detect Frameworks

**Ask:**
```
What frameworks did you detect?
```

**MCP calls:** `detect_frameworks`

**Response:**
```
Detected: FastAPI (confidence: 0.85)
Recommended pattern: python-function
Documentation: docs-cli/configuration/runners/python-function.md
```

### Step 3: Get Integration Steps

**Ask:**
```
Generate integration steps for FastAPI
```

**MCP calls:** `generate_integration_steps`

**Response:**
```
1. Install Fluxloop SDK: pip install fluxloop
2. Update simulation.yaml runner
3. Test integration: fluxloop run experiment

Estimated time: 10 minutes
```

### Step 4: Create Edit Plan

**Ask:**
```
Create an integration plan for my FastAPI app
```

**MCP calls:** `propose_edit_plan`

**Response:**
```
Summary: Add Fluxloop integration for fastapi project

Edit #1:
- File: app/main.py
- Add import: from fluxloop import fluxloop
- Add decorator: @fluxloop.trace()
- Anchor: After "app = FastAPI("

Post-checks: pytest, python -m app.main
Rollback: git restore -SW :/
```

### Step 5: Apply Changes

Review the plan, then manually apply or ask the AI assistant to implement it.

---

## Example 2: Express Server

### Scenario
TypeScript Express server at `src/server.ts`.

### Complete Workflow

**Ask Cursor/Claude:**
```
Run the complete Fluxloop integration workflow for my Express app
```

**MCP calls:** `run_integration_workflow`

**Response Summary:**
```
Profile:
- Languages: TypeScript, JavaScript
- Package managers: npm
- Entry points: src/server.ts
- Frameworks: Express (0.8 confidence)

Integration Plan:
- Install: npm install @fluxloop/sdk
- Edit: src/server.ts
  - Import: import { fluxloop } from '@fluxloop/sdk';
  - Code: app.use(fluxloop({ projectKey: '<PROJECT_KEY>' }));
  - Anchor: After "const app = express()"

Validation:
- ✅ Plan is valid
- ⚠️ Warning: File src/server.ts does not exist
```

**Next Steps:**
1. Create `src/server.ts` if it doesn't exist
2. Apply the import and middleware registration
3. Run `npm run build` to verify

---

## Example 3: Multi-Framework Project

### Scenario
Project with both FastAPI backend and Next.js frontend.

### Analysis

**Ask:**
```
Analyze my repository and suggest integration strategies
```

**Response:**
```
Detected frameworks:
1. FastAPI (0.85) - app/main.py
   → Use python-function runner
   
2. Next.js (0.85) - packages/website
   → Use http-rest runner for API routes

Recommended approach:
- Backend: Add @fluxloop.trace() to FastAPI endpoints
- Frontend: Instrument API routes in pages/api/
```

### Follow-up

**Ask:**
```
Generate separate integration plans for backend and frontend
```

**Response:**
Two edit plans with framework-specific guidance.

---

## Example 4: Troubleshooting Integration

### Scenario
Integration fails with "anchor not found" error.

### Diagnosis

**Ask:**
```
Validate this integration plan for my project:
[paste plan JSON]
```

**MCP calls:** `validate_edit_plan`

**Response:**
```
Issues: None
Warnings:
- Anchor pattern 'const app = express()' not found in src/server.ts
- Import already present in src/server.ts
```

### Resolution

**Ask:**
```
My Express app is initialized with:
const server = express()

Regenerate the plan with the correct anchor.
```

**Updated plan will use the correct pattern.**

---

## Example 5: Documentation Search

### Getting Specific Information

**Ask:**
```
How do I configure the python-async-generator runner?
```

**MCP calls:** `faq`

**Response:**
```
The python-async-generator pattern is used for streaming responses.

Configuration:
```yaml
runner:
  target: "module:async_generator_function"
  stream_output_path: "message.delta"
```

See: docs-cli/configuration/runners/python-async-generator.md
```

### Follow-up Questions

**Ask:**
```
What's the difference between python-function and python-async-generator?
```

**MCP searches documentation and explains differences with citations.**

---

## Example 6: Programmatic Usage

### Python Script Integration

```python
#!/usr/bin/env python
"""Generate integration report for a project."""

from fluxloop_mcp.tools import RunIntegrationWorkflowTool
import json

def generate_report(project_path: str) -> None:
    workflow = RunIntegrationWorkflowTool()
    result = workflow.run({"root": project_path})
    
    print("=" * 80)
    print(f"Integration Report for: {project_path}")
    print("=" * 80)
    
    profile = result["profile"]
    print(f"\nLanguages: {', '.join(profile['languages'])}")
    print(f"Frameworks: {', '.join(profile['frameworkCandidates'])}")
    
    detection = result["detection"]
    for fw in detection["frameworks"]:
        print(f"\n{fw['name']} (confidence: {fw['confidence']})")
        print(f"  Reasons: {', '.join(fw['reasons'])}")
    
    plan = result["edit_plan"]
    print(f"\n{plan['summary']}")
    print(f"Edits: {len(plan['edits'])}")
    
    validation = result["validation"]
    if validation["warnings"]:
        print("\n⚠️ Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")

if __name__ == "__main__":
    generate_report(".")
```

### Output
```
================================================================================
Integration Report for: /Users/user/myproject
================================================================================

Languages: python, typescript
Frameworks: fastapi, nextjs

fastapi (confidence: 0.85)
  Reasons: Python project with pip detected., Entry point app/main.py suggests FastAPI usage.

Add Fluxloop integration for fastapi project using python-function runner.
Edits: 1

⚠️ Warnings:
  - File app/main.py exists but anchor pattern not found.
```

---

## Example 7: CI/CD Integration Check

### GitHub Actions Workflow

```yaml
name: Validate Fluxloop Integration

on: [pull_request]

jobs:
  check-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install MCP Server
        run: pip install fluxloop-mcp
      
      - name: Analyze Project
        id: analyze
        run: |
          python - <<'PY'
          from fluxloop_mcp.tools import AnalyzeRepositoryTool
          import json
          result = AnalyzeRepositoryTool().analyze({"root": "."})
          print(json.dumps(result, indent=2))
          PY
      
      - name: Validate Integration
        run: |
          python - <<'PY'
          from fluxloop_mcp.tools import RunIntegrationWorkflowTool
          result = RunIntegrationWorkflowTool().run(
              {"root": ".", "question": "How do I integrate FluxLoop here?"}
          )
          validation = result["validation"]
          if not validation["valid"]:
              raise SystemExit(f"Validation failed: {validation['issues']}")
          PY
```

---

## Next Steps

- [Tool Reference](./tools-reference.md)
- [Advanced Configuration](./configuration.md)

