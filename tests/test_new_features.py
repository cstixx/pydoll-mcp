"""Tests for new PyDoll 2.12.4+ features and enhanced tools.

This test suite covers:
- Enhanced alert/dialog handling (handle_alert, handle_dialog)
- File upload/download with real PyDoll APIs
- PDF saving with file support
- Tab management (bring_tab_to_front)
- Download configuration tools
- File chooser interception
- Network monitoring enhancements
- Cloudflare captcha tools
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from pydoll_mcp.tools.page_tools import (
    handle_handle_alert,
    handle_handle_dialog,
    handle_save_pdf,
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
    handle_upload_file,
    handle_download_file,
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


class TestAlertDialogHandling:
    """Test enhanced alert and dialog handling tools."""

    @pytest.mark.asyncio
    async def test_handle_alert_accept(self):
        """Test handle_alert with accept=True."""
        with patch('pydoll_mcp.tools.page_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            # Mock dialog detection
            mock_tab.has_dialog = AsyncMock(return_value=True)
            mock_tab.get_dialog_message = AsyncMock(return_value="Test alert message")
            mock_tab.handle_dialog = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_handle_alert({
                "browser_id": "browser-1",
                "accept": True
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["accepted"] is True
            assert result_data["data"]["dialog_message"] == "Test alert message"
            assert result_data["data"]["dialog_detected"] is True
            mock_tab.handle_dialog.assert_awaited_once_with(accept=True)

    @pytest.mark.asyncio
    async def test_handle_alert_dismiss(self):
        """Test handle_alert with accept=False."""
        with patch('pydoll_mcp.tools.page_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.has_dialog = AsyncMock(return_value=False)
            mock_tab.handle_dialog = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_handle_alert({
                "browser_id": "browser-1",
                "accept": False
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["accepted"] is False
            mock_tab.handle_dialog.assert_awaited_once_with(accept=False)

    @pytest.mark.asyncio
    async def test_handle_dialog_with_prompt(self):
        """Test handle_dialog with prompt text."""
        with patch('pydoll_mcp.tools.page_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.has_dialog = AsyncMock(return_value=True)
            mock_tab.get_dialog_message = AsyncMock(return_value="Enter your name:")
            mock_tab.handle_dialog = AsyncMock()

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_handle_dialog({
                "browser_id": "browser-1",
                "accept": True,
                "prompt_text": "John Doe"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert result_data["data"]["prompt_text_entered"] == "John Doe"
            mock_tab.handle_dialog.assert_awaited_once_with(accept=True, prompt_text="John Doe")


class TestPDFSaving:
    """Test enhanced PDF saving functionality."""

    @pytest.mark.asyncio
    async def test_save_pdf_base64(self):
        """Test save_pdf without file path (returns base64)."""
        with patch('pydoll_mcp.tools.page_tools.get_browser_manager') as mock_manager:
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            mock_tab.print_to_pdf = AsyncMock(return_value="base64_pdf_data")

            mock_manager.return_value = mock_browser_manager
            mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

            result = await handle_save_pdf({
                "browser_id": "browser-1"
            })

            assert len(result) == 1
            result_data = json.loads(result[0].text)
            assert result_data["success"] is True
            assert "pdf_data" in result_data["data"]
            assert result_data["data"]["pdf_data"] == "base64_pdf_data"
            mock_tab.print_to_pdf.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_save_pdf_to_file(self):
        """Test save_pdf with file path."""
        with patch('pydoll_mcp.tools.page_tools.get_browser_manager') as mock_manager:
            import base64
            mock_browser_manager = AsyncMock()
            mock_tab = AsyncMock()

            # Create a temporary file path
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = os.path.join(tmpdir, "test.pdf")
                pdf_data = base64.b64encode(b"fake pdf content").decode('utf-8')

                mock_tab.print_to_pdf = AsyncMock(return_value=pdf_data)

                mock_manager.return_value = mock_browser_manager
                mock_browser_manager.get_tab_with_fallback.return_value = (mock_tab, "tab-1")

                result = await handle_save_pdf({
                    "browser_id": "browser-1",
                    "file_path": pdf_path
                })

                assert len(result) == 1
                result_data = json.loads(result[0].text)
                assert result_data["success"] is True
                assert "file_path" in result_data["data"]
                assert os.path.exists(pdf_path)

                # Verify file was written
                with open(pdf_path, "rb") as f:
                    assert f.read() == b"fake pdf content"


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
        """Test that new page tools are registered."""
        assert "handle_alert" in PAGE_TOOL_HANDLERS
        assert "save_pdf" in PAGE_TOOL_HANDLERS
        assert "handle_dialog" in PAGE_TOOL_HANDLERS

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

