---
title: AI Assistant Integration Guide - FluxLoop Complete Setup
audience: AI coding assistants (Cursor, Claude Code, GitHub Copilot, etc.)
purpose: Enable AI assistants to automatically integrate FluxLoop into user's agent code
---

# AI Assistant Guide: Integrating FluxLoop into Agent Code

## Context for AI Assistants

This guide provides step-by-step instructions for AI coding assistants to help users integrate FluxLoop SDK into their AI agent code and run the complete testing workflow. Follow these instructions sequentially when a user asks to "add FluxLoop" or "test my agent with FluxLoop."

---

## Quick Decision Tree

**Q: What does the user have?**

- ✅ Existing agent code → Go to [Section 1: Integration](#section-1-integration-steps)
- ❌ No agent code yet → Start with [Section 0: Setup New Project](#section-0-setup-new-project-optional)

**Q: What framework is the agent using?**

- LangChain → Use [LangChain Integration](#langchain-integration)
- LangGraph → Use [LangGraph Integration](#langgraph-integration)
- Custom/Other → Use [Generic Integration](#generic-integration)

---

## Section 0: Setup New Project (Optional)

If the user doesn't have an existing agent project:

```bash
# Install FluxLoop
pip install fluxloop-cli fluxloop

# Create new FluxLoop project
fluxloop init project --name <PROJECT_NAME>
cd fluxloop/<PROJECT_NAME>
```

This creates:
```
fluxloop/<PROJECT_NAME>/
├── setting.yaml          # Experiment configuration
├── .env                  # API keys and config
├── experiments/          # Results output directory
├── inputs/               # Generated inputs
└── recordings/           # Recorded function arguments
```

---

## Section 1: Integration Steps

### Step 1.1: Install FluxLoop SDK

Add to the user's project:

```bash
# If using pip
pip install fluxloop

# If using poetry
poetry add fluxloop

# If using requirements.txt
echo "fluxloop>=0.1.0" >> requirements.txt
pip install -r requirements.txt
```

### Step 1.2: Identify Target Function

**Ask the user (or infer from code):**

- What is the main entry point function for the agent?
- What are the function parameters?
- Is it sync or async?
- What framework is being used (if any)?

**Common patterns to look for:**

```python
# Pattern 1: WebSocket/Socket.IO handler
async def handle_message(connection_id, data, session, callbacks):
    ...

# Pattern 2: HTTP endpoint handler
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    ...

# Pattern 3: LangChain agent
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(...)
result = agent_executor.invoke({"input": user_input})

# Pattern 4: LangGraph workflow
from langgraph.graph import StateGraph
workflow = StateGraph(...)
result = workflow.invoke(initial_state)

# Pattern 5: Generic function
def process_user_query(query: str, context: dict):
    ...
```

### Step 1.3: Add FluxLoop Imports

At the top of the target file, add:

```python
import fluxloop
from fluxloop import trace, FluxLoopClient

# Optional: For explicit configuration
# from fluxloop import configure
```

---

## Section 2: Framework-Specific Integration

### LangChain Integration

#### Option A: Decorate AgentExecutor calls

```python
from fluxloop import trace
from langchain.agents import AgentExecutor

# Existing code
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Add FluxLoop tracing
@trace()
def run_agent(user_input: str):
    """Traced agent execution"""
    result = agent_executor.invoke({"input": user_input})
    return result

# Usage
result = run_agent("What is the weather today?")
```

#### Option B: Use LangChain callbacks (if available)

```python
from fluxloop.integrations.langchain import FluxLoopCallbackHandler

# When running the agent
callbacks = [FluxLoopCallbackHandler()]
result = agent_executor.invoke(
    {"input": user_input},
    config={"callbacks": callbacks}
)
```

### LangGraph Integration

```python
from fluxloop import trace
from langgraph.graph import StateGraph

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("action", action_node)
# ... graph setup ...
app = workflow.compile()

# Wrap the entire workflow invocation
@trace()
def run_workflow(initial_input: dict):
    """Traced LangGraph workflow"""
    result = app.invoke(initial_input)
    return result

# Usage
result = run_workflow({"messages": [user_message]})
```

### Generic Integration

For custom agents or any Python function:

```python
from fluxloop import trace

@trace()
async def handle_user_request(
    user_id: str,
    message: str,
    session_data: dict,
    callbacks: dict
):
    """
    Your agent logic with FluxLoop tracing.
    FluxLoop automatically captures:
    - Function inputs (user_id, message, session_data, callbacks)
    - Function outputs (return value)
    - Any LLM calls made during execution (if using OpenAI/Anthropic/etc)
    - Execution time and errors
    """
    # Your existing agent logic here
    response = await your_agent_logic(message, session_data)
    
    # Optional: Send to callback
    if callbacks.get('send'):
        await callbacks['send'](response)
    
    return response
```

---

## Section 3: Recording Production Context

To replay tests with realistic production context (session data, callbacks, etc.), record actual function calls:

### Step 3.1: Configure Recording

Add at application startup:

```python
import fluxloop

# In your main.py or app initialization
fluxloop.configure(
    record_args=True,
    recording_file="./recordings/args.jsonl"
)
```

### Step 3.2: Record Function Arguments

Add recording call inside the target function:

```python
@trace()
async def handle_message(connection_id, data, user_session, send_callback, error_callback):
    # Record the actual arguments for replay
    fluxloop.record_call_args(
        target="app.handler:MessageHandler.handle_message",  # Module:Class.method format
        connection_id=connection_id,
        data=data,
        user_session=user_session,
        send_callback=send_callback,
        error_callback=error_callback,
    )
    
    # Your agent logic
    result = await process_message(data, user_session)
    await send_callback(result)
    return result
```

### Step 3.3: Trigger Recording

Ask the user to:

1. Run the application normally (dev/staging environment)
2. Trigger the agent with ONE real request
3. Check that `recordings/args.jsonl` was created

---

## Section 4: FluxLoop Project Setup

### Step 4.1: Initialize FluxLoop Directory

Create FluxLoop workspace in the project:

```bash
# Create directories
mkdir -p fluxloop/my-test
cd fluxloop/my-test
mkdir -p experiments inputs recordings
```

### Step 4.2: Create Configuration File

Create `setting.yaml`:

```yaml
# FluxLoop Configuration
project_name: "my-agent-test"

# Target function to test
runner:
  target: "app.handler:MessageHandler.handle_message"  # Update this path
  working_directory: "../.."  # Path to project root from this config file

# Input generation settings
input_generation:
  provider: "openai"  # or "anthropic"
  model: "gpt-4o-mini"
  prompt: |
    Generate diverse user messages for a customer support agent.
    Vary the following:
    - Tone: polite, frustrated, confused, angry, casual
    - Length: very short (1-3 words), short, medium, long (100+ words)
    - Language: English, mix of languages, typos, slang
    - Edge cases: empty strings, special characters, emojis, code snippets
    - Content: simple requests, complex multi-part requests, unclear intent

# Argument replay settings (if using recorded args)
replay_args:
  enabled: true
  recording_file: "recordings/args.jsonl"
  override_param_path: "data.content"  # Which parameter to replace with generated inputs
  callable_providers:
    send_callback: "builtin:collector.send"  # Mock callback for testing
    error_callback: "builtin:collector.error"

# Experiment settings
inputs_file: "inputs/generated.yaml"
iterations: 50  # Number of test cases to run
output_directory: "experiments"
experiment_name: "variation-test"

# Optional: LLM tracing
collector:
  enabled: true
  endpoint: "http://localhost:8000"  # Optional: FluxLoop collector service
```

### Step 4.3: Create Environment File

Create `.env` file:

```bash
# API Keys for LLM providers
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# FluxLoop settings (optional)
FLUXLOOP_ENV=development
FLUXLOOP_PROJECT_ID=my-agent
```

---

## Section 5: Generate Test Inputs

### Step 5.1: Generate Inputs from Recording

If you have a recording file:

```bash
fluxloop generate inputs \
  --config setting.yaml \
  --from-recording recordings/args.jsonl \
  --limit 100
```

This creates `inputs/generated.yaml` with 100 variations.

### Step 5.2: Generate Inputs from Scratch

If no recording, create a manual template first:

Create `inputs/template.yaml`:

```yaml
inputs:
  - persona: "baseline"
    data:
      content: "Hello, I need help with my order"
      metadata:
        channel: "web"
```

Then generate variations:

```bash
fluxloop generate inputs \
  --config setting.yaml \
  --from-template inputs/template.yaml \
  --limit 100
```

### Step 5.3: Verify Generated Inputs

Check `inputs/generated.yaml`:

```bash
head -50 inputs/generated.yaml
```

You should see variations like:

```yaml
inputs:
  - persona: "polite_formal"
    data:
      content: "Good morning, I would like assistance with tracking my recent order."
  - persona: "frustrated_caps"
    data:
      content: "WHERE IS MY ORDER??? I'VE BEEN WAITING FOR WEEKS!!!"
  - persona: "minimal_typo"
    data:
      content: "hy cn u hlp me"
  # ... 97 more variations
```

---

## Section 6: Run Experiments

### Step 6.1: Execute Test Run

```bash
fluxloop run experiment --config setting.yaml
```

**What happens:**
1. FluxLoop loads the 100 generated inputs
2. For each input, it calls your target function with:
   - The varied input (replacing `data.content` or specified param)
   - Real recorded context (session, callbacks, etc.)
3. Captures all LLM calls, timings, outputs
4. Writes results to `experiments/<name>_<timestamp>/`

### Step 6.2: Monitor Progress

The CLI shows real-time progress:

```
Running experiment: variation-test
Progress: [====================] 100/100 (100%)
Success: 85 | Failed: 15 | Duration: 3m 24s
```

### Step 6.3: Check Results Directory

```bash
ls -la experiments/variation-test_20241022_143052/
```

Output files:
- `summary.json` - Overall stats (success rate, avg duration, etc.)
- `trace_summary.jsonl` - One line per test case
- `observations.jsonl` - Detailed step-by-step traces
- `traces.jsonl` - Full execution traces

---

## Section 7: Analyze Results

### Step 7.1: Parse to Human-Readable Format

```bash
fluxloop parse experiment \
  experiments/variation-test_20241022_143052 \
  --output per_trace_analysis \
  --overwrite
```

This creates individual Markdown files for each test case:

```
experiments/variation-test_20241022_143052/per_trace_analysis/
├── 00_polite_formal.md
├── 01_frustrated_caps.md
├── 02_minimal_typo.md
├── ...
└── 99_edge_case_empty.md
```

### Step 7.2: Review Failures

Open the parsed files to see exactly what happened:

```markdown
# Trace Analysis: frustrated_caps

**Trace ID:** 9eb64d0d-7bbf-41d0-9226-0bfc86892109  
**Persona:** frustrated_caps  
**Status:** ❌ Failed  
**Duration:** 2.3s  

## Input
```json
{
  "content": "WHERE IS MY ORDER??? I'VE BEEN WAITING FOR WEEKS!!!"
}
```

## Output
```json
{
  "error": "Unable to process request - missing order ID"
}
```

## Timeline
1. **Agent Start** (0.0s)
2. **LLM Call - Intent Recognition** (0.1s)
   - Model: gpt-4o-mini
   - Detected intent: "order_tracking"
   - Failed to extract order_id
3. **Error Handler** (2.1s)
   - Reason: Required field 'order_id' missing
```

### Step 7.3: Identify Patterns

Look for common failure patterns:

```bash
# Count failures by type
grep -h "Status: ❌" experiments/*/per_trace_analysis/*.md | wc -l

# Find all failed cases
grep -l "Status: ❌" experiments/*/per_trace_analysis/*.md
```

---

## Section 8: Iterate and Improve

### Step 8.1: Fix Identified Issues

Based on failures, update agent code:

```python
# Before: Agent fails on angry/caps input
@trace()
async def handle_message(connection_id, data, user_session, callbacks):
    # Missing input normalization
    result = await process(data['content'])
    return result

# After: Add input preprocessing
@trace()
async def handle_message(connection_id, data, user_session, callbacks):
    # Normalize input
    content = data['content'].strip().lower()
    
    # Validate
    if not content:
        return {"error": "Empty message", "fallback": "human_agent"}
    
    # Add context to LLM prompt
    enhanced_prompt = f"""
    User message (may be frustrated, use caps, or have typos): {data['content']}
    Original tone: preserve but respond professionally
    """
    
    result = await process(enhanced_prompt, user_session)
    return result
```

### Step 8.2: Regenerate Inputs (Optional)

Update generation prompt in `setting.yaml` to focus on specific edge cases:

```yaml
input_generation:
  prompt: |
    Generate customer support messages focusing on:
    - Missing order IDs (implicit vs explicit)
    - Extreme frustration with profanity
    - Multi-language mixing
    - Very long rambling messages (200+ words)
```

### Step 8.3: Re-run Tests

```bash
# Generate new inputs with updated prompt
fluxloop generate inputs --config setting.yaml --limit 100

# Run experiment again
fluxloop run experiment --config setting.yaml

# Compare results
fluxloop parse experiment experiments/<new_experiment_dir>
```

---

## Section 9: Common Integration Patterns

### Pattern 1: WebSocket Handler

```python
from fluxloop import trace
import socketio

sio = socketio.AsyncServer()

@sio.on('message')
@trace()
async def handle_socket_message(sid, data):
    """FluxLoop traces every WebSocket message"""
    fluxloop.record_call_args(
        target="app:handle_socket_message",
        sid=sid,
        data=data
    )
    
    response = await agent.process(data['content'])
    await sio.emit('response', response, room=sid)
    return response
```

### Pattern 2: FastAPI Endpoint

```python
from fastapi import FastAPI
from fluxloop import trace

app = FastAPI()

@app.post("/chat")
@trace()
async def chat_endpoint(request: ChatRequest):
    """FluxLoop traces every API request"""
    fluxloop.record_call_args(
        target="app:chat_endpoint",
        request=request.dict()
    )
    
    result = await agent.chat(request.message, request.session_id)
    return {"response": result}
```

### Pattern 3: Discord Bot

```python
import discord
from fluxloop import trace

client = discord.Client()

@client.event
@trace()
async def on_message(message):
    """FluxLoop traces every Discord message"""
    if message.author == client.user:
        return
    
    fluxloop.record_call_args(
        target="bot:on_message",
        message=message.content,
        author=message.author.name,
        channel=message.channel.name
    )
    
    response = await agent.process(message.content)
    await message.channel.send(response)
```

### Pattern 4: Slack Bot

```python
from slack_bolt.async_app import AsyncApp
from fluxloop import trace

app = AsyncApp()

@app.event("message")
@trace()
async def handle_message_events(event, say):
    """FluxLoop traces every Slack message"""
    fluxloop.record_call_args(
        target="slack_bot:handle_message_events",
        event=event,
        user=event['user'],
        text=event['text']
    )
    
    response = await agent.process(event['text'])
    await say(response)
```

---

## Section 10: Troubleshooting

### Issue 1: Import Error

**Error:** `ModuleNotFoundError: No module named 'fluxloop'`

**Solution:**
```bash
pip install fluxloop
# or
pip install --upgrade fluxloop
```

### Issue 2: Target Function Not Found

**Error:** `Could not import target: app.handler:MessageHandler.handle_message`

**Solution:**
- Check the module path is correct
- Ensure the file is in PYTHONPATH
- Use absolute imports
- Update `runner.working_directory` in `setting.yaml`

**Debug:**
```bash
# From the working_directory, try:
python -c "from app.handler import MessageHandler; print(MessageHandler.handle_message)"
```

### Issue 3: Recording File Not Created

**Error:** `FileNotFoundError: recordings/args.jsonl`

**Solution:**
```python
# Ensure configure() is called before any recording
import fluxloop

fluxloop.configure(
    record_args=True,
    recording_file="./recordings/args.jsonl"  # Full path recommended
)

# Create directory if needed
import os
os.makedirs("recordings", exist_ok=True)
```

### Issue 4: No LLM Calls Captured

**Issue:** Trace shows execution but no LLM calls

**Solution:**
- Ensure you're using supported LLM clients (OpenAI, Anthropic, LangChain)
- FluxLoop auto-instruments these libraries
- For custom clients, wrap them:

```python
from fluxloop import trace_llm_call

response = trace_llm_call(
    provider="custom",
    model="my-model",
    messages=[{"role": "user", "content": prompt}],
    call_fn=lambda: my_custom_llm_client.chat(prompt)
)
```

### Issue 5: Experiment Runs But No Output

**Error:** `experiments/` directory empty

**Solution:**
- Check `output_directory` in `setting.yaml`
- Ensure write permissions
- Check for errors in the console output
- Verify `iterations` > 0

### Issue 6: Input Generation Fails

**Error:** `OpenAI API key not found`

**Solution:**
```bash
# Set API key
export OPENAI_API_KEY=sk-...

# Or in .env file
echo "OPENAI_API_KEY=sk-..." >> .env

# Or in setting.yaml
input_generation:
  api_key: "sk-..."  # Not recommended, use env vars
```

---

## Section 11: AI Assistant Workflow Checklist

When helping a user integrate FluxLoop, follow this checklist:

### Phase 1: Discovery
- [ ] Identify the main agent entry point function
- [ ] Determine if it's sync or async
- [ ] Check what framework is being used (if any)
- [ ] List all function parameters
- [ ] Ask if user wants to record production context

### Phase 2: Installation
- [ ] Add `fluxloop` to dependencies
- [ ] Install via pip/poetry/requirements.txt
- [ ] Verify installation: `python -c "import fluxloop; print(fluxloop.__version__)"`

### Phase 3: Code Integration
- [ ] Add imports at top of file
- [ ] Add `@trace()` decorator to target function
- [ ] (Optional) Add `fluxloop.record_call_args()` for replay
- [ ] (Optional) Add `fluxloop.configure()` at startup
- [ ] Test that code still runs normally

### Phase 4: FluxLoop Project Setup
- [ ] Create `fluxloop/` directory structure
- [ ] Create `setting.yaml` configuration
- [ ] Create `.env` with API keys
- [ ] Update paths in config to match project structure

### Phase 5: Recording (Optional)
- [ ] User runs application normally
- [ ] User triggers agent with real request
- [ ] Verify `recordings/args.jsonl` was created
- [ ] Inspect recording to confirm data looks correct

### Phase 6: Input Generation
- [ ] Run `fluxloop generate inputs` command
- [ ] Verify `inputs/generated.yaml` was created
- [ ] Inspect first few inputs to confirm variety
- [ ] Adjust generation prompt if needed

### Phase 7: Experiment Execution
- [ ] Run `fluxloop run experiment` command
- [ ] Monitor progress in console
- [ ] Verify experiment completed
- [ ] Check that output directory was created

### Phase 8: Analysis
- [ ] Run `fluxloop parse experiment` command
- [ ] Review per-trace analysis files
- [ ] Identify patterns in failures
- [ ] Summarize findings for user

### Phase 9: Iteration
- [ ] Help user fix identified issues
- [ ] Re-run experiments
- [ ] Compare before/after results
- [ ] Repeat until satisfactory success rate

---

## Section 12: Code Templates for AI Assistants

### Template: Minimal Integration

Use this when user has a simple agent function:

```python
# Add this import at the top
from fluxloop import trace

# Add decorator to the main function
@trace()
def agent_function(user_input: str) -> str:
    """Your agent logic"""
    # Existing code stays the same
    response = your_existing_logic(user_input)
    return response
```

### Template: Full Integration with Recording

Use this when user wants production context replay:

```python
import fluxloop
from fluxloop import trace

# At application startup (e.g., main.py)
fluxloop.configure(
    record_args=True,
    recording_file="./recordings/args.jsonl"
)

# In your handler file
@trace()
async def handle_request(param1, param2, param3):
    """Main agent entry point"""
    
    # Record arguments for replay
    fluxloop.record_call_args(
        target="<module_path>:<ClassName>.<method_name>",
        param1=param1,
        param2=param2,
        param3=param3
    )
    
    # Your existing agent logic
    result = await your_agent(param1, param2)
    
    return result
```

### Template: setting.yaml

Use this template and customize based on user's needs:

```yaml
project_name: "<PROJECT_NAME>"

runner:
  target: "<module>:<Class>.<method>"  # e.g., "app.handler:MessageHandler.handle_message"
  working_directory: "."  # Path to project root

input_generation:
  provider: "openai"
  model: "gpt-4o-mini"
  prompt: |
    <CUSTOMIZE_THIS_PROMPT>
    Generate diverse inputs for testing an AI agent.
    Vary tone, length, language, and edge cases.

replay_args:
  enabled: false  # Set to true if using recordings
  recording_file: "recordings/args.jsonl"
  override_param_path: "data.content"  # Which param to vary
  callable_providers: {}  # Add mock callbacks if needed

inputs_file: "inputs/generated.yaml"
iterations: 50
output_directory: "experiments"
experiment_name: "test-run"
```

---

## Section 13: Success Criteria

After integration, verify these outcomes with the user:

### ✅ Integration Success
- [ ] Agent code runs normally with `@trace()` decorator
- [ ] No errors or warnings from FluxLoop
- [ ] (Optional) Recording file created with valid data

### ✅ Generation Success
- [ ] `inputs/generated.yaml` contains desired number of variations
- [ ] Inputs show diverse patterns (tone, length, edge cases)
- [ ] Inputs are realistic for the agent's domain

### ✅ Experiment Success
- [ ] Experiment completes without crashes
- [ ] Output directory contains all expected files
- [ ] `summary.json` shows reasonable success/failure rates
- [ ] Per-trace analysis files are generated and readable

### ✅ Analysis Success
- [ ] User can identify failure patterns
- [ ] User understands why certain inputs failed
- [ ] User has actionable next steps for improvements

---

## Final Notes for AI Assistants

### Best Practices

1. **Always verify paths**: Before running commands, check that files exist and paths are correct
2. **Start small**: First test with 5-10 inputs, then scale to 50-100
3. **Explain as you go**: Help users understand what each step does
4. **Show examples**: When parsing results, show 1-2 actual traces
5. **Iterate**: FluxLoop is iterative - help users go through multiple cycles

### When to Skip Steps

- **Skip recording** if agent has simple inputs (just strings/numbers)
- **Skip recording** if user wants to manually create input variations
- **Skip generation** if user already has a test dataset
- **Skip parsing** if user prefers JSON analysis over Markdown

### Common User Requests

- "Add FluxLoop to my agent" → Full integration (Section 1-8)
- "Test my agent with different inputs" → Focus on generation and experiments (Section 5-7)
- "Why is my agent failing on these inputs?" → Analysis and iteration (Section 7-8)
- "How do I replay production scenarios?" → Recording and replay (Section 3)

---

**End of AI Assistant Guide**

For more details, see:
- [End-to-End Workflow](./end-to-end-workflow.md)
- [Virtual Environment Setup](./virtual-environment-setup.md)
- Main documentation: https://docs.fluxloop.dev

