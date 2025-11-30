"""MCP Tools for PyDoll browser automation.

This module contains all the Model Context Protocol (MCP) tools that provide
browser automation capabilities to AI assistants like Claude.
"""

from typing import Any, Dict, List, Sequence

from mcp.types import Tool, TextContent

# Import unified tools (Fat Tools) - these are the recommended tools
from .registry import create_unified_tools, create_unified_handlers

# Import tool definitions and handlers from each category (legacy tools)
# Note: element_tools, screenshot_tools are fully deprecated (replaced by unified tools)
# Note: Some file_tools are deprecated (download_file, manage_downloads replaced by unified manage_file)
from .browser_tools import BROWSER_TOOLS, BROWSER_TOOL_HANDLERS
from .navigation_tools import NAVIGATION_TOOLS, NAVIGATION_TOOL_HANDLERS
from .script_tools import SCRIPT_TOOLS, SCRIPT_TOOL_HANDLERS
from .advanced_tools import ADVANCED_TOOLS, ADVANCED_TOOL_HANDLERS
from .protection_tools import PROTECTION_TOOLS, PROTECTION_TOOL_HANDLERS
from .network_tools import NETWORK_TOOLS, NETWORK_TOOL_HANDLERS
from .file_tools import FILE_TOOLS, FILE_TOOL_HANDLERS
from .search_automation import SEARCH_AUTOMATION_TOOLS, SEARCH_AUTOMATION_TOOL_HANDLERS
from .page_tools import PAGE_TOOLS, PAGE_TOOL_HANDLERS

# Create unified tools
UNIFIED_TOOLS = create_unified_tools()
UNIFIED_TOOL_HANDLERS = create_unified_handlers()

# Combine all tools and handlers (unified tools first for priority)
# Note: ELEMENT_TOOLS and SCREENSHOT_TOOLS removed (fully replaced by unified tools)
# Set to True to only register unified tools (recommended for LLM usage)
# Set to False to include all legacy tools for backward compatibility
UNIFIED_TOOLS_ONLY = True  # Change to False to include legacy tools

if UNIFIED_TOOLS_ONLY:
    # Only register unified tools - clean, minimal toolset
    ALL_TOOLS = list(UNIFIED_TOOLS)
else:
    # Include all legacy tools for backward compatibility
    ALL_TOOLS = (
        UNIFIED_TOOLS +  # Unified tools first
        BROWSER_TOOLS +
        NAVIGATION_TOOLS +
        SCRIPT_TOOLS +
        ADVANCED_TOOLS +
        PROTECTION_TOOLS +
        NETWORK_TOOLS +
        FILE_TOOLS +
        SEARCH_AUTOMATION_TOOLS +
        PAGE_TOOLS
    )

if UNIFIED_TOOLS_ONLY:
    # Only register unified tool handlers
    ALL_TOOL_HANDLERS = dict(UNIFIED_TOOL_HANDLERS)
else:
    # Include all legacy tool handlers
    ALL_TOOL_HANDLERS = {
        **UNIFIED_TOOL_HANDLERS,  # Unified handlers first (take precedence)
        **BROWSER_TOOL_HANDLERS,
        **NAVIGATION_TOOL_HANDLERS,
        # ELEMENT_TOOL_HANDLERS and SCREENSHOT_TOOL_HANDLERS removed (replaced by unified tools)
        **SCRIPT_TOOL_HANDLERS,
        **ADVANCED_TOOL_HANDLERS,
        **PROTECTION_TOOL_HANDLERS,
        **NETWORK_TOOL_HANDLERS,
        **FILE_TOOL_HANDLERS,
        **SEARCH_AUTOMATION_TOOL_HANDLERS,
        **PAGE_TOOL_HANDLERS,
    }

