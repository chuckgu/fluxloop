# Change Log

All notable changes to the FluxLoop VSCode Extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/chuckgu/fluxloop/releases/tag/vscode-v0.1.0

