"""Tool Registry for Unified Tools.

This module registers the unified "Fat Tools" as MCP Tool objects.
"""

from mcp.types import Tool

from .definitions import (
    BrowserAction,
    BrowserControlInput,
    ElementAction,
    ExecuteCDPInput,
    InteractElementInput,
    ManageTabInput,
    TabAction,
)
from .handlers import (
    handle_browser_control,
    handle_execute_cdp,
    handle_interact_element,
    handle_manage_tab,
)


def create_unified_tools() -> list[Tool]:
    """Create MCP Tool definitions for unified tools.

    Returns:
        List of MCP Tool objects
    """
    tools = []

    # Interact Element Tool
    tools.append(Tool(
        name="interact_element",
        description="Unified element interaction tool. Handles click, type, hover, press_key, drag, and scroll actions.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in ElementAction],
                    "description": "Action to perform: click, type, hover, press_key, drag, scroll"
                },
                "selector": {
                    "type": "object",
                    "description": "Element selector dictionary. Supports id, class_name, tag_name, text, name, type, placeholder, value, data_testid, data_id, aria_label, aria_role, css_selector, xpath",
                    "properties": {
                        "id": {"type": "string"},
                        "class_name": {"type": "string"},
                        "tag_name": {"type": "string"},
                        "text": {"type": "string"},
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "placeholder": {"type": "string"},
                        "value": {"type": "string"},
                        "data_testid": {"type": "string"},
                        "data_id": {"type": "string"},
                        "aria_label": {"type": "string"},
                        "aria_role": {"type": "string"},
                        "css_selector": {"type": "string"},
                        "xpath": {"type": "string"},
                    }
                },
                "value": {
                    "type": "string",
                    "description": "Value for type action or key for press_key action"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                },
                "click_type": {
                    "type": "string",
                    "enum": ["left", "right", "double", "middle"],
                    "default": "left",
                    "description": "Click type (for click action)"
                },
                "scroll_to_element": {
                    "type": "boolean",
                    "default": True,
                    "description": "Scroll element into view before action"
                },
                "human_like": {
                    "type": "boolean",
                    "default": True,
                    "description": "Use human-like behavior"
                },
                "typing_speed": {
                    "type": "string",
                    "enum": ["slow", "normal", "fast", "instant"],
                    "default": "normal",
                    "description": "Typing speed (for type action)"
                },
                "clear_first": {
                    "type": "boolean",
                    "default": True,
                    "description": "Clear existing text before typing (for type action)"
                }
            },
            "required": ["action", "selector", "browser_id"]
        }
    ))

    # Manage Tab Tool
    tools.append(Tool(
        name="manage_tab",
        description="Unified tab management tool. Handles create, close, refresh, activate, and list operations.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in TabAction],
                    "description": "Action to perform: create, close, refresh, activate, list"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID (required for close, refresh, activate actions)"
                },
                "url": {
                    "type": "string",
                    "description": "URL for create action"
                },
                "background": {
                    "type": "boolean",
                    "default": False,
                    "description": "Open tab in background (for create action)"
                },
                "wait_for_load": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for page to load (for create/refresh actions)"
                },
                "ignore_cache": {
                    "type": "boolean",
                    "default": False,
                    "description": "Ignore cache on refresh (for refresh action)"
                }
            },
            "required": ["action", "browser_id"]
        }
    ))

    # Browser Control Tool
    tools.append(Tool(
        name="browser_control",
        description="Unified browser control tool. Handles start, stop, get_state, and list operations.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in BrowserAction],
                    "description": "Action to perform: start, stop, get_state, list"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser ID (required for stop, get_state actions)"
                },
                "config": {
                    "type": "object",
                    "description": "Browser configuration dictionary (for start action)"
                },
                "browser_type": {
                    "type": "string",
                    "enum": ["chrome", "edge"],
                    "default": "chrome",
                    "description": "Browser type (for start action)"
                },
                "headless": {
                    "type": "boolean",
                    "default": False,
                    "description": "Run in headless mode (for start action)"
                },
                "window_width": {
                    "type": "integer",
                    "default": 1920,
                    "description": "Window width (for start action)"
                },
                "window_height": {
                    "type": "integer",
                    "default": 1080,
                    "description": "Window height (for start action)"
                },
                "stealth_mode": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable stealth mode (for start action)"
                },
                "proxy_server": {
                    "type": "string",
                    "description": "Proxy server (for start action)"
                },
                "user_agent": {
                    "type": "string",
                    "description": "Custom user agent (for start action)"
                }
            },
            "required": ["action"]
        }
    ))

    # Execute CDP Tool
    tools.append(Tool(
        name="execute_cdp_command",
        description="Execute raw Chrome DevTools Protocol (CDP) commands. Provides direct access to browser internals.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "CDP domain (e.g., 'Page', 'Network', 'DOM', 'Runtime', 'Debugger')",
                    "examples": ["Page", "Network", "DOM", "Runtime"]
                },
                "method": {
                    "type": "string",
                    "description": "CDP method name (e.g., 'printToPDF', 'navigate', 'evaluate')",
                    "examples": ["printToPDF", "navigate", "evaluate"]
                },
                "params": {
                    "type": "object",
                    "description": "CDP method parameters",
                    "default": {}
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                }
            },
            "required": ["domain", "method", "browser_id"]
        }
    ))

    return tools


def create_unified_handlers() -> dict[str, callable]:
    """Create handler mapping for unified tools.

    Returns:
        Dictionary mapping tool names to handler functions
    """
    async def wrap_handler(handler_func, input_class, args):
        """Wrapper that converts dict to Pydantic model and calls handler."""
        try:
            input_data = input_class(**args)
            return await handler_func(input_data)
        except Exception as e:
            # If Pydantic validation fails, return error
            from ..models import OperationResult
            from mcp.types import TextContent
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="ValidationError",
                message=f"Invalid input: {e}"
            ).json())]

    return {
        "interact_element": lambda args: wrap_handler(handle_interact_element, InteractElementInput, args),
        "manage_tab": lambda args: wrap_handler(handle_manage_tab, ManageTabInput, args),
        "browser_control": lambda args: wrap_handler(handle_browser_control, BrowserControlInput, args),
        "execute_cdp_command": lambda args: wrap_handler(handle_execute_cdp, ExecuteCDPInput, args),
    }

