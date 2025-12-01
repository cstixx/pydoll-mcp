"""Tool Registry for Unified Tools.

This module registers the unified "Fat Tools" as MCP Tool objects.
"""

from mcp.types import Tool

from .definitions import (
    BrowserAction,
    BrowserControlInput,
    CaptureMediaInput,
    DialogAction,
    ElementAction,
    ElementFindAction,
    ExecuteCDPInput,
    ExecuteScriptInput,
    FileAction,
    FindElementInput,
    InteractElementInput,
    InteractPageInput,
    ManageFileInput,
    ManageTabInput,
    NavigatePageInput,
    NavigationAction,
    ScreenshotAction,
    ScriptAction,
    TabAction,
)
from .handlers import (
    handle_browser_control,
    handle_capture_media,
    handle_execute_cdp,
    handle_execute_script,
    handle_find_element,
    handle_interact_element,
    handle_interact_page,
    handle_manage_file,
    handle_manage_tab,
    handle_navigate_page,
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
        description="⭐ RECOMMENDED: Unified element interaction tool. Handles click, type, hover, press_key, drag, and scroll actions. Replaces multiple legacy element tools.",
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
        description="⭐ RECOMMENDED: Unified tab management tool. Handles create, close, refresh, activate, and list operations. Replaces multiple legacy tab tools.",
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
        description="⭐ RECOMMENDED: Unified browser control tool. Handles start, stop, get_state, list, create_context, list_contexts, delete_context, grant_permissions, and reset_permissions operations. Replaces multiple legacy browser tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in BrowserAction],
                    "description": "Action to perform: start, stop, get_state, list, create_context, list_contexts, delete_context, grant_permissions, reset_permissions"
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
                },
                "context_name": {
                    "type": "string",
                    "description": "Context name (for create_context action)"
                },
                "context_id": {
                    "type": "string",
                    "description": "Context ID (for delete_context action)"
                },
                "origin": {
                    "type": "string",
                    "description": "URL origin (for grant_permissions and reset_permissions actions)"
                },
                "permissions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of permissions (for grant_permissions action)"
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

    # Navigate Page Tool
    tools.append(Tool(
        name="navigate_page",
        description="⭐ RECOMMENDED: Unified page navigation tool. Handles navigate, go_back, go_forward, get_url, get_title, get_source, wait operations. Replaces multiple legacy navigation tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in NavigationAction],
                    "description": "Action to perform: navigate, go_back, go_forward, get_url, get_title, get_source, wait_load, wait_network_idle, set_viewport, get_info"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                },
                "url": {
                    "type": "string",
                    "description": "URL for navigate action"
                },
                "wait_for_load": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for page to load"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Timeout in seconds"
                },
                "referrer": {
                    "type": "string",
                    "description": "Referrer URL for navigate action"
                },
                "width": {
                    "type": "integer",
                    "description": "Viewport width for set_viewport action"
                },
                "height": {
                    "type": "integer",
                    "description": "Viewport height for set_viewport action"
                }
            },
            "required": ["action", "browser_id"]
        }
    ))

    # Capture Media Tool
    tools.append(Tool(
        name="capture_media",
        description="⭐ RECOMMENDED: Unified screenshot and media capture tool. Handles screenshot, element_screenshot, generate_pdf, save_page_as_pdf, and save_pdf operations. Replaces multiple legacy screenshot and PDF tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in ScreenshotAction],
                    "description": "Action to perform: screenshot, element_screenshot, generate_pdf, save_page_as_pdf, save_pdf"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                },
                "selector": {
                    "type": "object",
                    "description": "Element selector for element_screenshot action"
                },
                "format": {
                    "type": "string",
                    "enum": ["png", "jpeg", "jpg"],
                    "default": "png",
                    "description": "Image format"
                },
                "quality": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "JPEG quality (1-100)"
                },
                "full_page": {
                    "type": "boolean",
                    "default": False,
                    "description": "Capture full page"
                },
                "file_name": {
                    "type": "string",
                    "description": "Output filename"
                },
                "save_to_file": {
                    "type": "boolean",
                    "default": True,
                    "description": "Save to file"
                },
                "return_base64": {
                    "type": "boolean",
                    "default": False,
                    "description": "Return as base64"
                },
                "pdf_format": {
                    "type": "string",
                    "enum": ["A4", "A3", "A5", "Letter", "Legal", "Tabloid"],
                    "default": "A4",
                    "description": "PDF format"
                },
                "orientation": {
                    "type": "string",
                    "enum": ["portrait", "landscape"],
                    "default": "portrait",
                    "description": "PDF orientation"
                },
                "include_background": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include background in PDF"
                },
                "file_path": {
                    "type": "string",
                    "description": "File path to save PDF (for save_pdf action)"
                },
                "print_background": {
                    "type": "boolean",
                    "default": True,
                    "description": "Print background graphics (for save_pdf action)"
                }
            },
            "required": ["action", "browser_id"]
        }
    ))

    # Execute Script Tool
    tools.append(Tool(
        name="execute_script",
        description="⭐ RECOMMENDED: Unified script execution tool. Handles execute, evaluate, inject, and get_console_logs operations. Replaces multiple legacy script tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in ScriptAction],
                    "description": "Action to perform: execute, evaluate, inject, get_console_logs"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                },
                "script": {
                    "type": "string",
                    "description": "JavaScript code to execute"
                },
                "expression": {
                    "type": "string",
                    "description": "Expression to evaluate (for evaluate action)"
                },
                "library": {
                    "type": "string",
                    "enum": ["jquery", "lodash", "axios", "moment", "custom"],
                    "description": "Library to inject"
                },
                "custom_url": {
                    "type": "string",
                    "description": "Custom library URL"
                },
                "wait_for_execution": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for execution to complete"
                },
                "return_result": {
                    "type": "boolean",
                    "default": True,
                    "description": "Return execution result"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Execution timeout in seconds"
                },
                "context": {
                    "type": "string",
                    "enum": ["page", "isolated"],
                    "default": "page",
                    "description": "Execution context"
                }
            },
            "required": ["action", "browser_id"]
        }
    ))

    # Manage File Tool
    tools.append(Tool(
        name="manage_file",
        description="⭐ RECOMMENDED: Unified file operations tool. Handles upload, download, and manage_downloads operations. Replaces multiple legacy file tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in FileAction],
                    "description": "Action to perform: upload, download, manage_downloads"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                },
                "file_path": {
                    "type": "string",
                    "description": "File path for upload/download"
                },
                "input_selector": {
                    "type": "object",
                    "description": "File input selector for upload action"
                },
                "url": {
                    "type": "string",
                    "description": "URL for download action"
                },
                "save_path": {
                    "type": "string",
                    "description": "Save path for download action"
                },
                "download_action": {
                    "type": "string",
                    "enum": ["list", "pause", "resume", "cancel"],
                    "description": "Download management action"
                },
                "download_id": {
                    "type": "string",
                    "description": "Download ID for manage_downloads action"
                },
                "wait_for_completion": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for operation to complete"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Operation timeout in seconds"
                }
            },
            "required": ["action", "browser_id"]
        }
    ))

    # Interact Page Tool (Dialogs)
    tools.append(Tool(
        name="interact_page",
        description="⭐ RECOMMENDED: Unified page interaction tool. Handles handle_dialog and handle_alert operations. Replaces multiple legacy page interaction tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in DialogAction],
                    "description": "Action to perform: handle_dialog, handle_alert"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                },
                "accept": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to accept or dismiss the dialog"
                },
                "prompt_text": {
                    "type": "string",
                    "description": "Text to enter into prompt dialog (for handle_dialog action)"
                }
            },
            "required": ["action", "browser_id"]
        }
    ))

    # Find Element Tool
    tools.append(Tool(
        name="find_element",
        description="⭐ RECOMMENDED: Unified element finding tool. Handles find, find_all, query, wait_for, get_text, get_attribute, check_visibility, get_parent operations. Replaces multiple legacy element finding tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [action.value for action in ElementFindAction],
                    "description": "Action to perform: find, find_all, query, wait_for, get_text, get_attribute, check_visibility, get_parent"
                },
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Tab ID, uses active tab if not specified"
                },
                "selector": {
                    "type": "object",
                    "description": "Element selector dictionary"
                },
                "css_selector": {
                    "type": "string",
                    "description": "CSS selector for query action"
                },
                "xpath": {
                    "type": "string",
                    "description": "XPath for query action"
                },
                "find_all": {
                    "type": "boolean",
                    "default": False,
                    "description": "Find all matching elements"
                },
                "timeout": {
                    "type": "integer",
                    "default": 10,
                    "description": "Timeout in seconds for wait_for action"
                },
                "wait_for_visible": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for element to be visible"
                },
                "attribute_name": {
                    "type": "string",
                    "description": "Attribute name for get_attribute action"
                },
                "search_shadow_dom": {
                    "type": "boolean",
                    "default": False,
                    "description": "Search within shadow DOM"
                }
            },
            "required": ["action", "browser_id", "selector"]
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
        "navigate_page": lambda args: wrap_handler(handle_navigate_page, NavigatePageInput, args),
        "capture_media": lambda args: wrap_handler(handle_capture_media, CaptureMediaInput, args),
        "execute_script": lambda args: wrap_handler(handle_execute_script, ExecuteScriptInput, args),
        "manage_file": lambda args: wrap_handler(handle_manage_file, ManageFileInput, args),
        "find_element": lambda args: wrap_handler(handle_find_element, FindElementInput, args),
        "interact_page": lambda args: wrap_handler(handle_interact_page, InteractPageInput, args),
    }

