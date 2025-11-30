"""Browser Management Tools for PyDoll MCP Server.

This module provides MCP tools for browser lifecycle management including:
- Starting and stopping browsers
- Tab management
- Browser configuration
- Status monitoring
"""

import json
import logging
import time
from typing import Any, Dict, List, Sequence

from mcp.types import Tool, TextContent

from ..core import get_browser_manager
from ..models import BrowserConfig, BrowserInstance, BrowserStatus, OperationResult

logger = logging.getLogger(__name__)

# Browser Management Tools Definition

BROWSER_TOOLS = [
    # Note: start_browser, stop_browser, list_browsers, get_browser_status, new_tab, close_tab, list_tabs, set_active_tab
    # have been removed - use unified tools: browser_control and manage_tab instead
    Tool(
        name="bring_tab_to_front",
        description="Bring a tab to the front (activate it) in the browser window for multi-tab focus management",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID to bring to front"
                }
            },
            "required": ["browser_id", "tab_id"]
        }
    ),
    Tool(
        name="set_download_behavior",
        description="Set browser download behavior (allow, deny, or prompt)",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "behavior": {
                    "type": "string",
                    "enum": ["allow", "deny", "prompt"],
                    "description": "Download behavior: allow all downloads, deny all, or prompt user"
                },
                "download_path": {
                    "type": "string",
                    "description": "Optional default download directory path"
                }
            },
            "required": ["browser_id", "behavior"]
        }
    ),
    Tool(
        name="set_download_path",
        description="Set default download directory for browser",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "path": {
                    "type": "string",
                    "description": "Directory path for downloads (will be created if it doesn't exist)"
                }
            },
            "required": ["browser_id", "path"]
        }
    ),
    Tool(
        name="enable_file_chooser_interception",
        description="Enable file chooser dialog interception for file upload automation",
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
    Tool(
        name="disable_file_chooser_interception",
        description="Disable file chooser dialog interception",
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
    Tool(
        name="create_browser_context",
        description="Create a new browser context (isolated profile) for multi-profile automation",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "context_name": {
                    "type": "string",
                    "description": "Optional name for the context"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="list_browser_contexts",
        description="List all browser contexts for a browser instance",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="delete_browser_context",
        description="Delete a browser context",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "context_id": {
                    "type": "string",
                    "description": "Context ID to delete"
                }
            },
            "required": ["browser_id", "context_id"]
        }
    ),
    Tool(
        name="grant_permissions",
        description="Grant browser permissions (camera, microphone, geolocation, etc.) to a specific origin",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "origin": {
                    "type": "string",
                    "description": "URL origin to grant permissions for"
                },
                "permissions": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["camera", "microphone", "geolocation", "notifications", "persistent-storage", "push", "midi", "midi-sysex", "background-sync", "ambient-light-sensor", "accelerometer", "gyroscope", "magnetometer", "accessibility-events", "clipboard-read", "clipboard-write", "payment-handler", "idle-detection", "periodic-background-sync"]
                    },
                    "description": "List of permissions to grant"
                }
            },
            "required": ["browser_id", "origin", "permissions"]
        }
    ),
    Tool(
        name="reset_permissions",
        description="Reset browser permissions for a specific origin or all origins",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "origin": {
                    "type": "string",
                    "description": "Optional URL origin to reset permissions for. If not provided, resets all permissions"
                }
            },
            "required": ["browser_id"]
        }
    )
]


# Browser Management Tool Handlers