# Tool categories for organization
TOOL_CATEGORIES = {
    "unified_tools": {
        "description": "Unified 'Fat Tools' - Recommended for LLM usage. Consolidates ~50-60 common granular tools (element interaction, element finding, tab management, browser control, navigation, screenshots/PDFs, script execution, file operations, page dialogs) into 10 powerful endpoints. Other tool categories remain as legacy tools.",
        "tools": [tool.name for tool in UNIFIED_TOOLS],
        "count": len(UNIFIED_TOOLS),
        "recommended": True
    },
    "browser_management": {
        "description": "Browser lifecycle and configuration management (legacy tools)",
        "tools": [tool.name for tool in BROWSER_TOOLS],
        "count": len(BROWSER_TOOLS),
        "legacy": True
    },
    "navigation_control": {
        "description": "Page navigation and URL management (legacy tools)",
        "tools": [tool.name for tool in NAVIGATION_TOOLS],
        "count": len(NAVIGATION_TOOLS),
        "legacy": True
    },
    # element_interaction category removed - fully replaced by unified tools (find_element, interact_element)
    "page_interaction": {
        "description": "General page-level interactions (legacy tools)",
        "tools": [tool.name for tool in PAGE_TOOLS],
        "count": len(PAGE_TOOLS),
        "legacy": True
    },
    # screenshot_media category removed - fully replaced by unified tool (capture_media)
    "script_execution": {
        "description": "JavaScript execution and scripting",
        "tools": [tool.name for tool in SCRIPT_TOOLS],
        "count": len(SCRIPT_TOOLS)
    },
    "advanced_automation": {
        "description": "Advanced automation and protection bypass",
        "tools": [tool.name for tool in ADVANCED_TOOLS],
        "count": len(ADVANCED_TOOLS)
    },
    "network_monitoring": {
        "description": "Network monitoring, interception, and event control",
        "tools": [tool.name for tool in NETWORK_TOOLS],
        "count": len(NETWORK_TOOLS)
    },
    "file_operations": {
        "description": "File upload, download, and management",
        "tools": [tool.name for tool in FILE_TOOLS],
        "count": len(FILE_TOOLS)
    },
    "search_automation": {
        "description": "Intelligent search automation with automatic element detection",
        "tools": [tool.name for tool in SEARCH_AUTOMATION_TOOLS],
        "count": len(SEARCH_AUTOMATION_TOOLS)
    }
}

# Statistics
TOTAL_TOOLS = len(ALL_TOOLS)
TOTAL_CATEGORIES = len(TOOL_CATEGORIES)

# Export everything
__all__ = [
    # Tool collections
    "ALL_TOOLS",
    "ALL_TOOL_HANDLERS",
    "UNIFIED_TOOLS",
    "UNIFIED_TOOL_HANDLERS",
    "UNIFIED_TOOLS_ONLY",
    "TOOL_CATEGORIES",

    # Individual category tools
    "BROWSER_TOOLS",
    "NAVIGATION_TOOLS",
    # ELEMENT_TOOLS removed (replaced by unified tools)
    "PAGE_TOOLS",
    # SCREENSHOT_TOOLS removed (replaced by unified tools)
    "SCRIPT_TOOLS",
    "ADVANCED_TOOLS",
    "PROTECTION_TOOLS",
    "NETWORK_TOOLS",
    "FILE_TOOLS",
    "SEARCH_AUTOMATION_TOOLS",

    # Individual category handlers
    "BROWSER_TOOL_HANDLERS",
    "NAVIGATION_TOOL_HANDLERS",
    # ELEMENT_TOOL_HANDLERS removed (replaced by unified tools)
    "PAGE_TOOL_HANDLERS",
    # SCREENSHOT_TOOL_HANDLERS removed (replaced by unified tools)
    "SCRIPT_TOOL_HANDLERS",
    "ADVANCED_TOOL_HANDLERS",
    "PROTECTION_TOOL_HANDLERS",
    "NETWORK_TOOL_HANDLERS",
    "FILE_TOOL_HANDLERS",
    "SEARCH_AUTOMATION_TOOL_HANDLERS",

    # Statistics
    "TOTAL_TOOLS",
    "TOTAL_CATEGORIES",

    # Helper functions
    "get_tool_by_name",
    "get_tools_by_category",
    "get_tool_info",
]


def get_tool_by_name(name: str) -> Tool | None:
    """Get a tool by its name.

    Args:
        name: Tool name to search for

    Returns:
        Tool object if found, None otherwise
    """
    for tool in ALL_TOOLS:
        if tool.name == name:
            return tool
    return None


def get_tools_by_category(category: str) -> List[Tool]:
    """Get all tools in a specific category.

    Args:
        category: Category name (e.g., 'browser_management')

    Returns:
        List of tools in the category
    """
    if category not in TOOL_CATEGORIES:
        return []

    tool_names = TOOL_CATEGORIES[category]["tools"]
    return [tool for tool in ALL_TOOLS if tool.name in tool_names]


