"""Configuration loader for the wall finishing robot application."""

import tomllib
from pathlib import Path
from typing import Any, Dict, Optional

from .schemas import Settings


class ConfigLoader:
    """Configuration loader that handles TOML files and environment variables."""

    def __init__(self, config_dir: str = "src/config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.toml"
        self.template_file = self.config_dir / "config.template.toml"

    def load_toml_config(self, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        if file_path is None:
            file_path = self.config_file

        if not file_path.exists():
            return {}

        try:
            with open(file_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config from {file_path}: {e}")
            return {}

    def merge_configs(
        self, base_config: Dict[str, Any], override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two configuration dictionaries recursively."""
        result = base_config.copy()

        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def load_settings(self) -> Settings:
        """Load and merge all configuration sources."""
        # Start with template config as base
        template_config = self.load_toml_config(self.template_file)

        # Override with actual config if it exists
        config = self.load_toml_config(self.config_file)
        merged_config = self.merge_configs(template_config, config)

        # Create Settings instance (this will also read from .env file)
        settings = Settings(**merged_config)

        return settings


# Global config loader instance
config_loader = ConfigLoader()


def get_settings() -> Settings:
    """Get the application settings."""
    return config_loader.load_settings()
