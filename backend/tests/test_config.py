import os
import pytest
from pathlib import Path
from backend.app.config.config import load_config, save_config, get_config_path
from backend.app.models.models import LLMConfig

def test_load_save_config():
    # Load current configuration
    original_config = load_config()
    
    # Save a test modification
    test_config = LLMConfig(
        provider="test-provider",
        base_url="http://test-url:1111",
        model="test-model",
        api_key="test-key",
        temperature=0.5
    )
    save_config(test_config)
    
    # Reload and verify
    reloaded = load_config()
    assert reloaded.provider == "test-provider"
    assert reloaded.base_url == "http://test-url:1111"
    assert reloaded.model == "test-model"
    assert reloaded.api_key == "test-key"
    assert reloaded.temperature == 0.5
    
    # Restore original config
    save_config(original_config)
