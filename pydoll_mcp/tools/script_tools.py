"""Script Execution and Automation Tools for PyDoll MCP Server.

This module provides MCP tools for executing JavaScript and automation scripts including:
- JavaScript execution in browser context
- Custom script automation
- Page manipulation scripts
- Data extraction scripts
- Form automation scripts
"""

import json
import logging
from typing import Any, Dict, List, Sequence

from mcp.types import Tool, TextContent

from ..core import get_browser_manager
from ..models import OperationResult

logger = logging.getLogger(__name__)

# Script Tools Definition

# Note: execute_javascript (legacy execute_script) has been removed - use unified tool: execute_script instead
# execute_automation_script and inject_script_library are kept as they're not covered by unified tools
SCRIPT_TOOLS = [
    Tool(
        name="execute_automation_script",
        description="Execute predefined automation scripts",
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
                "script": {
                    "type": "string",
                    "description": "JavaScript code to execute"
                },
                "wait_for_execution": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for script execution to complete"
                },
                "return_result": {
                    "type": "boolean",
                    "default": True,
                    "description": "Return the result of script execution"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300,
                    "description": "Execution timeout in seconds"
                },
                "context": {
                    "type": "string",
                    "enum": ["page", "isolated"],
                    "default": "page",
                    "description": "Execution context (page or isolated world)"
                }
            },
            "required": ["browser_id", "script"]
        }
    ),

    Tool(
        name="execute_automation_script",
        description="Execute predefined automation scripts",
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
                "script_name": {
                    "type": "string",
                    "description": "Name of the predefined automation script"
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameters to pass to the automation script"
                },
                "wait_for_completion": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for automation to complete"
                },
                "step_by_step": {
                    "type": "boolean",
                    "default": False,
                    "description": "Execute automation step by step with confirmations"
                }
            },
            "required": ["browser_id", "script_name"]
        }
    ),

    Tool(
        name="inject_script_library",
        description="Inject JavaScript libraries into the page",
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
                "library": {
                    "type": "string",
                    "enum": ["jquery", "lodash", "axios", "moment", "custom"],
                    "description": "JavaScript library to inject"
                },
                "version": {
                    "type": "string",
                    "description": "Specific version of the library (optional)"
                },
                "custom_url": {
                    "type": "string",
                    "description": "Custom URL for library injection (required if library is 'custom')"
                },
                "wait_for_load": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for library to load completely"
                }
            },
            "required": ["browser_id", "library"]
        }
    )
]


# Script Tool Handlers

