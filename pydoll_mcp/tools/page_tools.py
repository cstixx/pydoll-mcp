"""Page Tools for PyDoll MCP Server.

This module provides MCP tools for general page-level interactions.
"""

import logging
from typing import Any, Dict, Sequence

from mcp.types import Tool, TextContent
from pydoll.commands import PageCommands

from ..browser_manager import get_browser_manager
from ..models import OperationResult

logger = logging.getLogger(__name__)

# Page Tools Definition
PAGE_TOOLS = [
    Tool(
        name="handle_dialog",
        description="Handle JavaScript dialogs like alert, confirm, or prompt.",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Optional tab ID, uses active tab if not specified"
                },
                "accept": {
                    "type": "boolean",
                    "description": "Whether to accept or dismiss the dialog.",
                    "default": True
                },
                "prompt_text": {
                    "type": "string",
                    "description": "Text to enter into the prompt dialog."
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="save_page_as_pdf",
        description="Save the current page as a PDF file.",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Optional tab ID, uses active tab if not specified"
                }
            },
            "required": ["browser_id"]
        }
    ),
]

# Page Tool Handlers
async def handle_handle_dialog(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle JavaScript dialogs."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        accept = arguments.get("accept", True)
        prompt_text = arguments.get("prompt_text")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        await tab._execute_command(
            PageCommands.handle_javascript_dialog(accept=accept, prompt_text=prompt_text)
        )

        result = OperationResult(
            success=True,
            message="Dialog handled successfully.",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "accepted": accept,
                "prompt_text_entered": prompt_text
            }
        )
        logger.info(f"Dialog handled on tab {actual_tab_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to handle dialog: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to handle dialog."
        )
        return [TextContent(type="text", text=result.json())]

async def handle_save_page_as_pdf(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle save page as PDF request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        pdf_data = await tab.print_to_pdf(as_base64=True)

        result = OperationResult(
            success=True,
            message="Page saved as PDF successfully.",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "pdf_data": pdf_data
            }
        )
        logger.info(f"Page saved as PDF on tab {actual_tab_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to save page as PDF: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to save page as PDF."
        )
        return [TextContent(type="text", text=result.json())]

# Page Tool Handlers Dictionary
PAGE_TOOL_HANDLERS = {
    "handle_dialog": handle_handle_dialog,
    "save_page_as_pdf": handle_save_page_as_pdf,
}