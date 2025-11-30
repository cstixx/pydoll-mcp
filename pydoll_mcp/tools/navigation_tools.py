"""Navigation Tools for PyDoll MCP Server.

This module provides MCP tools for page navigation and URL management including:
- Page navigation and URL handling
- Page refresh and history management
- Page information extraction
- Wait conditions and load detection
"""

import logging
from typing import Any, Dict, Sequence
from urllib.parse import urlparse

from mcp.types import Tool, TextContent

from ..core import get_browser_manager
from ..models import OperationResult

logger = logging.getLogger(__name__)

# Navigation Tools Definition

NAVIGATION_TOOLS = [
    Tool(
        name="navigate_to",
        description="Navigate to a specific URL in a browser tab",
        inputSchema={
            "type": "object",
            "properties": {
                "browser_id": {
                    "type": "string",
                    "description": "Browser instance ID"
                },
                "url": {
                    "type": "string",
                    "description": "URL to navigate to"
                },
                "tab_id": {
                    "type": "string",
                    "description": "Optional tab ID, uses active tab if not specified"
                },
                "wait_for_load": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for page to fully load"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300,
                    "description": "Navigation timeout in seconds"
                },
                "referrer": {
                    "type": "string",
                    "description": "Optional referrer URL"
                }
            },
            "required": ["browser_id", "url"]
        }
    ),

    Tool(
        name="refresh_page",
        description="Refresh the current page in a browser tab",
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
                "ignore_cache": {
                    "type": "boolean",
                    "default": False,
                    "description": "Force refresh ignoring cache"
                },
                "wait_for_load": {
                    "type": "boolean",
                    "default": True,
                    "description": "Wait for page to reload"
                }
            },
            "required": ["browser_id"]
        }
    ),

    Tool(
        name="go_back",
        description="Navigate back in browser history",
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
                "steps": {
                    "type": "integer",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Number of steps to go back"
                }
            },
            "required": ["browser_id"]
        }
    ),

    Tool(
        name="get_current_url",
        description="Get the current URL of a browser tab",
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
        name="get_page_title",
        description="Get the title of the current page",
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
        name="get_page_source",
        description="Get the HTML source code of the current page",
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
                "include_resources": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include information about page resources"
                }
            },
            "required": ["browser_id"]
        }
    ),

    Tool(
        name="fetch_domain_commands",
        description="Fetch all possible commands available for the current domain from Chrome DevTools Protocol",
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
                "domain": {
                    "type": "string",
                    "description": "Chrome DevTools Protocol domain (e.g., 'Page', 'Network', 'DOM')"
                }
            },
            "required": ["browser_id"]
        }
    ),

    Tool(
        name="scroll",
        description="Scroll the page in various directions or to specific positions/elements",
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
                "direction": {
                    "type": "string",
                    "enum": ["up", "down", "left", "right", "to_element", "to_position", "to_top", "to_bottom"],
                    "default": "down",
                    "description": "Scroll direction or mode"
                },
                "amount": {
                    "type": "integer",
                    "description": "Number of pixels to scroll (for up/down/left/right)"
                },
                "element_selector": {
                    "type": "object",
                    "description": "Element selector for scroll_to_element (same as find_element parameters)"
                },
                "x": {
                    "type": "integer",
                    "description": "X coordinate for scroll_to_position"
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate for scroll_to_position"
                },
                "behavior": {
                    "type": "string",
                    "enum": ["auto", "smooth", "instant"],
                    "default": "smooth",
                    "description": "Scroll behavior"
                }
            },
            "required": ["browser_id", "direction"]
        }
    ),

    Tool(
        name="get_frame",
        description="Get access to an iframe/frame element for operations within the frame",
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
                "frame_selector": {
                    "type": "string",
                    "description": "Frame selector: CSS selector, XPath, name attribute, or id attribute"
                },
                "selector_type": {
                    "type": "string",
                    "enum": ["css", "xpath", "name", "id"],
                    "default": "css",
                    "description": "Type of frame selector"
                }
            },
            "required": ["browser_id", "frame_selector"]
        }
    )
]


