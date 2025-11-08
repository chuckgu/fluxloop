---
id: usage-cursor
title: Using with Cursor/Claude
sidebar_position: 3
---

# Using Fluxloop MCP with Cursor/Claude

Once configured, the Fluxloop MCP server enables your AI assistant to provide intelligent guidance for integrating Fluxloop into your projects.

## Example Workflows

### 1. Get Quick Answers

**In Cursor/Claude chat:**
```
How do I integrate Fluxloop with my FastAPI project?
```

**MCP Server Response:**
```
Based on the FastAPI documentation, you should:
1. Install the SDK: `pip install fluxloop`
2. Add the @fluxloop.trace() decorator to your endpoints
3. Configure the runner in configs/simulation.yaml

See: packages/website/docs-cli/configuration/runners/python-function.md
```

### 2. Analyze Your Project

**In Cursor/Claude:**
```
Analyze my current project for Fluxloop integration
```

**Behind the scenes:**
- MCP calls `analyze_repository` with your project root
- Returns languages, frameworks, entry points, risk flags

**Response:**
```
Your project uses:
- Languages: Python, TypeScript
- Frameworks: FastAPI (confidence: 0.85), Next.js (0.85)
- Entry points: services/collector/app/main.py
- Package managers: pip, npm

Recommended integration patterns:
- FastAPI → python-function runner
- Next.js → http-rest runner
```

### 3. Get Integration Steps

**In Cursor/Claude:**
```
Generate integration steps for my FastAPI service
```

**MCP Response:**
```
Framework: fastapi
Runner Pattern: python-function

Steps:
1. Install Fluxloop SDK
   pip install fluxloop

2. Update simulation.yaml runner
   Set `runner.target` to your FastAPI callable.

3. Test integration
   fluxloop run experiment

Estimated time: 10 minutes
```

### 4. Get Full Integration Plan

**In Cursor/Claude:**
```
Create a complete integration plan for my Express app
```

**MCP Response:**
```
Summary: Add Fluxloop integration for express project using http-rest runner.

Edits:
- File: src/server.ts
  Strategy: insert_middleware
  Anchor: After "const app = express()"
  Import: import { fluxloop } from '@fluxloop/sdk';
  Code: app.use(fluxloop({ projectKey: '<PROJECT_KEY>' }));

Post-checks:
- npm run build

Rollback: git restore -SW :/

Warnings:
- File src/server.ts does not exist; create it first
```

### 5. End-to-End Workflow

**In Cursor/Claude:**
```
Run the full Fluxloop integration workflow for my project
```

**MCP calls:** `run_integration_workflow`

**Returns:**
- Repository profile
- Framework detection results
- Integration steps
- Edit plan
- Validation report

## Best Practices

### Ask Specific Questions

❌ **Too vague:**
```
Tell me about Fluxloop
```

✅ **Better:**
```
How do I integrate Fluxloop with my Express server?
```

✅ **Best:**
```
I have an Express app at src/server.ts. Generate an integration plan for Fluxloop tracing.
```

### Provide Context

Include relevant details about your project:
- Framework and version
- Entry point file paths
- Package manager (npm, pip, etc.)
- Specific requirements (e.g., "async generator support")

### Verify Before Applying

Always review the integration plan before applying:
1. Check that files and anchors exist
2. Review post-checks (build, test commands)
3. Understand rollback instructions
4. Test in a git branch first

### Iterate on Warnings

If the MCP server returns warnings:
```
Warnings:
- File src/server.ts does not exist
- Anchor pattern 'const app = express()' not found
```

**Follow up:**
```
My Express app is in app/index.js, not src/server.ts. Regenerate the plan.
```

## Common Use Cases

### Use Case 1: New Project Integration

```
I just created a new FastAPI project at app/main.py.
How do I add Fluxloop tracing?
```

### Use Case 2: Existing Project Analysis

```
Analyze my repository and recommend the best Fluxloop integration approach.
```

### Use Case 3: Troubleshooting

```
I'm getting an error when running `fluxloop run experiment`.
The runner target is "app:main.handler". What's wrong?
```

### Use Case 4: Multi-Framework Projects

```
I have both a FastAPI backend (app/main.py) and Next.js frontend (src/pages/).
How should I integrate Fluxloop?
```

## Limitations

### Current Limitations (v0.1)
- **Framework Coverage**: Currently supports Express, FastAPI, Next.js, NestJS
- **Pattern Matching**: Uses simple regex anchors (no AST analysis yet)
- **Read-Only**: Analyzes code but doesn't modify files directly
- **Local Index**: Requires periodic manual updates for latest docs

### Planned Improvements (M3+)
- Expanded framework support (Django, Flask, Svelte, etc.)
- AST-based code analysis for precise anchor detection
- Streaming progress updates for long operations
- Auto-updating index from upstream docs

## Tips & Tricks

### Combine with Code Reading

```
Read my src/server.ts file, then propose a Fluxloop integration plan.
```

### Request Specific Patterns

```
I prefer using the python-async-generator runner pattern.
Generate steps for integrating with my OpenAI streaming agent.
```

### Validate Before Execution

```
Validate this integration plan:
[paste plan JSON]
```

## Next Steps

- [Tool Reference](./tools-reference.md) - Detailed tool documentation
- [Advanced Configuration](./configuration.md) - Customizing the MCP server
- [Examples](./examples.md) - Complete integration scenarios

