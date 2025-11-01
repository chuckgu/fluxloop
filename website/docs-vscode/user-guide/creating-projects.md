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

### Method 1: From Activity Bar

1. **Open FluxLoop Activity Bar**
   - Click the FluxLoop icon in the Activity Bar (left sidebar)

2. **Click "Create New Project"**
   - In the Projects view, click the "+" button
   - Or use the "Create FluxLoop Project" button

3. **Enter Project Details**
   - Project name: `my-chatbot`
   - Parent directory: Select where to create the project

4. **Project Created!**
   - New project structure created in `fluxloop/my-chatbot/`
   - Automatically set as active project

### Method 2: From Command Palette

1. **Open Command Palette**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)

2. **Run Command**
   ```
   FluxLoop: Create FluxLoop Project
   ```

3. **Follow Prompts**
   - Enter project name
   - Select parent directory

## Project Structure

After creation, your project contains:

```
fluxloop/my-chatbot/
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

If you already have a FluxLoop project:

1. **Command Palette** → `FluxLoop: Add Existing FluxLoop Project`
2. Select the project directory
3. Project added to Projects view

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