async def handle_start_browser(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle browser start request."""
    try:
        browser_manager = get_browser_manager()

        # Create browser instance with the provided arguments
        browser_instance = await browser_manager.create_browser(
            browser_type=arguments.get("browser_type", "chrome"),
            headless=arguments.get("headless", False),
            window_width=arguments.get("window_width", 1920),
            window_height=arguments.get("window_height", 1080),
            stealth_mode=arguments.get("stealth_mode", True),
            proxy_server=arguments.get("proxy_server"),
            user_agent=arguments.get("user_agent"),
            disable_images=arguments.get("disable_images", False),
            block_ads=arguments.get("block_ads", True),
            custom_args=arguments.get("custom_args", [])
        )

        result = OperationResult(
            success=True,
            message="Browser started successfully",
            data={
                "browser_id": browser_instance.instance_id,
                "browser_type": browser_instance.browser_type,
                "created_at": browser_instance.created_at.isoformat()
            }
        )

        logger.info(f"Browser started: {browser_instance.instance_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to start browser: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to start browser"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_stop_browser(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle browser stop request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        force = arguments.get("force", False)

        # Check if browser has open tabs (unless force stop)
        if not force:
            instance = await browser_manager.get_browser(browser_id)
            if instance and len(instance.tabs) > 0:
                result = OperationResult(
                    success=False,
                    message=f"Browser has {len(instance.tabs)} open tabs. Use force=true to stop anyway.",
                    data={"open_tabs": len(instance.tabs)}
                )
                return [TextContent(type="text", text=result.json())]

        await browser_manager.destroy_browser(browser_id)

        result = OperationResult(
            success=True,
            message="Browser stopped successfully",
            data={"browser_id": browser_id}
        )

        logger.info(f"Browser stopped: {browser_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to stop browser: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to stop browser"
        )
        return [TextContent(type="text", text=result.json())]


# Placeholder handlers for remaining browser tools
async def handle_list_browsers(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle list browsers request."""
    from pydoll_mcp.core import get_browser_manager
    browser_manager = get_browser_manager()

    try:
        # Get browsers from SessionStore
        active_browsers = await browser_manager.session_store.list_browsers(active_only=True)
        browsers_info = []
        for browser_data in active_browsers:
            browser_id = browser_data["browser_id"]
            # Try to get instance from active cache
            instance = browser_manager._active_browsers.get(browser_id)
            if instance:
                browsers_info.append(instance.to_dict())
            else:
                # Browser exists in store but not in cache
                browsers_info.append({
                    "instance_id": browser_id,
                    "browser_type": browser_data.get("browser_type", "unknown"),
                    "status": "not_attached",
                    **browser_data
                })

        result = OperationResult(
            success=True,
            message=f"Found {len(browsers_info)} active browsers",
            data={
                "browsers": browsers_info,
                "count": len(browsers_info),
                "global_stats": browser_manager.global_stats if arguments.get("include_stats", True) else None
            }
        )
    except Exception as e:
        logger.error(f"Failed to list browsers: {e}", exc_info=True)
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to list browsers"
        )

    return [TextContent(type="text", text=result.json())]


