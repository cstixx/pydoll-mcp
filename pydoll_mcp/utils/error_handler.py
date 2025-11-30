"""Error Handling Decorator for PyDoll MCP Server.

This module provides a decorator that enriches error responses with
contextual information to help LLMs understand and recover from failures.
"""

import asyncio
import logging
import os
import traceback
from functools import wraps
from typing import Any, Callable, Dict, Optional

from mcp.types import TextContent

from ..models import OperationResult

logger = logging.getLogger(__name__)

DEBUG_MODE = os.getenv("PYDOLL_DEBUG", "0").lower() in ("1", "true", "yes")


def enrich_errors(handler_func: Callable) -> Callable:
    """Decorator to enrich error responses with contextual information.

    This decorator wraps tool handlers to catch exceptions and add
    helpful context like DOM snapshots, page URLs, etc.

    Args:
        handler_func: Async handler function to wrap

    Returns:
        Wrapped handler function with error enrichment
    """
    @wraps(handler_func)
    async def wrapper(*args, **kwargs) -> list[TextContent]:
        """Wrapped handler with error enrichment."""
        # Get arguments (could be first positional arg or in kwargs)
        arguments = args[0] if args else kwargs

        try:
            return await handler_func(*args, **kwargs)

        except asyncio.TimeoutError as e:
            return await _handle_timeout_error(e, arguments)

        except (ValueError, AttributeError) as e:
            # Check if it's an element-related error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["element", "not found", "selector", "tab", "browser"]):
                return await _handle_element_error(e, arguments)
            return await _handle_generic_error(e, arguments)

        except Exception as e:
            return await _handle_generic_error(e, arguments)

    return wrapper


async def _handle_timeout_error(error: Exception, arguments: Any) -> list[TextContent]:
    """Handle timeout errors with page context."""
    try:
        from ..core import get_browser_manager
        from .dom_helper import get_page_context

        # Handle both dict and Pydantic model
        if isinstance(arguments, dict):
            browser_id = arguments.get("browser_id")
            tab_id = arguments.get("tab_id")
        else:
            browser_id = getattr(arguments, "browser_id", None)
            tab_id = getattr(arguments, "tab_id", None)

        context = {}
        if browser_id:
            try:
                browser_manager = get_browser_manager()
                tab, _ = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
                page_context = await get_page_context(tab)
                context.update(page_context)
            except Exception as e:
                logger.debug(f"Failed to get page context for timeout error: {e}")

        result = OperationResult(
            success=False,
            error="TimeoutError",
            message=str(error),
            metadata={
                "context": context,
                "error_type": "timeout"
            }
        )

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error in timeout error handler: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error="TimeoutError",
            message=str(error)
        ).json())]


async def _handle_element_error(error: Exception, arguments: Any) -> list[TextContent]:
    """Handle element-related errors with DOM snapshot."""
    try:
        from ..core import get_browser_manager
        from .dom_helper import get_dom_snapshot, get_page_context

        # Handle both dict and Pydantic model
        if isinstance(arguments, dict):
            browser_id = arguments.get("browser_id")
            tab_id = arguments.get("tab_id")
        else:
            browser_id = getattr(arguments, "browser_id", None)
            tab_id = getattr(arguments, "tab_id", None)

        context = {
            "dom_snapshot": None,
            "current_url": None,
            "page_title": None,
        }

        if browser_id:
            try:
                browser_manager = get_browser_manager()
                tab, _ = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

                # Get DOM snapshot
                dom_snapshot = await get_dom_snapshot(tab)
                context["dom_snapshot"] = dom_snapshot

                # Get page context
                page_context = await get_page_context(tab)
                context.update(page_context)

            except Exception as e:
                logger.debug(f"Failed to get DOM context for element error: {e}")

        result = OperationResult(
            success=False,
            error=type(error).__name__,
            message=str(error),
            metadata={
                "context": context,
                "error_type": "element_not_found"
            }
        )

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error in element error handler: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(error).__name__,
            message=str(error)
        ).json())]


async def _handle_generic_error(error: Exception, arguments: Any) -> list[TextContent]:
    """Handle generic errors with optional stack trace."""
    try:
        metadata = {
            "error_type": type(error).__name__,
        }

        # Add stack trace in debug mode
        if DEBUG_MODE:
            metadata["stack_trace"] = traceback.format_exc()

        # Try to get page context if browser_id is available
        # Handle both dict and Pydantic model
        if isinstance(arguments, dict):
            browser_id = arguments.get("browser_id")
            tab_id = arguments.get("tab_id")
        else:
            browser_id = getattr(arguments, "browser_id", None)
            tab_id = getattr(arguments, "tab_id", None)

        if browser_id:
            try:
                from ..core import get_browser_manager
                from .dom_helper import get_page_context

                browser_manager = get_browser_manager()
                tab, _ = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
                page_context = await get_page_context(tab)
                metadata["context"] = page_context
            except Exception:
                pass  # Ignore errors in context gathering

        result = OperationResult(
            success=False,
            error=type(error).__name__,
            message=str(error),
            metadata=metadata
        )

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error in generic error handler: {e}", exc_info=True)
        # Fallback to simple error response
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(error).__name__,
            message=str(error)
        ).json())]

