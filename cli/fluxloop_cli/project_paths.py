"""
Utilities for resolving FluxLoop scenario directories.

Architecture:
- Workspace: .fluxloop/
- Scenarios: .fluxloop/scenarios/{name}/
- State: .fluxloop/scenarios/{name}/.state/
"""

from pathlib import Path
from typing import Optional

from .constants import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_ROOT_DIR_NAME,
    CONFIG_DIRECTORY_NAME,
    CONFIG_SECTION_FILENAMES,
    FLUXLOOP_DIR_NAME,
    SCENARIOS_DIR_NAME,
    STATE_DIR_NAME,
    SCENARIO_CONFIG_FILENAME,
)


def _normalize_path(path: Path) -> Path:
    return path.expanduser().resolve()


# =============================================================================
# Workspace & Scenario Directories
# =============================================================================

def resolve_fluxloop_dir(base_dir: Optional[Path] = None) -> Path:
    """Resolve the .fluxloop workspace directory."""
    base = base_dir or Path.cwd()
    return _normalize_path(base / FLUXLOOP_DIR_NAME)


def resolve_scenarios_dir(base_dir: Optional[Path] = None) -> Path:
    """Resolve the .fluxloop/scenarios directory."""
    return resolve_fluxloop_dir(base_dir) / SCENARIOS_DIR_NAME


def resolve_scenario_dir(scenario_name: str, base_dir: Optional[Path] = None) -> Path:
    """Resolve the directory for a specific scenario."""
    return resolve_scenarios_dir(base_dir) / scenario_name


def resolve_scenario_state_dir(scenario_name: str, base_dir: Optional[Path] = None) -> Path:
    """Resolve the .state directory inside a scenario."""
    return resolve_scenario_dir(scenario_name, base_dir) / STATE_DIR_NAME


def resolve_scenario_config_dir(scenario_name: str, base_dir: Optional[Path] = None) -> Path:
    """Resolve the configs/ directory inside a scenario."""
    return resolve_scenario_dir(scenario_name, base_dir) / CONFIG_DIRECTORY_NAME


# =============================================================================
# Config File Resolution
# =============================================================================

def resolve_config_path(
    config_file: Path, 
    scenario_name: Optional[str] = None, 
    base_dir: Optional[Path] = None
) -> Path:
    """Resolve the path to a configuration file."""
    if config_file.is_absolute():
        return _normalize_path(config_file)

    # If scenario specified, resolve relative to scenario
    if scenario_name:
        scenario_dir = resolve_scenario_dir(scenario_name, base_dir)
        config_dir = scenario_dir / CONFIG_DIRECTORY_NAME
    else:
        config_dir = _normalize_path(base_dir or Path.cwd()) / CONFIG_DIRECTORY_NAME

    # Default: prefer simulation config inside configs/
    if config_file == DEFAULT_CONFIG_PATH:
        simulation_candidate = config_dir / CONFIG_SECTION_FILENAMES["simulation"]
        if simulation_candidate.exists() or config_dir.exists():
            return _normalize_path(simulation_candidate)

    # Explicit section filenames resolve relative to configs/
    if config_file.name in CONFIG_SECTION_FILENAMES.values():
        return _normalize_path(config_dir / config_file.name)

    # Explicit configs/ directory
    if config_file == Path(CONFIG_DIRECTORY_NAME):
        return _normalize_path(config_dir)

    if config_file.parent == Path(CONFIG_DIRECTORY_NAME):
        return _normalize_path(config_dir / config_file.name)

    # Default to current working directory
    return _normalize_path((base_dir or Path.cwd()) / config_file)


def resolve_config_section_path(
    section_key: str,
    scenario_name: Optional[str] = None,
    base_dir: Optional[Path] = None,
) -> Path:
    """Return the path to a specific configuration section file."""
    if section_key not in CONFIG_SECTION_FILENAMES:
        raise KeyError(f"Unknown configuration section: {section_key}")

    if scenario_name:
        config_dir = resolve_scenario_config_dir(scenario_name, base_dir)
    else:
        config_dir = _normalize_path(base_dir or Path.cwd()) / CONFIG_DIRECTORY_NAME
    
    return _normalize_path(config_dir / CONFIG_SECTION_FILENAMES[section_key])


