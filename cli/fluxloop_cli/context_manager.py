"""
Local context management for FluxLoop CLI.

Manages the current working context (project, scenario, bundle) stored in
.fluxloop/context.json within the project directory.

Design principle: Local context is a "pointer" to server resources.
Server is the Single Source of Truth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Context file location relative to project root
CONTEXT_DIR_NAME = ".fluxloop"
CONTEXT_FILE_NAME = "context.json"


@dataclass
class ProjectContext:
    """Current project reference."""
    id: str
    name: str
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}
    
    @classmethod
    def from_dict(cls, data: dict) -> ProjectContext:
        return cls(id=data["id"], name=data["name"])


@dataclass
class ScenarioContext:
    """Current scenario reference."""
    id: str
    name: str
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}
    
    @classmethod
    def from_dict(cls, data: dict) -> ScenarioContext:
        return cls(id=data["id"], name=data["name"])


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
    Server is the Single Source of Truth.
    """
    current_project: Optional[ProjectContext] = None
    current_scenario: Optional[ScenarioContext] = None
    current_bundle: Optional[BundleContext] = None
    last_updated: Optional[str] = None
    
    def to_dict(self) -> dict:
        data = {}
        if self.current_project:
            data["current_project"] = self.current_project.to_dict()
        if self.current_scenario:
            data["current_scenario"] = self.current_scenario.to_dict()
        if self.current_bundle:
            data["current_bundle"] = self.current_bundle.to_dict()
        data["last_updated"] = self.last_updated or datetime.now(timezone.utc).isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> LocalContext:
        return cls(
            current_project=ProjectContext.from_dict(data["current_project"]) 
                if data.get("current_project") else None,
            current_scenario=ScenarioContext.from_dict(data["current_scenario"]) 
                if data.get("current_scenario") else None,
            current_bundle=BundleContext.from_dict(data["current_bundle"]) 
                if data.get("current_bundle") else None,
            last_updated=data.get("last_updated"),
        )


def get_context_dir(base_dir: Optional[Path] = None) -> Path:
    """Get the .fluxloop directory path."""
    base = base_dir or Path.cwd()
    return base / CONTEXT_DIR_NAME


def get_context_file_path(base_dir: Optional[Path] = None) -> Path:
    """Get the full path to context.json."""
    return get_context_dir(base_dir) / CONTEXT_FILE_NAME


def ensure_context_dir(base_dir: Optional[Path] = None) -> Path:
    """Ensure .fluxloop directory exists."""
    context_dir = get_context_dir(base_dir)
    context_dir.mkdir(parents=True, exist_ok=True)
    return context_dir


def load_context(base_dir: Optional[Path] = None) -> Optional[LocalContext]:
    """
    Load local context from .fluxloop/context.json.
    
    Returns:
        LocalContext if found and valid, None otherwise.
    """
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
    """
    Save local context to .fluxloop/context.json.
    
    Args:
        context: LocalContext to save.
        base_dir: Base directory (defaults to cwd).
        
    Returns:
        Path to saved context file.
    """
    ensure_context_dir(base_dir)
    context_path = get_context_file_path(base_dir)
    
    # Update timestamp
    context.last_updated = datetime.now(timezone.utc).isoformat()
    
    context_path.write_text(json.dumps(context.to_dict(), indent=2))
    return context_path


def clear_context(base_dir: Optional[Path] = None) -> None:
    """Delete the context file."""
    context_path = get_context_file_path(base_dir)
    if context_path.exists():
        context_path.unlink()


def set_project(project_id: str, project_name: str, base_dir: Optional[Path] = None) -> LocalContext:
    """
    Set the current project in local context.
    
    Clears scenario and bundle when project changes.
    """
    context = load_context(base_dir) or LocalContext()
    
    # If project changes, clear scenario and bundle
    if context.current_project and context.current_project.id != project_id:
        context.current_scenario = None
        context.current_bundle = None
    
    context.current_project = ProjectContext(id=project_id, name=project_name)
    save_context(context, base_dir)
    return context


def set_scenario(scenario_id: str, scenario_name: str, base_dir: Optional[Path] = None) -> LocalContext:
    """
    Set the current scenario in local context.
    
    Clears bundle when scenario changes.
    """
    context = load_context(base_dir) or LocalContext()
    
    # If scenario changes, clear bundle
    if context.current_scenario and context.current_scenario.id != scenario_id:
        context.current_bundle = None
    
    context.current_scenario = ScenarioContext(id=scenario_id, name=scenario_name)
    save_context(context, base_dir)
    return context


def set_bundle(bundle_id: str, bundle_version: str, base_dir: Optional[Path] = None) -> LocalContext:
    """Set the current bundle in local context."""
    context = load_context(base_dir) or LocalContext()
    context.current_bundle = BundleContext(id=bundle_id, version=bundle_version)
    save_context(context, base_dir)
    return context


def get_current_project_id(base_dir: Optional[Path] = None) -> Optional[str]:
    """Get current project ID from context, or None if not set."""
    context = load_context(base_dir)
    if context and context.current_project:
        return context.current_project.id
    return None


def get_current_scenario_id(base_dir: Optional[Path] = None) -> Optional[str]:
    """Get current scenario ID from context, or None if not set."""
    context = load_context(base_dir)
    if context and context.current_scenario:
        return context.current_scenario.id
    return None
