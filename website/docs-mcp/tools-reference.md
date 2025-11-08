---
id: tools-reference
title: Tool Reference
sidebar_position: 4
---

# MCP Tool Reference

The Fluxloop MCP Server exposes the following tools via the Model Context Protocol.

## handshake

Returns server metadata and available capabilities.

### Input
```json
{
  "tool": "handshake"
}
```

### Output
```json
{
  "tool": "handshake",
  "data": {
    "name": "fluxloop",
    "version": "0.0.1",
    "capabilities": [
      "analyze_repository",
      "faq",
      "detect_frameworks",
      "generate_integration_steps",
      "propose_edit_plan",
      "validate_edit_plan",
      "run_integration_workflow"
    ]
  }
}
```

---

## faq

Searches indexed Fluxloop documentation and returns answers with citations.

### Input
```json
{
  "tool": "faq",
  "query": "How to integrate FastAPI?",
  "topK": 5
}
```

**Parameters:**
- `query` (required): Natural language question
- `topK` (optional): Number of results to retrieve (default: 5)
- `context` (optional): Additional hints like `{"detected_framework": "fastapi"}`

### Output
```json
{
  "tool": "faq",
  "data": {
    "answer": "## Overview\n- **When to Use**: ...\n\n### Related\n- docs/...",
    "citations": [
      "packages/website/docs-cli/configuration/runners/python-function.md",
      "docs/prd/..."
    ],
    "score": 0.97
  }
}
```

**Fields:**
- `answer`: Formatted markdown response with main content and related sections
- `citations`: List of source document paths (repo-relative)
- `score`: Relevance score (0-1)

---

## analyze_repository

Scans a repository to identify languages, frameworks, entry points, and structural metadata.

### Input
```json
{
  "tool": "analyze_repository",
  "root": "/path/to/project",
  "globs": ["**/*.py", "**/*.ts"]
}
```

**Parameters:**
- `root` (optional): Repository root path (default: `.`)
- `globs` (optional): File patterns to analyze (placeholder, not yet used)

### Output
```json
{
  "tool": "analyze_repository",
  "data": {
    "root": "/Users/user/Documents/myproject",
    "languages": ["python", "typescript"],
    "packageManagers": ["pip", "npm"],
    "entryPoints": ["app/main.py", "src/server.ts"],
    "frameworkCandidates": ["fastapi", "express"],
    "riskFlags": ["multiple_entrypoints"],
    "stats": {
      "files": 324,
      "loc": 27453
    }
  }
}
```

**Risk Flags:**
- `missing_entrypoint`: No recognizable entry point found
- `multiple_entrypoints`: Multiple entry points detected (may require clarification)

---

## detect_frameworks

Identifies frameworks based on repository profile and recommends integration patterns.

### Input
```json
{
  "tool": "detect_frameworks",
  "repository_profile": {
    "languages": ["python"],
    "packageManagers": ["pip"],
    "entryPoints": ["app/main.py"],
    "frameworkCandidates": ["fastapi"]
  }
}
```

**Parameters:**
- `repository_profile` (required): Output from `analyze_repository`

### Output
```json
{
  "tool": "detect_frameworks",
  "data": {
    "frameworks": [
      {
        "name": "fastapi",
        "confidence": 0.85,
        "insertAnchors": [
          {"filepath": "app/main.py", "pattern": "FastAPI("}
        ],
        "reasons": [
          "Python project with pip detected.",
          "Entry point app/main.py suggests FastAPI usage.",
          "Dependency analysis found fastapi."
        ]
      }
    ],
    "recommended_patterns": [
      {
        "framework": "fastapi",
        "runner_pattern": "python-function",
        "doc_url": "packages/website/docs-cli/configuration/runners/python-function.md",
        "confidence": 0.85
      }
    ]
  }
}
```

---

## generate_integration_steps

Creates a step-by-step integration checklist for a specific framework.

### Input
```json
{
  "tool": "generate_integration_steps",
  "framework": "express",
  "repository_profile": {
    "packageManagers": ["npm"],
    "entryPoints": ["src/server.ts"]
  }
}
```

**Parameters:**
- `framework` (required): Framework name (express, fastapi, nextjs, nestjs)
- `repository_profile` (optional): For package manager-specific commands

