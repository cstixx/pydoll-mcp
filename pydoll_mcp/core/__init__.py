"""Core modules for PyDoll MCP Server.

This package contains core functionality including browser management
and session persistence.
"""

from .browser_manager import (
    BrowserInstance,
    BrowserManager,
    BrowserMetrics,
    BrowserPool,
    get_browser_manager,
    cleanup_browser_manager,
)
from .session_store import SessionStore

__all__ = [
    "BrowserInstance",
    "BrowserManager",
    "BrowserMetrics",
    "BrowserPool",
    "get_browser_manager",
    "cleanup_browser_manager",
    "SessionStore",
]

