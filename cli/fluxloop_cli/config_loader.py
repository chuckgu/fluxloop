"""
Configuration loader for experiments.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import ValidationError

# Add shared schemas to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from schemas.config import ExperimentConfig


def load_experiment_config(config_file: Path) -> ExperimentConfig:
    """
    Load and validate experiment configuration from YAML file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Validated ExperimentConfig object
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    # Load YAML
    with open(config_file) as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError("Configuration file is empty")
    
    # Validate and create config object
    try:
        config = ExperimentConfig(**data)
        config.set_source_dir(config_file.parent)
        resolved_input_count = _resolve_input_count(config)
        config.set_resolved_input_count(resolved_input_count)
    except ValidationError as e:
        # Format validation errors nicely
        errors = []
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            msg = error["msg"]
            errors.append(f"  - {loc}: {msg}")
        
        raise ValueError(
            f"Invalid configuration:\n" + "\n".join(errors)
        )
    
    return config


def _resolve_input_count(config: ExperimentConfig) -> int:
    """Determine the effective number of inputs for this configuration."""
    if config.has_external_inputs() and config.inputs_file:
        inputs_path = (config.get_source_dir() / Path(config.inputs_file)
                       if config.get_source_dir() and not Path(config.inputs_file).is_absolute()
                       else Path(config.inputs_file)).resolve()

        if not inputs_path.exists():
            raise FileNotFoundError(f"Inputs file not found when loading config: {inputs_path}")

        with open(inputs_path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f)

        if not payload:
            raise ValueError(f"Inputs file is empty: {inputs_path}")

        if isinstance(payload, dict):
            entries = payload.get("inputs")
            if entries is None:
                raise ValueError("Inputs file must contain an 'inputs' list when using mapping format")
        elif isinstance(payload, list):
            entries = payload
        else:
            raise ValueError("Inputs file must be either a list or a mapping with an 'inputs' key")

        if not isinstance(entries, list):
            raise ValueError("Inputs entries must be provided as a list")

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