def resolve_config_directory(scenario_name: Optional[str] = None, base_dir: Optional[Path] = None) -> Path:
    """Return the canonical configs/ directory for the given context."""
    if scenario_name:
        return resolve_scenario_config_dir(scenario_name, base_dir)
    return _normalize_path(base_dir or Path.cwd()) / CONFIG_DIRECTORY_NAME


# =============================================================================
# Workspace Detection
# =============================================================================

def find_workspace_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find the workspace root by looking for .fluxloop directory.
    
    Searches from start_dir upward until finding .fluxloop/.
    """
    current = (start_dir or Path.cwd()).resolve()
    
    for parent in [current] + list(current.parents):
        fluxloop_dir = parent / FLUXLOOP_DIR_NAME
        if fluxloop_dir.exists() and fluxloop_dir.is_dir():
            return parent
        if parent == parent.parent:
            break
    
    return None


def find_scenario_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the current scenario root by looking for .state directory."""
    current = (start_dir or Path.cwd()).resolve()
    
    for parent in [current] + list(current.parents):
        state_dir = parent / STATE_DIR_NAME
        if state_dir.exists() and state_dir.is_dir():
            return parent
        
        # Check if we're inside a scenario by looking at parent structure
        if parent.parent and parent.parent.name == SCENARIOS_DIR_NAME:
            return parent
        
        if parent == parent.parent:
            break
    
    return None


def get_scenario_state_dir(scenario_root: Path) -> Path:
    """Get the state directory for a scenario."""
    return scenario_root / STATE_DIR_NAME


def is_workspace_initialized(base_dir: Optional[Path] = None) -> bool:
    """Check if the workspace has been initialized."""
    fluxloop_dir = resolve_fluxloop_dir(base_dir)
    return fluxloop_dir.exists() and (fluxloop_dir / SCENARIOS_DIR_NAME).exists()


# =============================================================================
# Backward Compatibility Functions
# =============================================================================

def resolve_root_dir(root: Optional[Path] = None) -> Path:
    """Resolve the FluxLoop root directory."""
    base = root if root is not None else Path(DEFAULT_ROOT_DIR_NAME)
    if base.is_absolute():
        return _normalize_path(base)
    return _normalize_path(Path.cwd() / base)


def resolve_project_dir(project: str, root: Optional[Path] = None) -> Path:
    """Resolve the directory for a specific project/scenario."""
    root_dir = resolve_root_dir(root)
    return _normalize_path(root_dir / project)


def resolve_project_relative(path: Path, project: Optional[str], root: Optional[Path]) -> Path:
    """Resolve a path relative to the project directory."""
    if path.is_absolute():
        return _normalize_path(path)

    if project:
        return _normalize_path(resolve_project_dir(project, root) / path)

    return _normalize_path(Path.cwd() / path)


def resolve_env_path(env_file: Path, project: Optional[str], root: Optional[Path]) -> Path:
    """Resolve the path for environment variable files."""
    if env_file.is_absolute() and env_file != Path(".env"):
        return _normalize_path(env_file)

    root_dir = resolve_root_dir(root)
    root_env = root_dir / ".env"

    if env_file != Path(".env"):
        return resolve_project_relative(env_file, project, root)

    # Prefer scenario .env when running inside a scenario directory
    scenario_root = find_scenario_root()
    if scenario_root:
        return _normalize_path(scenario_root / ".env")

    # If context points to a scenario, use that scenario's .env
    try:
        from .context_manager import find_workspace_root, load_context

        workspace_root = find_workspace_root()
        if workspace_root:
            context = load_context(workspace_root)
            if context and context.current_scenario and context.current_scenario.local_path:
                scenario_dir = (
                    workspace_root
                    / FLUXLOOP_DIR_NAME
                    / context.current_scenario.local_path
                )
                return _normalize_path(scenario_dir / ".env")
            scenarios_dir = workspace_root / FLUXLOOP_DIR_NAME / SCENARIOS_DIR_NAME
            if scenarios_dir.exists():
                scenario_dirs = [entry for entry in scenarios_dir.iterdir() if entry.is_dir()]
                if len(scenario_dirs) == 1:
                    return _normalize_path(scenario_dirs[0] / ".env")
    except Exception:
        # Fall back to legacy resolution if context isn't available
        pass

    if project:
        project_dir = resolve_project_dir(project, root)
        project_env = project_dir / ".env"
        return _normalize_path(project_env)

    if root_env.exists():
        return _normalize_path(root_env)

    return _normalize_path(Path.cwd() / env_file)
