"""Unified Tool Handlers for PyDoll MCP Server.

This module implements handlers for the "Fat Tools" - unified,
high-level tools that consolidate multiple granular operations.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, Sequence

from mcp.types import TextContent

from ..core import get_browser_manager
from ..models import OperationResult
from ..utils import enrich_errors
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
            # Ensure tab_id is a string (not a coroutine)
            if hasattr(tab_id, '__await__'):
                tab_id = await tab_id
            tab_id = str(tab_id) if tab_id is not None else str(browser_manager._generate_tab_id())
            browser_instance.tabs[tab_id] = new_tab

            # Save to SessionStore
            try:
                # Handle both property and method cases for current_url
                if hasattr(new_tab, 'current_url'):
                    url_attr = getattr(new_tab, 'current_url')
                    if callable(url_attr):
                        url_result = await url_attr()
                        # Handle coroutine results
                        if hasattr(url_result, '__await__'):
                            url_result = await url_result
                        # Ensure url is a string, not a coroutine
                        url = str(url_result) if url_result is not None else (input_data.url or "")
                    else:
                        # Handle coroutine properties
                        if hasattr(url_attr, '__await__'):
                            url_attr = await url_attr()
                        url = str(url_attr) if url_attr is not None else (input_data.url or "")
                else:
                    url = input_data.url or ""

                # Handle both property and method cases for page_title
                if hasattr(new_tab, 'page_title'):
                    title_attr = getattr(new_tab, 'page_title')
                    if callable(title_attr):
                        title_result = await title_attr()
                        # Handle coroutine results
                        if hasattr(title_result, '__await__'):
                            title_result = await title_result
                        # Ensure title is a string, not a coroutine
                        title = str(title_result) if title_result is not None else None
                    else:
                        # Handle coroutine properties
                        if hasattr(title_attr, '__await__'):
                            title_attr = await title_attr()
                        title = str(title_attr) if title_attr is not None else None
                else:
                    title = None
            except Exception:
                url = input_data.url or ""
                title = None

            # Ensure url and title are strings for serialization (not coroutines)
            url = str(url) if url is not None and not hasattr(url, '__await__') else (input_data.url or "")
            title = str(title) if title is not None and not hasattr(title, '__await__') else None

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
                    "action": "create",
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
                    "action": "close",
                    "browser_id": input_data.browser_id,
                    "tab_id": input_data.tab_id
                }
            )

        elif input_data.action == TabAction.REFRESH:
            tab_result = await browser_manager.get_tab_with_fallback(
                input_data.browser_id, input_data.tab_id
            )
            # Handle both tuple and single value returns
            if isinstance(tab_result, tuple) and len(tab_result) == 2:
                tab, actual_tab_id = tab_result
            else:
                # Fallback if mock doesn't return tuple
                tab = tab_result if tab_result else None
                actual_tab_id = input_data.tab_id or "tab-1"

            if not tab:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="TabNotFound",
                    message="Tab not found"
                ).json())]

            ignore_cache = input_data.ignore_cache if input_data.ignore_cache is not None else False
            wait_for_load = input_data.wait_for_load if input_data.wait_for_load is not None else True

            await tab.refresh(ignore_cache=ignore_cache, wait_for_load=wait_for_load)

            result = OperationResult(
                success=True,
                message="Tab refreshed successfully",
                data={
                    "action": "refresh",
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
                    "action": "activate",
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
                    # Handle both property and method cases
                    if hasattr(tab, 'current_url'):
                        url_attr = getattr(tab, 'current_url')
                        if callable(url_attr):
                            url = await url_attr()
                        else:
                            url = url_attr
                    else:
                        url = None

                    if hasattr(tab, 'page_title'):
                        title_attr = getattr(tab, 'page_title')
                        if callable(title_attr):
                            title = await title_attr()
                        else:
                            title = title_attr
                    else:
                        title = None
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
                    "action": "list",
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
                    "action": "start",
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
                    "action": "stop",
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

            browser_dict = browser_instance.to_dict()
            browser_dict["action"] = "get_state"
            result = OperationResult(
                success=True,
                message="Browser state retrieved",
                data=browser_dict
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
                    "action": "list",
                    "browsers": browsers_data
                }
            )

        elif input_data.action == BrowserAction.CREATE_CONTEXT:
            if not input_data.browser_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserIdRequired",
                    message="browser_id is required for create_context action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            context_name = input_data.context_name
            if hasattr(browser_instance.browser, 'create_browser_context'):
                try:
                    context = await browser_instance.browser.create_browser_context()
                    context_id = getattr(context, 'id', str(context))
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
                            "action": "create_context",
                            "browser_id": input_data.browser_id,
                            "context_id": context_id,
                            "context_name": context_name
                        }
                    )
                except Exception as e:
                    logger.warning(f"PyDoll create_browser_context failed: {e}")
                    result = OperationResult(
                        success=False,
                        error=str(e),
                        message="Failed to create browser context - PyDoll API may not support this feature"
                    )
            else:
                result = OperationResult(
                    success=False,
                    error="Browser context creation not supported",
                    message="PyDoll browser does not support create_browser_context method"
                )

        elif input_data.action == BrowserAction.LIST_CONTEXTS:
            if not input_data.browser_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserIdRequired",
                    message="browser_id is required for list_contexts action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            contexts_list = []
            if hasattr(browser_instance.browser, 'get_browser_contexts'):
                try:
                    contexts = await browser_instance.browser.get_browser_contexts()
                    if isinstance(contexts, list):
                        for ctx in contexts:
                            context_id = getattr(ctx, 'id', str(ctx))
                            contexts_list.append({
                                "id": context_id,
                                "name": getattr(ctx, 'name', None)
                            })
                    elif isinstance(contexts, dict):
                        contexts_list = [{"id": k, "name": v} for k, v in contexts.items()]
                except Exception as e:
                    logger.warning(f"PyDoll get_browser_contexts failed: {e}")

            if not contexts_list and hasattr(browser_instance, 'contexts'):
                contexts_attr = browser_instance.contexts
                # Handle both dict and coroutine cases
                if callable(contexts_attr):
                    try:
                        contexts_dict = await contexts_attr()
                    except Exception:
                        # If it's not awaitable or fails, try as regular attribute
                        contexts_dict = contexts_attr
                else:
                    contexts_dict = contexts_attr

                # Ensure contexts_dict is actually a dict, not a coroutine
                if hasattr(contexts_dict, '__await__'):
                    contexts_dict = await contexts_dict

                if contexts_dict and isinstance(contexts_dict, dict):
                    contexts_list = [
                        {"id": ctx_id, "name": ctx_info.get("name") if isinstance(ctx_info, dict) else None}
                        for ctx_id, ctx_info in contexts_dict.items()
                    ]

            result = OperationResult(
                success=True,
                message=f"Found {len(contexts_list)} browser context(s)",
                data={
                    "action": "list_contexts",
                    "browser_id": input_data.browser_id,
                    "contexts": contexts_list,
                    "count": len(contexts_list)
                }
            )

        elif input_data.action == BrowserAction.DELETE_CONTEXT:
            if not input_data.browser_id or not input_data.context_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ParametersRequired",
                    message="browser_id and context_id are required for delete_context action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            if hasattr(browser_instance.browser, 'delete_browser_context'):
                try:
                    await browser_instance.browser.delete_browser_context(input_data.context_id)
                    if hasattr(browser_instance, 'contexts') and input_data.context_id in browser_instance.contexts:
                        del browser_instance.contexts[input_data.context_id]
                    result = OperationResult(
                        success=True,
                        message="Browser context deleted successfully",
                        data={
                            "action": "delete_context",
                            "browser_id": input_data.browser_id,
                            "context_id": input_data.context_id
                        }
                    )
                except Exception as e:
                    logger.warning(f"PyDoll delete_browser_context failed: {e}")
                    result = OperationResult(
                        success=False,
                        error=str(e),
                        message="Failed to delete browser context"
                    )
            else:
                result = OperationResult(
                    success=False,
                    error="Browser context deletion not supported",
                    message="PyDoll browser does not support delete_browser_context method"
                )

        elif input_data.action == BrowserAction.GRANT_PERMISSIONS:
            if not input_data.browser_id or not input_data.origin or not input_data.permissions:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="ParametersRequired",
                    message="browser_id, origin, and permissions are required for grant_permissions action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            if hasattr(browser_instance.browser, 'grant_permissions'):
                try:
                    await browser_instance.browser.grant_permissions(
                        origin=input_data.origin,
                        permissions=input_data.permissions
                    )
                    result = OperationResult(
                        success=True,
                        message="Permissions granted successfully",
                        data={
                            "action": "grant_permissions",
                            "browser_id": input_data.browser_id,
                            "origin": input_data.origin,
                            "permissions": input_data.permissions
                        }
                    )
                except Exception as e:
                    logger.warning(f"PyDoll grant_permissions failed: {e}")
                    result = OperationResult(
                        success=False,
                        error=str(e),
                        message="Failed to grant permissions"
                    )
            else:
                result = OperationResult(
                    success=False,
                    error="Grant permissions not supported",
                    message="PyDoll browser does not support grant_permissions method"
                )

        elif input_data.action == BrowserAction.RESET_PERMISSIONS:
            if not input_data.browser_id:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserIdRequired",
                    message="browser_id is required for reset_permissions action"
                ).json())]

            browser_instance = await browser_manager.get_browser(input_data.browser_id)
            if not browser_instance:
                return [TextContent(type="text", text=OperationResult(
                    success=False,
                    error="BrowserNotFound",
                    message=f"Browser {input_data.browser_id} not found"
                ).json())]

            if hasattr(browser_instance.browser, 'reset_permissions'):
                try:
                    if input_data.origin:
                        await browser_instance.browser.reset_permissions(origin=input_data.origin)
                    else:
                        await browser_instance.browser.reset_permissions()
                    result = OperationResult(
                        success=True,
                        message="Permissions reset successfully",
                        data={
                            "action": "reset_permissions",
                            "browser_id": input_data.browser_id,
                            "origin": input_data.origin
                        }
                    )
                except Exception as e:
                    logger.warning(f"PyDoll reset_permissions failed: {e}")
                    result = OperationResult(
                        success=False,
                        error=str(e),
                        message="Failed to reset permissions"
                    )
            else:
                result = OperationResult(
                    success=False,
                    error="Reset permissions not supported",
                    message="PyDoll browser does not support reset_permissions method"
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
                "referrer": input_data.referrer,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_navigate_to(args)

        elif input_data.action == NavigationAction.GO_BACK:
            from .navigation_tools import handle_go_back
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "steps": 1,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_go_back(args)

        elif input_data.action == NavigationAction.GO_FORWARD:
            from .navigation_tools import handle_go_forward
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "steps": 1,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_go_forward(args)

        elif input_data.action == NavigationAction.GET_URL:
            from .navigation_tools import handle_get_current_url
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_get_current_url(args)

        elif input_data.action == NavigationAction.GET_TITLE:
            from .navigation_tools import handle_get_page_title
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_get_page_title(args)

        elif input_data.action == NavigationAction.GET_SOURCE:
            from .navigation_tools import handle_get_page_source
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_get_page_source(args)

        elif input_data.action == NavigationAction.WAIT_LOAD:
            from .navigation_tools import handle_wait_for_page_load
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "timeout": input_data.timeout,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_wait_for_page_load(args)

        elif input_data.action == NavigationAction.WAIT_NETWORK_IDLE:
            from .navigation_tools import handle_wait_for_network_idle
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "timeout": input_data.timeout,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "height": input_data.height,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_set_viewport_size(args)

        elif input_data.action == NavigationAction.GET_INFO:
            from .navigation_tools import handle_get_page_info
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "return_base64": input_data.return_base64,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "return_base64": input_data.return_base64,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "include_background": input_data.include_background,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_generate_pdf(args)

        elif input_data.action == ScreenshotAction.SAVE_PAGE_AS_PDF:
            # Save page as PDF (base64 encoded)
            pdf_data = await tab.print_to_pdf(as_base64=True)
            result = OperationResult(
                success=True,
                message="Page saved as PDF successfully",
                data={
                    "action": "save_page_as_pdf",
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "pdf_data": pdf_data
                }
            )
            return [TextContent(type="text", text=result.json())]

        elif input_data.action == ScreenshotAction.SAVE_PDF:
            # Save PDF with enhanced options and file saving support
            import base64
            import os
            from pathlib import Path

            pdf_format = input_data.pdf_format or "A4"
            print_background = input_data.print_background if input_data.print_background is not None else True

            # Generate PDF with options
            pdf_data = await tab.print_to_pdf(
                as_base64=True,
                format=pdf_format,
                print_background=print_background
            )

            result_data = {
                "action": "save_pdf",
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "format": pdf_format,
                "print_background": print_background
            }

            # Save to file if path provided
            if input_data.file_path:
                try:
                    pdf_path = Path(input_data.file_path)
                    pdf_path.parent.mkdir(parents=True, exist_ok=True)
                    pdf_bytes = base64.b64decode(pdf_data)
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_bytes)
                    result_data["file_path"] = str(pdf_path.absolute())
                    result_data["file_size"] = len(pdf_bytes)
                    message = f"Page saved as PDF to {input_data.file_path}"
                except Exception as save_error:
                    logger.error(f"Failed to save PDF to file: {save_error}")
                    result_data["pdf_data"] = pdf_data
                    result_data["save_error"] = str(save_error)
                    message = "PDF generated but file save failed. PDF data returned as base64."
            else:
                result_data["pdf_data"] = pdf_data
                message = "Page saved as PDF successfully (base64 encoded)."

            result = OperationResult(
                success=True,
                message=message,
                data=result_data
            )
            return [TextContent(type="text", text=result.json())]

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
                "context": input_data.context,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "expression": input_data.expression,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "custom_url": input_data.custom_url,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_inject_script(args)

        elif input_data.action == ScriptAction.GET_CONSOLE_LOGS:
            from .script_tools import handle_get_console_logs
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "input_selector": input_data.input_selector,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "timeout": input_data.timeout,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_download_file(args)

        elif input_data.action == FileAction.MANAGE_DOWNLOADS:
            from .file_tools import handle_manage_downloads
            args = {
                "browser_id": input_data.browser_id,
                "action": input_data.download_action or "list",
                "download_id": input_data.download_id,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                "search_shadow_dom": input_data.search_shadow_dom,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_find_element(args)

        elif input_data.action == ElementFindAction.FIND_ALL:
            from .element_tools import handle_find_element
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "selector": input_data.selector,
                "find_all": True,
                "search_shadow_dom": input_data.search_shadow_dom,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_find_element(args)

        elif input_data.action == ElementFindAction.QUERY:
            from .element_tools import handle_query
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "css_selector": input_data.css_selector,
                "xpath": input_data.xpath,
                "find_all": input_data.find_all,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
            }
            return await handle_query(args)

        elif input_data.action == ElementFindAction.WAIT_FOR:
            from .element_tools import handle_find_or_wait_element
            args = {
                "browser_id": input_data.browser_id,
                "tab_id": actual_tab_id,
                "selector": input_data.selector,
                "timeout": input_data.timeout,
                "wait_for_visible": input_data.wait_for_visible,
                "_tab": tab,  # Pass already-retrieved tab
                "_actual_tab_id": actual_tab_id
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
                # text can be a property or a method - try property first
                if hasattr(element, 'text'):
                    text_attr = getattr(element, 'text')
                    if callable(text_attr):
                        text = await text_attr()
                    else:
                        text = text_attr
                else:
                    text = str(element)
                result = OperationResult(
                    success=True,
                    message="Element text retrieved",
                    data={
                        "action": "get_text",
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
                        "action": "get_attribute",
                        "browser_id": input_data.browser_id,
                        "tab_id": actual_tab_id,
                        "attribute": input_data.attribute_name,
                        "attribute_value": attr_value
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
                        "action": "check_visibility",
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
                    "selector": input_data.selector,
                    "_tab": tab,  # Pass already-retrieved tab
                    "_actual_tab_id": actual_tab_id
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


@enrich_errors
async def handle_interact_page(input_data: InteractPageInput) -> Sequence[TextContent]:
    """Handle unified page interaction (dialogs).

    Consolidates handle_dialog and handle_alert operations.
    """
    try:
        browser_manager = get_browser_manager()
        tab, actual_tab_id = await browser_manager.get_tab_with_fallback(
            input_data.browser_id, input_data.tab_id
        )

        # Check if dialog exists and get message
        dialog_message = None
        dialog_exists = False
        try:
            dialog_exists = await tab.has_dialog()
            if dialog_exists:
                dialog_message = await tab.get_dialog_message()
        except Exception as e:
            logger.debug(f"Could not check dialog state: {e}")

        if input_data.action == DialogAction.HANDLE_DIALOG:
            accept = input_data.accept if input_data.accept is not None else True
            prompt_text = input_data.prompt_text
            await tab.handle_dialog(accept=accept, prompt_text=prompt_text)
            result = OperationResult(
                success=True,
                message="Dialog handled successfully",
                data={
                    "action": "handle_dialog",
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "accepted": accept,
                    "prompt_text_entered": prompt_text,
                    "dialog_message": dialog_message,
                    "dialog_detected": dialog_exists
                }
            )

        elif input_data.action == DialogAction.HANDLE_ALERT:
            accept = input_data.accept if input_data.accept is not None else True
            await tab.handle_dialog(accept=accept)
            result = OperationResult(
                success=True,
                message="Alert handled successfully",
                data={
                    "action": "handle_alert",
                    "browser_id": input_data.browser_id,
                    "tab_id": actual_tab_id,
                    "accepted": accept,
                    "dialog_message": dialog_message,
                    "dialog_detected": dialog_exists
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
        logger.error(f"Interact page failed: {e}", exc_info=True)
        return [TextContent(type="text", text=OperationResult(
            success=False,
            error=type(e).__name__,
            message=str(e)
        ).json())]

