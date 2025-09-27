"""
SDK Configuration management.
"""

import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables
load_dotenv()


class SDKConfig(BaseModel):
    """SDK configuration settings."""
    
    # Collector settings
    collector_url: Optional[str] = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_COLLECTOR_URL", "http://localhost:8000")
    )
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_API_KEY")
    )
    
    # Behavior settings
    enabled: bool = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_ENABLED", "true").lower() == "true"
    )
    debug: bool = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_DEBUG", "false").lower() == "true"
    )
    use_collector: bool = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_USE_COLLECTOR", "true").lower() == "true"
    )
    offline_store_enabled: bool = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_OFFLINE_ENABLED", "true").lower() == "true"
    )
    offline_store_dir: str = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_OFFLINE_DIR", "./fluxloop_artifacts")
    )
    
    # Performance settings
    batch_size: int = Field(
        default_factory=lambda: int(os.getenv("FLUXLOOP_BATCH_SIZE", "10"))
    )
    flush_interval: float = Field(
        default_factory=lambda: float(os.getenv("FLUXLOOP_FLUSH_INTERVAL", "5.0"))
    )
    max_queue_size: int = Field(
        default_factory=lambda: int(os.getenv("FLUXLOOP_MAX_QUEUE_SIZE", "1000"))
    )
    timeout: float = Field(
        default_factory=lambda: float(os.getenv("FLUXLOOP_TIMEOUT", "10.0"))
    )
    
    # Sampling
    sample_rate: float = Field(
        default_factory=lambda: float(os.getenv("FLUXLOOP_SAMPLE_RATE", "1.0"))
    )
    
    # Metadata
    service_name: Optional[str] = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_SERVICE_NAME")
    )
    environment: Optional[str] = Field(
        default_factory=lambda: os.getenv("FLUXLOOP_ENVIRONMENT", "development")
    )
    
    @field_validator("collector_url")
    def validate_collector_url(cls, v):
        """Ensure collector URL is valid."""
        if v is None:
            return None
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception as e:
            raise ValueError(f"Invalid collector URL: {e}")
        return v.rstrip("/")  # Remove trailing slash
    
    @field_validator("sample_rate")
    def validate_sample_rate(cls, v):
        """Ensure sample rate is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("sample_rate must be between 0 and 1")
        return v
    
    @field_validator("batch_size")
    def validate_batch_size(cls, v):
        """Ensure batch size is reasonable."""
        if v < 1:
            raise ValueError("batch_size must be at least 1")
        if v > 100:
            raise ValueError("batch_size must not exceed 100")
        return v


# Global configuration instance
_config = SDKConfig()


def configure(**kwargs) -> SDKConfig:
    """
    Configure the SDK.
    
    Args:
        **kwargs: Configuration parameters to override
        
    Returns:
        Updated configuration
        
    Example:
        >>> import fluxloop
        >>> fluxloop.configure(
        ...     collector_url="https://api.fluxloop.dev",
        ...     api_key="your-api-key"
        ... )
    """
    global _config
    
    # Update configuration with provided values
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")
    
    # Re-validate the configuration
    _config = SDKConfig(**_config.model_dump())
    
    return _config


def get_config() -> SDKConfig:
    """Get current SDK configuration."""
    return _config


def reset_config() -> SDKConfig:
    """Reset configuration to defaults."""
    global _config
    _config = SDKConfig()
    return _config
