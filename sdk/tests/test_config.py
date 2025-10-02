"""Tests for SDK configuration."""

import os
import pytest
from unittest.mock import patch

from fluxloop.config import SDKConfig, configure, get_config, reset_config


class TestSDKConfig:
    """Test the SDKConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SDKConfig()
        
        assert config.collector_url == "http://localhost:8000"
        assert config.api_key is None
        assert config.enabled is True
        assert config.debug is False
        assert config.batch_size == 10
        assert config.flush_interval == 5.0
        assert config.max_queue_size == 1000
        assert config.timeout == 10.0
        assert config.sample_rate == 1.0
        assert config.environment == "development"
        assert config.record_args is False
        assert config.recording_file is None
    
    def test_config_from_env_vars(self):
        """Test configuration from environment variables."""
        env_vars = {
            "FLUXLOOP_COLLECTOR_URL": "https://api.example.com",
            "FLUXLOOP_API_KEY": "test-key",
            "FLUXLOOP_ENABLED": "false",
            "FLUXLOOP_DEBUG": "true",
            "FLUXLOOP_BATCH_SIZE": "20",
            "FLUXLOOP_FLUSH_INTERVAL": "10.0",
            "FLUXLOOP_SAMPLE_RATE": "0.5",
            "FLUXLOOP_SERVICE_NAME": "test-service",
            "FLUXLOOP_ENVIRONMENT": "staging",
            "FLUXLOOP_RECORD_ARGS": "true",
            "FLUXLOOP_RECORDING_FILE": "/tmp/custom.jsonl",
        }
        
        with patch.dict(os.environ, env_vars):
            config = SDKConfig()
            
            assert config.collector_url == "https://api.example.com"
            assert config.api_key == "test-key"
            assert config.enabled is False
            assert config.debug is True
            assert config.batch_size == 20
            assert config.flush_interval == 10.0
            assert config.sample_rate == 0.5
            assert config.service_name == "test-service"
            assert config.environment == "staging"
            assert config.record_args is True
            assert config.recording_file == "/tmp/custom.jsonl"
    
    def test_collector_url_validation(self):
        """Test collector URL validation."""
        # Valid URLs
        config = SDKConfig(collector_url="http://localhost:8000")
        assert config.collector_url == "http://localhost:8000"
        
        config = SDKConfig(collector_url="https://api.example.com/")
        assert config.collector_url == "https://api.example.com"  # Trailing slash removed
        
        # Invalid URLs
        with pytest.raises(ValueError, match="Invalid collector URL"):
            SDKConfig(collector_url="not-a-url")
        
        with pytest.raises(ValueError, match="Invalid collector URL"):
            SDKConfig(collector_url="")
    
    def test_sample_rate_validation(self):
        """Test sample rate validation."""
        # Valid rates
        config = SDKConfig(sample_rate=0.0)
        assert config.sample_rate == 0.0
        
        config = SDKConfig(sample_rate=1.0)
        assert config.sample_rate == 1.0
        
        config = SDKConfig(sample_rate=0.5)
        assert config.sample_rate == 0.5
        
        # Invalid rates
        with pytest.raises(ValueError, match="sample_rate must be between 0 and 1"):
            SDKConfig(sample_rate=-0.1)
        
        with pytest.raises(ValueError, match="sample_rate must be between 0 and 1"):
            SDKConfig(sample_rate=1.1)
    
    def test_batch_size_validation(self):
        """Test batch size validation."""
        # Valid sizes
        config = SDKConfig(batch_size=1)
        assert config.batch_size == 1
        
        config = SDKConfig(batch_size=50)
        assert config.batch_size == 50
        
        config = SDKConfig(batch_size=100)
        assert config.batch_size == 100
        
        # Invalid sizes
        with pytest.raises(ValueError, match="batch_size must be at least 1"):
            SDKConfig(batch_size=0)
        
        with pytest.raises(ValueError, match="batch_size must not exceed 100"):
            SDKConfig(batch_size=101)


class TestConfigureFunctions:
    """Test the configuration functions."""
    
    def test_configure(self):
        """Test the configure function."""
        # Reset to defaults first
        reset_config()
        
        # Configure with new values
        config = configure(
            collector_url="https://new.example.com",
            api_key="new-key",
            debug=True,
            sample_rate=0.2
        )
        
        assert config.collector_url == "https://new.example.com"
        assert config.api_key == "new-key"
        assert config.debug is True
        assert config.sample_rate == 0.2
        
        # Verify global config is updated
        global_config = get_config()
        assert global_config.collector_url == "https://new.example.com"
        assert global_config.api_key == "new-key"
    
    def test_configure_invalid_parameter(self):
        """Test configure with invalid parameter."""
        with pytest.raises(ValueError, match="Unknown configuration parameter: invalid_param"):
            configure(invalid_param="value")
    
    def test_get_config(self):
        """Test getting current configuration."""
        reset_config()
        config1 = get_config()
        config2 = get_config()
        
        # Should return the same instance
        assert config1 is config2
    
    def test_reset_config(self):
        """Test resetting configuration to defaults."""
        # Configure with custom values
        configure(
            collector_url="https://custom.example.com",
            debug=True
        )
        
        # Reset
        config = reset_config()
        
        # Should be back to defaults
        assert config.collector_url == "http://localhost:8000"
        assert config.debug is False
        
        # Global config should also be reset
        global_config = get_config()
        assert global_config.collector_url == "http://localhost:8000"
        assert global_config.debug is False
