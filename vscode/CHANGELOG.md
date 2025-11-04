# Change Log

All notable changes to the FluxLoop VSCode Extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Parse Experiment Results**: New `Parse Results` action in the Results view to convert experiment traces into human-readable Markdown timelines
  - Appears at the top of each experiment folder for easy access
  - Prompts for custom output directory (defaults to `per_trace_analysis`)
  - Automatically checks for existing output and prompts to overwrite if needed
  - Parsed results appear in a new `per_trace_analysis/` folder within the Results view
- **Execution Wrapper Support**: New `fluxloop.executionWrapper` setting to prefix CLI commands
  - Enables seamless integration with `uv run`, `pipx run`, and other Python environment wrappers
  - `FluxLoop: Configure Execution Wrapper` command for easy setup via Command Palette
  - Automatically creates `.vscode/settings.json` with workspace-level configuration
- **Experiments Folder Grouping**: Experiment results now appear under a collapsible **Experiments** folder in the Results view for better organization
- **Enhanced File Listings**: Results view now shows `observations.jsonl` and `logs.json` in addition to existing artifact files
- **Timestamp Display**: Experiment folder descriptions now show formatted timestamps (YYYY-MM-DD HH:MM:SS) extracted from folder names for easier identification

### Changed

- **UX Improvements**:
  - Moved `Run Experiment` action from inside `Current Experiment` to root level in Experiments view for faster access
  - Docker execution option now shows "(coming soon)" with explanatory message when selected
  - Experiment result descriptions now display timestamp before success rate for chronological clarity
- **Results View Structure**: `per_trace_analysis/` folder is recursively browsable, supporting nested analysis outputs

### Fixed

- Experiments view and Results view now show identical file sets for consistency (`observations.jsonl`, `logs.json` added to Experiments view)

## [0.1.1] - 2025-11-04

### Fixed

- Register FluxLoop tree data providers before running CLI checks to prevent
  "There is no data provider registered that can provide view data" errors when
  the extension activates in VS Code.
- Ensure runtime dependencies (for example `yaml` and `which`) are bundled in
  the packaged VSIX so installations outside Cursor resolve required modules.
- Align installation docs and deployment tooling with the verified Open VSX
  distribution flow.

## [0.1.0] - 2024-XX-XX

### Added

- Initial release of FluxLoop VSCode Extension
- **Project-Centric Workflow**
  - Create and manage multiple FluxLoop projects from the Activity Bar
  - Switch between projects with a single click
  - Automatic project discovery and configuration validation
  
- **Input Management**
  - View and edit base inputs from `configs/input.yaml`
  - Generate input variations using LLM or deterministic strategies
  - Browse generated inputs and recordings in dedicated views
  
- **Experiment Execution**
  - Run experiments directly from VSCode
  - Monitor execution progress with real-time feedback
  - View runner configuration and iteration settings at a glance
  
- **Results Exploration**
  - Browse experiment outputs organized by run timestamp
  - Open traces, summaries, and artifacts with one click
  - Parse results into human-readable Markdown timelines
  
- **Recording Mode (Advanced)**
  - Toggle argument recording for complex function signatures
  - Enable/disable recording mode from Command Palette or Experiments view
  - Status panel shows current recording state and target file
  
- **System Status**
  - Real-time CLI and SDK installation checks
  - Configuration validation for `configs/` structure
  - Recording mode and environment status at a glance

### Configuration

- Support for multi-file configuration structure (v0.2.0):
  - `configs/project.yaml` - Project metadata, collector settings
  - `configs/input.yaml` - Personas, base inputs, LLM settings
  - `configs/simulation.yaml` - Runner, iterations, replay args
  - `configs/evaluation.yaml` - Evaluator definitions

[0.1.1]: https://github.com/chuckgu/fluxloop/releases/tag/vscode-v0.1.1
[0.1.0]: https://github.com/chuckgu/fluxloop/releases/tag/vscode-v0.1.0