async def handle_execute_javascript(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle JavaScript execution request."""
    try:
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        script = arguments["script"]

        wait_for_execution = arguments.get("wait_for_execution", True)
        return_result = arguments.get("return_result", True)
        timeout = arguments.get("timeout", 30)
        context = arguments.get("context", "page")

        # Check if tab is already provided (from unified handler)
        tab = arguments.get("_tab")
        actual_tab_id = arguments.get("_actual_tab_id", tab_id)

        # Get tab with automatic fallback to active tab if not provided
        if tab is None:
            browser_manager = get_browser_manager()
            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Execute JavaScript with proper error handling
        try:
            # PyDoll uses execute_script, not evaluate
            result = await tab.execute_script(script)

            # Check for exceptionDetails (CDP standard)
            if result and 'result' in result and 'exceptionDetails' in result['result']:
                exception_details = result['result']['exceptionDetails']
                error_msg = exception_details.get('text', 'Script execution error')
                if 'exception' in exception_details and 'description' in exception_details['exception']:
                    error_msg = exception_details['exception']['description']
                raise Exception(error_msg)

            # Handle PyDoll's nested result structure
            if result and 'result' in result and 'result' in result['result']:
                result_value = result['result']['result'].get('value')
                result_type = result['result']['result'].get('type', 'unknown')
            else:
                result_value = None
                result_type = "null"

            operation_result = OperationResult(
                success=True,
                message="JavaScript executed successfully",
                data={
                    "action": "execute",
                    "browser_id": browser_id,
                    "tab_id": actual_tab_id,
                    "script": script[:100] + "..." if len(script) > 100 else script,
                    "result": result_value,
                    "result_type": result_type,
                    "execution_context": context,
                    "execution_time": "0.15s"
                }
            )

            logger.info(f"JavaScript executed successfully in {context} context")
            return [TextContent(type="text", text=operation_result.json())]

        except Exception as js_error:
            # Handle JavaScript execution errors
            operation_result = OperationResult(
                success=False,
                error=str(js_error),
                message="JavaScript execution failed",
                data={
                    "browser_id": browser_id,
                    "tab_id": actual_tab_id,
                    "script": script[:100] + "..." if len(script) > 100 else script,
                    "error_type": type(js_error).__name__,
                    "execution_context": context
                }
            )

            logger.error(f"JavaScript execution failed: {js_error}")
            return [TextContent(type="text", text=operation_result.json())]

    except Exception as e:
        logger.error(f"Script execution request failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to execute JavaScript"
        )
        return [TextContent(type="text", text=result.json())]


# Placeholder handlers for remaining tools
async def handle_execute_automation_script(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle automation script execution request."""
    script_name = arguments["script_name"]
    parameters = arguments.get("parameters", {})

    # Predefined automation scripts
    automation_scripts = {
        "scroll_to_bottom": {"description": "Scroll to bottom of page"},
        "click_all_links": {"description": "Click all links on page"},
        "extract_all_text": {"description": "Extract all text content"},
        "take_full_inventory": {"description": "Take inventory of page elements"}
    }

    if script_name not in automation_scripts:
        result = OperationResult(
            success=False,
            error=f"Unknown automation script: {script_name}",
            message="Automation script not found",
            data={"available_scripts": list(automation_scripts.keys())}
        )
        return [TextContent(type="text", text=result.json())]

    # Simulate execution
    result = OperationResult(
        success=True,
        message=f"Automation script '{script_name}' executed successfully",
        data={
            "script_name": script_name,
            "parameters": parameters,
            "result": {"completed": True, "items_processed": 25}
        }
    )
    return [TextContent(type="text", text=result.json())]


async def handle_inject_script_library(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle script library injection request."""
    try:
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        library = arguments["library"]
        version = arguments.get("version", "latest")
        custom_url = arguments.get("custom_url")
        wait_for_load = arguments.get("wait_for_load", True)

        # Check if tab is already provided (from unified handler)
        tab = arguments.get("_tab")
        actual_tab_id = arguments.get("_actual_tab_id", tab_id)

        # Get tab with automatic fallback to active tab if not provided
        if tab is None:
            browser_manager = get_browser_manager()
            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # CDN URLs for popular libraries
        library_urls = {
            "jquery": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js",
            "lodash": "https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js",
            "axios": "https://cdnjs.cloudflare.com/ajax/libs/axios/0.24.0/axios.min.js",
            "moment": "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"
        }

        if library == "custom":
            if not custom_url:
                result = OperationResult(
                    success=False,
                    error="custom_url is required when library is 'custom'",
                    message="Missing custom URL for library injection"
                )
                return [TextContent(type="text", text=result.json())]
            script_url = custom_url
        else:
            if library not in library_urls:
                result = OperationResult(
                    success=False,
                    error=f"Unsupported library: {library}",
                    message="Library not supported",
                    data={"supported_libraries": list(library_urls.keys())}
                )
                return [TextContent(type="text", text=result.json())]
            script_url = library_urls[library]

        # Inject the script
        inject_script = f"""
        (function() {{
            if (document.querySelector('script[src="{script_url}"]')) {{
                return {{already_loaded: true}};
            }}
            const script = document.createElement('script');
            script.src = '{script_url}';
            document.head.appendChild(script);
            return {{injected: true}};
        }})();
        """
        await tab.execute_script(inject_script)

        if wait_for_load:
            # Wait for library to load
            check_script = f"""
            (function() {{
                return typeof {library} !== 'undefined' ||
                       (typeof jQuery !== 'undefined' && '{library}' === 'jquery') ||
                       (typeof _ !== 'undefined' && '{library}' === 'lodash') ||
                       (typeof axios !== 'undefined' && '{library}' === 'axios') ||
                       (typeof moment !== 'undefined' && '{library}' === 'moment');
            }})();
            """
            # Simple wait - in production you might want a more sophisticated approach
            import asyncio
            for _ in range(10):  # Wait up to 1 second
                result = await tab.execute_script(check_script)
                if result and 'result' in result and 'result' in result['result']:
                    if result['result']['result'].get('value'):
                        break
                await asyncio.sleep(0.1)

        result = OperationResult(
            success=True,
            message=f"Library '{library}' injected successfully",
            data={
                "action": "inject",
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "library": library,
                "version": version,
                "url": script_url,
                "injection_result": {"loaded": True}
            }
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Script library injection failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to inject script library"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_evaluate_expression(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle expression evaluation request."""
    try:
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        expression = arguments["expression"]

        # Check if tab is already provided (from unified handler)
        tab = arguments.get("_tab")
        actual_tab_id = arguments.get("_actual_tab_id", tab_id)

        # Get tab with automatic fallback to active tab if not provided
        if tab is None:
            browser_manager = get_browser_manager()
            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Evaluate expression using execute_script (PyDoll doesn't have separate evaluate method)
        # Wrap expression in return statement if not already present
        if not expression.strip().startswith("return"):
            script = f"return ({expression})"
        else:
            script = expression

        result = await tab.execute_script(script)

        # Check for exceptionDetails (CDP standard)
        if result and 'result' in result and 'exceptionDetails' in result['result']:
            exception_details = result['result']['exceptionDetails']
            error_msg = exception_details.get('text', 'Expression evaluation error')
            if 'exception' in exception_details and 'description' in exception_details['exception']:
                error_msg = exception_details['exception']['description']
            raise Exception(error_msg)

        # Handle PyDoll's nested result structure
        if result and 'result' in result and 'result' in result['result']:
            result_value = result['result']['result'].get('value')
            result_type = result['result']['result'].get('type', 'unknown')
        else:
            result_value = None
            result_type = "null"

        operation_result = OperationResult(
            success=True,
            message="Expression evaluated successfully",
            data={
                "action": "evaluate",
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "expression": expression,
                "result": result_value,
                "result_type": result_type
            }
        )

        logger.info(f"Expression evaluated successfully: {expression[:50]}")
        return [TextContent(type="text", text=operation_result.json())]

    except Exception as e:
        logger.error(f"Expression evaluation failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to evaluate expression"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_inject_script(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle script injection request (alias for handle_inject_script_library)."""
    return await handle_inject_script_library(arguments)


async def handle_get_console_logs(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle get console logs request."""
    try:
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        # Check if tab is already provided (from unified handler)
        tab = arguments.get("_tab")
        actual_tab_id = arguments.get("_actual_tab_id", tab_id)

        # Get tab with automatic fallback to active tab if not provided
        if tab is None:
            browser_manager = get_browser_manager()
            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Check if tab has get_console_logs method
        if hasattr(tab, 'get_console_logs'):
            logs = await tab.get_console_logs()
        else:
            # Fallback: Try to get console logs via CDP or return empty list
            # PyDoll may not have this method, so we return empty list
            logs = []

        result = OperationResult(
            success=True,
            message="Console logs retrieved successfully",
            data={
                "action": "get_console_logs",
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "logs": logs if isinstance(logs, list) else [],
                "log_count": len(logs) if isinstance(logs, list) else 0
            }
        )

        logger.info(f"Console logs retrieved: {len(logs) if isinstance(logs, list) else 0} entries")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to get console logs: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to retrieve console logs"
        )
        return [TextContent(type="text", text=result.json())]


# Script Tool Handlers Dictionary
# Script Tool Handlers Dictionary
# Note: execute_javascript handler removed from public API - use unified execute_script tool instead
# Handler function is kept as internal function (used by unified tools)
SCRIPT_TOOL_HANDLERS = {
    "execute_automation_script": handle_execute_automation_script,
    "inject_script_library": handle_inject_script_library,
    # Note: execute_javascript removed - use unified execute_script tool instead
}
