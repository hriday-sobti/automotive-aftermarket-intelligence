"""Configuration loader and application logging utilities."""

import os
import sys
import logging
from typing import Any, Dict
import yaml

_CONFIG_CACHE: Dict[str, Any] | None = None


def load_config(config_path: str = "config/project_config.yaml") -> Dict[str, Any]:
    """Load and cache project YAML configuration.

    Args:
        config_path: Relative or absolute path to project_config.yaml.

    Returns:
        Dictionary containing project configuration parameters.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    _CONFIG_CACHE = config
    return config


def setup_logger(name: str = "aftermarket", level: int = logging.INFO) -> logging.Logger:
    """Configure and return a standardized structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
