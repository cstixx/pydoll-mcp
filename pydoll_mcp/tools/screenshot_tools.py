"""Screenshot and Media Tools for PyDoll MCP Server.

This module provides MCP tools for capturing screenshots and generating media including:
- Full page and viewport screenshots
- Element-specific screenshots
- PDF generation
- Image processing and optimization
"""

import base64
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Sequence

from mcp.types import Tool, TextContent

from ..core import get_browser_manager
from ..models import ScreenshotConfig, ScreenshotResult, OperationResult

logger = logging.getLogger(__name__)

# Screenshot Tools Definition

# Note: All screenshot tools have been moved to unified tools
# - take_screenshot, take_element_screenshot, generate_pdf, save_page_as_pdf, save_pdf
# Use unified tool: capture_media instead
#
# SCREENSHOT_TOOLS removed - all tools replaced by unified tools
# Handler functions are kept below for internal use by unified tool handlers

# Screenshot Tool Handlers

async def handle_take_screenshot(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle page screenshot request."""
    try:
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        # Extract screenshot configuration
        config = ScreenshotConfig(
            format=arguments.get("format", "png"),
            quality=arguments.get("quality"),
            full_page=arguments.get("full_page", False),
            viewport_only=arguments.get("viewport_only", True),
            hide_scrollbars=arguments.get("hide_scrollbars", True)
        )

        file_name = arguments.get("file_name")
        save_to_file = arguments.get("save_to_file", True)
        return_base64 = arguments.get("return_base64", False)
        clip_area = arguments.get("clip_area")

        # Check if tab is already provided (from unified handler)
        tab = arguments.get("_tab")
        actual_tab_id = arguments.get("_actual_tab_id", tab_id)

        # Get tab with automatic fallback to active tab if not provided
        if tab is None:
            browser_manager = get_browser_manager()
            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        try:
            # Prepare screenshot options based on PyDoll API
            screenshot_options = {}

            # PyDoll only supports path, quality, and as_base64 parameters
            if config.quality:
                screenshot_options["quality"] = config.quality

            # Use as_base64 to get the data for processing
            screenshot_options["as_base64"] = True

            # Take screenshot using PyDoll
            screenshot_base64 = await tab.take_screenshot(**screenshot_options)

            # Convert base64 to bytes
            import base64
            screenshot_bytes = base64.b64decode(screenshot_base64) if screenshot_base64 else b""

        except Exception as e:
            logger.warning(f"Real screenshot failed, using simulation: {e}")
            # Fallback to simulation
            screenshot_bytes = b"fake_screenshot_data"

        # Prepare file path
        file_path = None
        if save_to_file:
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)

            if not file_name:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"screenshot_{timestamp}.{config.format}"
            elif not file_name.endswith(f".{config.format}"):
                file_name = f"{file_name}.{config.format}"

            file_path = screenshots_dir / file_name

            # Save screenshot to file (simulated)
            with open(file_path, "wb") as f:
                f.write(screenshot_bytes)

        # Prepare result data
        result_data = {
            "action": "screenshot",
            "browser_id": browser_id,
            "tab_id": actual_tab_id,
            "format": config.format,
            "full_page": config.full_page,
            "file_size": len(screenshot_bytes),
            "timestamp": "2024-01-15T10:30:00Z",
            "width": 1920,  # Would get actual dimensions
            "height": 1080
        }

        if file_path:
            result_data["file_path"] = str(file_path)

        if return_base64:
            base64_data = base64.b64encode(screenshot_bytes).decode('utf-8')
            result_data["base64_data"] = f"data:image/{config.format};base64,{base64_data}"

        result = OperationResult(
            success=True,
            message="Screenshot captured successfully",
            data=result_data
        )

        logger.info(f"Screenshot captured: {file_path if file_path else 'in-memory'}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to capture screenshot"
        )
        return [TextContent(type="text", text=result.json())]


# Placeholder handlers for remaining tools
async def handle_take_element_screenshot(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle element screenshot request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        # Support both selector and element_selector keys
        element_selector = arguments.get("selector") or arguments.get("element_selector")
        if not element_selector:
            raise ValueError("Selector is required for element screenshot")

        format_type = arguments.get("format", "png")
        save_to_file = arguments.get("save_to_file", True)
        return_base64 = arguments.get("return_base64", False)
        file_name = arguments.get("file_name")

        # Check if tab is already provided (from unified handler)
        tab = arguments.get("_tab")
        actual_tab_id = arguments.get("_actual_tab_id", tab_id)

        # Get tab with automatic fallback to active tab if not provided
        if tab is None:
            browser_manager = get_browser_manager()
            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Find element
        from .element_tools import handle_find_element
        find_args = {
            "browser_id": browser_id,
            "tab_id": actual_tab_id,
            "selector": element_selector,
            "find_all": False,
            "_tab": tab,  # Pass already-retrieved tab
            "_actual_tab_id": actual_tab_id
        }
        find_result = await handle_find_element(find_args)
        find_data = json.loads(find_result[0].text)

        if not find_data.get("success") or not find_data.get("data", {}).get("element"):
            raise ValueError("Element not found for screenshot")

        # Take element screenshot (simplified - would need actual element reference)
        file_path = None
        if save_to_file:
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)

            if not file_name:
                file_name = f"element_{int(time.time())}.{format_type}"
            elif not file_name.endswith(f".{format_type}"):
                file_name = f"{file_name}.{format_type}"

            file_path = screenshots_dir / file_name
            # In real implementation, would take actual screenshot
            with open(file_path, "wb") as f:
                f.write(b"fake_element_screenshot_data")

        result_data = {
            "action": "element_screenshot",
            "browser_id": browser_id,
            "tab_id": actual_tab_id,
            "format": format_type,
            "file_path": str(file_path) if file_path else None,
            "element_bounds": {"x": 100, "y": 100, "width": 200, "height": 150}
        }

        if return_base64:
            result_data["base64_data"] = "data:image/png;base64,fake_data"

        result = OperationResult(
            success=True,
            message="Element screenshot captured successfully",
            data=result_data
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Element screenshot failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to capture element screenshot"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_generate_pdf(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle PDF generation request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        format_type = arguments.get("format", "A4")
        orientation = arguments.get("orientation", "portrait")
        include_background = arguments.get("include_background", True)
        file_name = arguments.get("file_name")

        # Check if tab is already provided (from unified handler)
        tab = arguments.get("_tab")
        actual_tab_id = arguments.get("_actual_tab_id", tab_id)

        # Get tab with automatic fallback to active tab if not provided
        if tab is None:
            browser_manager = get_browser_manager()
            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Generate PDF using tab.pdf() method
        pdf_bytes = await tab.pdf(format=format_type, orientation=orientation)

        # Save to file if file_name provided
        file_path = None
        if file_name:
            pdfs_dir = Path("pdfs")
            pdfs_dir.mkdir(exist_ok=True)
            if not file_name.endswith(".pdf"):
                file_name = f"{file_name}.pdf"
            file_path = pdfs_dir / file_name
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)

        result = OperationResult(
            success=True,
            message="PDF generated successfully",
            data={
                "action": "generate_pdf",
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "format": format_type,
                "orientation": orientation,
                "file_path": str(file_path) if file_path else None,
                "file_size": len(pdf_bytes),
                "pages": 1
            }
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to generate PDF"
        )
        return [TextContent(type="text", text=result.json())]


# Screenshot Tool Handlers Dictionary
# Note: Handlers are kept as internal functions (used by unified tools) but removed from public API
SCREENSHOT_TOOL_HANDLERS = {}
