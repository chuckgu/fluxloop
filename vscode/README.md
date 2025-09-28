# FluxLoop VSCode Extension

Visual Studio Code extension for FluxLoop - AI Agent Simulation and Observability.

## Features

- 🚀 **Quick Start**: Initialize FluxLoop projects with a single command
- 🧪 **Run Experiments**: Execute simulations directly from VSCode
- 📊 **View Results**: Browse experiment results in the sidebar
- 🔍 **Status Monitoring**: Check system status and dependencies
- 🎯 **Multiple Environments**: Run in local Python, Docker, or Dev Containers

## Installation

1. Install from VSCode Marketplace:
   - Open VSCode
   - Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
   - Search for "FluxLoop"
   - Click Install

2. Install the FluxLoop CLI:
   ```bash
   pip install fluxloop-cli
   ```

## Quick Start

### Initialize a Project

1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Run `FluxLoop: Initialize Project`
3. Select a folder and project name
4. Choose whether to include example code

### Run an Experiment

1. Open a folder with `setting.yaml`
2. Click the FluxLoop icon in the activity bar
3. Click "Run Experiment" in the Experiments view

Or:
- Right-click on `setting.yaml` in the explorer
- Select "FluxLoop: Run Experiment"

### Run Single Agent

1. Open a Python file with your agent code
2. Right-click in the editor
3. Select "FluxLoop: Run Single Execution"
4. Enter the function name and input

## Views

### Experiments View
- Shows current experiment configuration
- Lists recent experiment results
- Quick access to run experiments

### Results View
- Displays experiment metrics
- Shows success rates and performance
- Links to detailed trace data

### Status View
- CLI installation status
- SDK installation status
- Collector connection status
- Configuration validation

## Commands

All commands are available through the Command Palette (Ctrl+Shift+P / Cmd+Shift+P):

- `FluxLoop: Initialize Project` - Create a new FluxLoop project
- `FluxLoop: Run Experiment` - Run the current experiment
- `FluxLoop: Run Single Execution` - Run a single agent execution
- `FluxLoop: Show Status` - Display system status
- `FluxLoop: Open Configuration` - Open setting.yaml
- `FluxLoop: Select Execution Environment` - Choose where to run experiments

## Settings

Configure the extension in VSCode settings:

- `fluxloop.collectorUrl` - URL of the FluxLoop collector service
- `fluxloop.apiKey` - API key for authentication
- `fluxloop.defaultEnvironment` - Default execution environment
- `fluxloop.autoInstallCli` - Automatically install CLI if not found
- `fluxloop.showOutputChannel` - Show output when running experiments

## Execution Environments

### Local Python
- Uses your current Python environment
- Fastest for development
- No additional setup required

### Docker
- Runs in isolated Docker container
- Consistent environment
- Requires Docker Desktop

### Dev Container
- Runs in your current Dev Container
- Perfect for containerized development
- Automatically detected

## Keyboard Shortcuts

- `Ctrl+Shift+F` / `Cmd+Shift+F` - Run current experiment
- `Ctrl+Shift+S` / `Cmd+Shift+S` - Show status

## Troubleshooting

### CLI Not Found
- The extension will prompt to install the CLI
- Or manually install: `pip install fluxloop-cli`

### No Workspace Folder
- Open a folder in VSCode before using FluxLoop commands

### Configuration Not Found
- Run `FluxLoop: Initialize Project` to create configuration

## Development

### Building the Extension

```bash
cd packages/vscode
npm install
npm run compile
```

### Testing

```bash
npm test
```

### Packaging

```bash
npm run package
```

## Contributing

Contributions are welcome! Please see the [main repository](https://github.com/fluxloop/fluxloop) for contribution guidelines.

## License

MIT