# Navigation Tool Handlers

async def handle_navigate_to(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle page navigation request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        url = arguments["url"]
        tab_id = arguments.get("tab_id")
        wait_for_load = arguments.get("wait_for_load", True)
        timeout = arguments.get("timeout", 30)
        referrer = arguments.get("referrer")

        # Validate URL
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = f"https://{url}"  # Default to HTTPS
        except Exception:
            raise ValueError(f"Invalid URL: {url}")

        # Get tab with automatic fallback to active tab
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Perform navigation using PyDoll's go_to method
        try:
            # PyDoll's go_to method accepts url and timeout parameters
            await tab.go_to(url, timeout=timeout)

            # Note: PyDoll's go_to already waits for page load by default
            # No need for additional wait_for_load_state

        except Exception as nav_error:
            logger.error(f"Navigation error: {nav_error}")
            raise Exception(f"Navigation failed: {nav_error}")

        # Get final URL and title using PyDoll properties
        try:
            # PyDoll uses 'current_url' property, not get_url()
            final_url = await tab.current_url

            # Get title by executing JavaScript
            title_result = await tab.execute_script('document.title')
            if title_result and 'result' in title_result and 'result' in title_result['result']:
                title = title_result['result']['result'].get('value', 'Untitled')
            else:
                title = "Untitled"
        except Exception as info_error:
            logger.warning(f"Could not get page info: {info_error}")
            final_url = url
            title = "Unknown"

        result = OperationResult(
            success=True,
            message=f"Successfully navigated to {final_url}",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "requested_url": url,
                "final_url": final_url,
                "page_title": title,
                "redirected": url != final_url
            }
        )

        logger.info(f"Navigation successful: {url} -> {final_url}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message=f"Failed to navigate to {url}"
        )
        return [TextContent(type="text", text=result.json())]


