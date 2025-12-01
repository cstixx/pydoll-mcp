"""Comprehensive tests for unified tools.

This module contains robust and comprehensive tests for all unified tools
to ensure they work correctly with all their actions and handle edge cases properly.
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pathlib import Path

from pydoll_mcp.tools.definitions import (
    ElementAction,
    TabAction,
    BrowserAction,
    NavigationAction,
    ScreenshotAction,
    ScriptAction,
    FileAction,
    ElementFindAction,
    DialogAction,
    InteractElementInput,
    ManageTabInput,
    BrowserControlInput,
    NavigatePageInput,
    CaptureMediaInput,
    ExecuteScriptInput,
    ManageFileInput,
    FindElementInput,
    InteractPageInput,
    ExecuteCDPInput,
)
from pydoll_mcp.tools.handlers import (
    handle_interact_element,
    handle_manage_tab,
    handle_browser_control,
    handle_navigate_page,
    handle_capture_media,
    handle_execute_script,
    handle_manage_file,
    handle_find_element,
    handle_interact_page,
    handle_execute_cdp,
)
from pydoll_mcp.models import OperationResult


class TestInteractElement:
    """Comprehensive tests for interact_element unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_element = AsyncMock()
            mock_tab.query = AsyncMock(return_value=mock_element)
            mock_tab.find = AsyncMock(return_value=mock_element)
            mock_tab.press_key = AsyncMock()
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab, mock_element

    @pytest.mark.asyncio
    async def test_click_action_left(self, mock_setup):
        """Test click action with left click."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.CLICK,
            browser_id="browser-1",
            selector={"css_selector": "button"},
            click_type="left"
        )

        result = await handle_interact_element(input_data)

        assert len(result) == 1
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "click"
        mock_element.click.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_click_action_right(self, mock_setup):
        """Test click action with right click."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.CLICK,
            browser_id="browser-1",
            selector={"css_selector": "button"},
            click_type="right"
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        mock_element.right_click.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_click_action_double(self, mock_setup):
        """Test click action with double click."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.CLICK,
            browser_id="browser-1",
            selector={"css_selector": "button"},
            click_type="double"
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        mock_element.double_click.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_type_action(self, mock_setup):
        """Test type action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.TYPE,
            browser_id="browser-1",
            selector={"css_selector": "input"},
            value="test text",
            clear_first=True
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "type"
        mock_element.clear.assert_awaited_once()
        mock_element.type.assert_awaited_once_with("test text", human_like=True, typing_speed="normal")

    @pytest.mark.asyncio
    async def test_type_action_no_value(self, mock_setup):
        """Test type action without value should fail."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.TYPE,
            browser_id="browser-1",
            selector={"css_selector": "input"},
            value=None
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is False
        assert "ValueRequired" in result_data["error"]

    @pytest.mark.asyncio
    async def test_hover_action(self, mock_setup):
        """Test hover action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.HOVER,
            browser_id="browser-1",
            selector={"css_selector": "button"}
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "hover"
        mock_element.hover.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_press_key_action(self, mock_setup):
        """Test press_key action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.PRESS_KEY,
            browser_id="browser-1",
            selector={"css_selector": "input"},
            value="Enter"
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "press_key"
        mock_tab.press_key.assert_awaited_once_with("Enter")

    @pytest.mark.asyncio
    async def test_press_key_no_value(self, mock_setup):
        """Test press_key action without value should fail."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.PRESS_KEY,
            browser_id="browser-1",
            selector={"css_selector": "input"},
            value=None
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is False
        assert "ValueRequired" in result_data["error"]

    @pytest.mark.asyncio
    async def test_scroll_action(self, mock_setup):
        """Test scroll action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.SCROLL,
            browser_id="browser-1",
            selector={"css_selector": "div"}
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "scroll"

    @pytest.mark.asyncio
    async def test_element_not_found(self, mock_setup):
        """Test handling when element is not found."""
        mock_manager, mock_tab, mock_element = mock_setup
        mock_tab.query = AsyncMock(return_value=None)
        mock_tab.find = AsyncMock(return_value=None)

        input_data = InteractElementInput(
            action=ElementAction.CLICK,
            browser_id="browser-1",
            selector={"css_selector": "nonexistent"}
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is False
        assert "ElementNotFound" in result_data["error"]

    @pytest.mark.asyncio
    async def test_selector_xpath(self, mock_setup):
        """Test element finding with xpath selector."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.CLICK,
            browser_id="browser-1",
            selector={"xpath": "//button[@id='test']"}
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        mock_tab.query.assert_awaited_once_with("//button[@id='test']")

    @pytest.mark.asyncio
    async def test_selector_natural_attributes(self, mock_setup):
        """Test element finding with natural attributes."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = InteractElementInput(
            action=ElementAction.CLICK,
            browser_id="browser-1",
            selector={"id": "test-button", "tag_name": "button"}
        )

        result = await handle_interact_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        mock_tab.find.assert_awaited_once()


class TestManageTab:
    """Comprehensive tests for manage_tab unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and browser instance."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_browser_instance = AsyncMock()
            mock_browser_instance.instance_id = "browser-1"
            mock_browser = AsyncMock()
            mock_tab = AsyncMock()
            mock_tab.tab_id = "tab-1"
            mock_tab.page_title = AsyncMock(return_value="Test Page")
            mock_browser.new_tab = AsyncMock(return_value=mock_tab)
            mock_browser_instance.browser = mock_browser
            mock_browser_instance.tabs = {"tab-1": mock_tab}
            mock_browser_instance.active_tab_id = "tab-1"

            mock_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            yield mock_manager, mock_browser_instance, mock_browser, mock_tab

    @pytest.mark.asyncio
    async def test_create_tab(self, mock_setup):
        """Test create tab action."""
        mock_manager, mock_browser_instance, mock_browser, mock_tab = mock_setup

        input_data = ManageTabInput(
            action=TabAction.CREATE,
            browser_id="browser-1",
            url="https://example.com"
        )

        result = await handle_manage_tab(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "create"
        mock_browser.new_tab.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_tab(self, mock_setup):
        """Test close tab action."""
        mock_manager, mock_browser_instance, mock_browser, mock_tab = mock_setup
        mock_browser.close_tab = AsyncMock()

        input_data = ManageTabInput(
            action=TabAction.CLOSE,
            browser_id="browser-1",
            tab_id="tab-1"
        )

        result = await handle_manage_tab(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "close"

    @pytest.mark.asyncio
    async def test_refresh_tab(self, mock_setup):
        """Test refresh tab action."""
        mock_manager, mock_browser_instance, mock_browser, mock_tab = mock_setup
        mock_tab.reload = AsyncMock()

        input_data = ManageTabInput(
            action=TabAction.REFRESH,
            browser_id="browser-1",
            tab_id="tab-1",
            ignore_cache=True
        )

        result = await handle_manage_tab(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "refresh"

    @pytest.mark.asyncio
    async def test_activate_tab(self, mock_setup):
        """Test activate tab action."""
        mock_manager, mock_browser_instance, mock_browser, mock_tab = mock_setup
        mock_browser_instance.activate_tab = AsyncMock()

        input_data = ManageTabInput(
            action=TabAction.ACTIVATE,
            browser_id="browser-1",
            tab_id="tab-1"
        )

        result = await handle_manage_tab(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "activate"

    @pytest.mark.asyncio
    async def test_list_tabs(self, mock_setup):
        """Test list tabs action."""
        mock_manager, mock_browser_instance, mock_browser, mock_tab = mock_setup

        input_data = ManageTabInput(
            action=TabAction.LIST,
            browser_id="browser-1"
        )

        result = await handle_manage_tab(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "list"
        assert "tabs" in result_data["data"]


class TestBrowserControl:
    """Comprehensive tests for browser_control unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            yield mock_manager

    @pytest.mark.asyncio
    async def test_start_browser(self, mock_setup):
        """Test start browser action."""
        mock_manager = mock_setup

        mock_instance = AsyncMock()
        mock_instance.instance_id = "browser-1"
        mock_instance.to_dict = Mock(return_value={"browser_id": "browser-1"})
        mock_manager.create_browser = AsyncMock(return_value=mock_instance)

        input_data = BrowserControlInput(
            action=BrowserAction.START,
            browser_type="chrome",
            headless=True
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "start"
        mock_manager.create_browser.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stop_browser(self, mock_setup):
        """Test stop browser action."""
        mock_manager = mock_setup
        mock_manager.destroy_browser = AsyncMock()

        input_data = BrowserControlInput(
            action=BrowserAction.STOP,
            browser_id="browser-1"
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "stop"
        mock_manager.destroy_browser.assert_awaited_once_with("browser-1")

    @pytest.mark.asyncio
    async def test_get_state(self, mock_setup):
        """Test get_state browser action."""
        mock_manager = mock_setup

        mock_instance = AsyncMock()
        mock_instance.instance_id = "browser-1"
        mock_instance.to_dict = Mock(return_value={"browser_id": "browser-1", "status": "active"})
        mock_manager.get_browser = AsyncMock(return_value=mock_instance)

        input_data = BrowserControlInput(
            action=BrowserAction.GET_STATE,
            browser_id="browser-1"
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_state"

    @pytest.mark.asyncio
    async def test_list_browsers(self, mock_setup):
        """Test list browsers action."""
        mock_manager = mock_setup

        mock_instance = AsyncMock()
        mock_instance.instance_id = "browser-1"
        mock_instance.to_dict = Mock(return_value={"browser_id": "browser-1"})
        mock_manager.session_store.list_browsers = AsyncMock(return_value=[{
            "browser_id": "browser-1",
            "browser_type": "chrome",
            "created_at": "2024-01-01T00:00:00Z",
            "last_activity": "2024-01-01T00:00:00Z"
        }])

        input_data = BrowserControlInput(
            action=BrowserAction.LIST
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "list"
        assert "browsers" in result_data["data"]

    @pytest.mark.asyncio
    async def test_create_context(self, mock_setup):
        """Test create_context action."""
        mock_manager = mock_setup

        mock_browser_instance = AsyncMock()
        mock_browser_instance.instance_id = "browser-1"
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_context.context_id = "context-1"
        mock_browser.create_context = AsyncMock(return_value=mock_context)
        mock_browser_instance.browser = mock_browser
        mock_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

        input_data = BrowserControlInput(
            action=BrowserAction.CREATE_CONTEXT,
            browser_id="browser-1",
            context_name="test-context"
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "create_context"

    @pytest.mark.asyncio
    async def test_list_contexts(self, mock_setup):
        """Test list_contexts action."""
        mock_manager = mock_setup

        mock_browser_instance = AsyncMock()
        mock_browser_instance.instance_id = "browser-1"
        mock_browser = AsyncMock()
        mock_browser.list_contexts = AsyncMock(return_value=["context-1", "context-2"])
        mock_browser_instance.browser = mock_browser
        mock_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

        input_data = BrowserControlInput(
            action=BrowserAction.LIST_CONTEXTS,
            browser_id="browser-1"
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "list_contexts"

    @pytest.mark.asyncio
    async def test_delete_context(self, mock_setup):
        """Test delete_context action."""
        mock_manager = mock_setup

        mock_browser_instance = AsyncMock()
        mock_browser_instance.instance_id = "browser-1"
        mock_browser = AsyncMock()
        mock_browser.delete_context = AsyncMock()
        mock_browser_instance.browser = mock_browser
        mock_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

        input_data = BrowserControlInput(
            action=BrowserAction.DELETE_CONTEXT,
            browser_id="browser-1",
            context_id="context-1"
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "delete_context"

    @pytest.mark.asyncio
    async def test_grant_permissions(self, mock_setup):
        """Test grant_permissions action."""
        mock_manager = mock_setup

        mock_browser_instance = AsyncMock()
        mock_browser_instance.instance_id = "browser-1"
        mock_browser = AsyncMock()
        mock_browser.grant_permissions = AsyncMock()
        mock_browser_instance.browser = mock_browser
        mock_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

        input_data = BrowserControlInput(
            action=BrowserAction.GRANT_PERMISSIONS,
            browser_id="browser-1",
            origin="https://example.com",
            permissions=["geolocation", "notifications"]
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "grant_permissions"

    @pytest.mark.asyncio
    async def test_reset_permissions(self, mock_setup):
        """Test reset_permissions action."""
        mock_manager = mock_setup

        mock_browser_instance = AsyncMock()
        mock_browser_instance.instance_id = "browser-1"
        mock_browser = AsyncMock()
        mock_browser.reset_permissions = AsyncMock()
        mock_browser_instance.browser = mock_browser
        mock_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

        input_data = BrowserControlInput(
            action=BrowserAction.RESET_PERMISSIONS,
            browser_id="browser-1",
            origin="https://example.com"
        )

        result = await handle_browser_control(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "reset_permissions"


class TestNavigatePage:
    """Comprehensive tests for navigate_page unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_tab.url = "https://example.com"
            mock_tab.page_title = AsyncMock(return_value="Example Page")
            mock_tab.page_source = AsyncMock(return_value="<html>...</html>")
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab

    @pytest.mark.asyncio
    async def test_navigate_action(self, mock_setup):
        """Test navigate action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.go_to = AsyncMock()

        input_data = NavigatePageInput(
            action=NavigationAction.NAVIGATE,
            browser_id="browser-1",
            url="https://example.com"
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "navigate"
        mock_tab.go_to.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_go_back_action(self, mock_setup):
        """Test go_back action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.go_back = AsyncMock()

        input_data = NavigatePageInput(
            action=NavigationAction.GO_BACK,
            browser_id="browser-1"
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "go_back"
        mock_tab.go_back.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_go_forward_action(self, mock_setup):
        """Test go_forward action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.go_forward = AsyncMock()

        input_data = NavigatePageInput(
            action=NavigationAction.GO_FORWARD,
            browser_id="browser-1"
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "go_forward"
        mock_tab.go_forward.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_url_action(self, mock_setup):
        """Test get_url action."""
        mock_manager, mock_tab = mock_setup

        input_data = NavigatePageInput(
            action=NavigationAction.GET_URL,
            browser_id="browser-1"
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_url"
        assert "url" in result_data["data"]

    @pytest.mark.asyncio
    async def test_get_title_action(self, mock_setup):
        """Test get_title action."""
        mock_manager, mock_tab = mock_setup

        input_data = NavigatePageInput(
            action=NavigationAction.GET_TITLE,
            browser_id="browser-1"
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_title"
        assert "title" in result_data["data"]

    @pytest.mark.asyncio
    async def test_get_source_action(self, mock_setup):
        """Test get_source action."""
        mock_manager, mock_tab = mock_setup

        input_data = NavigatePageInput(
            action=NavigationAction.GET_SOURCE,
            browser_id="browser-1"
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_source"
        assert "source" in result_data["data"]

    @pytest.mark.asyncio
    async def test_wait_load_action(self, mock_setup):
        """Test wait_load action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.wait_for_load = AsyncMock()

        input_data = NavigatePageInput(
            action=NavigationAction.WAIT_LOAD,
            browser_id="browser-1",
            timeout=10
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "wait_load"

    @pytest.mark.asyncio
    async def test_wait_network_idle_action(self, mock_setup):
        """Test wait_network_idle action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.wait_for_network_idle = AsyncMock()

        input_data = NavigatePageInput(
            action=NavigationAction.WAIT_NETWORK_IDLE,
            browser_id="browser-1",
            timeout=10
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "wait_network_idle"

    @pytest.mark.asyncio
    async def test_set_viewport_action(self, mock_setup):
        """Test set_viewport action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.set_viewport = AsyncMock()

        input_data = NavigatePageInput(
            action=NavigationAction.SET_VIEWPORT,
            browser_id="browser-1",
            width=1920,
            height=1080
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "set_viewport"
        mock_tab.set_viewport.assert_awaited_once_with(1920, 1080)

    @pytest.mark.asyncio
    async def test_get_info_action(self, mock_setup):
        """Test get_info action."""
        mock_manager, mock_tab = mock_setup

        input_data = NavigatePageInput(
            action=NavigationAction.GET_INFO,
            browser_id="browser-1"
        )

        result = await handle_navigate_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_info"
        assert "info" in result_data["data"]


class TestCaptureMedia:
    """Comprehensive tests for capture_media unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab

    @pytest.mark.asyncio
    async def test_screenshot_action(self, mock_setup):
        """Test screenshot action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.screenshot = AsyncMock(return_value=b"fake_image_data")

        input_data = CaptureMediaInput(
            action=ScreenshotAction.SCREENSHOT,
            browser_id="browser-1",
            format="png",
            save_to_file=False,
            return_base64=True
        )

        result = await handle_capture_media(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "screenshot"

    @pytest.mark.asyncio
    async def test_element_screenshot_action(self, mock_setup):
        """Test element_screenshot action."""
        mock_manager, mock_tab = mock_setup

        mock_element = AsyncMock()
        mock_element.screenshot = AsyncMock(return_value=b"fake_image_data")
        mock_tab.query = AsyncMock(return_value=mock_element)

        input_data = CaptureMediaInput(
            action=ScreenshotAction.ELEMENT_SCREENSHOT,
            browser_id="browser-1",
            selector={"css_selector": "div"},
            format="png"
        )

        result = await handle_capture_media(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "element_screenshot"

    @pytest.mark.asyncio
    async def test_generate_pdf_action(self, mock_setup):
        """Test generate_pdf action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.pdf = AsyncMock(return_value=b"fake_pdf_data")

        input_data = CaptureMediaInput(
            action=ScreenshotAction.GENERATE_PDF,
            browser_id="browser-1",
            pdf_format="A4",
            orientation="portrait"
        )

        result = await handle_capture_media(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "generate_pdf"

    @pytest.mark.asyncio
    async def test_save_page_as_pdf_action(self, mock_setup):
        """Test save_page_as_pdf action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.print_to_pdf = AsyncMock(return_value="base64_pdf_data")

        input_data = CaptureMediaInput(
            action=ScreenshotAction.SAVE_PAGE_AS_PDF,
            browser_id="browser-1"
        )

        result = await handle_capture_media(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "save_page_as_pdf"
        assert "pdf_data" in result_data["data"]

    @pytest.mark.asyncio
    async def test_save_pdf_action(self, mock_setup):
        """Test save_pdf action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.print_to_pdf = AsyncMock(return_value="base64_pdf_data")

        input_data = CaptureMediaInput(
            action=ScreenshotAction.SAVE_PDF,
            browser_id="browser-1",
            pdf_format="A4",
            print_background=True
        )

        result = await handle_capture_media(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "save_pdf"
        assert "pdf_data" in result_data["data"]

    @pytest.mark.asyncio
    async def test_save_pdf_with_file_path(self, mock_setup, tmp_path):
        """Test save_pdf action with file path."""
        mock_manager, mock_tab = mock_setup
        import base64
        pdf_bytes = b"fake_pdf_content"
        mock_tab.print_to_pdf = AsyncMock(return_value=base64.b64encode(pdf_bytes).decode())

        pdf_file = tmp_path / "test.pdf"
        input_data = CaptureMediaInput(
            action=ScreenshotAction.SAVE_PDF,
            browser_id="browser-1",
            file_path=str(pdf_file)
        )

        result = await handle_capture_media(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert "file_path" in result_data["data"]


class TestExecuteScript:
    """Comprehensive tests for execute_script unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab

    @pytest.mark.asyncio
    async def test_execute_action(self, mock_setup):
        """Test execute action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.execute_script = AsyncMock(return_value={"result": {"value": "success"}})

        input_data = ExecuteScriptInput(
            action=ScriptAction.EXECUTE,
            browser_id="browser-1",
            script="console.log('test');"
        )

        result = await handle_execute_script(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "execute"
        mock_tab.execute_script.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_evaluate_action(self, mock_setup):
        """Test evaluate action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.evaluate = AsyncMock(return_value={"result": {"value": 42}})

        input_data = ExecuteScriptInput(
            action=ScriptAction.EVALUATE,
            browser_id="browser-1",
            expression="2 + 2"
        )

        result = await handle_execute_script(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "evaluate"

    @pytest.mark.asyncio
    async def test_inject_action(self, mock_setup):
        """Test inject action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.inject_script = AsyncMock()

        input_data = ExecuteScriptInput(
            action=ScriptAction.INJECT,
            browser_id="browser-1",
            library="jquery"
        )

        result = await handle_execute_script(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "inject"

    @pytest.mark.asyncio
    async def test_get_console_logs_action(self, mock_setup):
        """Test get_console_logs action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.get_console_logs = AsyncMock(return_value=[{"level": "info", "message": "test"}])

        input_data = ExecuteScriptInput(
            action=ScriptAction.GET_CONSOLE_LOGS,
            browser_id="browser-1"
        )

        result = await handle_execute_script(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_console_logs"
        assert "logs" in result_data["data"]


class TestManageFile:
    """Comprehensive tests for manage_file unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab

    @pytest.mark.asyncio
    async def test_upload_action(self, mock_setup, tmp_path):
        """Test upload action."""
        mock_manager, mock_tab = mock_setup

        # Create a temporary file for upload
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")

        mock_element = AsyncMock()
        mock_tab.query = AsyncMock(return_value=mock_element)
        mock_element.upload_file = AsyncMock()

        input_data = ManageFileInput(
            action=FileAction.UPLOAD,
            browser_id="browser-1",
            file_path=str(test_file),
            input_selector={"css_selector": "input[type='file']"}
        )

        result = await handle_manage_file(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "upload"

    @pytest.mark.asyncio
    async def test_download_action(self, mock_setup):
        """Test download action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.download = AsyncMock(return_value={"download_id": "download-1"})

        input_data = ManageFileInput(
            action=FileAction.DOWNLOAD,
            browser_id="browser-1",
            url="https://example.com/file.pdf",
            save_path="/path/to/save"
        )

        result = await handle_manage_file(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "download"

    @pytest.mark.asyncio
    async def test_manage_downloads_list(self, mock_setup):
        """Test manage_downloads list action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.list_downloads = AsyncMock(return_value=[{"id": "download-1", "status": "completed"}])

        input_data = ManageFileInput(
            action=FileAction.MANAGE_DOWNLOADS,
            browser_id="browser-1",
            download_action="list"
        )

        result = await handle_manage_file(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "manage_downloads"


class TestFindElement:
    """Comprehensive tests for find_element unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_element = AsyncMock()
            mock_element.text = "Test Element"
            mock_element.get_attribute = AsyncMock(return_value="test-value")
            mock_tab.find = AsyncMock(return_value=mock_element)
            mock_tab.find_all = AsyncMock(return_value=[mock_element, mock_element])
            mock_tab.query = AsyncMock(return_value=mock_element)
            mock_tab.query_all = AsyncMock(return_value=[mock_element])
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab, mock_element

    @pytest.mark.asyncio
    async def test_find_action(self, mock_setup):
        """Test find action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = FindElementInput(
            action=ElementFindAction.FIND,
            browser_id="browser-1",
            selector={"css_selector": "button"}
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "find"
        assert "element" in result_data["data"]

    @pytest.mark.asyncio
    async def test_find_all_action(self, mock_setup):
        """Test find_all action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = FindElementInput(
            action=ElementFindAction.FIND_ALL,
            browser_id="browser-1",
            selector={"css_selector": "button"}
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "find_all"
        assert "elements" in result_data["data"]

    @pytest.mark.asyncio
    async def test_query_action(self, mock_setup):
        """Test query action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = FindElementInput(
            action=ElementFindAction.QUERY,
            browser_id="browser-1",
            selector={"css_selector": "button.test"},
            css_selector="button.test"
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "query"

    @pytest.mark.asyncio
    async def test_wait_for_action(self, mock_setup):
        """Test wait_for action."""
        mock_manager, mock_tab, mock_element = mock_setup
        mock_tab.wait_for_selector = AsyncMock(return_value=mock_element)

        input_data = FindElementInput(
            action=ElementFindAction.WAIT_FOR,
            browser_id="browser-1",
            selector={"css_selector": "button"},
            timeout=10
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "wait_for"

    @pytest.mark.asyncio
    async def test_get_text_action(self, mock_setup):
        """Test get_text action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = FindElementInput(
            action=ElementFindAction.GET_TEXT,
            browser_id="browser-1",
            selector={"css_selector": "button"}
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_text"
        assert "text" in result_data["data"]

    @pytest.mark.asyncio
    async def test_get_attribute_action(self, mock_setup):
        """Test get_attribute action."""
        mock_manager, mock_tab, mock_element = mock_setup

        input_data = FindElementInput(
            action=ElementFindAction.GET_ATTRIBUTE,
            browser_id="browser-1",
            selector={"css_selector": "button"},
            attribute_name="id"
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_attribute"
        assert "attribute_value" in result_data["data"]

    @pytest.mark.asyncio
    async def test_check_visibility_action(self, mock_setup):
        """Test check_visibility action."""
        mock_manager, mock_tab, mock_element = mock_setup
        mock_element.is_visible = AsyncMock(return_value=True)

        input_data = FindElementInput(
            action=ElementFindAction.CHECK_VISIBILITY,
            browser_id="browser-1",
            selector={"css_selector": "button"}
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "check_visibility"
        assert "visible" in result_data["data"]

    @pytest.mark.asyncio
    async def test_get_parent_action(self, mock_setup):
        """Test get_parent action."""
        mock_manager, mock_tab, mock_element = mock_setup
        mock_parent = AsyncMock()
        mock_element.parent = mock_parent

        input_data = FindElementInput(
            action=ElementFindAction.GET_PARENT,
            browser_id="browser-1",
            selector={"css_selector": "button"}
        )

        result = await handle_find_element(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "get_parent"


class TestInteractPage:
    """Comprehensive tests for interact_page unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab

    @pytest.mark.asyncio
    async def test_handle_dialog_accept(self, mock_setup):
        """Test handle_dialog action with accept."""
        mock_manager, mock_tab = mock_setup
        mock_tab.handle_dialog = AsyncMock()

        input_data = InteractPageInput(
            action=DialogAction.HANDLE_DIALOG,
            browser_id="browser-1",
            accept=True,
            prompt_text="test"
        )

        result = await handle_interact_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "handle_dialog"

    @pytest.mark.asyncio
    async def test_handle_dialog_dismiss(self, mock_setup):
        """Test handle_dialog action with dismiss."""
        mock_manager, mock_tab = mock_setup
        mock_tab.handle_dialog = AsyncMock()

        input_data = InteractPageInput(
            action=DialogAction.HANDLE_DIALOG,
            browser_id="browser-1",
            accept=False
        )

        result = await handle_interact_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True

    @pytest.mark.asyncio
    async def test_handle_alert(self, mock_setup):
        """Test handle_alert action."""
        mock_manager, mock_tab = mock_setup
        mock_tab.handle_alert = AsyncMock()

        input_data = InteractPageInput(
            action=DialogAction.HANDLE_ALERT,
            browser_id="browser-1",
            accept=True
        )

        result = await handle_interact_page(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        assert result_data["data"]["action"] == "handle_alert"


class TestExecuteCDP:
    """Comprehensive tests for execute_cdp_command unified tool."""

    @pytest.fixture
    def mock_setup(self):
        """Setup mock browser manager and tab."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_tab.execute_cdp_command = AsyncMock(return_value={"result": "success"})
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            yield mock_manager, mock_tab

    @pytest.mark.asyncio
    async def test_execute_cdp_command(self, mock_setup):
        """Test execute CDP command."""
        mock_manager, mock_tab = mock_setup

        input_data = ExecuteCDPInput(
            browser_id="browser-1",
            domain="Page",
            method="navigate",
            params={"url": "https://example.com"}
        )

        result = await handle_execute_cdp(input_data)
        result_data = json.loads(result[0].text)
        assert result_data["success"] is True
        mock_tab.execute_cdp_command.assert_awaited_once_with("Page.navigate", {"url": "https://example.com"})


class TestErrorHandling:
    """Comprehensive error handling tests for unified tools."""

    @pytest.mark.asyncio
    async def test_invalid_browser_id(self):
        """Test handling of invalid browser ID."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_tab_with_fallback = AsyncMock(side_effect=ValueError("Browser not found"))
            mock_get_manager.return_value = mock_manager

            input_data = InteractElementInput(
                action=ElementAction.CLICK,
                browser_id="invalid-browser",
                selector={"css_selector": "button"}
            )

            result = await handle_interact_element(input_data)
            result_data = json.loads(result[0].text)
            assert result_data["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_tab_id(self):
        """Test handling of invalid tab ID."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_tab_with_fallback = AsyncMock(side_effect=ValueError("Tab not found"))
            mock_get_manager.return_value = mock_manager

            input_data = NavigatePageInput(
                action=NavigationAction.GET_URL,
                browser_id="browser-1",
                tab_id="invalid-tab"
            )

            result = await handle_navigate_page(input_data)
            result_data = json.loads(result[0].text)
            assert result_data["success"] is False

    @pytest.mark.asyncio
    async def test_missing_required_parameters(self):
        """Test handling of missing required parameters."""
        # Test with missing browser_id
        with pytest.raises(Exception):  # Pydantic validation should raise
            InteractElementInput(
                action=ElementAction.CLICK,
                selector={"css_selector": "button"}
                # browser_id missing
            )

    @pytest.mark.asyncio
    async def test_script_execution_error(self):
        """Test handling of script execution errors."""
        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_tab.execute_script = AsyncMock(side_effect=Exception("Script error"))
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))
            mock_get_manager.return_value = mock_manager

            input_data = ExecuteScriptInput(
                action=ScriptAction.EXECUTE,
                browser_id="browser-1",
                script="invalid javascript"
            )

            result = await handle_execute_script(input_data)
            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "error" in result_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

