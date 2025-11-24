---
id: tools-reference
title: Tool Reference
sidebar_position: 4
---

# MCP Tool Reference

The Fluxloop MCP Server exposes the following tools via the Model Context Protocol. All tools communicate via stdio using JSON messages.

## Overview

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `handshake` | Server metadata | - | Server info + capabilities |
| `faq` | Documentation search | Query string | Answer + citations |
| `analyze_repository` | Project analysis | Root path | Profile with languages, frameworks, etc. |
| `detect_frameworks` | Framework detection | Repository profile | Detected frameworks with confidence |
| `generate_integration_steps` | Integration checklist | Framework name | Step-by-step guide |
| `propose_edit_plan` | Edit plan creation | Framework + profile | Structured edit plan |
| `validate_edit_plan` | Plan validation | Edit plan + root | Validation results |
| `run_integration_workflow` | End-to-end workflow | Root path | Complete analysis + plan |
| `fetch_integration_context` | VS Code planner context | Root path | Integration workflow payload |
| `fetch_base_input_context` | Base input context | Root path | Input samples + settings |
| `fetch_experiment_context` | Experiment context | Root path | Experiment summaries |
| `fetch_insight_context` | Insight context | Root path | Evaluation reports |

---

## handshake

Returns server metadata and available capabilities.

### Input
```json
{
  "type": "handshake",
  "id": "1"
}
```

### Output
```json
{
  "type": "response",
  "id": "1",
  "result": {
    "name": "fluxloop-mcp",
    "version": "0.1.1",
    "capabilities": {
      "tools": [
        "handshake",
        "faq",
        "analyze_repository",
        "detect_frameworks",
        "generate_integration_steps",
        "propose_edit_plan",
        "validate_edit_plan",
        "run_integration_workflow",
        "fetch_integration_context",
        "fetch_base_input_context",
        "fetch_experiment_context",
        "fetch_insight_context"
      ]
    }
  }
}
```

**Fields:**
- `name`: Server name
- `version`: Server version
- `capabilities.tools`: List of available tool names

---

## faq

Searches indexed Fluxloop documentation and returns answers with citations using hybrid BM25 + embedding retrieval.

### Input
```json
{
  "type": "request",
  "id": "2",
  "tool": "faq",
  "params": {
    "query": "How to integrate FastAPI?",
    "topK": 5,
    "context": {"detected_framework": "fastapi"}
  }
}
```

**Parameters:**
- `query` (required): Natural language question
- `topK` (optional): Number of results to retrieve (default: 5, max: 20)
- `context` (optional): Additional hints like `{"detected_framework": "fastapi"}`

### Output
```json
{
  "type": "response",
  "id": "2",
  "result": {
    "answer": "## Overview\nTo integrate FastAPI with Fluxloop:\n\n1. Install the SDK...\n\n### Related Topics\n- docs/...",
    "citations": [
      "packages/website/docs-cli/configuration/runners/python-function.md",
      "packages/website/docs-sdk/integration/fastapi.md"
    ],
    "score": 0.97,
    "chunks_used": 3
  }
}
```

**Fields:**
- `answer`: Formatted markdown response with main content and related sections
- `citations`: List of source document paths (repository-relative)
- `score`: Average relevance score (0-1)
- `chunks_used`: Number of document chunks used to generate answer

**Use Cases:**
- Quick documentation lookup
- Context-aware answers based on detected framework
- Finding relevant examples and guides

---

## analyze_repository

Scans a repository to identify languages, frameworks, entry points, package managers, and structural metadata.

### Input
```json
{
  "type": "request",
  "id": "3",
  "tool": "analyze_repository",
  "params": {
    "root": "/path/to/project",
    "globs": ["**/*.py", "**/*.ts"]
  }
}
```

**Parameters:**
- `root` (optional): Repository root path (default: `.`)
- `globs` (optional): File patterns to analyze (future use)

### Output
```json
{
  "type": "response",
  "id": "3",
  "result": {
    "root": "/Users/user/Documents/myproject",
    "languages": ["python", "typescript"],
    "packageManagers": ["pip", "npm"],
    "entryPoints": ["app/main.py", "src/server.ts"],
    "frameworkCandidates": ["fastapi", "express"],
    "riskFlags": ["multiple_entrypoints"],
    "stats": {
      "files": 324,
      "loc": 27453,
      "directories": 45
    }
  }
}
```

**Risk Flags:**
- `missing_entrypoint`: No recognizable entry point found
- `multiple_entrypoints`: Multiple entry points detected (may need clarification)
- `mixed_package_managers`: Multiple package managers in same language
- `large_repository`: More than 100k LOC (may take time to analyze)

