"""Utility modules for PyDoll MCP Server.

This package contains utility functions for error handling,
DOM manipulation, and other shared functionality.
"""

from .dom_helper import get_dom_snapshot, get_page_context
from .error_handler import enrich_errors

__all__ = [
    "enrich_errors",
    "get_dom_snapshot",
    "get_page_context",
]

