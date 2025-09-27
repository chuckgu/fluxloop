"""
Configuration loader for experiments.
"""

import sys
from pathlib import Path
from typing import Any, Dict

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