**Detection Heuristics:**
- **Languages**: File extensions (`.py`, `.ts`, `.js`, `.go`, etc.)
- **Package Managers**: Presence of lock files (`package-lock.json`, `requirements.txt`, etc.)
- **Entry Points**: Common patterns (`main.py`, `server.ts`, `app.js`, etc.)
- **Frameworks**: Import patterns and dependency analysis

---

## detect_frameworks

Identifies frameworks based on repository profile and recommends integration patterns with confidence scoring.

### Input
```json
{
  "type": "request",
  "id": "4",
  "tool": "detect_frameworks",
  "params": {
    "repository_profile": {
      "languages": ["python"],
      "packageManagers": ["pip"],
      "entryPoints": ["app/main.py"],
      "frameworkCandidates": ["fastapi"]
    }
  }
}
```

**Parameters:**
- `repository_profile` (required): Output from `analyze_repository`

### Output
```json
{
  "type": "response",
  "id": "4",
  "result": {
    "frameworks": [
      {
        "name": "fastapi",
        "confidence": 0.85,
        "version_detected": "0.104.1",
        "insertAnchors": [
          {"filepath": "app/main.py", "pattern": "FastAPI\\("}
        ],
        "reasons": [
          "Python project with pip detected.",
          "Entry point app/main.py suggests FastAPI usage.",
          "Dependency analysis found fastapi==0.104.1."
        ]
      }
    ],
    "recommended_patterns": [
      {
        "framework": "fastapi",
        "runner_pattern": "python-function",
        "doc_url": "packages/website/docs-cli/configuration/runners/python-function.md",
        "confidence": 0.85,
        "rationale": "FastAPI endpoints are Python callables, best suited for python-function runner."
      }
    ]
  }
}
```

**Confidence Levels:**
- `0.9-1.0`: Very confident (framework explicitly declared)
- `0.7-0.89`: Confident (strong signals from dependencies and structure)
- `0.5-0.69`: Moderate (some indicators present)
- `0.0-0.49`: Low (weak signals, may be false positive)

**Supported Frameworks:**
- **FastAPI**: Python async web framework
- **Express**: Node.js web framework
- **Next.js**: React framework for production
- **NestJS**: Progressive Node.js framework
- More coming: Django, Flask, Svelte, Remix

---

## generate_integration_steps

Creates a step-by-step integration checklist for a specific framework with package manager-aware commands.

### Input
```json
{
  "type": "request",
  "id": "5",
  "tool": "generate_integration_steps",
  "params": {
    "framework": "express",
    "repository_profile": {
      "packageManagers": ["npm"],
      "entryPoints": ["src/server.ts"]
    }
  }
}
```

**Parameters:**
- `framework` (required): Framework name (express, fastapi, nextjs, nestjs)
- `repository_profile` (optional): For package manager-specific commands

### Output
```json
{
  "type": "response",
  "id": "5",
  "result": {
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
        "doc_ref": "packages/website/docs-cli/configuration/runners/http-rest.md",
        "code_snippet": "import { fluxloop } from '@fluxloop/sdk';\napp.use(fluxloop({ projectKey: '<PROJECT_KEY>' }));"
      },
      {
        "id": "configure_project",
        "title": "Update FluxLoop config",
        "details": "Set runner.target in configs/simulation.yaml to point to your Express entry point.",
        "doc_ref": "packages/website/docs-cli/configuration/simulation-config.md"
      },
      {
        "id": "test_integration",
        "title": "Test integration",
        "details": "Run: fluxloop run experiment --iterations 1",
        "doc_ref": "packages/website/docs-cli/commands/run.md"
      }
    ],
    "estimated_time": "10-15 minutes",
    "package_manager": "npm",
    "warnings": [],
    "prerequisites": [
      "Node.js 16+ installed",
      "FluxLoop CLI installed: pip install fluxloop-cli"
    ]
  }
}
```

**Step Structure:**
- `id`: Unique step identifier
- `title`: Human-readable step name
- `details`: Detailed instructions
- `doc_ref`: Link to relevant documentation
- `code_snippet` (optional): Code to add/modify

---

## propose_edit_plan

Generates a structured plan with specific file edits, anchors, payload, and validation checks.

### Input
```json
{
  "type": "request",
  "id": "6",
  "tool": "propose_edit_plan",
  "params": {
    "framework": "fastapi",
    "repository_profile": {
      "entryPoints": ["app/main.py"],
      "packageManagers": ["pip"]
    },
    "root": "."
  }
}
```

