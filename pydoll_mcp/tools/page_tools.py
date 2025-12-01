"""Page Tools for PyDoll MCP Server.

This module provides MCP tools for general page-level interactions.
"""

import logging
from typing import Any, Dict, Sequence

from mcp.types import Tool, TextContent
from pydoll.commands import PageCommands

from ..core import get_browser_manager
from ..models import OperationResult

logger = logging.getLogger(__name__)

# Page Tools Definition
# Note: handle_dialog, handle_alert, save_page_as_pdf, save_pdf have been removed
# Use unified tools: interact_page (for dialogs) and capture_media (for PDFs) instead
PAGE_TOOLS = []

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

        # Check if dialog exists and get message
        dialog_message = None
        dialog_exists = False
        try:
            dialog_exists = await tab.has_dialog()
            if dialog_exists:
                dialog_message = await tab.get_dialog_message()
        except Exception as e:
            logger.debug(f"Could not check dialog state: {e}")

        # Handle dialog using native PyDoll API
        await tab.handle_dialog(accept=accept, prompt_text=prompt_text)

        result = OperationResult(
            success=True,
            message="Dialog handled successfully.",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "accepted": accept,
                "prompt_text_entered": prompt_text,
                "dialog_message": dialog_message,
                "dialog_detected": dialog_exists
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

async def handle_handle_alert(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle JavaScript alert/confirm dialogs (simplified interface)."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        accept = arguments.get("accept", True)

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Check if dialog exists and get message
        dialog_message = None
        dialog_exists = False
        try:
            dialog_exists = await tab.has_dialog()
            if dialog_exists:
                dialog_message = await tab.get_dialog_message()
        except Exception as e:
            logger.debug(f"Could not check dialog state: {e}")

        # Handle dialog using native PyDoll API
        await tab.handle_dialog(accept=accept)

        result = OperationResult(
            success=True,
            message="Alert handled successfully.",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "accepted": accept,
                "dialog_message": dialog_message,
                "dialog_detected": dialog_exists
            }
        )
        logger.info(f"Alert handled on tab {actual_tab_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to handle alert: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to handle alert."
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

async def handle_save_pdf(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle save PDF request with enhanced options and file saving support."""
    import base64
    import os
    from pathlib import Path

    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        file_path = arguments.get("file_path")
        pdf_format = arguments.get("format", "A4")
        print_background = arguments.get("print_background", True)

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Generate PDF with options
        pdf_data = await tab.print_to_pdf(
            as_base64=True,
            format=pdf_format,
            print_background=print_background
        )

        result_data = {
            "browser_id": browser_id,
            "tab_id": actual_tab_id,
            "format": pdf_format,
            "print_background": print_background
        }

        # Save to file if path provided
        if file_path:
            try:
                # Ensure directory exists
                pdf_path = Path(file_path)
                pdf_path.parent.mkdir(parents=True, exist_ok=True)

                # Decode and save PDF
                pdf_bytes = base64.b64decode(pdf_data)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)

                result_data["file_path"] = str(pdf_path.absolute())
                result_data["file_size"] = len(pdf_bytes)
                message = f"Page saved as PDF to {file_path}"
            except Exception as save_error:
                logger.error(f"Failed to save PDF to file: {save_error}")
                result_data["pdf_data"] = pdf_data
                result_data["save_error"] = str(save_error)
                message = "PDF generated but file save failed. PDF data returned as base64."
        else:
            result_data["pdf_data"] = pdf_data
            message = "Page saved as PDF successfully (base64 encoded)."

        result = OperationResult(
            success=True,
            message=message,
            data=result_data
        )
        logger.info(f"PDF saved on tab {actual_tab_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to save PDF: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to save PDF."
        )
        return [TextContent(type="text", text=result.json())]

# Page Tool Handlers Dictionary
# Note: handle_dialog, handle_alert, save_page_as_pdf, save_pdf handlers removed from public API
# Use unified tools: interact_page (for dialogs) and capture_media (for PDFs) instead
# Handler functions are kept as internal functions (used by unified tools)
PAGE_TOOL_HANDLERS = {}
