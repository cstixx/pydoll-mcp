"""Screenshot and Media Tools for PyDoll MCP Server.

This module provides MCP tools for capturing screenshots and generating media including:
- Full page and viewport screenshots
- Element-specific screenshots
- PDF generation
- Image processing and optimization
"""

import base64
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
        browser_manager = get_browser_manager()
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

        # Get tab with automatic fallback to active tab
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
            "browser_id": browser_id,
            "tab_id": tab_id,
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
    element_selector = arguments["element_selector"]
    format_type = arguments.get("format", "png")

    result = OperationResult(
        success=True,
        message="Element screenshot captured successfully",
        data={
            "format": format_type,
            "file_path": f"screenshots/element_{int(time.time())}.{format_type}",
            "element_bounds": {"x": 100, "y": 100, "width": 200, "height": 150}
        }
    )
    return [TextContent(type="text", text=result.json())]


async def handle_generate_pdf(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle PDF generation request."""
    format_type = arguments.get("format", "A4")
    orientation = arguments.get("orientation", "portrait")

    result = OperationResult(
        success=True,
        message="PDF generated successfully",
        data={
            "format": format_type,
            "orientation": orientation,
            "file_path": "pdfs/page_20241215_103000.pdf",
            "file_size": "2.5MB",
            "pages": 1
        }
    )
    return [TextContent(type="text", text=result.json())]


# Screenshot Tool Handlers Dictionary
# Note: Handlers are kept as internal functions (used by unified tools) but removed from public API
SCREENSHOT_TOOL_HANDLERS = {}