**Parameters:**
- `framework` (required): Framework name
- `repository_profile` (optional): For intelligent file selection
- `root` (optional): Repository root for validation (default: `.`)

### Output
```json
{
  "type": "response",
  "id": "6",
  "result": {
    "summary": "Add Fluxloop integration for fastapi project using python-function runner.",
    "edits": [
      {
        "filepath": "app/main.py",
        "strategy": "add_decorator",
        "anchors": [
          {"type": "after_match", "pattern": "app = FastAPI\\("}
        ],
        "payload": {
          "import": "from fluxloop import fluxloop",
          "code": "@fluxloop.trace()\nasync def handler(request: Request):\n    ...",
          "location": "above_function"
        },
        "rationale": "FastAPI endpoints should be decorated for tracing"
      }
    ],
    "postChecks": [
      "pytest tests/",
      "python -m app.main"
    ],
    "rollback": {
      "instruction": "git restore -SW :/",
      "description": "Restore all working tree changes"
    },
    "warnings": [
      "File app/main.py exists but anchor pattern not found.",
      "Manual verification recommended before applying."
    ],
    "prerequisites": [
      "Git repository initialized",
      "FluxLoop SDK installed: pip install fluxloop"
    ]
  }
}
```

**Edit Strategies:**
- `add_decorator`: Add @fluxloop.trace() to functions
- `insert_middleware`: Add middleware to web framework
- `add_import`: Add import statement
- `modify_config`: Update configuration file

**Anchor Types:**
- `after_match`: Insert after pattern match
- `before_match`: Insert before pattern match
- `replace_match`: Replace matched pattern
- `append_file`: Append to end of file

---

## validate_edit_plan

Validates an edit plan by checking file existence, anchor patterns, duplicate code, and structural correctness.

### Input
```json
{
  "type": "request",
  "id": "7",
  "tool": "validate_edit_plan",
  "params": {
    "plan": {
      "summary": "...",
      "edits": [...],
      "postChecks": [...]
    },
    "root": "."
  }
}
```

**Parameters:**
- `plan` (required): Edit plan object (from `propose_edit_plan`)
- `root` (optional): Repository root (default: `.`)

### Output
```json
{
  "type": "response",
  "id": "7",
  "result": {
    "valid": false,
    "issues": [
      "Required field 'summary' missing from plan"
    ],
    "warnings": [
      "Edit #0: file 'src/server.ts' does not exist.",
      "Edit #0: anchor pattern 'const app = express()' not found in src/server.ts",
      "Edit #0: import 'from fluxloop import fluxloop' already present in src/server.ts"
    ],
    "checks_performed": [
      "Plan structure validation",
      "File existence checks",
      "Anchor pattern verification",
      "Duplicate code detection"
    ]
  }
}
```

**Validation Checks:**
1. **Required Fields**: `summary`, `edits`, `filepath`, `strategy`
2. **File Existence**: Each edit's target file exists
3. **Anchor Patterns**: Anchor regex matches target file content
4. **Duplicate Detection**: Import/code not already present
5. **Post-Checks**: Commands are valid and safe
6. **Rollback**: Rollback instructions provided

**Issue Severity:**
- `issues`: Blocking problems (plan cannot be applied)
- `warnings`: Non-blocking concerns (plan may work but review recommended)

---

## run_integration_workflow

Executes the complete integration pipeline: analyze → detect → steps → plan → validate in a single call.

### Input
```json
{
  "type": "request",
  "id": "8",
  "tool": "run_integration_workflow",
  "params": {
    "root": "."
  }
}
```

**Parameters:**
- `root` (optional): Repository root (default: `.`)

### Output
```json
{
  "type": "response",
  "id": "8",
  "result": {
    "profile": { /* analyze_repository output */ },
    "detection": { /* detect_frameworks output */ },
    "integration_steps": { /* generate_integration_steps output */ },
    "edit_plan": { /* propose_edit_plan output */ },
    "validation": { /* validate_edit_plan output */ }
  }
}
```

**Use Cases:**
- Initial project assessment
- Generating comprehensive integration reports
- Automated onboarding flows
- CI/CD integration checks

**Benefits:**
- Single call reduces round trips
- Consistent workflow execution
- Complete context for decision making

---

## fetch_integration_context

Returns repository profile and integration workflow payloads for VS Code Flux Agent planner (Integration mode).

### Input
```json
{
  "type": "request",
  "id": "9",
  "tool": "fetch_integration_context",
  "params": {
    "root": "."
  }
}
```