# Placeholder handlers for remaining tools
async def handle_refresh_page(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle page refresh request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        ignore_cache = arguments.get("ignore_cache", False)
        wait_for_load = arguments.get("wait_for_load", True)

        # Get tab with automatic fallback to active tab
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Refresh page
        if ignore_cache:
            await tab.reload(ignore_cache=True)
        else:
            await tab.reload()

        if wait_for_load:
            await tab.wait_for_load_state("load")

        # Get current URL and title after refresh
        url_result = await tab.execute_script("return window.location.href")
        url = url_result.get('result', {}).get('result', {}).get('value', '')
        title_result = await tab.execute_script("return document.title")
        title = title_result.get('result', {}).get('result', {}).get('value', '')

        result = OperationResult(
            success=True,
            message="Page refreshed successfully",
            data={
                "browser_id": browser_id,
                "tab_id": tab_id,
                "url": url,
                "title": title,
                "ignore_cache": ignore_cache
            }
        )

        logger.info(f"Page refresh successful: {url}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Page refresh failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to refresh page"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_go_back(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle browser back navigation."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        steps = arguments.get("steps", 1)

        # Get browser instance
        browser_instance = await browser_manager.get_browser(browser_id)
        if not browser_instance:
            raise ValueError(f"Browser {browser_id} not found")

        # Get tab - if tab_id is provided, use it; otherwise use active tab or first available
        if tab_id:
            tab = browser_instance.tabs.get(tab_id)
            if not tab:
                raise ValueError(f"Tab {tab_id} not found in browser {browser_id}")
        else:
            # Use active tab or first available tab
            if browser_instance.active_tab_id and browser_instance.active_tab_id in browser_instance.tabs:
                tab = browser_instance.tabs[browser_instance.active_tab_id]
            elif browser_instance.tabs:
                tab = next(iter(browser_instance.tabs.values()))
            elif hasattr(browser_instance.browser, 'tab'):
                tab = browser_instance.browser.tab
            else:
                raise ValueError(f"No tabs available in browser {browser_id}")

        # Navigate back the specified number of steps
        for _ in range(steps):
            await tab.go_back()

        # Get current URL after navigation
        url_result = await tab.execute_script("return window.location.href")
        url = url_result.get('result', {}).get('result', {}).get('value', '')
        title_result = await tab.execute_script("return document.title")
        title = title_result.get('result', {}).get('result', {}).get('value', '')

        result = OperationResult(
            success=True,
            message=f"Navigated back {steps} step(s)",
            data={
                "browser_id": browser_id,
                "tab_id": tab_id,
                "steps": steps,
                "current_url": url,
                "current_title": title
            }
        )

        logger.info(f"Back navigation successful: {steps} steps")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Back navigation failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message=f"Failed to navigate back {steps} step(s)"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_get_current_url(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle get current URL request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        # Get browser instance
        browser_instance = await browser_manager.get_browser(browser_id)
        if not browser_instance:
            raise ValueError(f"Browser {browser_id} not found")

        # Get tab - if tab_id is provided, use it; otherwise use active tab or first available
        if tab_id:
            tab = browser_instance.tabs.get(tab_id)
            if not tab:
                raise ValueError(f"Tab {tab_id} not found in browser {browser_id}")
        else:
            # Use active tab or first available tab
            if browser_instance.active_tab_id and browser_instance.active_tab_id in browser_instance.tabs:
                tab = browser_instance.tabs[browser_instance.active_tab_id]
            elif browser_instance.tabs:
                tab = next(iter(browser_instance.tabs.values()))
            elif hasattr(browser_instance.browser, 'tab'):
                tab = browser_instance.browser.tab
            else:
                raise ValueError(f"No tabs available in browser {browser_id}")

        # Get current URL using JavaScript
        url_result = await tab.execute_script("return window.location.href")
        url = url_result.get('result', {}).get('result', {}).get('value', '')

        result = OperationResult(
            success=True,
            message="Current URL retrieved successfully",
            data={
                "browser_id": browser_id,
                "tab_id": tab_id,
                "url": url
            }
        )

        logger.info(f"Current URL retrieved: {url}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to get current URL: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to retrieve current URL"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_get_page_title(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle get page title request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")

        # Get browser instance
        browser_instance = await browser_manager.get_browser(browser_id)
        if not browser_instance:
            raise ValueError(f"Browser {browser_id} not found")

        # Get tab - if tab_id is provided, use it; otherwise use active tab or first available
        if tab_id:
            tab = browser_instance.tabs.get(tab_id)
            if not tab:
                raise ValueError(f"Tab {tab_id} not found in browser {browser_id}")
        else:
            # Use active tab or first available tab
            if browser_instance.active_tab_id and browser_instance.active_tab_id in browser_instance.tabs:
                tab = browser_instance.tabs[browser_instance.active_tab_id]
            elif browser_instance.tabs:
                tab = next(iter(browser_instance.tabs.values()))
            elif hasattr(browser_instance.browser, 'tab'):
                tab = browser_instance.browser.tab
            else:
                raise ValueError(f"No tabs available in browser {browser_id}")

        # Get page title
        title_result = await tab.execute_script("return document.title")
        title = title_result.get('result', {}).get('result', {}).get('value', '')
        url_result = await tab.execute_script("return window.location.href")
        url = url_result.get('result', {}).get('result', {}).get('value', '')

        result = OperationResult(
            success=True,
            message="Page title retrieved successfully",
            data={
                "browser_id": browser_id,
                "tab_id": tab_id,
                "title": title,
                "url": url
            }
        )

        logger.info(f"Page title retrieved: {title}")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to get page title: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to retrieve page title"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_get_page_source(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle get page source request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        include_resources = arguments.get("include_resources", False)

        # Get browser instance
        browser_instance = await browser_manager.get_browser(browser_id)
        if not browser_instance:
            raise ValueError(f"Browser {browser_id} not found")

        # Get tab - if tab_id is provided, use it; otherwise use active tab or first available
        if tab_id:
            tab = browser_instance.tabs.get(tab_id)
            if not tab:
                raise ValueError(f"Tab {tab_id} not found in browser {browser_id}")
        else:
            # Use active tab or first available tab
            if browser_instance.active_tab_id and browser_instance.active_tab_id in browser_instance.tabs:
                tab = browser_instance.tabs[browser_instance.active_tab_id]
            elif browser_instance.tabs:
                tab = next(iter(browser_instance.tabs.values()))
            elif hasattr(browser_instance.browser, 'tab'):
                tab = browser_instance.browser.tab
            else:
                raise ValueError(f"No tabs available in browser {browser_id}")

        # Get page source
        source_result = await tab.execute_script("return document.documentElement.outerHTML")
        source = source_result.get('result', {}).get('result', {}).get('value', '')
        url_result = await tab.execute_script("return window.location.href")
        url = url_result.get('result', {}).get('result', {}).get('value', '')
        title_result = await tab.execute_script("return document.title")
        title = title_result.get('result', {}).get('result', {}).get('value', '')

        data = {
            "browser_id": browser_id,
            "tab_id": tab_id,
            "url": url,
            "title": title,
            "source": source,
            "length": len(source)
        }

        # Include resources information if requested
        if include_resources:
            try:
                # Get basic page metrics
                data["resources"] = {
                    "source_size": len(source),
                    "encoding": "utf-8",
                    "content_type": "text/html"
                }
            except Exception as e:
                logger.warning(f"Failed to get resource information: {e}")

        result = OperationResult(
            success=True,
            message="Page source retrieved successfully",
            data=data
        )

        logger.info(f"Page source retrieved: {len(source)} characters")
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to get page source: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to retrieve page source"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_fetch_domain_commands(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle fetch domain commands request using PyDoll 2.12.4+ feature."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        domain = arguments.get("domain")

        # Get browser instance
        browser_instance = await browser_manager.get_browser(browser_id)
        if not browser_instance:
            raise ValueError(f"Browser {browser_id} not found")

        # Get tab - if tab_id is provided, use it; otherwise use active tab or first available
        if tab_id:
            tab = browser_instance.tabs.get(tab_id)
            if not tab:
                raise ValueError(f"Tab {tab_id} not found in browser {browser_id}")
        else:
            # Use active tab or first available tab
            if browser_instance.active_tab_id and browser_instance.active_tab_id in browser_instance.tabs:
                tab = browser_instance.tabs[browser_instance.active_tab_id]
            elif browser_instance.tabs:
                tab = next(iter(browser_instance.tabs.values()))
            elif hasattr(browser_instance.browser, 'tab'):
                tab = browser_instance.browser.tab
            else:
                raise ValueError(f"No tabs available in browser {browser_id}")

        # Call PyDoll's fetch_domain_commands method (available in 2.3.1+)
        if domain:
            commands = await tab.fetch_domain_commands(domain)
            message = f"Successfully fetched commands for domain: {domain}"
        else:
            # Fetch all available domains
            commands = await tab.fetch_domain_commands()
            message = "Successfully fetched all available domain commands"

        result = OperationResult(
            success=True,
            message=message,
            data={
                "browser_id": browser_id,
                "tab_id": tab_id,
                "domain": domain,
                "commands": commands,
                "command_count": len(commands) if isinstance(commands, list) else sum(len(cmds) for cmds in commands.values())
            }
        )

        logger.info(f"Domain commands fetched successfully: {domain or 'all'}")
        return [TextContent(type="text", text=result.json())]

    except AttributeError:
        # Fallback for older PyDoll versions (should not occur with 2.12.4+)
        logger.warning("fetch_domain_commands not available in current PyDoll version")
        result = OperationResult(
            success=False,
            error="Feature requires PyDoll 2.3.1 or higher",
            message="Please upgrade PyDoll to use this feature"
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Failed to fetch domain commands: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to fetch domain commands"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_scroll(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle page scrolling request."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        direction = arguments.get("direction", "down")
        amount = arguments.get("amount", 500)
        element_selector = arguments.get("element_selector")
        x = arguments.get("x")
        y = arguments.get("y")
        behavior = arguments.get("behavior", "smooth")

        # Get tab
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        if direction == "to_element":
            if not element_selector:
                raise ValueError("element_selector is required for scroll_to_element")

            # Find element and scroll to it
            from .element_tools import handle_find_element
            find_args = {**element_selector, "browser_id": browser_id, "tab_id": actual_tab_id}
            find_result = await handle_find_element(find_args)
            find_data = OperationResult.parse_raw(find_result[0].text)

            if not find_data.success or not find_data.data.get("elements"):
                raise ValueError("Element not found for scrolling")

            # Find element object and scroll
            if element_selector.get("css_selector"):
                element = await tab.query(element_selector["css_selector"])
            elif element_selector.get("xpath"):
                element = await tab.query(element_selector["xpath"])
            else:
                find_params = {k: v for k, v in element_selector.items()
                             if k in ["tag_name", "id", "class_name", "text", "name",
                                     "type", "placeholder", "value"]}
                element = await tab.find(**find_params, raise_exc=False)

            if element:
                await element.scroll_into_view()
                scroll_info = "Scrolled to element"
            else:
                raise ValueError("Element not found for scrolling")

        elif direction == "to_position":
            if x is None or y is None:
                raise ValueError("x and y coordinates are required for scroll_to_position")

            script = f"window.scrollTo({{left: {x}, top: {y}, behavior: '{behavior}'}});"
            await tab.execute_script(script)
            scroll_info = f"Scrolled to position ({x}, {y})"

        elif direction == "to_top":
            script = f"window.scrollTo({{top: 0, behavior: '{behavior}'}});"
            await tab.execute_script(script)
            scroll_info = "Scrolled to top"

        elif direction == "to_bottom":
            script = f"window.scrollTo({{top: document.body.scrollHeight, behavior: '{behavior}'}});"
            await tab.execute_script(script)
            scroll_info = "Scrolled to bottom"

        else:
            # Directional scrolling
            scroll_x = 0
            scroll_y = 0

            if direction == "down":
                scroll_y = amount
            elif direction == "up":
                scroll_y = -amount
            elif direction == "right":
                scroll_x = amount
            elif direction == "left":
                scroll_x = -amount

            script = f"window.scrollBy({{left: {scroll_x}, top: {scroll_y}, behavior: '{behavior}'}});"
            await tab.execute_script(script)
            scroll_info = f"Scrolled {direction} by {amount} pixels"

        # Get current scroll position
        scroll_result = await tab.execute_script("return {x: window.scrollX, y: window.scrollY};")
        scroll_pos = {}
        if scroll_result and 'result' in scroll_result and 'result' in scroll_result['result']:
            scroll_pos = scroll_result['result']['result'].get('value', {})

        result = OperationResult(
            success=True,
            message=scroll_info,
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "direction": direction,
                "amount": amount if direction in ["up", "down", "left", "right"] else None,
                "scroll_position": scroll_pos,
                "behavior": behavior
            }
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Scroll failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to scroll page"
        )
        return [TextContent(type="text", text=result.json())]


async def handle_get_frame(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle get frame request for iframe access."""
    try:
        browser_manager = get_browser_manager()
        browser_id = arguments["browser_id"]
        tab_id = arguments.get("tab_id")
        frame_selector = arguments["frame_selector"]
        selector_type = arguments.get("selector_type", "css")

        # Get tab
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(browser_id, tab_id)

        # Check if PyDoll has get_frame method
        if hasattr(tab, 'get_frame'):
            try:
                frame = await tab.get_frame(frame_selector)
                frame_info = {
                    "frame_id": getattr(frame, 'frame_id', None),
                    "url": getattr(frame, 'url', None),
                    "name": getattr(frame, 'name', None),
                }

                result = OperationResult(
                    success=True,
                    message="Frame accessed successfully",
                    data={
                        "browser_id": browser_id,
                        "tab_id": actual_tab_id,
                        "frame_selector": frame_selector,
                        "frame": frame_info
                    }
                )
                return [TextContent(type="text", text=result.json())]
            except Exception as e:
                logger.warning(f"PyDoll get_frame failed: {e}, using fallback")

        # Fallback: Use JavaScript to access frame
        frame_element = None
        if selector_type == "css":
            script = f"document.querySelector('{frame_selector}');"
            frame_result = await tab.execute_script(script)
            if frame_result and 'result' in frame_result:
                frame_element = frame_result['result']
        elif selector_type == "xpath":
            script = f"""
            (function() {{
                const result = document.evaluate('{frame_selector}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                return result.singleNodeValue;
            }})();
            """
            frame_result = await tab.execute_script(script)
            if frame_result and 'result' in frame_result:
                frame_element = frame_result['result']
        elif selector_type == "name":
            script = f"document.querySelector('iframe[name=\"{frame_selector}\"]') || document.querySelector('frame[name=\"{frame_selector}\"]');"
            frame_result = await tab.execute_script(script)
            if frame_result and 'result' in frame_result:
                frame_element = frame_result['result']
        elif selector_type == "id":
            script = f"document.getElementById('{frame_selector}');"
            frame_result = await tab.execute_script(script)
            if frame_result and 'result' in frame_result:
                frame_element = frame_result['result']

        if not frame_element:
            raise ValueError(f"Frame not found with selector: {frame_selector}")

        # Get frame information
        frame_info_script = """
        (function(frame) {
            if (!frame) return null;
            return {
                tagName: frame.tagName,
                id: frame.id,
                name: frame.name,
                src: frame.src || frame.getAttribute('src'),
                contentWindow: frame.contentWindow ? 'available' : null
            };
        })(arguments[0]);
        """

        # Note: We can't directly pass frame_element to execute_script
        # Instead, we'll get frame info using the selector
        info_script = f"""
        (function() {{
            let frame;
            if ('{selector_type}' === 'css') {{
                frame = document.querySelector('{frame_selector}');
            }} else if ('{selector_type}' === 'xpath') {{
                const result = document.evaluate('{frame_selector}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                frame = result.singleNodeValue;
            }} else if ('{selector_type}' === 'name') {{
                frame = document.querySelector('iframe[name="{frame_selector}"]') || document.querySelector('frame[name="{frame_selector}"]');
            }} else if ('{selector_type}' === 'id') {{
                frame = document.getElementById('{frame_selector}');
            }}

            if (!frame) return null;
            return {{
                tagName: frame.tagName,
                id: frame.id,
                name: frame.name,
                src: frame.src || frame.getAttribute('src'),
                hasContentWindow: !!frame.contentWindow
            }};
        }})();
        """

        frame_info_result = await tab.execute_script(info_script)
        frame_info = {}
        if frame_info_result and 'result' in frame_info_result and 'result' in frame_info_result['result']:
            frame_info = frame_info_result['result']['result'].get('value', {})

        result = OperationResult(
            success=True,
            message="Frame accessed successfully",
            data={
                "browser_id": browser_id,
                "tab_id": actual_tab_id,
                "frame_selector": frame_selector,
                "selector_type": selector_type,
                "frame": frame_info,
                "note": "Frame access via JavaScript fallback. Use execute_script with frame.contentWindow for frame operations."
            }
        )
        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Get frame failed: {e}")
        result = OperationResult(
            success=False,
            error=str(e),
            message="Failed to get frame"
        )
        return [TextContent(type="text", text=result.json())]


# Navigation Tool Handlers Dictionary
NAVIGATION_TOOL_HANDLERS = {
    "navigate_to": handle_navigate_to,
    "refresh_page": handle_refresh_page,
    "go_back": handle_go_back,
    "get_current_url": handle_get_current_url,
    "get_page_title": handle_get_page_title,
    "get_page_source": handle_get_page_source,
    "fetch_domain_commands": handle_fetch_domain_commands,
    "scroll": handle_scroll,
    "get_frame": handle_get_frame,
}
