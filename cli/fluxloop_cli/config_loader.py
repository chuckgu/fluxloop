"""
Configuration loader for experiments.
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import ValidationError

from .project_paths import resolve_config_path
from .config_schema import (
    CONFIG_SECTION_FILENAMES,
    CONFIG_SECTION_ORDER,
    CONFIG_REQUIRED_KEYS,
    iter_section_paths,
    is_legacy_config,
)
from .constants import CONFIG_DIRECTORY_NAME

# Add shared schemas to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from fluxloop.schemas import ExperimentConfig, VariationStrategy


def load_experiment_config(
    config_file: Path,
    *,
    project: Optional[str] = None,
    root: Optional[Path] = None,
    require_inputs_file: bool = True,
) -> ExperimentConfig:
    """
    Load and validate experiment configuration from YAML file.
    """
    resolved_path = resolve_config_path(config_file, project, root)

    structure, project_root, config_dir = _detect_config_context(resolved_path)

    if structure == "legacy":
        if not resolved_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {resolved_path}")

        data = _load_yaml_mapping(resolved_path)
        source_dir = resolved_path.parent
    else:
        # Multi-section configuration
        merged: Dict[str, Any] = {}
        missing_required = []

        for section_path in iter_section_paths(project_root):
            if not section_path.exists():
                key = section_path.name
                logical_key = _section_key_from_filename(section_path.name)
                if logical_key in CONFIG_REQUIRED_KEYS:
                    missing_required.append(section_path.name)
                continue

            section_data = _load_yaml_mapping(section_path)
            _deep_merge(merged, section_data)

        if missing_required:
            raise FileNotFoundError(
                "Missing required configuration sections: "
                + ", ".join(missing_required)
            )

        if not merged:
            raise ValueError(
                f"No configuration data found in {config_dir}"
            )

        data = merged
        source_dir = project_root

    _normalize_variation_strategies(data)
    _normalize_runner_target(data)

    # Validate and create config object
    try:
        config = ExperimentConfig(**data)
        config.set_source_dir(source_dir)
        resolved_input_count = _resolve_input_count(
            config,
            require_inputs_file=require_inputs_file,
        )
        config.set_resolved_input_count(resolved_input_count)
    except ValidationError as e:
        errors = []
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            msg = error["msg"]
            errors.append(f"  - {loc}: {msg}")

        raise ValueError(
            "Invalid configuration:\n" + "\n".join(errors)
        )

    return config


def _resolve_input_count(
    config: ExperimentConfig,
    *,
    require_inputs_file: bool = True,
) -> int:
    """Determine the effective number of inputs for this configuration."""
    if config.inputs_file:
        inputs_path = (config.get_source_dir() / Path(config.inputs_file)
                       if config.get_source_dir() and not Path(config.inputs_file).is_absolute()
                       else Path(config.inputs_file)).resolve()

        if not inputs_path.exists():
            if require_inputs_file:
                raise FileNotFoundError(
                    f"Inputs file not found when loading config: {inputs_path}"
                )
            return len(config.base_inputs)

        with open(inputs_path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f)

        if not payload:
            if require_inputs_file:
                raise ValueError(f"Inputs file is empty: {inputs_path}")
            return len(config.base_inputs)

        if isinstance(payload, dict):
            entries = payload.get("inputs")
            if entries is None:
                if require_inputs_file:
                    raise ValueError("Inputs file must contain an 'inputs' list when using mapping format")
                return len(config.base_inputs)
        elif isinstance(payload, list):
            entries = payload
        else:
            raise ValueError("Inputs file must be either a list or a mapping with an 'inputs' key")

        if not isinstance(entries, list):
            if require_inputs_file:
                raise ValueError("Inputs entries must be provided as a list")
            return len(config.base_inputs)

        return len(entries)

    # No external file – rely on base_inputs multiplied by variation count
    base_count = len(config.base_inputs)
    variation_multiplier = max(1, config.variation_count)
    return base_count * variation_multiplier if base_count else variation_multiplier


def save_experiment_config(config: ExperimentConfig, config_file: Path) -> None:
    """
    Save experiment configuration to YAML file.
    
    Args:
        config: ExperimentConfig object to save
        config_file: Path to save configuration to
    """
    # Convert to dict and save
    data = config.to_dict()
    
    with open(config_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def merge_config_overrides(
    config: ExperimentConfig,
    overrides: Dict[str, Any]
) -> ExperimentConfig:
    """
    Merge override values into configuration.
    
    Args:
        config: Base configuration
        overrides: Dictionary of overrides (dot notation supported)
        
    Returns:
        New configuration with overrides applied
    """
    # Convert config to dict
    data = config.to_dict()
    
    # Apply overrides
    for key, value in overrides.items():
        # Support dot notation (e.g., "runner.timeout")
        keys = key.split(".")
        current = data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    # Create new config
    return ExperimentConfig(**data)


def _load_yaml_mapping(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        payload = yaml.safe_load(f)

    if payload is None:
        return {}

    if not isinstance(payload, dict):
        raise ValueError(f"Configuration file must contain a mapping: {path}")

    return payload


def _deep_merge(target: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value
    return target


def _normalize_variation_strategies(payload: Dict[str, Any]) -> None:
    """Ensure variation strategies are represented as enum-compatible strings."""

    strategies = payload.get("variation_strategies")
    if not isinstance(strategies, list):
        return

    normalized = []
    for entry in strategies:
        if isinstance(entry, VariationStrategy):
            normalized.append(entry.value)
            continue

        candidate: Optional[str]
        if isinstance(entry, str):
            candidate = entry
        elif isinstance(entry, dict):
            candidate = (
                entry.get("type")
                or entry.get("name")
                or entry.get("strategy")
                or entry.get("value")
            )
        else:
            candidate = str(entry)

        if not candidate:
            continue

        canonical = (
            candidate.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        alias_map = {
            "error_prone": (
                VariationStrategy.ERROR_PRONE.value
                if hasattr(VariationStrategy, "ERROR_PRONE")
                else VariationStrategy.TYPO.value
            ),
        }

        canonical = alias_map.get(canonical, canonical)

        normalized.append(canonical)

    # Remove duplicates while preserving order
    seen = set()
    deduped = []
    for item in normalized:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)

    payload["variation_strategies"] = deduped


def _normalize_runner_target(payload: Dict[str, Any]) -> None:
    """Populate runner.module_path/function_name when only target is provided."""

    runner = payload.get("runner")
    if not isinstance(runner, dict):
        return

    target = runner.get("target")
    module_path = runner.get("module_path")
    function_name = runner.get("function_name")

    if target and (not module_path or not function_name):
        if ":" in target:
            module_part, attr_part = target.split(":", 1)
            runner.setdefault("module_path", module_part)
            if "." in attr_part:
                # module:Class.method -> record class.method as function placeholder
                runner.setdefault("function_name", attr_part)
            else:
                runner.setdefault("function_name", attr_part)

def _detect_config_context(resolved_path: Path) -> tuple[str, Path, Path]:
    """Determine whether the path points to legacy or multi-section config."""

    if resolved_path.is_dir():
        if resolved_path.name == CONFIG_DIRECTORY_NAME:
            return "multi", resolved_path.parent, resolved_path
        if (resolved_path / CONFIG_DIRECTORY_NAME).exists():
            return "multi", resolved_path, resolved_path / CONFIG_DIRECTORY_NAME
        return "legacy", resolved_path, resolved_path

    if resolved_path.parent.name == CONFIG_DIRECTORY_NAME:
        return "multi", resolved_path.parent.parent, resolved_path.parent

    if is_legacy_config(resolved_path.name):
        return "legacy", resolved_path.parent, resolved_path.parent

    return "legacy", resolved_path.parent, resolved_path.parent


def _section_key_from_filename(filename: str) -> Optional[str]:
    for key, value in CONFIG_SECTION_FILENAMES.items():
        if value == filename:
            return key
    return None
