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

Best for most users—FluxLoop reuses your open workspace as the agent source, auto-detects its environment, and places the FluxLoop configs in a shared root (`~/FluxLoopProjects` by default).

1. **Launch the wizard**  
   - Projects view → **Create New Project…**  
   - or Command Palette → `FluxLoop: Create FluxLoop Project`
2. **Choose flow → Default (Recommended)**
3. **Name your project** (preview shows target location, e.g. `~/FluxLoopProjects/support-agent`)
4. **Select environment**  
   - Wizard lists interpreters discovered via VS Code Python extension, `.venv`, Poetry, Conda, pyenv, uv, etc.  
   - Options include:
     - ⭐ Detected workspace venv (preferred)
     - 📂 **Choose another environment…** to browse anywhere
     - ⚠️ **Use system Python** (fallback only)
   - If required packages (`fluxloop-cli`, `fluxloop`, `fluxloop-mcp`) are missing, a dialog offers:
     - **Install automatically** (runs pip inside chosen env)
     - **Install manually** (opens terminal with instructions)
     - **Select different environment**
5. **Include sample agent?** (toggle)
6. **Finish**
   - Wizard runs `fluxloop init project` inside the shared root
   - Sets `fluxloop.projectRoot` in workspace settings (change anytime under Settings → FluxLoop → Project Root)
   - Registers the project and makes it active in VSCode

### Method 2: Custom Flow (Advanced)

Use when you need full control—e.g., mono-repos, remote folders, or keeping configs beside your source tree.

1. Run `FluxLoop: Create FluxLoop Project`
2. Choose **Custom (Advanced)**
3. Pick a destination folder for the FluxLoop project (can be inside the repo)
4. Enter project name (created inside the folder you picked)
5. Select environment:
   - Create/select a `.venv` within your repo, or browse to any interpreter/Conda env
   - Same package installation dialog appears if dependencies are missing
6. Include sample agent (optional)
7. Finish—FluxLoop writes configs exactly where you pointed and saves per-folder settings:
   - `fluxloop.targetSourceRoot`
   - `fluxloop.executionMode`
   - `fluxloop.pythonPath` / `fluxloop.mcpCommandPath` if custom executables were chosen

## Project Structure

After creation, your FluxLoop project (default flow) lives under the shared root:

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

FluxLoop also updates `.vscode/settings.json` with:

```json
{
  "fluxloop.executionMode": "auto",
  "fluxloop.targetSourceRoot": "/path/to/your/workspace",
  "fluxloop.projectRoot": "~/FluxLoopProjects"
}
```

Adjust these in Settings UI or directly in the JSON file.

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
- [Managing Inputs](./managing-inputs) - Generate/groom inputs
- [Running Experiments](./running-experiments) - Execute simulations
- [Viewing Results](./viewing-results) - Analyze experiment output
