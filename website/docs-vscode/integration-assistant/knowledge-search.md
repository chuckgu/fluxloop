---
sidebar_position: 3
---

# Knowledge Search

Use Knowledge Search to query FluxLoop documentation directly from VSCode without leaving your editor.

## How to Use

### Method 1: Integration View Button

1. Open the **FluxLoop** activity bar
2. Navigate to the **Integration** view
3. Click **Knowledge Search** button at the top
4. Enter your question in the input box

### Method 2: Command Palette

1. Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
2. Type and select: `FluxLoop: Open Knowledge Search`
3. Enter your question

## What You Can Ask

Knowledge Search is backed by the FluxLoop MCP server, which indexes:

- Official FluxLoop documentation
- SDK and CLI guides
- Framework-specific recipes
- Code examples and samples

### Example Queries

**Integration Questions:**
- "How do I integrate FastAPI with FluxLoop?"
- "What's the best runner pattern for Express.js?"
- "How to configure simulation.yaml for WebSocket handlers?"

**Troubleshooting:**
- "Why are my traces not showing up?"
- "How to fix recording mode errors?"
- "What does 'runner target not found' mean?"

**Configuration:**
- "How do I set up replay_args in simulation.yaml?"
- "What evaluation metrics are available?"
- "How to configure LLM input generation?"

## Understanding Results

Knowledge Search returns:

1. **Answer**: Synthesized response based on indexed documentation
2. **Citations**: Source file paths and sections where information was found
3. **Output**: Full response appears in the FluxLoop output channel

### Example Output

```
==========================================================
[MCP FAQ] How do I integrate FastAPI with FluxLoop?
----------------------------------------------------------
Answer:

To integrate FluxLoop SDK into a FastAPI application:

1. Install the SDK:
   pip install fluxloop

2. Add the @fluxloop.trace() decorator to your endpoint:
   
   from fluxloop import fluxloop
   
   @app.post("/chat")
   @fluxloop.trace()
   async def chat_endpoint(request: ChatRequest):
       # Your handler code
       pass

3. Configure configs/simulation.yaml with runner target:
   
   runner:
     target: "app.main:chat_endpoint"

Citations:
- packages/website/docs-sdk/integration/fastapi.md
- packages/website/docs-cli/configuration/runner-targets.md
```

## Tips for Better Results

### Be Specific

❌ **Too Vague**: "How to use FluxLoop?"  
✅ **Better**: "How do I trace a Next.js API route with FluxLoop SDK?"

### Include Context

❌ **Minimal**: "runner configuration"  
✅ **Better**: "How to configure runner for an async generator in Python?"

### Reference Your Stack

❌ **Generic**: "How to set up tracing?"  
✅ **Better**: "How to set up tracing in a NestJS controller with TypeScript?"

## Viewing Search History

Recent searches are stored in the **Integration** view under **Recent Suggestions**:

1. Expand **Recent Suggestions**
2. Click any entry to view the full result again
3. Results are stored per-project

## Clear History

To clear suggestion history:

1. Right-click on **Recent Suggestions** in the Integration view
2. Select **Clear History**

Or use Command Palette: `FluxLoop: Clear Integration Suggestion History`

## Troubleshooting

### "fluxloop-mcp package is not installed"

Install the MCP package:

```bash
pip install fluxloop-mcp
```

Then click **Connect MCP** in the Integration view.

### "MCP Index not found"

Build the knowledge index:

```bash
fluxloop-mcp rebuild-index
```

Or if you cloned the repo:

```bash
cd packages/mcp
./scripts/rebuild_index.sh
```

### "No response returned"

Check the FluxLoop output channel for detailed error messages. Common causes:

- Index not built or corrupted
- Python environment issues
- fluxloop-mcp not in PATH

## Next Steps

- [Using Flux Agent](./flux-agent.md) - Generate code integration suggestions
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

