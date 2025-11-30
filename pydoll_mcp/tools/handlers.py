"""Unified Tool Handlers for PyDoll MCP Server.

This module implements handlers for the "Fat Tools" - unified,
high-level tools that consolidate multiple granular operations.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Sequence

from mcp.types import TextContent

from ..core import get_browser_manager
from ..models import OperationResult
from ..utils import enrich_errors
from .definitions import (
    BrowserAction,
    BrowserControlInput,
    CaptureMediaInput,
    ElementAction,
    ElementFindAction,
    ExecuteCDPInput,
    ExecuteScriptInput,
    FileAction,
    FindElementInput,
    InteractElementInput,
    ManageFileInput,
    ManageTabInput,
    NavigatePageInput,
    NavigationAction,
    ScreenshotAction,
    ScriptAction,
    TabAction,
)

logger = logging.getLogger(__name__)


@enrich_errors
async def handle_interact_element(input_data: InteractElementInput) -> Sequence[TextContent]:
    """Handle unified element interaction.

    Consolidates click, type, hover, press_key, drag, and scroll operations.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        # Find the element
        selector = input_data.selector
        element = None

        try:
            if selector.get("css_selector"):
                element = await tab.query(selector["css_selector"])
            elif selector.get("xpath"):
                element = await tab.query(selector["xpath"])
            else:
                # Use find() with natural attributes
                find_params = {
                    k: v for k, v in selector.items()
                    if k in ["tag_name", "id", "class_name", "text", "name",
                            "type", "placeholder", "value", "data_testid",
                            "data_id", "aria_label", "aria_role"]
                }
                element = await tab.find(**find_params, raise_exc=False)
        except Exception as e:
            logger.error(f"Element finding failed: {e}")
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="ElementNotFound",
                message=f"Failed to find element: {e}"
            ).json())]

        if not element:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="ElementNotFound",
                message="Element not found with provided selector"
            ).json())]

        # Scroll to element if requested
        if input_data.scroll_to_element:
            try:
                await element.scroll_into_view()
            except Exception as e:
                logger.debug(f"Scroll to element failed: {e}")

        # Perform action based on type
        if input_data.action == ElementAction.CLICK:
            click_type = input_data.click_type or "left"
            if click_type == "double":
                await element.double_click()
            elif click_type == "right":
                await element.right_click()
            else:
                await element.click()

            result = OperationResult(
                success=True,
                message="Element clicked successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "action": "click",
                    "click_type": click_type
                }
            )

        elif input_data.action == ElementAction.TYPE:
            if input_data.value is None:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ValueRequired",
                    message="Value is required for type action"
                ).json())]

            if input_data.clear_first:
                try:
                    await element.clear()
                except Exception:
                    pass  # Some elements don't support clear

            typing_speed = input_data.typing_speed or "normal"
            human_like = input_data.human_like if input_data.human_like is not None else True

            await element.type(input_data.value, human_like=human_like, typing_speed=typing_speed)

            result = OperationResult(
                success=True,
                message="Text typed successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "action": "type",
                    "text_length": len(input_data.value)
                }
            )

        elif input_data.action == ElementAction.HOVER:
            await element.hover()
            result = OperationResult(
                success=True,
                message="Element hovered successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "action": "hover"
                }
            )

        elif input_data.action == ElementAction.PRESS_KEY:
            if input_data.value is None:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ValueRequired",
                    message="Key value is required for press_key action"
                ).json())]

            await tab.press_key(input_data.value)
            result = OperationResult(
                success=True,
                message="Key pressed successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "action": "press_key",
                    "key": input_data.value
                }
            )

        elif input_data.action == ElementAction.SCROLL:
            # Scroll the element or page
            if hasattr(element, 'scroll_into_view'):
                await element.scroll_into_view()
            result = OperationResult(
                success=True,
                message="Scrolled successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "action": "scroll"
                }
            )

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Interact element failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_manage_tab(input_data: ManageTabInput) -> Sequence[TextContent]:
    """Handle unified tab management.

    Consolidates create, close, refresh, activate, and list operations.
    """
    try:
        browser_manager = get_browser_manager()

        if input_data.action == TabAction.CREATE:
            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            if input_data.url:
                new_tab = await browser_instance.browser.new_tab(input_data.url)
            else:
                new_tab = await browser_instance.browser.new_tab()

            tab_id = browser_manager._generate_tab_id()
            browser_instance.tabs[tab_id] = new_tab

            # Save to SessionStore
            try:
                url = await new_tab.current_url() if hasattr(new_tab, 'current_url') else input_data.url
                title = await new_tab.page_title() if hasattr(new_tab, 'page_title') else None
            except Exception:
                url = input_data.url
                title = None

            await browser_manager.session_store.save_tab(
                tab_id=tab_id,
                browser_id=input_data.browser_id,
                url=url,
                title=title
            )

            result = OperationResult(
                success=True,
                message="Tab created successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": tab_id,
                    "url": url
                }
            )

        elif input_data.action == TabAction.CLOSE:
            if not input_data.tab_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="TabIdRequired",
                    message="tab_id is required for close action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            tab = browser_instance.tabs.get(input_data.tab_id)
            if tab:
                await tab.close()
                del browser_instance.tabs[input_data.tab_id]

            await browser_manager.session_store.delete_tab(input_data.tab_id)

            result = OperationResult(
                success=True,
                message="Tab closed successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": input_data.tab_id
                }
            )

        elif input_data.action == TabAction.REFRESH:
            if not input_data.tab_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="TabIdRequired",
                    message="tab_id is required for refresh action"
                ).json())]

            tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
                input_data.browser_id, input_data.tab_id
            )

            ignore_cache = input_data.ignore_cache if input_data.ignore_cache is not None else False
            wait_for_load = input_data.wait_for_load if input_data.wait_for_load is not None else True

            await tab.refresh(ignore_cache=ignore_cache, wait_for_load=wait_for_load)

            result = OperationResult(
                success=True,
                message="Tab refreshed successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id
                }
            )

        elif input_data.action == TabAction.ACTIVATE:
            if not input_data.tab_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="TabIdRequired",
                    message="tab_id is required for activate action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            if input_data.tab_id in browser_instance.tabs:
                browser_instance.active_tab_id = input_data.tab_id
                # Try to bring tab to front if method exists
                tab = browser_instance.tabs[input_data.tab_id]
                if hasattr(tab, 'bring_to_front'):
                    await tab.bring_to_front()

            result = OperationResult(
                success=True,
                message="Tab activated successfully",
                data={
                    "browser_id": input_data.browser_id,
                    "tab_id": input_data.tab_id
                }
            )

        elif input_data.action == TabAction.LIST:
            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            tabs_data = []
            for tab_id, tab in browser_instance.tabs.items():
                try:
                    url = await tab.current_url() if hasattr(tab, 'current_url') else None
                    title = await tab.page_title() if hasattr(tab, 'page_title') else None
                except Exception:
                    url = None
                    title = None

                tabs_data.append({
                    "tab_id": tab_id,
                    "url": url,
                    "title": title,
                    "is_active": tab_id == browser_instance.active_tab_id
                })

            result = OperationResult(
                success=True,
                message=f"Found {len(tabs_data)} tab(s)",
                data={
                    "browser_id": input_data.browser_id,
                    "tabs": tabs_data
                }
            )

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Manage tab failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_browser_control(input_data: BrowserControlInput) -> Sequence[TextContent]:
    """Handle unified browser control.

    Consolidates start, stop, get_state, and list operations.
    """
    try:
        browser_manager = get_browser_manager()

        if input_data.action == BrowserAction.START:
            # Build config from input
            config = input_data.config or {}
            if input_data.browser_type:
                config["browser_type"] = input_data.browser_type
            if input_data.headless is not None:
                config["headless"] = input_data.headless
            if input_data.window_width:
                config["window_width"] = input_data.window_width
            if input_data.window_height:
                config["window_height"] = input_data.window_height
            if input_data.stealth_mode is not None:
                config["stealth_mode"] = input_data.stealth_mode
            if input_data.proxy_server:
                config["proxy"] = input_data.proxy_server
            if input_data.user_agent:
                config["user_agent"] = input_data.user_agent

            browser_instance = await browser_manager.create_browser(**config)

            result = OperationResult(
                success=True,
                message="Browser started successfully",
                data={
                    "browser_id": browser_instance.instance_id,
                    "browser_type": browser_instance.browser_type,
                    "tabs_count": len(browser_instance.tabs)
                }
            )

        elif input_data.action == BrowserAction.STOP:
            if not input_data.browser_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserIdRequired",
                    message="browser_id is required for stop action"
                ).json())]

            await browser_manager.destroy_browser(input_data.browser_id)

            result = OperationResult(
                success=True,
                message="Browser stopped successfully",
                data={
                    "browser_id": input_data.browser_id
                }
            )

        elif input_data.action == BrowserAction.GET_STATE:
            if not input_data.browser_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserIdRequired",
                    message="browser_id is required for get_state action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            result = OperationResult(
                success=True,
                message="Browser state retrieved",
                data=browser_instance.to_dict()
            )

        elif input_data.action == BrowserAction.LIST:
            active_browsers = await browser_manager.session_store.list_browsers(active_only=True)

            browsers_data = []
            for browser_data in active_browsers:
                browsers_data.append({
                    "browser_id": browser_data["browser_id"],
                    "browser_type": browser_data["browser_type"],
                    "created_at": browser_data["created_at"],
                    "last_activity": browser_data["last_activity"]
                })

            result = OperationResult(
                success=True,
                message=f"Found {len(browsers_data)} active browser(s)",
                data={
                    "browsers": browsers_data
                }
            )

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Browser control failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_execute_cdp(input_data: ExecuteCDPInput) -> Sequence[TextContent]:
    """Handle CDP command execution.

    Provides direct access to Chrome DevTools Protocol commands.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        # Construct CDP command
        command = f"{input_data.domain}.{input_data.method}"

        # Try to execute via PyDoll's CDP interface
        # PyDoll may expose this differently - check for common patterns
        try:
            if hasattr(tab, 'execute_cdp_command'):
                result = await tab.execute_cdp_command(command, input_data.params)
            elif hasattr(tab, '_connection') and hasattr(tab._connection, 'send'):
                # Direct CDP connection access
                result = await tab._connection.send(command, input_data.params)
            else:
                # Fallback: try to access via browser's CDP connection
                browser_instance = await browser_manager.get_browser(input_data.browser_id)
                if browser_instance and hasattr(browser_instance.browser, 'execute_cdp_command'):
                    result = await browser_instance.browser.execute_cdp_command(command, input_data.params)
                else:
                    raise AttributeError("CDP command execution not available in this PyDoll version")
        except AttributeError as e:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="CDPNotAvailable",
                message=f"CDP command execution not available: {e}"
            ).json())]
        except Exception as e:
            logger.error(f"CDP command execution failed: {e}", exc_info=True)
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="CDPExecutionError",
                message=f"Failed to execute CDP command: {e}"
            ).json())]

        return [TextContent(type="text", text=OperationResult(
            success=True,
            message="CDP command executed successfully",
            data={
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "command": command,
                "result": result
            }
        ).json())]

    except Exception as e:
        logger.error(f"Execute CDP failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_navigate_page(input_data: NavigatePageInput) -> Sequence[TextContent]:
    """Handle unified page navigation.

    Consolidates navigate, go_back, go_forward, get_url, get_title, get_source, wait operations.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        if input_data.action == NavigationAction.NAVIGATE:
            if not input_data.url:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="UrlRequired",
                    message="URL is required for navigate action"
                ).json())]

            # Use legacy handler for navigation to ensure compatibility
            from .navigation_tools import handle_navigate_to
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "url": input_data.url,
                "wait_for_load": input_data.wait_for_load,
                "timeout": input_data.timeout,
                "referrer": input_data.referrer
            }
            return await handle_navigate_to(args)

        elif input_data.action == NavigationAction.GO_BACK:
            from .navigation_tools import handle_go_back
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "steps": 1
            }
            return await handle_go_back(args)

        elif input_data.action == NavigationAction.GO_FORWARD:
            from .navigation_tools import handle_go_forward
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "steps": 1
            }
            return await handle_go_forward(args)

        elif input_data.action == NavigationAction.GET_URL:
            from .navigation_tools import handle_get_current_url
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id
            }
            return await handle_get_current_url(args)

        elif input_data.action == NavigationAction.GET_TITLE:
            from .navigation_tools import handle_get_page_title
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id
            }
            return await handle_get_page_title(args)

        elif input_data.action == NavigationAction.GET_SOURCE:
            from .navigation_tools import handle_get_page_source
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id
            }
            return await handle_get_page_source(args)

        elif input_data.action == NavigationAction.WAIT_LOAD:
            from .navigation_tools import handle_wait_for_page_load
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "timeout": input_data.timeout
            }
            return await handle_wait_for_page_load(args)

        elif input_data.action == NavigationAction.WAIT_NETWORK_IDLE:
            from .navigation_tools import handle_wait_for_network_idle
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "timeout": input_data.timeout
            }
            return await handle_wait_for_network_idle(args)

        elif input_data.action == NavigationAction.SET_VIEWPORT:
            if not input_data.width or not input_data.height:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="WidthHeightRequired",
                    message="Width and height are required for set_viewport action"
                ).json())]

            from .navigation_tools import handle_set_viewport_size
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "width": input_data.width,
                "height": input_data.height
            }
            return await handle_set_viewport_size(args)

        elif input_data.action == NavigationAction.GET_INFO:
            from .navigation_tools import handle_get_page_info
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id
            }
            return await handle_get_page_info(args)

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Navigate page failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_capture_media(input_data: CaptureMediaInput) -> Sequence[TextContent]:
    """Handle unified screenshot and media capture.

    Consolidates take_screenshot, take_element_screenshot, generate_pdf operations.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        if input_data.action == ScreenshotAction.SCREENSHOT:
            # Import screenshot handler logic
            from .screenshot_tools import handle_take_screenshot
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "format": input_data.format,
                "quality": input_data.quality,
                "full_page": input_data.full_page,
                "file_name": input_data.file_name,
                "save_to_file": input_data.save_to_file,
                "return_base64": input_data.return_base64
            }
            return await handle_take_screenshot(args)

        elif input_data.action == ScreenshotAction.ELEMENT_SCREENSHOT:
            if not input_data.selector:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="SelectorRequired",
                    message="Selector is required for element_screenshot action"
                ).json())]

            from .screenshot_tools import handle_take_element_screenshot
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "selector": input_data.selector,
                "format": input_data.format,
                "quality": input_data.quality,
                "file_name": input_data.file_name,
                "save_to_file": input_data.save_to_file,
                "return_base64": input_data.return_base64
            }
            return await handle_take_element_screenshot(args)

        elif input_data.action == ScreenshotAction.GENERATE_PDF:
            from .screenshot_tools import handle_generate_pdf
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "file_name": input_data.file_name,
                "format": input_data.pdf_format,
                "orientation": input_data.orientation,
                "include_background": input_data.include_background
            }
            return await handle_generate_pdf(args)

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

    except Exception as e:
        logger.error(f"Capture media failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_execute_script(input_data: ExecuteScriptInput) -> Sequence[TextContent]:
    """Handle unified script execution.

    Consolidates execute_javascript, evaluate_expression, inject_script, get_console_logs operations.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        if input_data.action == ScriptAction.EXECUTE:
            if not input_data.script:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ScriptRequired",
                    message="Script is required for execute action"
                ).json())]

            from .script_tools import handle_execute_javascript
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "script": input_data.script,
                "wait_for_execution": input_data.wait_for_execution,
                "return_result": input_data.return_result,
                "timeout": input_data.timeout,
                "context": input_data.context
            }
            return await handle_execute_javascript(args)

        elif input_data.action == ScriptAction.EVALUATE:
            if not input_data.expression:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ExpressionRequired",
                    message="Expression is required for evaluate action"
                ).json())]

            from .script_tools import handle_evaluate_expression
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "expression": input_data.expression
            }
            return await handle_evaluate_expression(args)

        elif input_data.action == ScriptAction.INJECT:
            if not input_data.library:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="LibraryRequired",
                    message="Library is required for inject action"
                ).json())]

            from .script_tools import handle_inject_script
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "library": input_data.library,
                "custom_url": input_data.custom_url
            }
            return await handle_inject_script(args)

        elif input_data.action == ScriptAction.GET_CONSOLE_LOGS:
            from .script_tools import handle_get_console_logs
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id
            }
            return await handle_get_console_logs(args)

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Execute script failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_manage_file(input_data: ManageFileInput) -> Sequence[TextContent]:
    """Handle unified file operations.

    Consolidates upload_file, download_file, manage_downloads operations.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        if input_data.action == FileAction.UPLOAD:
            if not input_data.file_path or not input_data.input_selector:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="FilePathAndSelectorRequired",
                    message="file_path and input_selector are required for upload action"
                ).json())]

            from .file_tools import handle_upload_file
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "file_path": input_data.file_path,
                "input_selector": input_data.input_selector
            }
            return await handle_upload_file(args)

        elif input_data.action == FileAction.DOWNLOAD:
            from .file_tools import handle_download_file
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "url": input_data.url,
                "save_path": input_data.save_path,
                "wait_for_completion": input_data.wait_for_completion,
                "timeout": input_data.timeout
            }
            return await handle_download_file(args)

        elif input_data.action == FileAction.MANAGE_DOWNLOADS:
            from .file_tools import handle_manage_downloads
            args = {
                "browser_id": input_data.browser_id,
                "action": input_data.download_action or "list",
                "download_id": input_data.download_id
            }
            return await handle_manage_downloads(args)

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

    except Exception as e:
        logger.error(f"Manage file failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]


@enrich_errors
async def handle_find_element(input_data: FindElementInput) -> Sequence[TextContent]:
    """Handle unified element finding.

    Consolidates find_element, find_elements, query, wait_for_element, get_element_text, get_element_attribute operations.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        if input_data.action == ElementFindAction.FIND:
            from .element_tools import handle_find_element
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "selector": input_data.selector,
                "find_all": False,
                "search_shadow_dom": input_data.search_shadow_dom
            }
            return await handle_find_element(args)

        elif input_data.action == ElementFindAction.FIND_ALL:
            from .element_tools import handle_find_element
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "selector": input_data.selector,
                "find_all": True,
                "search_shadow_dom": input_data.search_shadow_dom
            }
            return await handle_find_element(args)

        elif input_data.action == ElementFindAction.QUERY:
            from .element_tools import handle_query
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "css_selector": input_data.css_selector,
                "xpath": input_data.xpath,
                "find_all": input_data.find_all
            }
            return await handle_query(args)

        elif input_data.action == ElementFindAction.WAIT_FOR:
            from .element_tools import handle_find_or_wait_element
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "selector": input_data.selector,
                "timeout": input_data.timeout,
                "wait_for_visible": input_data.wait_for_visible
            }
            return await handle_find_or_wait_element(args)

        elif input_data.action == ElementFindAction.GET_TEXT:
            find_params = {
                k: v for k, v in input_data.selector.items()
                if k in ["tag_name", "id", "class_name", "text", "name",
                        "type", "placeholder", "value", "data_testid",
                        "data_id", "aria_label", "aria_role"]
            }
            element = await tab.find(**find_params, raise_exc=False)
            if element:
                text = await element.text()
                result = OperationResult(
                    success=True,
                    message="Element text retrieved",
                    data={
                        "browser_id": input_data.browser_id,
                        "tab_id": actual_tab_id,
                        "text": text
                    }
                )
            else:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ElementNotFound",
                    message="Element not found"
                ).json())]

        elif input_data.action == ElementFindAction.GET_ATTRIBUTE:
            if not input_data.attribute_name:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="AttributeNameRequired",
                    message="attribute_name is required for get_attribute action"
                ).json())]

            find_params = {
                k: v for k, v in input_data.selector.items()
                if k in ["tag_name", "id", "class_name", "text", "name",
                        "type", "placeholder", "value", "data_testid",
                        "data_id", "aria_label", "aria_role"]
            }
            element = await tab.find(**find_params, raise_exc=False)
            if element:
                attr_value = await element.get_attribute(input_data.attribute_name)
                result = OperationResult(
                    success=True,
                    message="Attribute retrieved",
                    data={
                        "browser_id": input_data.browser_id,
                        "tab_id": actual_tab_id,
                        "attribute": input_data.attribute_name,
                        "value": attr_value
                    }
                )
            else:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ElementNotFound",
                    message="Element not found"
                ).json())]

        elif input_data.action == ElementFindAction.CHECK_VISIBILITY:
            find_params = {
                k: v for k, v in input_data.selector.items()
                if k in ["tag_name", "id", "class_name", "text", "name",
                        "type", "placeholder", "value", "data_testid",
                        "data_id", "aria_label", "aria_role"]
            }
            element = await tab.find(**find_params, raise_exc=False)
            if element:
                is_visible = await element.is_visible()
                result = OperationResult(
                    success=True,
                    message="Visibility checked",
                    data={
                        "browser_id": input_data.browser_id,
                        "tab_id": actual_tab_id,
                        "visible": is_visible
                    }
                )
            else:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ElementNotFound",
                    message="Element not found"
                ).json())]

        elif input_data.action == ElementFindAction.GET_PARENT:
            find_params = {
                k: v for k, v in input_data.selector.items()
                if k in ["tag_name", "id", "class_name", "text", "name",
                        "type", "placeholder", "value", "data_testid",
                        "data_id", "aria_label", "aria_role"]
            }
            element = await tab.find(**find_params, raise_exc=False)
            if element:
                from .element_tools import handle_get_parent_element
                args = {
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "selector": input_data.selector
                }
                return await handle_get_parent_element(args)
            else:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ElementNotFound",
                    message="Element not found"
                ).json())]

        else:
            return [TextContent(type="text", text=OperationResult(
                success=False,
                error="UnsupportedAction",
                message=f"Action {input_data.action} not yet implemented"
            ).json())]

        return [TextContent(type="text", text=result.json())]

    except Exception as e:
        logger.error(f"Find element failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]