### Output
```json
{
  "tool": "generate_integration_steps",
  "data": {
    "framework": "express",
    "runner_pattern": "http-rest",
    "steps": [
      {
        "id": "install_sdk",
        "title": "Install Fluxloop SDK",
        "details": "npm install @fluxloop/sdk",
        "doc_ref": "packages/website/docs-cli/configuration/runners/http-rest.md"
      },
      {
        "id": "add_middleware",
        "title": "Register middleware",
        "details": "Add `app.use(fluxloop())` after Express app initialization.",
        "doc_ref": "packages/website/docs-cli/configuration/runners/http-rest.md"
      }
    ],
    "estimated_time": "10 minutes",
    "package_manager": "npm",
    "warnings": []
  }
}
```

---

## propose_edit_plan

Generates a structured plan with specific file edits, anchors, and validation checks.

### Input
```json
{
  "tool": "propose_edit_plan",
  "framework": "fastapi",
  "repository_profile": {
    "entryPoints": ["app/main.py"],
    "packageManagers": ["pip"]
  },
  "root": "."
}
```

**Parameters:**
- `framework` (required): Framework name
- `repository_profile` (optional): For intelligent file selection
- `root` (optional): Repository root for validation (default: `.`)

### Output
```json
{
  "tool": "propose_edit_plan",
  "data": {
    "summary": "Add Fluxloop integration for fastapi project using python-function runner.",
    "edits": [
      {
        "filepath": "app/main.py",
        "strategy": "add_decorator",
        "anchors": [
          {"type": "after_match", "pattern": "app = FastAPI("}
        ],
        "payload": {
          "import": "from fluxloop import fluxloop",
          "code": "@fluxloop.trace()\nasync def handler(...):\n    ..."
        }
      }
    ],
    "postChecks": ["pytest", "python -m app.main"],
    "rollback": {"instruction": "git restore -SW :/"},
    "warnings": [
      "File app/main.py exists but anchor pattern not found."
    ]
  }
}
```

---

## validate_edit_plan

Validates an edit plan by checking file existence, anchor patterns, and potential conflicts.

### Input
```json
{
  "tool": "validate_edit_plan",
  "plan": {
    "summary": "...",
    "edits": [...],
    "postChecks": [...]
  },
  "root": "."
}
```

**Parameters:**
- `plan` (required): Edit plan object (from `propose_edit_plan`)
- `root` (optional): Repository root (default: `.`)

### Output
```json
{
  "tool": "validate_edit_plan",
  "data": {
    "valid": true,
    "issues": [],
    "warnings": [
      "Edit #0: file 'src/server.ts' does not exist."
    ]
  }
}
```

**Validation Checks:**
- Required fields (`summary`, `edits`, `filepath`, `strategy`)
- File existence for each edit
- Anchor pattern presence in target files
- Duplicate import/code detection
- Post-checks and rollback instructions

---

## run_integration_workflow

Executes the complete integration pipeline: analyze → detect → steps → plan → validate.

### Input
```json
{
  "tool": "run_integration_workflow",
  "root": "."
}
```

**Parameters:**
- `root` (optional): Repository root (default: `.`)

### Output
```json
{
  "tool": "run_integration_workflow",
  "data": {
    "profile": { /* analyze_repository output */ },
    "detection": { /* detect_frameworks output */ },
    "integration_steps": { /* generate_integration_steps output */ },
    "edit_plan": { /* propose_edit_plan output */ },
    "validation": { /* validate_edit_plan output */ }
  }
}
```

This tool provides a complete analysis in one call, ideal for:
- Initial project assessment
- Generating comprehensive integration reports
- Automated onboarding flows

---

## Error Handling

All tools return structured errors when invoked incorrectly:

```json
{
  "type": "error",
  "error": {
    "code": "tool_error",
    "message": "framework is required"
  }
}
```

**Common Error Codes:**
- `unknown_tool`: Tool name not recognized
- `tool_error`: Tool-specific validation failure
- `invalid_payload`: Malformed request
- `internal_error`: Unexpected server failure

---

## Tool Chaining

MCP tools can be chained for advanced workflows:

```
1. analyze_repository → Get project profile
2. detect_frameworks → Identify frameworks
3. generate_integration_steps → Get checklist
4. propose_edit_plan → Create edit plan
5. validate_edit_plan → Verify plan safety
```

Or use `run_integration_workflow` for automatic chaining.

## Next Steps

- [Advanced Configuration](./configuration.md)
- [Examples](./examples.md)

