import os
import json
from pathlib import Path
from backend.app.models.models import LLMConfig

CONFIG_DIR = Path(os.path.expanduser("~")) / ".secure-review"
CONFIG_FILE = CONFIG_DIR / "config.json"

def get_config_path() -> Path:
    return CONFIG_FILE

def load_config() -> LLMConfig:
    if not CONFIG_FILE.exists():
        save_config(LLMConfig())
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            # Filter keys to handle old/extra keys gracefully
            valid_keys = LLMConfig.model_fields.keys()
            filtered_data = {k: v for k, v in data.items() if k in valid_keys}
            return LLMConfig(**filtered_data)
    except Exception:
        return LLMConfig()

def save_config(config: LLMConfig) -> None:
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config.model_dump(), f, indent=2)
    except Exception as e:
        print(f"Error saving config to {CONFIG_FILE}: {e}")