def get_tool_info() -> Dict[str, Any]:
    """Get comprehensive tool information.

    Returns:
        Dictionary with tool statistics and information
    """
    unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
    legacy_tool_names = [tool.name for tool in ALL_TOOLS if tool.name not in unified_tool_names]

    return {
        "total_tools": TOTAL_TOOLS,
        "unified_tools": len(UNIFIED_TOOLS),
        "legacy_tools": len(legacy_tool_names),
        "total_categories": TOTAL_CATEGORIES,
        "categories": TOOL_CATEGORIES,
        "tool_names": [tool.name for tool in ALL_TOOLS],
        "unified_tool_names": unified_tool_names,
        "recommended_tools": unified_tool_names,  # Unified tools are recommended
        "capabilities": {
            "browser_automation": True,
            "captcha_bypass": True,
            "network_monitoring": True,
            "element_finding": True,
            "javascript_execution": True,
            "stealth_mode": True,
            "screenshot_capture": True,
            "multi_browser_support": True,
            "unified_tools": True,  # Unified tools architecture available
        }
    }


# Utility functions for tool execution

async def execute_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Execute a tool by name with given arguments.

    Args:
        name: Tool name to execute
        arguments: Tool arguments

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool not found
    """
    if name not in ALL_TOOL_HANDLERS:
        raise ValueError(f"Tool '{name}' not found")

    handler = ALL_TOOL_HANDLERS[name]
    return await handler(arguments)


def validate_tool_arguments(name: str, arguments: Dict[str, Any]) -> bool:
    """Validate arguments for a specific tool.

    Args:
        name: Tool name
        arguments: Arguments to validate

    Returns:
        True if arguments are valid

    Raises:
        ValueError: If tool not found or arguments invalid
    """
    tool = get_tool_by_name(name)
    if not tool:
        raise ValueError(f"Tool '{name}' not found")

    # Basic validation - in a full implementation, this would check against
    # the tool's input schema defined in the Tool object
    required_params = getattr(tool, 'required_parameters', [])

    for param in required_params:
        if param not in arguments:
            raise ValueError(f"Missing required parameter: {param}")

    return True


# Tool discovery helpers

def search_tools(query: str) -> List[Tool]:
    """Search tools by name or description.

    Args:
        query: Search query

    Returns:
        List of matching tools
    """
    query_lower = query.lower()
    results = []

    for tool in ALL_TOOLS:
        if (query_lower in tool.name.lower() or
            query_lower in tool.description.lower()):
            results.append(tool)

    return results


def get_tools_with_capability(capability: str) -> List[Tool]:
    """Get tools that provide a specific capability.

    Args:
        capability: Capability to search for

    Returns:
        List of tools with the capability
    """
    capability_mapping = {
        "captcha": ["bypass_cloudflare", "bypass_recaptcha", "enable_stealth_mode"],
        "screenshot": ["take_screenshot", "take_element_screenshot", "generate_pdf"],
        "network": ["enable_network_monitoring", "intercept_requests", "extract_api_responses"],
        "javascript": ["execute_script", "execute_script_on_element", "evaluate_expression"],
        "automation": ["click_element", "type_text", "find_element", "navigate_to"],
    }

    tool_names = capability_mapping.get(capability, [])
    return [tool for tool in ALL_TOOLS if tool.name in tool_names]


# Version and compatibility information

TOOLS_VERSION = "1.0.0"
MIN_PYDOLL_VERSION = "2.12.4"
MIN_MCP_VERSION = "1.0.0"

COMPATIBILITY_INFO = {
    "tools_version": TOOLS_VERSION,
    "min_pydoll_version": MIN_PYDOLL_VERSION,
    "min_mcp_version": MIN_MCP_VERSION,
    "supported_browsers": ["chrome", "edge"],
    "supported_platforms": ["windows", "macos", "linux"],
    "python_requirement": ">=3.8",
}


def get_compatibility_info() -> Dict[str, Any]:
    """Get tool compatibility information.

    Returns:
        Compatibility information dictionary
    """
    return COMPATIBILITY_INFO.copy()
