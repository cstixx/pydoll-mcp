"""Centralized Configuration Management for PyDoll MCP Server.

This module provides centralized configuration using Pydantic Settings,
replacing scattered os.getenv() calls throughout the codebase.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file if it exists
load_dotenv()


class Settings(BaseSettings):
    """Global settings for PyDoll MCP Server.

    All settings can be overridden via environment variables.
    Settings are loaded from .env file if present, then from environment.
    """

    model_config = SettingsConfigDict(
        env_prefix="PYDOLL_",
        case_sensitive=False,
        extra="ignore",
    )

    # Browser Configuration
    browser_type: str = Field(default="chrome", description="Browser type: chrome or edge")
    headless_mode: bool = Field(default=False, description="Run browser in headless mode")
    window_width: int = Field(default=1920, ge=100, le=7680, description="Browser window width in pixels")
    window_height: int = Field(default=1080, ge=100, le=4320, description="Browser window height in pixels")
    stealth_mode: bool = Field(default=True, description="Enable stealth mode to avoid detection")

    # Network Configuration
    default_proxy: Optional[str] = Field(default=None, description="Proxy server in format host:port")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent string")

    # Resource Limits
    max_browsers: int = Field(default=3, ge=1, description="Maximum number of browser instances")
    max_tabs_per_browser: int = Field(default=10, ge=1, description="Maximum tabs per browser instance")

    # Paths
    download_path: Path = Field(
        default_factory=lambda: Path.home() / ".local" / "share" / "pydoll-mcp" / "downloads",
        description="Default download directory"
    )
    session_db_path: Path = Field(
        default_factory=lambda: Path.home() / ".local" / "share" / "pydoll-mcp" / "sessions.db",
        description="SQLite database path for session persistence"
    )

    # Performance Settings
    cleanup_interval: int = Field(default=300, ge=60, description="Cleanup interval in seconds (5 minutes)")
    idle_timeout: int = Field(default=1800, ge=60, description="Idle timeout in seconds (30 minutes)")

    # Feature Flags
    disable_images: bool = Field(default=False, description="Disable image loading for faster browsing")
    block_ads: bool = Field(default=True, description="Block advertisement requests")

    # Binary Paths (optional)
    binary_path: Optional[str] = Field(default=None, description="Custom browser binary path")
    user_data_dir: Optional[str] = Field(default=None, description="Custom user data directory")

    def __init__(self, **kwargs):
        """Initialize settings and ensure directories exist."""
        super().__init__(**kwargs)
        # Ensure download directory exists
        self.download_path.mkdir(parents=True, exist_ok=True)
        # Ensure session database directory exists
        self.session_db_path.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings: The global settings instance (singleton)
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience accessor
settings = get_settings()

