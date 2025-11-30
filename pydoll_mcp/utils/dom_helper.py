"""DOM Helper Utilities for PyDoll MCP Server.

This module provides utilities for extracting and formatting DOM information
for LLM consumption, particularly for error context enrichment.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def get_dom_snapshot(tab, max_length: int = 2000) -> str:
    """Get a simplified DOM snapshot for LLM context.

    Extracts text content and structure information from the page,
    limited to a reasonable size for LLM consumption.

    Args:
        tab: PyDoll Tab object
        max_length: Maximum length of snapshot in characters

    Returns:
        Formatted string with DOM information
    """
    try:
        # Get page text content
        text_content = ""
        try:
            if hasattr(tab, 'execute_script'):
                text_content = await tab.execute_script("""
                    return document.body ? document.body.innerText || document.body.textContent : '';
                """)
            elif hasattr(tab, 'evaluate'):
                text_content = await tab.evaluate("document.body.innerText || document.body.textContent")
        except Exception as e:
            logger.debug(f"Failed to get text content: {e}")
            text_content = ""

        # Get element counts
        element_counts = {}
        try:
            if hasattr(tab, 'execute_script'):
                counts = await tab.execute_script("""
                    return {
                        total: document.querySelectorAll('*').length,
                        buttons: document.querySelectorAll('button').length,
                        inputs: document.querySelectorAll('input, textarea, select').length,
                        links: document.querySelectorAll('a').length,
                        images: document.querySelectorAll('img').length
                    };
                """)
                element_counts = counts if isinstance(counts, dict) else {}
        except Exception as e:
            logger.debug(f"Failed to get element counts: {e}")

        # Truncate text content if too long
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "... (truncated)"

        # Format output
        lines = []
        lines.append("=== DOM Snapshot ===")

        if element_counts:
            lines.append(f"Elements: {element_counts.get('total', 'unknown')} total")
            lines.append(f"  - Buttons: {element_counts.get('buttons', 0)}")
            lines.append(f"  - Inputs: {element_counts.get('inputs', 0)}")
            lines.append(f"  - Links: {element_counts.get('links', 0)}")
            lines.append(f"  - Images: {element_counts.get('images', 0)}")

        if text_content:
            lines.append("\nPage Text Content:")
            lines.append(text_content)
        else:
            lines.append("\n(No text content available)")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get DOM snapshot: {e}", exc_info=True)
        return f"Error generating DOM snapshot: {e}"


async def get_page_context(tab) -> Dict[str, Any]:
    """Get comprehensive page context information.

    Args:
        tab: PyDoll Tab object

    Returns:
        Dictionary with page context (URL, title, ready state, etc.)
    """
    context = {
        "url": None,
        "title": None,
        "ready_state": None,
    }

    try:
        # Get URL
        try:
            if hasattr(tab, 'current_url'):
                context["url"] = await tab.current_url()
            elif hasattr(tab, 'url'):
                context["url"] = tab.url
        except Exception as e:
            logger.debug(f"Failed to get URL: {e}")

        # Get title
        try:
            if hasattr(tab, 'page_title'):
                context["title"] = await tab.page_title()
            elif hasattr(tab, 'title'):
                context["title"] = tab.title
        except Exception as e:
            logger.debug(f"Failed to get title: {e}")

        # Get ready state
        try:
            if hasattr(tab, 'execute_script'):
                context["ready_state"] = await tab.execute_script("return document.readyState")
        except Exception as e:
            logger.debug(f"Failed to get ready state: {e}")

    except Exception as e:
        logger.error(f"Failed to get page context: {e}", exc_info=True)

    return context

