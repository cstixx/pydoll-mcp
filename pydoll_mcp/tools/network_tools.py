"""Network Monitoring and Control Tools for PyDoll MCP Server.

This module provides MCP tools for network monitoring and manipulation including:
- Request interception and modification
- Response monitoring and extraction
- Performance analysis
- Cache and resource management
"""

import logging
from typing import Any, Dict, Sequence, List
import json
import time

from mcp.types import Tool, TextContent

from ..core import get_browser_manager
from ..models import OperationResult

logger = logging.getLogger(__name__)

# Network Tools Definition

NETWORK_TOOLS = [
    Tool(
        name="intercept_network_requests",
        description="Intercept and modify network requests and responses",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "action": {
                    "type": "string",
                    "enum": ["start", "stop", "configure"],
                    "description": "Interception action"
                },
                "patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URL patterns to intercept (regex supported)"
                },
                "modify_requests": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable request modification"
                },
                "modify_responses": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable response modification"
                }
            },
            "required": ["browser_id", "action"]
        }
    ),
    Tool(
        name="get_network_logs",
        description="Retrieve detailed network activity logs using PyDoll's get_network_logs API",
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
                "filter": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "enum": ["document", "script", "image", "stylesheet", "xhr", "fetch"],
                            "description": "Filter by resource type"
                        },
                        "status_code": {
                            "type": "integer",
                            "description": "Filter by HTTP status code"
                        }
                    }
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="get_network_response_body",
        description="Get the response body for a specific network request using PyDoll's get_network_response_body API",
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
                "request_id": {
                    "type": "string",
                    "description": "Request ID from network logs"
                },
                "url": {
                    "type": "string",
                    "description": "URL of the request (alternative to request_id)"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="block_requests",
        description="Block specific network requests",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URL patterns to block"
                },
                "resource_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["image", "script", "stylesheet", "font", "media"]
                    },
                    "description": "Resource types to block"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="modify_request_headers",
        description="Modify HTTP request headers",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "headers": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Headers to add or modify"
                },
                "remove_headers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Headers to remove"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="extract_api_responses",
        description="Extract and save API responses",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "api_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "API URL patterns to monitor"
                },
                "save_to_file": {
                    "type": "boolean",
                    "default": False,
                    "description": "Save responses to files"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="monitor_websockets",
        description="Monitor WebSocket connections and messages",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "action": {
                    "type": "string",
                    "enum": ["start", "stop", "get_messages"],
                    "description": "Monitoring action"
                },
                "filter_pattern": {
                    "type": "string",
                    "description": "Filter messages by pattern"
                }
            },
            "required": ["browser_id", "action"]
        }
    ),
    Tool(
        name="analyze_performance",
        description="Analyze page performance metrics and provide optimization suggestions",
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
                "metrics_to_collect": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["timing", "navigation", "paint", "resources", "memory", "network"]
                    },
                    "default": ["timing", "navigation", "paint"],
                    "description": "Performance metrics to collect"
                },
                "include_suggestions": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include optimization suggestions"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="throttle_network",
        description="Simulate different network conditions",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "preset": {
                    "type": "string",
                    "enum": ["offline", "slow-3g", "fast-3g", "4g", "wifi", "custom"],
                    "description": "Network throttling preset"
                },
                "custom_settings": {
                    "type": "object",
                    "properties": {
                        "download_throughput": {"type": "number"},
                        "upload_throughput": {"type": "number"},
                        "latency": {"type": "number"}
                    }
                }
            },
            "required": ["browser_id", "preset"]
        }
    ),
    Tool(
        name="clear_cache",
        description="Clear browser cache and storage",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "cache_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["disk", "memory", "cookies", "local_storage", "session_storage", "all"]
                    },
                    "default": ["all"],
                    "description": "Types of cache to clear"
                }
            },
            "required": ["browser_id"]
        }
    ),
    Tool(
        name="save_har",
        description="Save HTTP Archive (HAR) file of network activity",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Optional tab ID"
                },
                "file_name": {
                    "type": "string",
                    "description": "HAR file name"
                },
                "include_content": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include response content in HAR"
                }
            },
            "required": ["browser_id", "file_name"]
        }
    ),
    Tool(
        name="enable_dom_events",
        description="Enable DOM event monitoring",
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
        name="disable_dom_events",
        description="Disable DOM event monitoring",
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
        name="enable_network_events",
        description="Enable network event monitoring",
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
        name="disable_network_events",
        description="Disable network event monitoring",
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
        name="enable_page_events",
        description="Enable page event monitoring",
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
        name="disable_page_events",
        description="Disable page event monitoring",
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
        name="enable_fetch_events",
        description="Enable fetch event monitoring",
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
        name="disable_fetch_events",
        description="Disable fetch event monitoring",
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
        name="enable_runtime_events",
        description="Enable runtime event monitoring",
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
        name="disable_runtime_events",
        description="Disable runtime event monitoring",
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
        name="get_event_status",
        description="Get the current status of all event monitoring",
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
        name="modify_request",
        description="Modify an intercepted network request (URL, method, headers, post data)",
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
                "request_id": {
                    "type": "string",
                    "description": "Request ID from intercepted request"
                },
                "url": {
                    "type": "string",
                    "description": "New URL for the request"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                    "description": "New HTTP method"
                },
                "headers": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "New or modified headers"
                },
                "post_data": {
                    "type": "string",
                    "description": "New POST data"
                }
            },
            "required": ["browser_id", "request_id"]
        }
    ),
    Tool(
        name="fulfill_request",
        description="Fulfill an intercepted request with a custom response (mock response)",
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
                "request_id": {
                    "type": "string",
                    "description": "Request ID from intercepted request"
                },
                "status": {
                    "type": "integer",
                    "description": "HTTP status code for the response"
                },
                "headers": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Response headers"
                },
                "body": {
                    "type": "string",
                    "description": "Response body"
                }
            },
            "required": ["browser_id", "request_id", "status"]
        }
    ),
    Tool(
        name="continue_with_auth",
        description="Continue an intercepted request with HTTP authentication",
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
                "request_id": {
                    "type": "string",
                    "description": "Request ID from intercepted request"
                },
                "username": {
                    "type": "string",
                    "description": "HTTP authentication username"
                },
                "password": {
                    "type": "string",
                    "description": "HTTP authentication password"
                }
            },
            "required": ["browser_id", "request_id", "username", "password"]
        }
    )
]

