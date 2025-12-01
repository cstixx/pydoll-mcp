"""Tests for new PyDoll 2.12.4+ features and enhanced tools.


This test suite covers:
- Tab management (bring_tab_to_front)
- Download configuration tools
- File chooser interception
- Network monitoring enhancements
- Cloudflare captcha tools
- Unified tools (replacing legacy alert/dialog, file upload/download, PDF saving)
"""

from pydoll_mcp.tools.element_tools import (
    handle_find_or_wait_element,
    handle_query,
    handle_press_key
)
import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from mcp.types import TextContent

from pydoll_mcp.tools.page_tools import (
    PAGE_TOOL_HANDLERS
)
from pydoll_mcp.tools.browser_tools import (
    handle_bring_tab_to_front,
    handle_set_download_behavior,
    handle_set_download_path,
    handle_enable_file_chooser_interception,
    handle_disable_file_chooser_interception,
    BROWSER_TOOL_HANDLERS
)
from pydoll_mcp.tools.file_tools import (
    FILE_TOOL_HANDLERS
)
from pydoll_mcp.tools.network_tools import (
    handle_get_network_logs,
    handle_get_network_response_body,
    NETWORK_TOOL_HANDLERS
)
from pydoll_mcp.tools.protection_tools import (
    handle_bypass_cloudflare,
    handle_enable_cloudflare_auto_solve,
    handle_disable_cloudflare_auto_solve,
    PROTECTION_TOOL_HANDLERS
)
from pydoll_mcp.tools import (
    UNIFIED_TOOLS,
    UNIFIED_TOOL_HANDLERS
)
from pydoll_mcp.tools.navigation_tools import (
    handle_scroll,
    handle_get_frame,
    NAVIGATION_TOOL_HANDLERS
)
# Note: create_browser_context, grant_permissions, reset_permissions handlers removed
# Use unified browser_control tool instead
from pydoll_mcp.tools.network_tools import (
    handle_enable_dom_events,
    handle_disable_dom_events,
    handle_enable_network_events,
    handle_disable_network_events,
    handle_enable_page_events,
    handle_disable_page_events,
    handle_enable_fetch_events,
    handle_disable_fetch_events,
    handle_enable_runtime_events,
    handle_disable_runtime_events,
    handle_get_event_status,
    handle_modify_request,
    handle_fulfill_request,
    handle_continue_with_auth,
)


# Note: TestAlertDialogHandling and TestPDFSaving removed
# These tools (handle_alert, handle_dialog, save_pdf) are now in unified tools:
# - Use interact_page tool for dialogs
# - Use capture_media tool for PDFs


