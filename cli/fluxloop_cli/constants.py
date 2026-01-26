"""Shared constants for the FluxLoop CLI."""

from pathlib import Path


# =============================================================================
# Workspace Structure
# =============================================================================

# Workspace root directory (contains scenarios, project.json, context.json)
FLUXLOOP_DIR_NAME = ".fluxloop"

# Scenarios container directory (inside .fluxloop/)
SCENARIOS_DIR_NAME = "scenarios"

# State directory inside each scenario
STATE_DIR_NAME = ".state"

# Workspace-level files
PROJECT_JSON_FILENAME = "project.json"      # Web Project connection
CONTEXT_JSON_FILENAME = "context.json"      # Current scenario pointer

# Default root (for backward compatibility with existing commands)
DEFAULT_ROOT_DIR_NAME = FLUXLOOP_DIR_NAME


# =============================================================================
# Config Files
# =============================================================================

CONFIG_DIRECTORY_NAME = "configs"
SCENARIO_CONFIG_FILENAME = "scenario.yaml"
PROJECT_CONFIG_FILENAME = "project.yaml"    # Legacy alias for scenario.yaml
INPUT_CONFIG_FILENAME = "input.yaml"
SIMULATION_CONFIG_FILENAME = "simulation.yaml"
EVALUATION_CONFIG_FILENAME = "evaluation.yaml"

DEFAULT_CONFIG_FILENAME = "setting.yaml"
LEGACY_CONFIG_FILENAMES = ("fluxloop.yaml",)
DEFAULT_CONFIG_PATH = Path(DEFAULT_CONFIG_FILENAME)

CONFIG_SECTION_FILENAMES = {
    "scenario": SCENARIO_CONFIG_FILENAME,
    "project": PROJECT_CONFIG_FILENAME,     # Legacy alias
    "input": INPUT_CONFIG_FILENAME,
    "simulation": SIMULATION_CONFIG_FILENAME,
    "evaluation": EVALUATION_CONFIG_FILENAME,
}

CONFIG_SECTION_ORDER = ("scenario", "input", "simulation", "evaluation")