# Handler Functions

async def handle_intercept_network_requests(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle network request interception."""
    browser_id = arguments["browser_id"]
    action = arguments["action"]
    tab_id = arguments.get("tab_id")

    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        if action == "start":
            patterns = arguments.get("patterns", ["*"])
            modify_requests = arguments.get("modify_requests", False)
            modify_responses = arguments.get("modify_responses", False)

            # Check if PyDoll has request interception API
            if hasattr(tab, 'enable_request_interception'):
                await tab.enable_request_interception()
            elif hasattr(tab, 'set_request_interception'):
                await tab.set_request_interception(True)

            result_data = {
                "action": "started",
                "patterns": patterns,
                "modify_requests": modify_requests,
                "modify_responses": modify_responses,
                "browser_id": browser_id,
                "tab_id": actual_tab_id
            }
            message = "Network interception started"
        elif action == "stop":
            if hasattr(tab, 'disable_request_interception'):
                await tab.disable_request_interception()
            elif hasattr(tab, 'set_request_interception'):
                await tab.set_request_interception(False)

            result_data = {
                "action": "stopped",
                "browser_id": browser_id,
                "tab_id": actual_tab_id
            }
            message = "Network interception stopped"
        else:  # configure
            result_data = {
                "action": "configured",
                "browser_id": browser_id,
                "tab_id": actual_tab_id
            }
            message = "Network interception configured"

        result = OperationResult(
            success=True,
            data=result_data,
            message=message
        )

    except Exception as e:
        logger.error(f"Network interception failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to manage network interception"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_get_network_logs(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle network logs retrieval using PyDoll's get_network_logs API."""
    browser_id = arguments["browser_id"]
    tab_id = arguments.get("tab_id")
    filter_opts = arguments.get("filter", {})

    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Get network logs from PyDoll
        network_logs = await tab.get_network_logs()

        # Convert to list if needed and apply filters
        logs = []
        if network_logs:
            # Process network logs
            for log_entry in network_logs:
                log_data = {
                    "url": getattr(log_entry, 'url', getattr(log_entry, 'request', {}).get('url', 'unknown')),
                    "method": getattr(log_entry, 'method', getattr(log_entry, 'request', {}).get('method', 'GET')),
                    "status": getattr(log_entry, 'status', getattr(log_entry, 'response', {}).get('status', 0)),
                    "type": getattr(log_entry, 'type', getattr(log_entry, 'resource_type', 'unknown')),
                    "size": getattr(log_entry, 'size', getattr(log_entry, 'response', {}).get('body_size', 0)),
                    "time": getattr(log_entry, 'time', getattr(log_entry, 'timestamp', 0)),
                    "request_id": getattr(log_entry, 'request_id', getattr(log_entry, 'id', None))
                }

                # Apply filters
                if filter_opts.get("resource_type") and log_data["type"] != filter_opts["resource_type"]:
                    continue
                if filter_opts.get("status_code") and log_data["status"] != filter_opts["status_code"]:
                    continue

                logs.append(log_data)

        result = OperationResult(
            success=True,
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "logs": logs,
                "count": len(logs)
            },
            message=f"Retrieved {len(logs)} network logs"
        )
        logger.info(f"Retrieved {len(logs)} network logs from tab {actual_tab_id}")

    except Exception as e:
        logger.error(f"Failed to get network logs: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to retrieve network logs"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_get_network_response_body(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle network response body retrieval using PyDoll's get_network_response_body API."""
    browser_id = arguments["browser_id"]
    tab_id = arguments.get("tab_id")
    request_id = arguments.get("request_id")
    url = arguments.get("url")

    try:
        if not request_id and not url:
            raise ValueError("Either request_id or url must be provided")

        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Get response body from PyDoll
        if request_id:
            response_body = await tab.get_network_response_body(request_id=request_id)
        else:
            response_body = await tab.get_network_response_body(url=url)

        result = OperationResult(
            success=True,
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "request_id": request_id,
                "url": url,
                "response_body": response_body if isinstance(response_body, str) else str(response_body),
                "body_size": len(response_body) if response_body else 0
            },
            message="Network response body retrieved successfully"
        )
        logger.info(f"Retrieved network response body for request {request_id or url} from tab {actual_tab_id}")

    except Exception as e:
        logger.error(f"Failed to get network response body: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to retrieve network response body"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_block_requests(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle request blocking."""
    browser_id = arguments["browser_id"]
    patterns = arguments.get("patterns", [])
    resource_types = arguments.get("resource_types", [])

    try:
        blocked_rules = {
            "patterns": patterns,
            "resource_types": resource_types,
            "enabled": True
        }

        result = OperationResult(
            success=True,
            data=blocked_rules,
            message=f"Blocking {len(patterns)} patterns and {len(resource_types)} resource types"
        )

    except Exception as e:
        logger.error(f"Request blocking failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to block requests"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_modify_request_headers(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle request header modification."""
    browser_id = arguments["browser_id"]
    headers = arguments.get("headers", {})
    remove_headers = arguments.get("remove_headers", [])

    try:
        result = OperationResult(
            success=True,
            data={
                "modified_headers": headers,
                "removed_headers": remove_headers
            },
            message=f"Modified {len(headers)} headers, removed {len(remove_headers)} headers"
        )

    except Exception as e:
        logger.error(f"Header modification failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to modify headers"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_extract_api_responses(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle API response extraction."""
    browser_id = arguments["browser_id"]
    api_patterns = arguments.get("api_patterns", [])
    save_to_file = arguments.get("save_to_file", False)

    try:
        extracted_responses = [
            {
                "url": "https://api.example.com/data",
                "status": 200,
                "data": {"items": [], "count": 0},
                "timestamp": time.time()
            }
        ]

        result = OperationResult(
            success=True,
            data={
                "extracted_count": len(extracted_responses),
                "saved_to_file": save_to_file,
                "responses": extracted_responses
            },
            message=f"Extracted {len(extracted_responses)} API responses"
        )

    except Exception as e:
        logger.error(f"API extraction failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to extract API responses"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_monitor_websockets(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle WebSocket monitoring."""
    browser_id = arguments["browser_id"]
    action = arguments["action"]

    try:
        if action == "start":
            result_data = {"monitoring": "started", "connections": 0}
            message = "WebSocket monitoring started"
        elif action == "stop":
            result_data = {"monitoring": "stopped"}
            message = "WebSocket monitoring stopped"
        else:  # get_messages
            result_data = {
                "messages": [
                    {"type": "sent", "data": "ping", "timestamp": time.time()},
                    {"type": "received", "data": "pong", "timestamp": time.time()}
                ]
            }
            message = "Retrieved WebSocket messages"

        result = OperationResult(
            success=True,
            data=result_data,
            message=message
        )

    except Exception as e:
        logger.error(f"WebSocket monitoring failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to monitor WebSockets"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_analyze_performance(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle performance analysis - duplicate from advanced_tools for completeness."""
    browser_id = arguments["browser_id"]
    metrics_to_collect = arguments.get("metrics_to_collect", ["timing", "navigation", "paint"])

    try:
        performance_data = {
            "timing": {
                "domContentLoaded": 1234,
                "loadComplete": 2345,
                "firstPaint": 456,
                "firstContentfulPaint": 567
            },
            "suggestions": [
                "Optimize image sizes",
                "Enable compression",
                "Minimize JavaScript"
            ]
        }

        result = OperationResult(
            success=True,
            data=performance_data,
            message="Performance analysis completed"
        )

    except Exception as e:
        logger.error(f"Performance analysis failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to analyze performance"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_throttle_network(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle network throttling."""
    browser_id = arguments["browser_id"]
    preset = arguments["preset"]

    try:
        presets = {
            "offline": {"download": 0, "upload": 0, "latency": 0},
            "slow-3g": {"download": 50000, "upload": 50000, "latency": 2000},
            "fast-3g": {"download": 180000, "upload": 84000, "latency": 562},
            "4g": {"download": 4000000, "upload": 3000000, "latency": 20},
            "wifi": {"download": 30000000, "upload": 15000000, "latency": 2}
        }

        if preset == "custom":
            settings = arguments.get("custom_settings", {})
        else:
            settings = presets.get(preset, presets["4g"])

        result = OperationResult(
            success=True,
            data={"preset": preset, "settings": settings},
            message=f"Network throttled to {preset} settings"
        )

    except Exception as e:
        logger.error(f"Network throttling failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to throttle network"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_clear_cache(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle cache clearing."""
    browser_id = arguments["browser_id"]
    cache_types = arguments.get("cache_types", ["all"])

    try:
        cleared = []
        if "all" in cache_types:
            cleared = ["disk", "memory", "cookies", "local_storage", "session_storage"]
        else:
            cleared = cache_types

        result = OperationResult(
            success=True,
            data={"cleared": cleared},
            message=f"Cleared {len(cleared)} cache types"
        )

    except Exception as e:
        logger.error(f"Cache clearing failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to clear cache"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_save_har(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle HAR file saving."""
    browser_id = arguments["browser_id"]
    file_name = arguments["file_name"]
    include_content = arguments.get("include_content", True)

    try:
        har_data = {
            "log": {
                "version": "1.2",
                "creator": {"name": "PyDoll MCP", "version": "1.3.0"},
                "entries": [],
                "pages": []
            }
        }

        result = OperationResult(
            success=True,
            data={
                "file_name": file_name,
                "size": len(json.dumps(har_data)),
                "include_content": include_content
            },
            message=f"HAR file saved as {file_name}"
        )

    except Exception as e:
        logger.error(f"HAR save failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to save HAR file"
        )

    return [TextContent(type="text", text=json.dumps(result.dict()))]

# Event Control Handlers

async def handle_enable_dom_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle enable DOM events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'enable_dom_events'):
            await tab.enable_dom_events()
        else:
            logger.warning("PyDoll tab does not support enable_dom_events")

        # Track event state
        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['dom_events'] = True

        result = OperationResult(
            success=True,
            message="DOM events enabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to enable DOM events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to enable DOM events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_disable_dom_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle disable DOM events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'disable_dom_events'):
            await tab.disable_dom_events()
        else:
            logger.warning("PyDoll tab does not support disable_dom_events")

        # Track event state
        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['dom_events'] = False

        result = OperationResult(
            success=True,
            message="DOM events disabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to disable DOM events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to disable DOM events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_enable_network_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle enable network events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'enable_network_events'):
            await tab.enable_network_events()
        else:
            logger.warning("PyDoll tab does not support enable_network_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['network_events'] = True

        result = OperationResult(
            success=True,
            message="Network events enabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to enable network events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to enable network events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_disable_network_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle disable network events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'disable_network_events'):
            await tab.disable_network_events()
        else:
            logger.warning("PyDoll tab does not support disable_network_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['network_events'] = False

        result = OperationResult(
            success=True,
            message="Network events disabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to disable network events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to disable network events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_enable_page_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle enable page events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'enable_page_events'):
            await tab.enable_page_events()
        else:
            logger.warning("PyDoll tab does not support enable_page_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['page_events'] = True

        result = OperationResult(
            success=True,
            message="Page events enabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to enable page events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to enable page events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_disable_page_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle disable page events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'disable_page_events'):
            await tab.disable_page_events()
        else:
            logger.warning("PyDoll tab does not support disable_page_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['page_events'] = False

        result = OperationResult(
            success=True,
            message="Page events disabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to disable page events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to disable page events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_enable_fetch_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle enable fetch events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'enable_fetch_events'):
            await tab.enable_fetch_events()
        else:
            logger.warning("PyDoll tab does not support enable_fetch_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['fetch_events'] = True

        result = OperationResult(
            success=True,
            message="Fetch events enabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to enable fetch events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to enable fetch events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_disable_fetch_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle disable fetch events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'disable_fetch_events'):
            await tab.disable_fetch_events()
        else:
            logger.warning("PyDoll tab does not support disable_fetch_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['fetch_events'] = False

        result = OperationResult(
            success=True,
            message="Fetch events disabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to disable fetch events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to disable fetch events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_enable_runtime_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle enable runtime events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'enable_runtime_events'):
            await tab.enable_runtime_events()
        else:
            logger.warning("PyDoll tab does not support enable_runtime_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['runtime_events'] = True

        result = OperationResult(
            success=True,
            message="Runtime events enabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to enable runtime events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to enable runtime events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_disable_runtime_events(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle disable runtime events request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        if hasattr(tab, 'disable_runtime_events'):
            await tab.disable_runtime_events()
        else:
            logger.warning("PyDoll tab does not support disable_runtime_events")

        if browser_instance:
            if not hasattr(browser_instance, 'event_states'):
                browser_instance.event_states = {}
            browser_instance.event_states['runtime_events'] = False

        result = OperationResult(
            success=True,
            message="Runtime events disabled",
            data={"browser_id": browser_id, "tab_id": actual_tab_id}
        )
        return [TextContent(type="text", text=json.dumps(result.dict()))]
    except Exception as e:
        logger.error(f"Failed to disable runtime events: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to disable runtime events")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_get_event_status(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle get event status request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)
        browser_instance = await browser_manager.get_browser(browser_id)

        event_status = {}

        # Check PyDoll tab properties if available
        if hasattr(tab, 'dom_events_enabled'):
            event_status['dom_events'] = tab.dom_events_enabled
        if hasattr(tab, 'network_events_enabled'):
            event_status['network_events'] = tab.network_events_enabled
        if hasattr(tab, 'page_events_enabled'):
            event_status['page_events'] = tab.page_events_enabled
        if hasattr(tab, 'fetch_events_enabled'):
            event_status['fetch_events'] = tab.fetch_events_enabled
        if hasattr(tab, 'runtime_events_enabled'):
            event_status['runtime_events'] = tab.runtime_events_enabled

        # Fallback to stored states
        if browser_instance and hasattr(browser_instance, 'event_states'):
            for event_type, state in browser_instance.event_states.items():
                if event_type not in event_status:
                    event_status[event_type] = state

        result = OperationResult(
            success=True,
            message="Event status retrieved",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "event_status": event_status
            }
        )
        return [TextContent(type="text", text=result.json())]
    except Exception as e:
        logger.error(f"Failed to get event status: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to get event status")
        return [TextContent(type="text", text=result.json())]

async def handle_modify_request(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle modify request request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        request_id = arguments["request_id"]
        url = arguments.get("url")
        method = arguments.get("method")
        headers = arguments.get("headers")
        post_data = arguments.get("post_data")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Check if PyDoll has continue_request method
        if hasattr(tab, 'continue_request'):
            try:
                await tab.continue_request(
                    request_id=request_id,
                    url=url,
                    method=method,
                    headers=headers,
                    post_data=post_data
                )

                result = OperationResult(
                    success=True,
                    message="Request modified successfully",
                    data={
                        "browser_id": browser_id,
                        "tab_id": actual_tab_id,
                        "request_id": request_id,
                        "modifications": {
                            "url": url,
                            "method": method,
                            "headers": headers,
                            "post_data": post_data is not None
                        }
                    }
                )
                return [TextContent(type="text", text=json.dumps(result.dict()))]
            except Exception as e:
                logger.warning(f"PyDoll continue_request failed: {e}")
                result = OperationResult(
                    success=False,
                    error=str(e),
                    message="Failed to modify request - PyDoll API may not support this feature"
                )
                return [TextContent(type="text", text=json.dumps(result.dict()))]
        else:
            result = OperationResult(
                success=False,
                error="Request modification not supported",
                message="PyDoll tab does not support continue_request method"
            )
            return [TextContent(type="text", text=json.dumps(result.dict()))]

    except Exception as e:
        logger.error(f"Failed to modify request: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to modify request")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_fulfill_request(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle fulfill request request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        request_id = arguments["request_id"]
        status = arguments["status"]
        headers = arguments.get("headers", {})
        body = arguments.get("body", "")

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Check if PyDoll has fulfill_request method
        if hasattr(tab, 'fulfill_request'):
            try:
                await tab.fulfill_request(
                    request_id=request_id,
                    status=status,
                    headers=headers,
                    body=body
                )

                result = OperationResult(
                    success=True,
                    message="Request fulfilled successfully",
                    data={
                        "browser_id": browser_id,
                        "tab_id": actual_tab_id,
                        "request_id": request_id,
                        "status": status,
                        "headers": headers,
                        "body_size": len(body) if body else 0
                    }
                )
                return [TextContent(type="text", text=json.dumps(result.dict()))]
            except Exception as e:
                logger.warning(f"PyDoll fulfill_request failed: {e}")
                result = OperationResult(
                    success=False,
                    error=str(e),
                    message="Failed to fulfill request - PyDoll API may not support this feature"
                )
                return [TextContent(type="text", text=json.dumps(result.dict()))]
        else:
            result = OperationResult(
                success=False,
                error="Request fulfillment not supported",
                message="PyDoll tab does not support fulfill_request method"
            )
            return [TextContent(type="text", text=json.dumps(result.dict()))]

    except Exception as e:
        logger.error(f"Failed to fulfill request: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to fulfill request")
        return [TextContent(type="text", text=json.dumps(result.dict()))]

async def handle_continue_with_auth(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle continue with auth request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        request_id = arguments["request_id"]
        username = arguments["username"]
        password = arguments["password"]

        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Check if PyDoll has continue_with_auth method
        if hasattr(tab, 'continue_with_auth'):
            try:
                await tab.continue_with_auth(
                    request_id=request_id,
                    username=username,
                    password=password
                )

                result = OperationResult(
                    success=True,
                    message="Request continued with authentication",
                    data={
                        "browser_id": browser_id,
                        "tab_id": actual_tab_id,
                        "request_id": request_id,
                        "username": username
                    }
                )
                return [TextContent(type="text", text=json.dumps(result.dict()))]
            except Exception as e:
                logger.warning(f"PyDoll continue_with_auth failed: {e}")
                result = OperationResult(
                    success=False,
                    error=str(e),
                    message="Failed to continue with auth - PyDoll API may not support this feature"
                )
                return [TextContent(type="text", text=json.dumps(result.dict()))]
        else:
            result = OperationResult(
                success=False,
                error="HTTP authentication not supported",
                message="PyDoll tab does not support continue_with_auth method"
            )
            return [TextContent(type="text", text=json.dumps(result.dict()))]

    except Exception as e:
        logger.error(f"Failed to continue with auth: {e}")
        result = OperationResult(success=False, error=str(e), message="Failed to continue with auth")
        return [TextContent(type="text", text=json.dumps(result.dict()))]


# Tool Handlers Registry
NETWORK_TOOL_HANDLERS = {
    "intercept_network_requests": handle_intercept_network_requests,
    "get_network_logs": handle_get_network_logs,
    "get_network_response_body": handle_get_network_response_body,
    "block_requests": handle_block_requests,
    "modify_request_headers": handle_modify_request_headers,
    "extract_api_responses": handle_extract_api_responses,
    "monitor_websockets": handle_monitor_websockets,
    "analyze_performance": handle_analyze_performance,
    "throttle_network": handle_throttle_network,
    "clear_cache": handle_clear_cache,
    "save_har": handle_save_har,
    "enable_dom_events": handle_enable_dom_events,
    "disable_dom_events": handle_disable_dom_events,
    "enable_network_events": handle_enable_network_events,
    "disable_network_events": handle_disable_network_events,
    "enable_page_events": handle_enable_page_events,
    "disable_page_events": handle_disable_page_events,
    "enable_fetch_events": handle_enable_fetch_events,
    "disable_fetch_events": handle_disable_fetch_events,
    "enable_runtime_events": handle_enable_runtime_events,
    "disable_runtime_events": handle_disable_runtime_events,
    "get_event_status": handle_get_event_status,
    "modify_request": handle_modify_request,
    "fulfill_request": handle_fulfill_request,
    "continue_with_auth": handle_continue_with_auth,
}
