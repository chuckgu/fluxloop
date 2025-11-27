**FluxLoop: Automatically Test AI Agents Against 100+ Input Variations (Open Source)**

**TL;DR:** Generate 100+ realistic input variations with LLM, replay them against your agent in realistic production contexts, get structured results showing exactly which scenarios succeed/fail.

---

**The Core Problem**

You built an AI agent. You test it with:

- ✅ "Hello, I need help with my order"
- ✅ "Can you check my account balance?"

It works! You deploy. Then users hit it with:

- ❌ "yo so like my thing isn’t working lol"
- ❌ "hi....... can someone help me...... its urgent........."
- ❌ "你好！我需要帮助" (unexpected language)
- ❌ "ORDER #12345 NOT RECEIVED!!!!" (all caps, no context)
- ❌ 500-word rambling message with 10 different requests

**You never tested these cases because:**

1. Writing 100 test cases manually is tedious
2. You don't know what edge cases exist
3. Running them requires production-like context (callbacks, session data, etc.)

---

**FluxLoop's Solution: Automated Input Variation + Context Replay**

### The Workflow

```python
# 1. Record ONE real call from staging (with all context)
@fluxloop.agent()
async def handle_message(connection_id, data, user_session, callbacks):
    result = await your_agent_logic(data)
    return result

fluxloop.record_call_args(target="app:handle_message", **all_kwargs)
# Captures: connection_id, session data, callbacks, everything

```

```bash
# 2. Generate 100 input variations automatically
fluxloop generate inputs \\
  --config setting.yaml \\
  --from-recording recordings/args.jsonl \\
  --limit 100

# This creates variations like:
# - Formal: "Good morning, I require assistance with order tracking."
# - Casual: "hey can u check where my package is"
# - Frustrated: "THIS IS THE 3RD TIME I'M ASKING!!!"
# - Multilingual: Mix of languages
# - Edge cases: Empty, very long, special characters, etc.

```

```yaml
# 3. Configure what to vary
# setting.yaml
input_generation:
  provider: "openai"
  model: "gpt-4o-mini"
  prompt: |
    Generate diverse customer support inquiries with different:
    - Tones (polite, frustrated, confused)
    - Lengths (short, verbose)
    - Languages (English, Spanglish, etc.)
    - Edge cases (typos, all caps, emojis)

```

```bash
# 4. Run simulation with ALL variations
fluxloop run experiment --config setting.yaml

# FluxLoop:
# - Loads the recorded production context (session, callbacks, etc.)
# - Replays it 100 times, each with a different input
# - Your agent runs with REAL code, REAL LLM calls
# - Generates structured artifacts

```

**Results:**

```
experiments/exp_20241005/
├── summary.json          # 100 runs: 85 success, 15 failed
├── trace_summary.jsonl   # Per-input results
├── observations.jsonl    # Every LLM call, every step
└── per_trace_analysis/   # Human-readable breakdown
    ├── 00_polite_inquiry.md        ✅ Success
    ├── 01_all_caps_angry.md        ❌ Failed (why?)
    ├── 02_multilingual.md          ✅ Success
    └── ...

```

---

**Why This Matters**

### Before FluxLoop:

```python
# Manual testing
test_input_1 = "Hello, help me"
test_input_2 = "I need support"
test_input_3 = "Can you assist?"
# ... do you write 100 of these? No.

```

### With FluxLoop:

```bash
# Automatic generation
fluxloop generate inputs --limit 100
# → 100 diverse, realistic variations in 30 seconds

```

### The Real Value:

✅ **Discover edge cases you never thought of**

✅ **See exactly which input patterns break your agent**

✅ **Replay with real production context** (no manual mocking)

✅ **Reproducible results** for debugging

✅ **Iterate fast**: change prompt → regenerate 100 variations → re-run

---

**Real Example: Customer Support Bot**

**Recorded context (once):**

- `user_session`: {"user_id": "123", "tier": "premium", "history": [...]}
- `send_callback`: Real WebSocket sender
- `db_connection`: Real database connection

**Generated inputs (100 variations):**

1. "Hi, my order #5432 hasn't arrived yet"
2. "YO WHERE IS MY STUFF"
3. "Buenos días, necesito ayuda con mi pedido"
4. "........................hello"
5. [empty string]
6. "I ordered something last week and I think it was supposed to arrive yesterday but I'm not sure and also I have another question about my account and..."
... 94 more

**Simulation results:**

- ✅ 78 handled correctly
- ⚠️ 15 needed fallback to human agent (acceptable)
- ❌ 7 crashed or gave wrong answers (need fixes!)

**The 7 failures reveal:**

- Agent can't handle empty input → add validation
- Multi-language not supported → add detection
- Very long inputs truncate critical info → fix prompt window

**Without FluxLoop, you'd never find these before production.**

---

**Key Features**

### 🎯 LLM-Powered Input Generation

- Define generation strategy in plain English
- Automatic variation across: tone, length, language, edge cases
- Use your own prompts or built-in templates

### 🔄 Context Replay (No Manual Mocking)

- Record real function calls with all arguments
- Replay with different inputs, same context
- Works with callbacks, WebSocket handlers, database connections

### 🧪 Offline-First Simulation

- Everything runs locally
- No cloud dependencies during simulation
- Your data never leaves your machine

### 📊 Structured Artifacts

- JSON/JSONL output for programmatic analysis
- Human-readable Markdown timelines
- Compatible with any evaluation backend

### 🚀 Framework-Agnostic

- Works with LangChain, LangGraph, AutoGPT, custom agents
- Just add `@fluxloop.agent()` decorator
- Python 3.9+

---

**Getting Started (5 minutes)**

```bash
pip install fluxloop-cli fluxloop

# Initialize project
fluxloop init project --name my-agent
cd fluxloop/my-agent

# Configure LLM for input generation
export OPENAI_API_KEY=sk-...

# Generate 50 input variations
fluxloop generate inputs --config setting.yaml --limit 50

# Run simulation
fluxloop run experiment --config setting.yaml

# Parse results to human-readable format
fluxloop parse experiment experiments/<latest>/

```

⭐ GitHub: [[link]](https://github.com/chuckgu/fluxloop)

---

**Why Open Source?**

AI agent testing is a universal problem. We need:

- **Community-driven input generation strategies**
- **Standard evaluation contracts**
- **Framework integrations**
- **Novel evaluation methodologies**

**We're looking for contributors who want to:**

- 🔧 Build input generators for specific domains (medical, legal, finance)
- 🧪 Develop evaluation metrics and scoring systems
- 📝 Create integration guides for popular frameworks
- 🎨 Improve CLI/VSCode extension UX

**Early contributors define the standard.** This is foundational infrastructure for AI reliability.

---

**FAQ**

*Q: How is input generation different from unit tests?*

A: Unit tests use fixed inputs you write manually. FluxLoop generates diverse, realistic variations automatically using LLM.

*Q: Can I use my own input generation logic?*

A: Yes! Bring your own generator or use FluxLoop's LLM-based one.

*Q: Does this replace LangSmith/Helicone?*

A: No. Those monitor production. FluxLoop simulates pre-production. Use both.

*Q: What if my agent uses GPT-4?*

A: Each simulation run makes real LLM calls. You can see token usage in `summary.json`.

*Q: How fast is it?*

A: Generating 100 inputs: ~30 seconds. Running 100 simulations: depends on your agent (parallel execution supported).

---

**License:** Apache 2.0

**Start testing your agent properly.** 🚀