class TestTabManagement:
    """Test tab management enhancements."""

    @pytest.mark.asyncio
    async def test_bring_tab_to_front(self):
        """Test bring_tab_to_front tool."""
        with patch('pydoll_mcp.tools.browser_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            mock_browser_instance.tabs = {"tab-1": mock_tab}
            mock_browser_instance.active_tab_id = None

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_bring_tab_to_front({
                "browser_id": "browser-1",
                "tab_id": "tab-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["tab_id"] == "tab-1"
            mock_tab.bring_to_front.assert_awaited_once()
            assert mock_browser_instance.active_tab_id == "tab-1"


class TestDownloadConfiguration:
    """Test download configuration tools."""

    @pytest.mark.asyncio
    async def test_set_download_behavior(self):
        """Test set_download_behavior tool."""
        with patch('pydoll_mcp.tools.browser_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_browser = AsyncMock()

            mock_browser_instance.browser = mock_browser
            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_set_download_behavior({
                "browser_id": "browser-1",
                "behavior": "allow"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["behavior"] == "allow"
            mock_browser.set_download_behavior.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_download_path(self):
        """Test set_download_path tool."""
        with patch('pydoll_mcp.tools.browser_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_browser = AsyncMock()

            mock_browser_instance.browser = mock_browser
            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            with tempfile.TemporaryDirectory() as tmpdir:
                result = await handle_set_download_path({
                    "browser_id": "browser-1",
                    "path": tmpdir
                })

                assert len(result) == 1
                result_data = json.loads(result[0].text)
                assert result_data["success"] is True
                assert "path" in result_data["data"]
                mock_browser.set_download_path.assert_awaited_once()


class TestFileChooserInterception:
    """Test file chooser interception tools."""

    @pytest.mark.asyncio
    async def test_enable_file_chooser_interception(self):
        """Test enable_file_chooser_interception tool."""
        with patch('pydoll_mcp.tools.browser_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_intercept_file_chooser_dialog = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_enable_file_chooser_interception({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            mock_tab.enable_intercept_file_chooser_dialog.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_disable_file_chooser_interception(self):
        """Test disable_file_chooser_interception tool."""
        with patch('pydoll_mcp.tools.browser_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.disable_intercept_file_chooser_dialog = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_disable_file_chooser_interception({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            mock_tab.disable_intercept_file_chooser_dialog.assert_awaited_once()


class TestFileUploadDownload:
    """Test file upload and download with real PyDoll APIs."""

    @pytest.mark.asyncio
    async def test_upload_file(self):
        """Test file upload using expect_file_chooser."""
        with patch('pydoll_mcp.tools.file_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_element = AsyncMock()

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
                tmp_file.write(b"test content")
                tmp_path = tmp_file.name

            try:
                # Mock file chooser generator
                async def file_chooser_gen():
                    yield None

                mock_tab.expect_file_chooser = MagicMock(return_value=file_chooser_gen())
                mock_tab.find = AsyncMock(return_value=mock_element)
                mock_element.click = AsyncMock()

                mock_manager.return_value = mock_browser_manager
                mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

                result = await handle_upload_file({
                    "browser_id": "browser-1",
                    "file_path": tmp_path,
                    "input_selector": {"css_selector": "input[type='file']"}
                })

                assert len(result) == 1
                result_data = json.loads(result[0].text)
                assert result_data["success"] is True
                assert result_data["data"]["upload_status"] == "completed"
                mock_tab.expect_file_chooser.assert_called_once()
                mock_element.click.assert_awaited_once()
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_download_file(self):
        """Test file download using expect_download."""
        with patch('pydoll_mcp.tools.file_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_tab = AsyncMock()

            # Mock download object
            mock_download = Mock()
            mock_download.filename = "test.pdf"
            mock_download.path = Path("/tmp/test.pdf")
            mock_download.size = 1024
            mock_download.id = "dl-123"

            async def download_gen():
                yield mock_download

            mock_tab.expect_download = MagicMock(return_value=download_gen())
            mock_tab.go_to = AsyncMock()
            mock_browser_instance.browser = mock_browser
            mock_browser.set_download_behavior = AsyncMock()
            mock_browser.set_download_path = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_download_file({
                "browser_id": "browser-1",
                "url": "https://example.com/file.pdf",
                "wait_for_completion": True
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["status"] == "completed"
            mock_tab.expect_download.assert_called_once()


class TestNetworkMonitoring:
    """Test network monitoring enhancements."""

    @pytest.mark.asyncio
    async def test_get_network_logs(self):
        """Test get_network_logs with real API."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            # Mock network log entries
            mock_log1 = Mock()
            mock_log1.url = "https://example.com/api"
            mock_log1.method = "GET"
            mock_log1.status = 200
            mock_log1.type = "xhr"
            mock_log1.size = 1024
            mock_log1.time = 123.45
            mock_log1.request_id = "req-1"

            mock_log2 = Mock()
            mock_log2.url = "https://example.com/style.css"
            mock_log2.method = "GET"
            mock_log2.status = 200
            mock_log2.type = "stylesheet"
            mock_log2.size = 2048
            mock_log2.time = 45.67
            mock_log2.request_id = "req-2"

            mock_tab.get_network_logs = AsyncMock(return_value=[mock_log1, mock_log2])

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_get_network_logs({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["count"] == 2
            assert len(result_data["data"]["logs"]) == 2
            assert result_data["data"]["logs"][0]["url"] == "https://example.com/api"
            mock_tab.get_network_logs.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_network_response_body(self):
        """Test get_network_response_body tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.get_network_response_body = AsyncMock(return_value='{"key": "value"}')

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_get_network_response_body({
                "browser_id": "browser-1",
                "request_id": "req-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert "response_body" in result_data["data"]
            mock_tab.get_network_response_body.assert_awaited_once_with(request_id="req-1")


class TestCloudflareCaptcha:
    """Test Cloudflare captcha bypass tools."""

    @pytest.mark.asyncio
    async def test_enable_cloudflare_auto_solve(self):
        """Test enable_cloudflare_auto_solve tool."""
        with patch('pydoll_mcp.tools.protection_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_auto_solve_cloudflare_captcha = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_enable_cloudflare_auto_solve({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            mock_tab.enable_auto_solve_cloudflare_captcha.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_disable_cloudflare_auto_solve(self):
        """Test disable_cloudflare_auto_solve tool."""
        with patch('pydoll_mcp.tools.protection_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.disable_auto_solve_cloudflare_captcha = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_disable_cloudflare_auto_solve({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            mock_tab.disable_auto_solve_cloudflare_captcha.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_bypass_cloudflare(self):
        """Test bypass_cloudflare with auto-solve."""
        with patch('pydoll_mcp.tools.protection_tools.get_browser_manager') as mock_manager:
            import asyncio
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_auto_solve_cloudflare_captcha = AsyncMock()

            # Mock expect_and_bypass_cloudflare_captcha generator
            async def bypass_gen():
                yield None

            mock_tab.expect_and_bypass_cloudflare_captcha = MagicMock(return_value=bypass_gen())

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_bypass_cloudflare({
                "browser_id": "browser-1",
                "auto_solve": True,
                "max_attempts": 3
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["bypass_method"] == "auto_solve_cloudflare_captcha"
            mock_tab.enable_auto_solve_cloudflare_captcha.assert_awaited_once()


class TestToolRegistration:
    """Test that all new tools are properly registered."""

    def test_page_tool_handlers_registered(self):
        """Test that page tools are registered."""
        # Note: handle_alert, handle_dialog, save_pdf removed - use unified tools instead
        # PAGE_TOOLS is now empty as all tools moved to unified tools
        assert isinstance(PAGE_TOOL_HANDLERS, dict)

    def test_browser_tool_handlers_registered(self):
        """Test that new browser tools are registered."""
        assert "bring_tab_to_front" in BROWSER_TOOL_HANDLERS
        assert "set_download_behavior" in BROWSER_TOOL_HANDLERS
        assert "set_download_path" in BROWSER_TOOL_HANDLERS
        assert "enable_file_chooser_interception" in BROWSER_TOOL_HANDLERS
        assert "disable_file_chooser_interception" in BROWSER_TOOL_HANDLERS

    def test_network_tool_handlers_registered(self):
        """Test that new network tools are registered."""
        assert "get_network_response_body" in NETWORK_TOOL_HANDLERS

    def test_protection_tool_handlers_registered(self):
        """Test that new protection tools are registered."""
        assert "enable_cloudflare_auto_solve" in PROTECTION_TOOL_HANDLERS
        assert "disable_cloudflare_auto_solve" in PROTECTION_TOOL_HANDLERS

    def test_element_tool_handlers_registered(self):
        """Test that element tools are registered in unified tools."""
        # Element tools are now in unified tools (find_element, interact_element)
        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
        assert "find_element" in unified_tool_names
        assert "interact_element" in unified_tool_names

        # Check that unified tool handlers are registered
        assert "find_element" in UNIFIED_TOOL_HANDLERS
        assert "interact_element" in UNIFIED_TOOL_HANDLERS

        # Verify that find_element supports wait functionality (find_or_wait_element replacement)
        find_tool = next(t for t in UNIFIED_TOOLS if t.name == "find_element")
        assert "action" in find_tool.inputSchema["properties"]
        assert "wait_for" in find_tool.inputSchema["properties"]["action"]["enum"]

        # Verify that interact_element supports press_key functionality
        interact_tool = next(t for t in UNIFIED_TOOLS if t.name == "interact_element")
        assert "action" in interact_tool.inputSchema["properties"]
        assert "press_key" in interact_tool.inputSchema["properties"]["action"]["enum"]

    def test_navigation_tool_handlers_registered(self):
        """Test that new navigation tools are registered."""
        assert "scroll" in NAVIGATION_TOOL_HANDLERS
        assert "get_frame" in NAVIGATION_TOOL_HANDLERS

    def test_browser_context_handlers_registered(self):
        """Test that browser context tools are registered."""
        # Browser context tools are now in unified browser_control tool
        browser_control_tool = next(t for t in UNIFIED_TOOLS if t.name == "browser_control")
        assert browser_control_tool is not None

        # Check that browser_control supports context and permissions actions
        action_enum = browser_control_tool.inputSchema["properties"]["action"]["enum"]
        assert "create_context" in action_enum
        assert "list_contexts" in action_enum
        assert "delete_context" in action_enum
        assert "grant_permissions" in action_enum
        assert "reset_permissions" in action_enum

        # Note: Legacy handlers removed from public API - use unified browser_control tool instead
        # Handler functions still exist internally for unified tools to use

    def test_network_event_handlers_registered(self):
        """Test that event control tools are registered."""
        assert "enable_dom_events" in NETWORK_TOOL_HANDLERS
        assert "disable_dom_events" in NETWORK_TOOL_HANDLERS
        assert "enable_network_events" in NETWORK_TOOL_HANDLERS
        assert "disable_network_events" in NETWORK_TOOL_HANDLERS
        assert "enable_page_events" in NETWORK_TOOL_HANDLERS
        assert "disable_page_events" in NETWORK_TOOL_HANDLERS
        assert "enable_fetch_events" in NETWORK_TOOL_HANDLERS
        assert "disable_fetch_events" in NETWORK_TOOL_HANDLERS
        assert "enable_runtime_events" in NETWORK_TOOL_HANDLERS
        assert "disable_runtime_events" in NETWORK_TOOL_HANDLERS
        assert "get_event_status" in NETWORK_TOOL_HANDLERS
        assert "modify_request" in NETWORK_TOOL_HANDLERS
        assert "fulfill_request" in NETWORK_TOOL_HANDLERS
        assert "continue_with_auth" in NETWORK_TOOL_HANDLERS


class TestElementFindingEnhancements:
    """Test element finding enhancements."""

    @pytest.mark.asyncio
    async def test_find_or_wait_element_success(self):
        """Test find_or_wait_element when element is found."""
        with patch('pydoll_mcp.tools.element_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_element = Mock()
            mock_element.tag_name = "button"
            mock_element.text = "Click Me"
            mock_element.id = "btn-1"
            mock_element.class_name = "primary"
            mock_element.name = None
            mock_element.type = None
            mock_element.href = None

            # Element found on first try
            mock_tab.find = AsyncMock(return_value=mock_element)

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_find_or_wait_element({
                "browser_id": "browser-1",
                "id": "btn-1",
                "timeout": 30,
                "poll_interval": 0.5
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["element"]["id"] == "btn-1"
            assert result_data["data"]["element"]["tag_name"] == "button"

    @pytest.mark.asyncio
    async def test_find_or_wait_element_timeout(self):
        """Test find_or_wait_element when element is not found (timeout)."""
        with patch('pydoll_mcp.tools.element_tools.get_browser_manager') as mock_manager:
            import asyncio
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            # Element never found
            mock_tab.find = AsyncMock(return_value=None)

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_find_or_wait_element({
                "browser_id": "browser-1",
                "id": "non-existent",
                "timeout": 1,  # Short timeout for testing
                "poll_interval": 0.1
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is False
            assert "timeout" in result_data["error"].lower() or "not found" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_query_css_selector(self):
        """Test query tool with CSS selector."""
        with patch('pydoll_mcp.tools.element_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_element = Mock()
            mock_element.tag_name = "div"
            mock_element.text = "Test Content"
            mock_element.id = "test-div"
            mock_element.class_name = "container"
            mock_element.name = None
            mock_element.type = None
            mock_element.href = None

            mock_tab.query = AsyncMock(return_value=mock_element)

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_query({
                "browser_id": "browser-1",
                "css_selector": ".container",
                "find_all": False
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["count"] == 1
            assert result_data["data"]["selector_type"] == "css"
            mock_tab.query.assert_awaited_once_with(".container")

    @pytest.mark.asyncio
    async def test_query_xpath(self):
        """Test query tool with XPath."""
        with patch('pydoll_mcp.tools.element_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_element = Mock()
            mock_element.tag_name = "button"
            mock_element.text = "Submit"
            mock_element.id = "submit-btn"
            mock_element.class_name = None
            mock_element.name = None
            mock_element.type = None
            mock_element.href = None

            mock_tab.query = AsyncMock(return_value=mock_element)

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_query({
                "browser_id": "browser-1",
                "xpath": "//button[@id='submit-btn']",
                "find_all": False
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["selector_type"] == "xpath"
            mock_tab.query.assert_awaited_once_with("//button[@id='submit-btn']")

    @pytest.mark.asyncio
    async def test_press_key_single_key(self):
        """Test press_key with a single key."""
        with patch('pydoll_mcp.tools.element_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_keyboard = AsyncMock()
            mock_tab.keyboard = mock_keyboard

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_press_key({
                "browser_id": "browser-1",
                "key": "Enter"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["key"] == "Enter"
            mock_keyboard.press.assert_awaited_once_with("Enter")

    @pytest.mark.asyncio
    async def test_press_key_combination(self):
        """Test press_key with key combination."""
        with patch('pydoll_mcp.tools.element_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_keyboard = AsyncMock()
            mock_tab.keyboard = mock_keyboard

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_press_key({
                "browser_id": "browser-1",
                "key": "Control+c"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            # Verify keyboard API was used
            assert mock_keyboard.down.called or mock_keyboard.press.called

    @pytest.mark.asyncio
    async def test_press_key_with_element_focus(self):
        """Test press_key with element selector to focus first."""
        with patch('pydoll_mcp.tools.element_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_element = AsyncMock()
            mock_keyboard = AsyncMock()
            mock_tab.keyboard = mock_keyboard
            mock_tab.query = AsyncMock(return_value=mock_element)

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_press_key({
                "browser_id": "browser-1",
                "key": "Enter",
                "element_selector": {"css_selector": "input"}
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["element_focused"] is True
            mock_element.click.assert_awaited_once()


class TestNavigationEnhancements:
    """Test navigation enhancements."""

    @pytest.mark.asyncio
    async def test_scroll_down(self):
        """Test scroll tool with down direction."""
        with patch('pydoll_mcp.tools.navigation_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.execute_script = AsyncMock(return_value={
                'result': {
                    'result': {
                        'value': {'x': 0, 'y': 500}
                    }
                }
            })

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_scroll({
                "browser_id": "browser-1",
                "direction": "down",
                "amount": 500
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["direction"] == "down"
            assert result_data["data"]["amount"] == 500
            mock_tab.execute_script.assert_awaited()

    @pytest.mark.asyncio
    async def test_scroll_to_element(self):
        """Test scroll tool with to_element direction."""
        with patch('pydoll_mcp.tools.navigation_tools.get_browser_manager') as mock_manager, \
             patch('pydoll_mcp.tools.element_tools.handle_find_element') as mock_find:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()
            mock_element = AsyncMock()

            # Mock find_element result
            from pydoll_mcp.models import OperationResult
            find_result = OperationResult(
                success=True,
                data={"elements": [{"id": "target", "tag_name": "div"}]}
            )
            mock_find.return_value = [TextContent(type="text", text=find_result.json())]

            mock_tab.query = AsyncMock(return_value=mock_element)
            mock_tab.execute_script = AsyncMock(return_value={
                'result': {
                    'result': {
                        'value': {'x': 0, 'y': 1000}
                    }
                }
            })

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_scroll({
                "browser_id": "browser-1",
                "direction": "to_element",
                "element_selector": {"css_selector": "#target"}
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["direction"] == "to_element"
            mock_element.scroll_into_view.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_scroll_to_position(self):
        """Test scroll tool with to_position direction."""
        with patch('pydoll_mcp.tools.navigation_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.execute_script = AsyncMock(return_value={
                'result': {
                    'result': {
                        'value': {'x': 100, 'y': 200}
                    }
                }
            })

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_scroll({
                "browser_id": "browser-1",
                "direction": "to_position",
                "x": 100,
                "y": 200
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["direction"] == "to_position"
            mock_tab.execute_script.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_frame_css_selector(self):
        """Test get_frame tool with CSS selector."""
        with patch('pydoll_mcp.tools.navigation_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            # Mock execute_script - first call finds frame element, second call gets frame info
            frame_element_result = {
                'result': {
                    'result': {
                        'value': {'tagName': 'IFRAME'}  # Frame element found
                    }
                }
            }
            frame_info_result = {
                'result': {
                    'result': {
                        'value': {
                            'tagName': 'IFRAME',
                            'id': 'frame-1',
                            'name': 'test-frame',
                            'src': 'https://example.com/frame.html',
                            'hasContentWindow': True
                        }
                    }
                }
            }
            # execute_script is called twice - once to find frame, once to get info
            mock_tab.execute_script = AsyncMock(side_effect=[frame_element_result, frame_info_result])

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_get_frame({
                "browser_id": "browser-1",
                "frame_selector": "#frame-1",
                "selector_type": "css"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            # Frame info structure should have the frame details
            frame_info = result_data["data"]["frame"]
            # Check that frame info contains expected keys
            assert "tagName" in frame_info or "id" in frame_info or "name" in frame_info
            if "id" in frame_info:
                assert frame_info["id"] == "frame-1"

    @pytest.mark.asyncio
    async def test_get_frame_with_pydoll_api(self):
        """Test get_frame tool with PyDoll API if available."""
        with patch('pydoll_mcp.tools.navigation_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            # Create a proper mock frame object with serializable attributes
            class MockFrame:
                def __init__(self):
                    self.frame_id = "frame-1"
                    self.id = "frame-1"
                    self.url = "https://example.com/frame.html"
                    self.name = "test-frame"

            mock_frame = MockFrame()
            mock_tab.get_frame = AsyncMock(return_value=mock_frame)

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_get_frame({
                "browser_id": "browser-1",
                "frame_selector": "#frame-1",
                "selector_type": "css"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["frame"]["frame_id"] == "frame-1"
            mock_tab.get_frame.assert_awaited_once_with("#frame-1")


# Note: TestBrowserContextManagement and TestPermissionsManagement removed
# These tools (create_browser_context, grant_permissions, reset_permissions) are now in unified browser_control tool


class TestEventSystem:
    """Test event system control tools."""

    @pytest.mark.asyncio
    async def test_enable_dom_events(self):
        """Test enable_dom_events tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_dom_events = AsyncMock()
            mock_browser_instance.event_states = {}

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_enable_dom_events({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert mock_browser_instance.event_states.get('dom_events') is True
            mock_tab.enable_dom_events.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_disable_dom_events(self):
        """Test disable_dom_events tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.disable_dom_events = AsyncMock()
            mock_browser_instance.event_states = {}

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_disable_dom_events({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert mock_browser_instance.event_states.get('dom_events') is False

    @pytest.mark.asyncio
    async def test_get_event_status(self):
        """Test get_event_status tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            # Set up event status attributes
            mock_tab.dom_events_enabled = True
            mock_tab.network_events_enabled = False
            mock_tab.page_events_enabled = True
            mock_tab.fetch_events_enabled = None  # Not set, will use fallback
            mock_tab.runtime_events_enabled = None  # Not set, will use fallback

            # Set up event states in browser instance
            mock_browser_instance.event_states = {
                'fetch_events': True,
                'runtime_events': False
            }

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_get_event_status({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert "event_status" in result_data["data"]
            event_status = result_data["data"]["event_status"]
            assert event_status.get('dom_events') is True
            assert event_status.get('network_events') is False

    @pytest.mark.asyncio
    async def test_enable_network_events(self):
        """Test enable_network_events tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_network_events = AsyncMock()
            mock_browser_instance.event_states = {}

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_enable_network_events({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert mock_browser_instance.event_states.get('network_events') is True

    @pytest.mark.asyncio
    async def test_enable_page_events(self):
        """Test enable_page_events tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_page_events = AsyncMock()
            mock_browser_instance.event_states = {}

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_enable_page_events({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert mock_browser_instance.event_states.get('page_events') is True

    @pytest.mark.asyncio
    async def test_enable_fetch_events(self):
        """Test enable_fetch_events tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_fetch_events = AsyncMock()
            mock_browser_instance.event_states = {}

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_enable_fetch_events({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert mock_browser_instance.event_states.get('fetch_events') is True

    @pytest.mark.asyncio
    async def test_enable_runtime_events(self):
        """Test enable_runtime_events tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_browser_instance = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.enable_runtime_events = AsyncMock()
            mock_browser_instance.event_states = {}

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")
            mock_browser_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            result = await handle_enable_runtime_events({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert mock_browser_instance.event_states.get('runtime_events') is True


class TestRequestInterceptionEnhancements:
    """Test request interception enhancements."""

    @pytest.mark.asyncio
    async def test_modify_request(self):
        """Test modify_request tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.continue_request = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_modify_request({
                "browser_id": "browser-1",
                "request_id": "req-1",
                "url": "https://modified.com",
                "method": "POST",
                "headers": {"X-Custom": "value"}
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            mock_tab.continue_request.assert_awaited_once_with(
                request_id="req-1",
                url="https://modified.com",
                method="POST",
                headers={"X-Custom": "value"},
                post_data=None
            )

    @pytest.mark.asyncio
    async def test_fulfill_request(self):
        """Test fulfill_request tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.fulfill_request = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_fulfill_request({
                "browser_id": "browser-1",
                "request_id": "req-1",
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": '{"success": true}'
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["status"] == 200
            mock_tab.fulfill_request.assert_awaited_once_with(
                request_id="req-1",
                status=200,
                headers={"Content-Type": "application/json"},
                body='{"success": true}'
            )

    @pytest.mark.asyncio
    async def test_continue_with_auth(self):
        """Test continue_with_auth tool."""
        with patch('pydoll_mcp.tools.network_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.continue_with_auth = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_continue_with_auth({
                "browser_id": "browser-1",
                "request_id": "req-1",
                "username": "user",
                "password": "pass"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["username"] == "user"
            mock_tab.continue_with_auth.assert_awaited_once_with(
                request_id="req-1",
                username="user",
                password="pass"
            )