### Output
```json
{
  "type": "response",
  "id": "9",
  "result": {
    "mode": "integration",
    "repository_profile": { /* analyze_repository output */ },
    "integration_workflow": { /* run_integration_workflow output */ },
    "structure_context": {
      "key_files": ["app/main.py", "configs/simulation.yaml"],
      "directories": ["app/", "configs/", "tests/"]
    },
    "rag_topics": [
      "fastapi_integration",
      "python_function_runner",
      "simulation_config"
    ]
  }
}
```

**Used by:** VS Code Flux Agent Integration mode

---

## fetch_base_input_context

Packages base input samples, service settings, and RAG topics for Base Input mode (future).

### Input
```json
{
  "type": "request",
  "id": "10",
  "tool": "fetch_base_input_context",
  "params": {
    "root": "."
  }
}
```

### Output
```json
{
  "type": "response",
  "id": "10",
  "result": {
    "mode": "base_input",
    "existing_inputs": {
      "base_inputs": [...],
      "personas": [...]
    },
    "service_context": "Customer support chatbot for ...",
    "rag_topics": [
      "persona_design",
      "input_generation",
      "variation_strategies"
    ]
  }
}
```

**Status:** Planned for VS Code extension

---

## fetch_experiment_context

Summarizes past experiments, runner configs, and simulation templates for Experiment mode (future).

### Input
```json
{
  "type": "request",
  "id": "11",
  "tool": "fetch_experiment_context",
  "params": {
    "root": "."
  }
}
```

### Output
```json
{
  "type": "response",
  "id": "11",
  "result": {
    "mode": "experiment",
    "recent_experiments": [...],
    "runner_config": {...},
    "simulation_templates": [...],
    "rag_topics": [
      "experiment_execution",
      "runner_configuration",
      "multi_turn_mode"
    ]
  }
}
```

**Status:** Planned for VS Code extension

---

## fetch_insight_context

Collects evaluation reports and aggregated metrics for Insight mode (future).

### Input
```json
{
  "type": "request",
  "id": "12",
  "tool": "fetch_insight_context",
  "params": {
    "root": "."
  }
}
```

### Output
```json
{
  "type": "response",
  "id": "12",
  "result": {
    "mode": "insight",
    "evaluation_reports": [...],
    "aggregated_metrics": {...},
    "rag_topics": [
      "evaluation_config",
      "success_criteria",
      "report_generation"
    ]
  }
}
```

**Status:** Planned for VS Code extension

---

## Error Handling

All tools return structured errors when invoked incorrectly:

```json
{
  "type": "error",
  "id": "42",
  "error": {
    "code": "tool_error",
    "message": "framework is required",
    "details": {
      "missing_param": "framework",
      "valid_frameworks": ["fastapi", "express", "nextjs", "nestjs"]
    }
  }
}
```

**Common Error Codes:**
- `unknown_tool`: Tool name not recognized
- `tool_error`: Tool-specific validation failure
- `invalid_payload`: Malformed request parameters
- `internal_error`: Unexpected server failure
- `file_not_found`: Target file doesn't exist
- `index_error`: Knowledge index not available

---

## Tool Chaining

MCP tools are designed to be chained for advanced workflows:

```
Standard Pipeline:
1. analyze_repository → Get project profile
2. detect_frameworks → Identify frameworks
3. generate_integration_steps → Get checklist
4. propose_edit_plan → Create edit plan
5. validate_edit_plan → Verify plan safety

Or use run_integration_workflow for automatic chaining.

VS Code Flux Agent Pipeline:
1. fetch_integration_context → Get mode-specific context
2. Use planner to generate plan with LLM
3. validate_edit_plan → Verify generated plan
4. Apply changes via VS Code extension
```

## Protocol Details

### Message Format

All messages follow this structure:

```json
{
  "type": "request | response | error | handshake",
  "id": "client-supplied-id",
  "tool": "tool_name",
  "params": { /* tool-specific parameters */ },
  "result": { /* successful response */ },
  "error": { /* error details */ }
}
```

### Request/Response Correlation

- Client provides unique `id` for each request
- Server echoes `id` in response/error
- Enables async request handling

### Transport

- **Protocol**: stdio (standard input/output)
- **Format**: JSON (one message per line)
- **Encoding**: UTF-8

## Next Steps

- **[Configuration](./configuration.md)** - Advanced configuration options
- **[Examples](./examples.md)** - Complete integration scenarios
- **[Usage with Cursor](./usage-cursor.md)** - Practical usage guide