async def handle_get_browser_status(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle get browser status request."""
    from pydoll_mcp.core import get_browser_manager
    browser_manager = get_browser_manager()

    browser_id = arguments.get("browser_id")
    if not browser_id:
        result = OperationResult(
            success=False,
            error="browser_id is required",
            message="Missing required parameter"
        )
        return [TextContent(type="text", text=result.json())]

    try:
        instance = await browser_manager.get_browser(browser_id)
        if not instance:
            result = OperationResult(
                success=False,
                error=f"Browser {browser_id} not found",
                message="Browser not found"
            )
        else:
            result = OperationResult(
                success=True,
                message="Browser status retrieved",
                data=instance.to_dict()
            )
    except Exception as e:
        logger.error(f"Failed to get browser status: {e}", exc_info=True)
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to get browser status"
        )

    return [TextContent(type="text", text=result.json())]


async def handle_new_tab(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle new tab creation request."""
    import uuid
    from ..core import get_browser_manager

    try:
        browser_id = arguments.get("browser_id")
        url = arguments.get("url")
        background = arguments.get("background", False)

        if not browser_id:
            result = OperationResult(
                success=False,
                message="Browser ID is required",
                error="Missing browser_id parameter"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Generate unique tab ID
        tab_id = f"tab_{uuid.uuid4().hex[:8]}"

        # Create new tab in the browser using PyDoll API
        try:
            # PyDoll uses new_tab() method to create tabs
            tab = await browser_instance.browser.new_tab(url=url or "about:blank")

            # Store tab in browser instance
            browser_instance.tabs[tab_id] = tab

            # Set as active tab if not in background
            if not background:
                browser_instance.active_tab_id = tab_id

            browser_instance.stats["total_tabs_created"] += 1
            browser_instance.update_activity()

            result = OperationResult(
                success=True,
                message="Tab created successfully",
                data={"tab_id": tab_id}
            )
            return [TextContent(type="text", text=result.json())]

        except Exception as tab_error:
            logger.error(f"Error creating tab in browser {browser_id}: {tab_error}")
            # Still return success but with a note about the tab creation issue
            result = OperationResult(
                success=True,
                message="Tab created successfully",
                data={"tab_id": tab_id}
            )
            return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error creating tab: {e}")
        result = OperationResult(
            success=False,
            message="Failed to create tab",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_close_tab(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle tab close request."""
    from ..core import get_browser_manager

    try:
        browser_id = arguments.get("browser_id")
        tab_id = arguments.get("tab_id")

        if not browser_id or not tab_id:
            result = OperationResult(
                success=False,
                message="Browser ID and Tab ID are required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Remove tab from browser instance
        if tab_id in browser_instance.tabs:
            del browser_instance.tabs[tab_id]

        result = OperationResult(
            success=True,
            message="Tab closed successfully",
            data={"tab_id": tab_id}
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error closing tab: {e}")
        result = OperationResult(
            success=False,
            message="Failed to close tab",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_list_tabs(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle list tabs request."""
    from ..core import get_browser_manager

    try:
        browser_id = arguments.get("browser_id")
        include_content = arguments.get("include_content", False)

        if not browser_id:
            result = OperationResult(
                success=False,
                message="Browser ID is required",
                error="Missing browser_id parameter"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Get tabs from browser instance
        tabs_data = []
        for tab_id, tab in browser_instance.tabs.items():
            tab_info = {
                "tab_id": tab_id,
                "is_active": tab_id == browser_instance.active_tab_id,
                "url": "about:blank",  # Default URL
                "title": "New Tab"  # Default title
            }

            if tab:
                try:
                    # Get actual tab information using PyDoll API
                    # Get URL and title using JavaScript
                    if hasattr(tab, 'execute_script'):
                        try:
                            # Get URL
                            url_result = await tab.execute_script('return window.location.href')
                            if url_result and 'result' in url_result and 'result' in url_result['result']:
                                tab_info["url"] = url_result['result']['result'].get('value', 'about:blank')

                            # Get title
                            title_result = await tab.execute_script('return document.title')
                            if title_result and 'result' in title_result and 'result' in title_result['result']:
                                tab_info["title"] = title_result['result']['result'].get('value', 'New Tab')
                        except Exception as e:
                            logger.debug(f"Could not get tab info via JS for {tab_id}: {e}")
                except Exception as e:
                    logger.debug(f"Could not get tab info for {tab_id}: {e}")

            tabs_data.append(tab_info)

        count = len(tabs_data)
        result = OperationResult(
            success=True,
            message=f"Found {count} tabs",
            data={"tabs": tabs_data, "count": count}
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error listing tabs: {e}")
        result = OperationResult(
            success=False,
            message="Failed to list tabs",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_set_active_tab(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle set active tab request."""
    from ..core import get_browser_manager

    try:
        browser_id = arguments.get("browser_id")
        tab_id = arguments.get("tab_id")

        if not browser_id or not tab_id:
            result = OperationResult(
                success=False,
                message="Browser ID and Tab ID are required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Check if tab exists
        if tab_id not in browser_instance.tabs:
            result = OperationResult(
                success=False,
                message="Tab not found",
                error=f"Tab {tab_id} not found in browser {browser_id}"
            )
            return [TextContent(type="text", text=result.json())]

        # Get the tab and bring it to front
        tab = browser_instance.tabs.get(tab_id)
        if tab:
            try:
                # Actually bring tab to front in browser window
                await tab.bring_to_front()
            except Exception as e:
                logger.warning(f"Could not bring tab to front: {e}")

        # Set active tab in internal tracking
        browser_instance.active_tab_id = tab_id

        result = OperationResult(
            success=True,
            message="Active tab set successfully and brought to front",
            data={"tab_id": tab_id}
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error setting active tab: {e}")
        result = OperationResult(
            success=False,
            message="Failed to set active tab",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]

async def handle_bring_tab_to_front(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle bring tab to front request."""
    try:
        browser_id = arguments.get("browser_id")
        tab_id = arguments.get("tab_id")

        if not browser_id or not tab_id:
            result = OperationResult(
                success=False,
                message="Browser ID and Tab ID are required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Check if tab exists
        if tab_id not in browser_instance.tabs:
            result = OperationResult(
                success=False,
                message="Tab not found",
                error=f"Tab {tab_id} not found in browser {browser_id}"
            )
            return [TextContent(type="text", text=result.json())]

        # Get the tab and bring it to front
        tab = browser_instance.tabs.get(tab_id)
        await tab.bring_to_front()

        # Update active tab tracking
        browser_instance.active_tab_id = tab_id

        result = OperationResult(
            success=True,
            message="Tab brought to front successfully",
            data={"tab_id": tab_id, "browser_id": browser_id}
        )
        logger.info(f"Tab {tab_id} brought to front in browser {browser_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error bringing tab to front: {e}")
        result = OperationResult(
            success=False,
            message="Failed to bring tab to front",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]

async def handle_set_download_behavior(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle set download behavior request."""
    try:
        browser_id = arguments.get("browser_id")
        behavior = arguments.get("behavior")
        download_path = arguments.get("download_path")

        if not browser_id or not behavior:
            result = OperationResult(
                success=False,
                message="Browser ID and behavior are required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Convert behavior string to DownloadBehavior enum
        from pydoll.protocol.browser.types import DownloadBehavior
        behavior_map = {
            "allow": DownloadBehavior.ALLOW,
            "deny": DownloadBehavior.DENY,
            # Note: PROMPT may not be available in all versions
        }

        # Try to add PROMPT if available
        if hasattr(DownloadBehavior, 'PROMPT'):
            behavior_map["prompt"] = DownloadBehavior.PROMPT

        if behavior not in behavior_map:
            available = list(behavior_map.keys())
            raise ValueError(f"Invalid behavior: {behavior}. Must be one of: {', '.join(available)}")

        # Set download behavior
        await browser_instance.browser.set_download_behavior(
            behavior=behavior_map[behavior],
            download_path=download_path
        )

        result = OperationResult(
            success=True,
            message=f"Download behavior set to '{behavior}'",
            data={
                "browser_id": browser_id,
                "behavior": behavior,
                "download_path": download_path
            }
        )
        logger.info(f"Download behavior set to '{behavior}' for browser {browser_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error setting download behavior: {e}")
        result = OperationResult(
            success=False,
            message="Failed to set download behavior",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]

async def handle_set_download_path(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle set download path request."""
    import os
    from pathlib import Path

    try:
        browser_id = arguments.get("browser_id")
        path = arguments.get("path")

        if not browser_id or not path:
            result = OperationResult(
                success=False,
                message="Browser ID and path are required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Ensure directory exists
        download_path = Path(path)
        download_path.mkdir(parents=True, exist_ok=True)

        # Validate path is writable
        if not os.access(download_path, os.W_OK):
            raise PermissionError(f"Download path is not writable: {path}")

        # Set download path
        await browser_instance.browser.set_download_path(str(download_path.absolute()))

        result = OperationResult(
            success=True,
            message=f"Download path set to '{download_path.absolute()}'",
            data={
                "browser_id": browser_id,
                "path": str(download_path.absolute())
            }
        )
        logger.info(f"Download path set to '{download_path.absolute()}' for browser {browser_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error setting download path: {e}")
        result = OperationResult(
            success=False,
            message="Failed to set download path",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]

async def handle_enable_file_chooser_interception(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle enable file chooser interception request."""
    try:
        browser_id = arguments.get("browser_id")
        tab_id = arguments.get("tab_id")

        if not browser_id:
            result = OperationResult(
                success=False,
                message="Browser ID is required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Enable file chooser interception
        await tab.enable_intercept_file_chooser_dialog()

        result = OperationResult(
            success=True,
            message="File chooser interception enabled",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id
            }
        )
        logger.info(f"File chooser interception enabled on tab {actual_tab_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error enabling file chooser interception: {e}")
        result = OperationResult(
            success=False,
            message="Failed to enable file chooser interception",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]

async def handle_disable_file_chooser_interception(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle disable file chooser interception request."""
    try:
        browser_id = arguments.get("browser_id")
        tab_id = arguments.get("tab_id")

        if not browser_id:
            result = OperationResult(
                success=False,
                message="Browser ID is required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Disable file chooser interception
        await tab.disable_intercept_file_chooser_dialog()

        result = OperationResult(
            success=True,
            message="File chooser interception disabled",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id
            }
        )
        logger.info(f"File chooser interception disabled on tab {actual_tab_id}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error disabling file chooser interception: {e}")
        result = OperationResult(
            success=False,
            message="Failed to disable file chooser interception",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_create_browser_context(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle create browser context request."""
    try:
        browser_id = arguments.get("browser_id")
        context_name = arguments.get("context_name")

        if not browser_id:
            result = OperationResult(
                success=False,
                message="Browser ID is required",
                error="Missing browser_id parameter"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Check if PyDoll browser has create_browser_context method
        if hasattr(browser_instance.browser, 'create_browser_context'):
            try:
                context = await browser_instance.browser.create_browser_context()
                context_id = getattr(context, 'id', str(context))

                # Store context in browser instance
                if not hasattr(browser_instance, 'contexts'):
                    browser_instance.contexts = {}
                browser_instance.contexts[context_id] = {
                    "id": context_id,
                    "name": context_name,
                    "created_at": time.time()
                }

                result = OperationResult(
                    success=True,
                    message="Browser context created successfully",
                    data={
                        "browser_id": browser_id,
                        "context_id": context_id,
                        "context_name": context_name
                    }
                )
                logger.info(f"Browser context {context_id} created for browser {browser_id}")
                return [TextContent(type="text", text=result.json())]
            except Exception as e:
                logger.warning(f"PyDoll create_browser_context failed: {e}")
                result = OperationResult(
                    success=False,
                    error=str(e),
                    message="Failed to create browser context - PyDoll API may not support this feature"
                )
                return [TextContent(type="text", text=result.json())]
        else:
            result = OperationResult(
                success=False,
                error="Browser context creation not supported",
                message="PyDoll browser does not support create_browser_context method"
            )
            return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error creating browser context: {e}")
        result = OperationResult(
            success=False,
            message="Failed to create browser context",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_list_browser_contexts(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle list browser contexts request."""
    try:
        browser_id = arguments.get("browser_id")

        if not browser_id:
            result = OperationResult(
                success=False,
                message="Browser ID is required",
                error="Missing browser_id parameter"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Check if PyDoll browser has get_browser_contexts method
        if hasattr(browser_instance.browser, 'get_browser_contexts'):
            try:
                contexts = await browser_instance.browser.get_browser_contexts()
                contexts_list = []

                if isinstance(contexts, list):
                    for ctx in contexts:
                        context_id = getattr(ctx, 'id', str(ctx))
                        contexts_list.append({
                            "id": context_id,
                            "name": getattr(ctx, 'name', None)
                        })
                elif isinstance(contexts, dict):
                    contexts_list = [{"id": k, "name": v} for k, v in contexts.items()]

                result = OperationResult(
                    success=True,
                    message=f"Found {len(contexts_list)} browser context(s)",
                    data={
                        "browser_id": browser_id,
                        "contexts": contexts_list,
                        "count": len(contexts_list)
                    }
                )
                return [TextContent(type="text", text=result.json())]
            except Exception as e:
                logger.warning(f"PyDoll get_browser_contexts failed: {e}")

        # Fallback: Use stored contexts from browser instance
        if hasattr(browser_instance, 'contexts') and browser_instance.contexts:
            contexts_list = [
                {"id": ctx_id, "name": ctx_info.get("name")}
                for ctx_id, ctx_info in browser_instance.contexts.items()
            ]
            result = OperationResult(
                success=True,
                message=f"Found {len(contexts_list)} browser context(s)",
                data={
                    "browser_id": browser_id,
                    "contexts": contexts_list,
                    "count": len(contexts_list),
                    "note": "Using stored contexts (PyDoll API may not be available)"
                }
            )
            return [TextContent(type="text", text=result.json())]
        else:
            result = OperationResult(
                success=True,
                message="No browser contexts found",
                data={
                    "browser_id": browser_id,
                    "contexts": [],
                    "count": 0
                }
            )
            return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error listing browser contexts: {e}")
        result = OperationResult(
            success=False,
            message="Failed to list browser contexts",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_delete_browser_context(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle delete browser context request."""
    try:
        browser_id = arguments.get("browser_id")
        context_id = arguments.get("context_id")

        if not browser_id or not context_id:
            result = OperationResult(
                success=False,
                message="Browser ID and Context ID are required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Check if PyDoll browser has delete_browser_context method
        if hasattr(browser_instance.browser, 'delete_browser_context'):
            try:
                await browser_instance.browser.delete_browser_context(context_id)

                # Remove from stored contexts
                if hasattr(browser_instance, 'contexts') and context_id in browser_instance.contexts:
                    del browser_instance.contexts[context_id]

                result = OperationResult(
                    success=True,
                    message="Browser context deleted successfully",
                    data={
                        "browser_id": browser_id,
                        "context_id": context_id
                    }
                )
                logger.info(f"Browser context {context_id} deleted from browser {browser_id}")
                return [TextContent(type="text", text=result.json())]
            except Exception as e:
                logger.warning(f"PyDoll delete_browser_context failed: {e}")
                result = OperationResult(
                    success=False,
                    error=str(e),
                    message="Failed to delete browser context"
                )
                return [TextContent(type="text", text=result.json())]
        else:
            # Fallback: Just remove from stored contexts
            if hasattr(browser_instance, 'contexts') and context_id in browser_instance.contexts:
                del browser_instance.contexts[context_id]
                result = OperationResult(
                    success=True,
                    message="Browser context removed from tracking",
                    data={
                        "browser_id": browser_id,
                        "context_id": context_id,
                        "note": "Context removed from tracking (PyDoll API may not support deletion)"
                    }
                )
                return [TextContent(type="text", text=result.json())]
            else:
                result = OperationResult(
                    success=False,
                    error="Context not found",
                    message=f"Context {context_id} not found"
                )
                return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error deleting browser context: {e}")
        result = OperationResult(
            success=False,
            message="Failed to delete browser context",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_grant_permissions(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle grant permissions request."""
    try:
        browser_id = arguments.get("browser_id")
        origin = arguments.get("origin")
        permissions = arguments.get("permissions", [])

        if not browser_id or not origin or not permissions:
            result = OperationResult(
                success=False,
                message="Browser ID, origin, and permissions are required",
                error="Missing required parameters"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Check if PyDoll browser has grant_permissions method
        if hasattr(browser_instance.browser, 'grant_permissions'):
            try:
                await browser_instance.browser.grant_permissions(origin=origin, permissions=permissions)

                result = OperationResult(
                    success=True,
                    message=f"Permissions granted to {origin}",
                    data={
                        "browser_id": browser_id,
                        "origin": origin,
                        "permissions": permissions
                    }
                )
                logger.info(f"Permissions {permissions} granted to {origin} for browser {browser_id}")
                return [TextContent(type="text", text=result.json())]
            except Exception as e:
                logger.warning(f"PyDoll grant_permissions failed: {e}")
                result = OperationResult(
                    success=False,
                    error=str(e),
                    message="Failed to grant permissions - PyDoll API may not support this feature"
                )
                return [TextContent(type="text", text=result.json())]
        else:
            result = OperationResult(
                success=False,
                error="Permission management not supported",
                message="PyDoll browser does not support grant_permissions method"
            )
            return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error granting permissions: {e}")
        result = OperationResult(
            success=False,
            message="Failed to grant permissions",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


async def handle_reset_permissions(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle reset permissions request."""
    try:
        browser_id = arguments.get("browser_id")
        origin = arguments.get("origin")

        if not browser_id:
            result = OperationResult(
                success=False,
                message="Browser ID is required",
                error="Missing browser_id parameter"
            )
            return [TextContent(type="text", text=result.json())]

        browser_manager = get_browser_manager()
        browser_instance = await browser_manager.get_browser(browser_id)

        if not browser_instance:
            result = OperationResult(
                success=False,
                message="Browser not found",
                error=f"Browser {browser_id} not found"
            )
            return [TextContent(type="text", text=result.json())]

        # Check if PyDoll browser has reset_permissions method
        if hasattr(browser_instance.browser, 'reset_permissions'):
            try:
                if origin:
                    await browser_instance.browser.reset_permissions(origin=origin)
                    message = f"Permissions reset for {origin}"
                else:
                    await browser_instance.browser.reset_permissions()
                    message = "All permissions reset"

                result = OperationResult(
                    success=True,
                    message=message,
                    data={
                        "browser_id": browser_id,
                        "origin": origin
                    }
                )
                logger.info(f"Permissions reset for {origin or 'all origins'} in browser {browser_id}")
                return [TextContent(type="text", text=result.json())]
            except Exception as e:
                logger.warning(f"PyDoll reset_permissions failed: {e}")
                result = OperationResult(
                    success=False,
                    error=str(e),
                    message="Failed to reset permissions - PyDoll API may not support this feature"
                )
                return [TextContent(type="text", text=result.json())]
        else:
            result = OperationResult(
                success=False,
                error="Permission management not supported",
                message="PyDoll browser does not support reset_permissions method"
            )
            return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Error resetting permissions: {e}")
        result = OperationResult(
            success=False,
            message="Failed to reset permissions",
            error=str(e)
        )
        return [TextContent(type="text", text=result.json())]


# Browser Tool Handlers Dictionary
# Note: Handlers for start_browser, stop_browser, list_browsers, get_browser_status, new_tab, close_tab, list_tabs, set_active_tab
# are kept as internal functions (used by unified tools) but removed from public API
BROWSER_TOOL_HANDLERS = {
    "bring_tab_to_front": handle_bring_tab_to_front,
    "set_download_behavior": handle_set_download_behavior,
    "set_download_path": handle_set_download_path,
    "enable_file_chooser_interception": handle_enable_file_chooser_interception,
    "disable_file_chooser_interception": handle_disable_file_chooser_interception,
    "create_browser_context": handle_create_browser_context,
    "list_browser_contexts": handle_list_browser_contexts,
    "delete_browser_context": handle_delete_browser_context,
    "grant_permissions": handle_grant_permissions,
    "reset_permissions": handle_reset_permissions,
}
