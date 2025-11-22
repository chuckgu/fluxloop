---
sidebar_position: 1
---

# Creating Projects

Learn how to create and manage FluxLoop projects in VSCode.

## Prerequisites

1. **FluxLoop CLI and SDK installed**
   ```bash
   pip install fluxloop-cli fluxloop
   ```

2. **FluxLoop VSCode Extension installed**
   - Open VSCode Extensions (Cmd+Shift+X)
   - Search for "FluxLoop"
   - Click Install

## Creating Your First Project

### Method 1: Default Flow (Recommended)

1. **Launch the wizard**
   - Click **Create New Project…** in the Projects view  
   - or run `FluxLoop: Create FluxLoop Project`
2. **Select the flow**
   - Choose **Default (Recommended)**
3. **Name your FluxLoop project**
   - Enter a name (preview shows `~/FluxLoopProjects/<name>` by default)  
   - The shared root is configurable via **Settings → FluxLoop → Project Root**
4. **Pick an environment**
   - Auto-detected interpreters (workspace `.venv`, Poetry, Conda, pyenv) are listed first
   - QuickPick includes:
     - ⭐ Detected workspace environment
     - 📂 **Choose another environment…** (browse to any folder)
     - ⚠️ **Use system Python** (fallback)
   - Missing package dialog offers automatic install, manual terminal, or re-select options
5. **Include sample agent (optional)**
6. **Finish**
   - `fluxloop init project` runs inside the shared root
   - Project is registered and activated in VSCode

### Method 2: Custom Flow (Advanced)

Use this when you need to place the FluxLoop project alongside your source repo or manage multiple envs manually.

1. **Launch the wizard** (`FluxLoop: Create FluxLoop Project`)
2. **Choose Custom (Advanced)**
3. **Pick FluxLoop project folder**
4. **Enter project name** (created inside the folder you picked)
5. **Select environment**
   - Create a `.venv` inside the project or browse to any interpreter
6. **Include sample agent (optional)**
7. **Finish**
   - Same initialization steps as Default flow, but settings (`fluxloop.targetSourceRoot`, `fluxloop.executionMode`) are saved relative to the custom folder

## Project Structure

After creation, your project contains:

```
~/FluxLoopProjects/my-chatbot/        # Default flow result (configurable)
├── configs/
│   ├── project.yaml       # Project metadata
│   ├── input.yaml         # Input generation
│   ├── simulation.yaml    # Experiment config
│   └── evaluation.yaml    # Evaluators
├── .env                   # Environment variables
├── examples/
│   └── simple_agent.py    # Sample agent
├── experiments/           # Results (created on run)
├── inputs/                # Generated inputs
└── recordings/            # Recorded args (optional)
```

> Custom flow places the project wherever you choose, but the directory structure is identical.

## Configuring Your Project

### 1. Update Project Metadata

Click on **Projects** → **Your Project** → **Configure**

Edit `configs/project.yaml`:
```yaml
project:
  name: my-chatbot
  version: "1.0.0"
  description: "Customer support chatbot"
```

### 2. Add Your Agent Code

Replace the example agent:

```python
# examples/chatbot.py
import fluxloop

@fluxloop.agent()
def run(user_message: str) -> str:
    """Your chatbot logic"""
    response = generate_response(user_message)
    return response
```

Update `configs/simulation.yaml`:
```yaml
runner:
  target: "examples.chatbot:run"
```

### 3. Define Personas and Inputs

Click **Inputs** → **Base Inputs** → Edit

Add to `configs/input.yaml`:
```yaml
personas:
  - name: frustrated_customer
    description: Customer with unresolved issue
  
  - name: new_customer
    description: First-time user

base_inputs:
  - input: "I've been waiting for 3 days!"
    persona: frustrated_customer
  
  - input: "How do I create an account?"
    persona: new_customer
```

## Managing Multiple Projects

### Add Existing Project

If you already have a FluxLoop project (Default or Custom flow):

1. **Command Palette** → `FluxLoop: Add Existing FluxLoop Project`
2. Select the project directory (the folder containing `configs/`)
3. Project added to Projects view (shared root detection is optional)

### Switch Between Projects

Click on any project in the Projects view to make it active.

The status bar shows the active project:
```
FluxLoop: my-chatbot
```

### Remove Project

Right-click project → **Remove Project**

This only removes from VSCode, doesn't delete files.

## Project Status Indicators

The Projects view shows status for each project:

- ✅ **Green check**: Configuration valid
- ⚠️ **Yellow warning**: Configuration issues
- ❌ **Red X**: Missing required files

Click on the status icon to see details.

## Best Practices

### 1. One Project Per Agent

Create separate projects for different agents:
```
fluxloop/
├── customer-support/
├── sales-assistant/
└── technical-qa/
```

### 2. Version Control

Initialize git in your project:
```bash
cd fluxloop/my-chatbot
git init
git add configs/ examples/
git commit -m "Initial project setup"
```

Add `.gitignore`:
```
.env
experiments/
inputs/generated.yaml
recordings/
```

### 3. Environment Variables

Store secrets in `.env` (never commit):
```bash
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
```

### 4. Start Simple

Begin with:
- 3-5 personas
- 5-10 base inputs
- 10 iterations per input

Expand as you validate the setup.

## Troubleshooting

### "CLI Not Found"

Install FluxLoop CLI:
```bash
pip install fluxloop-cli
```

Check status in **Status** view.

### "Invalid Configuration"

Click the warning icon to see specific issues:
- Missing required fields
- Invalid YAML syntax
- File path errors

### "Project Not Loading"

Ensure your project has:
- `configs/` directory
- Required YAML files
- Valid `.env` file

## Next Steps

- [Managing Inputs](./managing-inputs) - Generate and manage inputs
- [Running Experiments](./running-experiments) - Execute simulations
- [Viewing Results](./viewing-results) - Analyze experiment output
