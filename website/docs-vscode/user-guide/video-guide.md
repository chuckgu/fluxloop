---
sidebar_position: 0
---

# Video Guide

Get a quick look at the core features of the FluxLoop VSCode Extension through these video guides.

---

## 1. Projects

There are two ways to create a FluxLoop project.

### Default Mode - Auto (Automatic Detection)

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/ov8ju0gLBfQ"
  title="FluxLoop - Default Mode (Auto Detection)"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

**Auto mode** automatically detects virtual environments like `.venv` or `venv` within your workspace and completes the setup instantly. This is the recommended way for most users.

- **Quick Start**: Skip manual environment setup and create projects immediately.
- **Seamless Workflow**: Keeps your existing project structure intact.
- **Organized Management**: Simulation data is stored separately in a shared folder (`~/FluxLoopProjects`).

### Default Mode - Manual (Manual Selection)

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/iYN_w10ql8I"
  title="FluxLoop - Default Mode (Manual Selection)"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

**Manual mode** is for when virtual environments are not in standard locations or when you need to specify a particular interpreter from multiple options.

- **Granular Control**: Choose from any environment detected by the VS Code Python extension.
- **Custom Path**: Manually browse and select a virtual environment folder if it's not listed.
- **Flexibility**: Suitable for environments using various Python distributions like Conda, Pyenv, etc.

### Custom Mode (Advanced)

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/cK0Wbf81Ung"
  title="FluxLoop - Custom Mode Project Creation"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

**Custom mode** is for when you want full control over the project location and configuration.

- Ideal for complex structures like monorepos or remote folders.
- Allows placing FluxLoop configs inside the source tree for easier Git management.
- Supports independent environment settings per project.

:::warning Important Note on Environment Selection
Both modes include a step to select a Python environment during project creation.

**If you have a virtual environment (venv, Conda, etc.) where your agent actually runs, make sure to select it.** Otherwise, the system's default Python will be used, which might lack the necessary packages, leading to errors during experiments.
:::

---

## 2. Environment

Learn how to configure and check the status of your Python environment. Use this when agent dependencies change or when testing in different virtual environments.

### System Console

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/CUc8v3JLX2Q"
  title="FluxLoop - Environment Setup"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

- **Select Environment**: Choose the Python interpreter for your project. Automatically detects environments like venv, Conda, Poetry, pyenv, uv, and allows manual path specification if needed.
- **Show Environment**: View detailed info about the currently selected environment (Python version, installed packages, etc.) to ensure consistency.

---

## 3. Inputs

Generate and manage large-scale input data for agent testing.

### Generate New Inputs

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/eXO_Xs1I8Ps"
  title="FluxLoop - Generate Inputs"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

A **Base Input configuration is required before generating inputs**. Define personas and base input values in `configs/input.yaml`, then use the Generate feature to automatically create hundreds of variations. Generated inputs are saved in the `inputs/` folder and can be manually edited to refine your dataset.

---

## 4. Experiments

Prepare simulations and run experiments to observe your agent's behavior.

### Prepare Simulation

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/zq2xDacSXLg"
  title="FluxLoop - Prepare Simulation"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

:::info Note
Prepare Simulation is a guide that walks you through the configuration process. For actual agent integration, refer to the following:

- [FluxLoop SDK Basic Usage](/sdk/getting-started/basic-usage) - Applying SDK decorators to your agent code.
- [Runner Configuration Guide](/cli/configuration/runner-targets) - Setting up various runner patterns (Python, HTTP, Subprocess, etc.).
- [pytest Integration](/cli/workflows/pytest-integration) - Integrating FluxLoop simulations with existing test code.
:::

### Run Experiment

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/xPH86AVkfzY"
  title="FluxLoop - Run Experiment"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

Execute experiments based on the prepared configurations.

- **Real-time Monitoring**: Instantly track experiment progress and logs from the dashboard.
- **Parallel Execution**: Process large volumes of inputs in parallel across multiple processes to save time.
- **Trace Viewer**: Analyze the detailed execution flow (Trace) of each running simulation in real-time.

:::tip Struggling with complex Args settings?
If configuring simulation arguments (`args`) is too complex, try [Recording Mode](./recording-mode). Record the actual arguments used during agent execution and reuse them in your experiments.
:::

---

## 5. Evaluation

Analyze and evaluate experiment results using quantitative metrics.

<iframe
  width="100%"
  height="400"
  src="https://www.youtube.com/embed/0zHYjQlNOS0"
  title="FluxLoop - Evaluation"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

Evaluation proceeds in three steps, allowing you to **compare and analyze multiple experiment results** to track your agent's performance improvement at a glance:

1. **Configure**: Set up evaluation rubrics and metrics.
2. **Parse**: Extract key data required for evaluation from experiment results (Traces).
3. **Evaluate**: Calculate scores and gain insights through LLM or rule-based evaluators.

---

## Next Steps

For more details on each feature, please refer to the documents below:

- [Creating Projects](./creating-projects) - Detailed project setup guide.
- [Environment Setup](./environment-setup) - Configuring Python environments.
- [Managing Inputs](./managing-inputs) - Creating and managing input data.
- [Running Experiments](./running-experiments) - How to run simulations.
- [Viewing Results](./viewing-results) - Analyzing experiment results.
