"""
Local context management for FluxLoop CLI.

Architecture:
- .fluxloop/project.json: Web Project connection (workspace level)
- .fluxloop/context.json: Current scenario pointer (workspace level)
- .fluxloop/scenarios/{name}/.state/sync.json: Scenario sync state

Design principle: Local context is a "pointer" to server resources.
Server is the Single Source of Truth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .constants import (
    FLUXLOOP_DIR_NAME,
    SCENARIOS_DIR_NAME,
    STATE_DIR_NAME,
    PROJECT_JSON_FILENAME,
    CONTEXT_JSON_FILENAME,
)


# =============================================================================
# Web Project Connection (workspace level)
# =============================================================================

@dataclass
class WebProjectConnection:
    """
    Connection to a Web Project (stored in .fluxloop/project.json).
    
    This links the local workspace to a Web Project.
    """
    project_id: str
    project_name: str
    api_url: str = "https://api.fluxloop.ai"
    connected_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "api_url": self.api_url,
            "connected_at": self.connected_at or datetime.now(timezone.utc).isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> WebProjectConnection:
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            api_url=data.get("api_url", "https://api.fluxloop.ai"),
            connected_at=data.get("connected_at"),
        )


# =============================================================================
# Context Data Classes
# =============================================================================

@dataclass
class ScenarioContext:
    """Current scenario reference (maps to Web Scenario)."""
    id: str
    name: str
    local_path: Optional[str] = None  # e.g., "scenarios/order-cancel"
    
    def to_dict(self) -> dict:
        data = {"id": self.id, "name": self.name}
        if self.local_path:
            data["local_path"] = self.local_path
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> ScenarioContext:
        return cls(
            id=data["id"], 
            name=data["name"],
            local_path=data.get("local_path"),
        )


@dataclass
class BundleContext:
    """Current bundle reference."""
    id: str
    version: str
    
    def to_dict(self) -> dict:
        return {"id": self.id, "version": self.version}
    
    @classmethod
    def from_dict(cls, data: dict) -> BundleContext:
        return cls(id=data["id"], version=data["version"])


@dataclass
class LocalContext:
    """
    Local context state stored in .fluxloop/context.json.
    
    This is a pointer to server resources, not a cache.
    """
    current_scenario: Optional[ScenarioContext] = None
    current_bundle: Optional[BundleContext] = None
    last_updated: Optional[str] = None
    
    def to_dict(self) -> dict:
        data = {}
        if self.current_scenario:
            data["current_scenario"] = self.current_scenario.to_dict()
        if self.current_bundle:
            data["current_bundle"] = self.current_bundle.to_dict()
        data["last_updated"] = self.last_updated or datetime.now(timezone.utc).isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> LocalContext:
        return cls(
            current_scenario=ScenarioContext.from_dict(data["current_scenario"]) 
                if data.get("current_scenario") else None,
            current_bundle=BundleContext.from_dict(data["current_bundle"]) 
                if data.get("current_bundle") else None,
            last_updated=data.get("last_updated"),
        )


# =============================================================================
# Workspace Directory Functions
# =============================================================================

def get_fluxloop_dir(base_dir: Optional[Path] = None) -> Path:
    """Get the .fluxloop workspace directory path."""
    base = base_dir or Path.cwd()
    workspace_root = find_workspace_root(base)
    if workspace_root:
        return workspace_root / FLUXLOOP_DIR_NAME
    return base / FLUXLOOP_DIR_NAME


def ensure_fluxloop_dir(base_dir: Optional[Path] = None) -> Path:
    """Ensure .fluxloop workspace directory exists."""
    fluxloop_dir = get_fluxloop_dir(base_dir)
    fluxloop_dir.mkdir(parents=True, exist_ok=True)
    return fluxloop_dir


def get_scenarios_dir(base_dir: Optional[Path] = None) -> Path:
    """Get the .fluxloop/scenarios directory path."""
    return get_fluxloop_dir(base_dir) / SCENARIOS_DIR_NAME


def ensure_scenarios_dir(base_dir: Optional[Path] = None) -> Path:
    """Ensure .fluxloop/scenarios directory exists."""
    scenarios_dir = get_scenarios_dir(base_dir)
    scenarios_dir.mkdir(parents=True, exist_ok=True)
    return scenarios_dir


def get_scenario_dir(scenario_name: str, base_dir: Optional[Path] = None) -> Path:
    """Get the directory for a specific scenario."""
    return get_scenarios_dir(base_dir) / scenario_name


def get_state_dir(scenario_dir: Path) -> Path:
    """Get the .state directory inside a scenario."""
    return scenario_dir / STATE_DIR_NAME


def ensure_state_dir(scenario_dir: Path) -> Path:
    """Ensure .state directory exists inside a scenario."""
    state_dir = get_state_dir(scenario_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


# =============================================================================
# Project Connection (workspace ↔ Web Project)
# =============================================================================

def get_project_json_path(base_dir: Optional[Path] = None) -> Path:
    """Get the path to .fluxloop/project.json."""
    return get_fluxloop_dir(base_dir) / PROJECT_JSON_FILENAME


def load_project_connection(base_dir: Optional[Path] = None) -> Optional[WebProjectConnection]:
    """Load Web Project connection from .fluxloop/project.json."""
    project_json_path = get_project_json_path(base_dir)
    
    if not project_json_path.exists():
        return None
    
    try:
        data = json.loads(project_json_path.read_text())
        return WebProjectConnection.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Warning: Failed to load project.json: {e}")
        return None


def save_project_connection(connection: WebProjectConnection, base_dir: Optional[Path] = None) -> Path:
    """Save Web Project connection to .fluxloop/project.json."""
    ensure_fluxloop_dir(base_dir)
    project_json_path = get_project_json_path(base_dir)
    project_json_path.write_text(json.dumps(connection.to_dict(), indent=2))
    return project_json_path


def select_web_project(
    project_id: str, 
    project_name: str, 
    api_url: str = "https://api.fluxloop.ai",
    base_dir: Optional[Path] = None
) -> WebProjectConnection:
    """Select a Web Project for this workspace."""
    connection = WebProjectConnection(
        project_id=project_id,
        project_name=project_name,
        api_url=api_url,
        connected_at=datetime.now(timezone.utc).isoformat(),
    )
    save_project_connection(connection, base_dir)
    return connection


def get_current_web_project_id(base_dir: Optional[Path] = None) -> Optional[str]:
    """Get current Web Project ID from project.json."""
    connection = load_project_connection(base_dir)
    return connection.project_id if connection else None


# =============================================================================
# Context Functions (current scenario)
# =============================================================================

def get_context_file_path(base_dir: Optional[Path] = None) -> Path:
    """Get the full path to context.json."""
    return get_fluxloop_dir(base_dir) / CONTEXT_JSON_FILENAME


def load_context(base_dir: Optional[Path] = None) -> Optional[LocalContext]:
    """Load local context from .fluxloop/context.json."""
    context_path = get_context_file_path(base_dir)
    
    if not context_path.exists():
        return None
    
    try:
        data = json.loads(context_path.read_text())
        return LocalContext.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Warning: Failed to load context: {e}")
        return None


def save_context(context: LocalContext, base_dir: Optional[Path] = None) -> Path:
    """Save local context to .fluxloop/context.json."""
    ensure_fluxloop_dir(base_dir)
    context_path = get_context_file_path(base_dir)
    context.last_updated = datetime.now(timezone.utc).isoformat()
    context_path.write_text(json.dumps(context.to_dict(), indent=2))
    return context_path


def clear_context(base_dir: Optional[Path] = None) -> None:
    """Delete the context file."""
    context_path = get_context_file_path(base_dir)
    if context_path.exists():
        context_path.unlink()


def set_scenario(
    scenario_id: str, 
    scenario_name: str, 
    local_path: Optional[str] = None,
    base_dir: Optional[Path] = None
) -> LocalContext:
    """Set the current scenario in local context."""
    context = load_context(base_dir) or LocalContext()
    
    # If scenario changes, clear bundle
    if context.current_scenario and context.current_scenario.id != scenario_id:
        context.current_bundle = None
    
    context.current_scenario = ScenarioContext(
        id=scenario_id, 
        name=scenario_name,
        local_path=local_path or f"{SCENARIOS_DIR_NAME}/{scenario_name}",
    )
    save_context(context, base_dir)
    return context


def set_bundle(bundle_id: str, bundle_version: str, base_dir: Optional[Path] = None) -> LocalContext:
    """Set the current bundle in local context."""
    context = load_context(base_dir) or LocalContext()
    context.current_bundle = BundleContext(id=bundle_id, version=bundle_version)
    save_context(context, base_dir)
    return context


def get_current_scenario_id(base_dir: Optional[Path] = None) -> Optional[str]:
    """Get current scenario ID from context."""
    context = load_context(base_dir)
    return context.current_scenario.id if context and context.current_scenario else None


def get_current_scenario(base_dir: Optional[Path] = None) -> Optional[ScenarioContext]:
    """Get current scenario from context."""
    context = load_context(base_dir)
    return context.current_scenario if context else None


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
        if (parent / FLUXLOOP_DIR_NAME).exists():
            return parent
        if parent == parent.parent:
            break
    
    return None


def find_scenario_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find the scenario root by looking for .state directory.
    """
    current = (start_dir or Path.cwd()).resolve()
    
    for parent in [current] + list(current.parents):
        if (parent / STATE_DIR_NAME).exists():
            return parent
        if parent == parent.parent:
            break
    
    return None


# =============================================================================
# Backward Compatibility Aliases
# =============================================================================

# For commands that still use project terminology
def get_current_project_id(base_dir: Optional[Path] = None) -> Optional[str]:
    """Get current Web Project ID (alias for get_current_web_project_id)."""
    return get_current_web_project_id(base_dir)


def set_project(project_id: str, project_name: str, base_dir: Optional[Path] = None):
    """Set current project (alias for select_web_project)."""
    return select_web_project(project_id, project_name, base_dir=base_dir)
