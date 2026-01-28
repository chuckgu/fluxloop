---
sidebar_position: 3
---

# First Test

Run your first FluxLoop agent test end-to-end.

## Prerequisites

- FluxLoop CLI installed (`pip install fluxloop-cli`)
- Python 3.8+ environment
- FluxLoop API Key (from [app.fluxloop.ai](https://app.fluxloop.ai))

## Step 1: Create Your Project

```bash
# Initialize a new FluxLoop project
fluxloop init scenario --name my-first-agent

# Navigate to project directory
cd my-first-agent
```

**What you get:**

```
my-first-agent/
├── fluxloop.yaml          # Main configuration file
├── .env                   # Environment variables
├── src/
│   └── agent.py           # Sample agent code
├── results/               # Local test results
└── scenarios/             # Test scenarios
```

## Step 2: Authenticate

Set up your API key to connect to the Web Platform:

```bash
fluxloop auth login
# Enter your API key when prompted
```

This saves your credentials securely and enables cloud features like scenario syncing and result uploading.

## Step 3: Review Sample Agent

Open `src/agent.py` to see a basic instrumented agent:

```python
import fluxloop

@fluxloop.agent(name="SimpleAgent")
def run(input_text: str) -> str:
    """A simple echo agent that responds to user input."""
    return f"Echo: {input_text}"
```

The agent is already configured in `fluxloop.yaml`:

```yaml
runner:
  target: "src.agent:run"
  type: python-function
```

## Step 4: Generate Test Inputs

Create variations of base inputs for testing:

```bash
# Generate 10 input variations
fluxloop generate --limit 10
```

**Output:**

```
Generating inputs...
✓ Generated 10 input variations
✓ Saved to local bundle
```

## Step 5: Run Your First Test

Execute the test with generated inputs:

```bash
fluxloop test
```

**What happens:**

1. Loads inputs from the local bundle
2. Calls your agent function for each input
3. Captures performance metrics and traces
4. Saves results to `./results/`

**Output:**

```
Running tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 10/10 [00:05]

✓ Test completed!
Local results: ./results/run_20250128_120000/
```

## Step 6: Upload Results

Upload your results to the Web Platform for visualization and analysis:

```bash
fluxloop sync upload
```

**Output:**

```
Uploading results...
✓ Results uploaded successfully
📊 View on Web: https://results.fluxloop.ai/run/run_20250128_120000
```

Open the link to see:
- Interactive conversation traces
- Token usage and cost analysis
- Latency breakdown
- Success/failure status

## Step 7: Test Against a Scenario

Try pulling a curated scenario from the Web Platform and testing against it:

```bash
# Pull a scenario (replace with your scenario ID)
fluxloop sync pull --scenario onboarding-tests

# Run test against the scenario
fluxloop test --scenario onboarding-tests --upload
```

The `--upload` flag automatically uploads results after the test completes.

## Congratulations! 🎉

You've successfully:

✅ Created a FluxLoop project  
✅ Authenticated with the platform  
✅ Generated test inputs  
✅ Run a local test  
✅ Uploaded results to the cloud  
✅ Tested against a scenario  

## Next Steps

- **[Installation Guide](./installation)** - Detailed setup for various environments
- **[CLI Reference](../commands/test)** - Full command documentation
- **[Web Platform Guide](/docs/platform/platform-overview)** - Learn about cloud features
- **[Claude Code Integration](/claude-code/)** - Test agents directly in your IDE
