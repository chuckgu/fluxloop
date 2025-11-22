---
sidebar_position: 4
---

# Using Flux Agent

Flux Agent analyzes your code and generates intelligent integration suggestions by combining MCP repository analysis with LLM-powered reasoning.

## What is Flux Agent?

Flux Agent is an AI assistant that:

1. **Understands Your Code**: Analyzes the active file, selected code blocks, and project structure
2. **Consults Knowledge**: Queries the MCP server for framework-specific recipes and patterns
3. **Generates Suggestions**: Uses OpenAI models to create detailed, contextualized integration plans
4. **Presents Results**: Shows suggestions in a dedicated panel with copy/check actions

## How to Use Flux Agent

### Step 1: Open a File

Open the file where you want to integrate FluxLoop (e.g., `src/server.ts`, `app/main.py`).

### Step 2: Select Context (Optional)

If you want Flux Agent to focus on a specific code block:

1. Highlight the relevant function, class, or middleware section
2. The agent will prioritize this selection in its analysis

### Step 3: Run Flux Agent

**Method 1: Integration View**
1. Open **FluxLoop** activity bar → **Integration** view
2. Click **Run Flux Agent** button

**Method 2: Command Palette**
1. Press `Cmd+Shift+P` (or `Ctrl+Shift+P`)
2. Type and select: `FluxLoop: Run Flux Agent`

### Step 4: Choose a Mode

After clicking **Run Flux Agent**, the extension prompts you to pick a mode:

| Mode | When to use it | MCP context |
| --- | --- | --- |
| **Integration** | Need end-to-end integration guidance (default) | Repository profile + integration workflow |
| **Base Input** | Want new base input candidates or personas | `inputs/` samples + service settings |
| **Experiment** | Planning `simulation.yaml` or multi-turn scripts | Runner configs + recent experiments |
| **Insight** | Reviewing evaluation logs / telemetry | `experiments/*/summary.json`, metrics |

Each mode still analyzes your current file/selection, but emphasizes different MCP datasets before calling the LLM.

### Step 5: Review Suggestions

The agent opens a dedicated panel showing:

- **Summary**: Overview of detected frameworks and recommended changes
- **Repository Analysis**: Detected languages, package managers, entry points
- **Suggested Changes**: Step-by-step integration instructions with code snippets
- **Validation Checklist**: Post-integration verification steps
- **References**: Citations to source documentation

### Step 6: Apply Changes

Review each suggested change and apply manually:

1. **Copy Code Snippets**: Click copy buttons or select and copy
2. **Navigate to Anchors**: Agent tells you where to insert code
3. **Verify**: Run suggested validation commands (e.g., `npm run lint`)

## Example Workflow

### Express.js Integration

**Scenario**: You want to trace API requests in an Express app.

1. Open `src/server.ts`
2. Highlight the Express app initialization code:
   ```typescript
   const app = express();
   app.use(express.json());
   ```
3. Run Flux Agent

**Sample Suggestion:**

```markdown
# Flux Agent Suggestion

## Summary
Detected Express.js application. Recommended integration using HTTP REST runner pattern.

## Repository Analysis
- **Framework**: Express (confidence: 0.95)
- **Language**: TypeScript
- **Package Manager**: npm
- **Entry Points**: src/server.ts

## Suggested Changes

### 1. Install FluxLoop SDK
```bash
npm install @fluxloop/sdk
```

### 2. Add SDK Import and Middleware
**File**: `src/server.ts`
**Anchor**: After `const app = express();`

Add:
```typescript
import { fluxloop } from '@fluxloop/sdk';

app.use(fluxloop({ 
  projectKey: process.env.FLUXLOOP_PROJECT_KEY 
}));
```

### 3. Configure Runner
**File**: `configs/simulation.yaml`

Add:
```yaml
runner:
  http:
    method: POST
    url: "http://localhost:3000/api/chat"
    headers:
      Content-Type: application/json
```

## Validation Checklist
- [ ] Run `npm run build` - ensure no TypeScript errors
- [ ] Start server and verify `/health` endpoint responds
- [ ] Run `fluxloop run` to test integration

## References
- packages/website/docs-sdk/integration/express.md
- packages/website/docs-cli/configuration/runners/http-rest.md
```

## Understanding Suggestions

### Section: Summary
High-level overview of what the agent detected and recommends. Gives you quick context.

### Section: Repository Analysis
Raw data from MCP `run_integration_workflow` tool showing:
- Detected frameworks with confidence scores
- Languages and package managers
- Entry points and risk flags

### Section: Suggested Changes
Step-by-step instructions with:
- **File paths**: Where to make changes
- **Anchors**: Code patterns to locate insertion points
- **Code snippets**: Ready-to-copy code blocks
- **Context**: Why this change is needed

### Section: Validation Checklist
Post-integration verification steps:
- Build commands to ensure no errors
- Test endpoints or functions
- Linting and type-checking

### Section: References
Source documentation links (citations from MCP server).

## Tips for Better Suggestions

### 1. Provide Clear Context

- Select the exact code block you want to enhance
- Open the main entry point file (e.g., `server.ts`, `main.py`)
- Ensure your `configs/` directory exists for better project analysis

### 2. Use Specific Selections

❌ **Select entire file** (agent gets overwhelmed)  
✅ **Select the middleware section or route handler**

### 3. Iterate

If the first suggestion isn't perfect:
- Adjust your code selection
- Run Flux Agent again with refined context
- Each run is stored in **Recent Suggestions**

### 4. Combine with Knowledge Search

Before running Flux Agent:
1. Use **Knowledge Search** to understand concepts
2. Then use **Flux Agent** for specific integration steps

## Advanced: Customizing Prompts

The agent constructs prompts with these sections:

1. **User Goal**: "Generate FluxLoop integration suggestions"
2. **File Context**: Current file path and content (truncated to 4000 chars)
3. **Selection**: Highlighted code block (if any)
4. **MCP Analysis**: Repository profile, frameworks, and edit plan
5. **Output Format**: Structured Markdown with sections

The LLM combines all these inputs to generate contextualized suggestions.

## Viewing History

All Flux Agent runs are stored in **Recent Suggestions**:

1. Expand **Integration** → **Recent Suggestions**
2. Click any entry to reopen the full suggestion panel
3. History includes:
   - File path and selection
   - MCP workflow results
   - LLM-generated suggestion

History is limited to the 5 most recent suggestions per project.

## Next Steps

- [Knowledge Search](./knowledge-search.md) - Search documentation
- [Integration View](../views/integration-view.md) - View reference
- [Troubleshooting](./troubleshooting.md) - Common issues

