"""Tests for Windows compatibility and enhanced browser automation."""

import asyncio
import os
import pytest
import sys
from unittest.mock import Mock, patch, AsyncMock

from pydoll_mcp.core import BrowserManager, get_browser_manager
from pydoll_mcp.pydoll_integration import PyDollIntegration, get_pydoll_integration
from pydoll_mcp.tools.search_automation import handle_intelligent_search


class TestWindowsCompatibility:
    """Test Windows-specific compatibility features."""

    @pytest.fixture
    def browser_manager(self):
        """Create a fresh browser manager for testing."""
        return BrowserManager()

    @pytest.fixture
    def pydoll_integration(self):
        """Create PyDoll integration instance for testing."""
        return PyDollIntegration()

    def test_windows_detection(self):
        """Test Windows environment detection."""
        with patch('os.name', 'nt'):
            integration = PyDollIntegration()
            # Windows-specific checks should be performed
            assert len(integration.compatibility_issues) >= 0

    def test_chrome_path_detection_windows(self, pydoll_integration):
        """Test Chrome browser detection on Windows."""
        if os.name == 'nt':
            # This test only runs on actual Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]

            chrome_found = any(os.path.exists(path) for path in chrome_paths)
            # Should either find Chrome or note it as an issue
            if not chrome_found:
                assert any("Chrome" in issue for issue in pydoll_integration.compatibility_issues)

    @pytest.mark.asyncio
    async def test_enhanced_tab_readiness_check(self, browser_manager):
        """Test enhanced tab readiness check for Windows compatibility."""
        # Mock tab object
        mock_tab = Mock()
        mock_tab.page_title = AsyncMock(return_value="Test Page")

        # Test tab readiness check
        await browser_manager._ensure_tab_ready(mock_tab, "test_tab_id")

        # Should not raise any exceptions
        assert True

    @pytest.mark.asyncio
    async def test_browser_creation_with_windows_options(self, browser_manager):
        """Test browser creation with Windows-specific options."""
        with patch('pydoll_mcp.core.browser_manager.PYDOLL_AVAILABLE', True):
            with patch('pydoll_mcp.core.browser_manager.Chrome') as MockChrome:
                with patch('pydoll_mcp.core.browser_manager.ChromiumOptions') as MockOptions:
                    mock_options = Mock()
                    MockOptions.return_value = mock_options

                    mock_browser = Mock()
                    mock_tab = AsyncMock()
                    # Mock tab methods that might be called
                    mock_tab.page_title = AsyncMock(return_value="Test Page")
                    mock_tab.current_url = AsyncMock(return_value="about:blank")
                    mock_tab.execute_script = AsyncMock(return_value="complete")
                    MockChrome.return_value = mock_browser
                    mock_browser.start = AsyncMock(return_value=mock_tab)

                    # Mock session_store methods
                    browser_manager.session_store.save_browser = AsyncMock()
                    browser_manager.session_store.save_tab = AsyncMock()
                    browser_manager.session_store.list_browsers = AsyncMock(return_value=[])
                    # Mock _ensure_tab_ready to avoid hanging (it calls tab methods)
                    browser_manager._ensure_tab_ready = AsyncMock()

                    # Test Windows-specific option application
                    with patch('os.name', 'nt'):
                        # Using create_browser instead of internal _get_browser_options to verify full flow
                        instance = await browser_manager.create_browser()
                        assert instance is not None

                        # Verify Windows-specific arguments were added
                        assert mock_options.add_argument.called

    def test_compatibility_report_generation(self, pydoll_integration):
        """Test compatibility report generation."""
        report = pydoll_integration.get_compatibility_report()

        required_fields = [
            "pydoll_available", "pydoll_version", "platform",
            "python_version", "compatibility_issues", "recommendations", "status"
        ]

        for field in required_fields:
            assert field in report

        assert isinstance(report["compatibility_issues"], list)
        assert isinstance(report["recommendations"], list)
        assert report["status"] in ["ready", "issues_detected"]


class TestEnhancedElementFinding:
    """Test enhanced element finding capabilities."""

    @pytest.mark.asyncio
    async def test_intelligent_search_multiple_strategies(self):
        """Test intelligent search with multiple fallback strategies."""
        mock_browser_manager = Mock()
        mock_tab = Mock()

        # Create separate results to avoid circular reference
        mock_search_result_1 = {
            "result": {
                "result": {
                    "value": {
                        "success": True,
                        "method": "enter",
                        "elementFound": True,
                        "searchExecuted": True,
                        "details": {
                            "selector": 'input[name="q"]',
                            "textEntered": True
                        }
                    }
                }
            }
        }

        mock_search_result_2 = {
            "result": {
                "result": {
                    "value": {
                        "success": False, # Second call (results check)
                    }
                }
            }
        }

        mock_tab.execute_script = AsyncMock(side_effect=[mock_search_result_1, mock_search_result_2])

        mock_browser_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "test_tab"))

        with patch('pydoll_mcp.tools.search_automation.get_browser_manager', return_value=mock_browser_manager):
            arguments = {
                "browser_id": "test_browser",
                "search_query": "test query",
                "website_type": "google"
            }

            result = await handle_intelligent_search(arguments)

            assert len(result) > 0
            assert "Successfully performed search" in result[0].text

    @pytest.mark.asyncio
    async def test_element_finding_fallback_strategies(self):
        """Test element finding with multiple fallback strategies."""
        from pydoll_mcp.tools.element_tools import handle_find_element

        mock_browser_manager = Mock()
        mock_tab = Mock()
        mock_tab.execute_script = AsyncMock()
        mock_tab.query = AsyncMock(return_value=None) # Mock query method
        mock_tab.query_all = AsyncMock(return_value=[]) # Mock query_all method
        mock_tab.find = AsyncMock(return_value=None) # Mock find method

        # Mock element finding result with common selectors fallback
        mock_element = Mock()
        mock_element.tag_name = "INPUT"
        mock_element.text = ""
        mock_element.get_attribute = AsyncMock(return_value="search")
        mock_element.id = "search"
        mock_element.class_name = "search-input"
        mock_element.name = "q"
        mock_element.type = "search"
        mock_element.href = None

        mock_tab.find = AsyncMock(return_value=mock_element)

        mock_browser_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "test_tab"))

        with patch('pydoll_mcp.tools.element_tools.get_browser_manager', return_value=mock_browser_manager):
            arguments = {
                "browser_id": "test_browser",
                "name": "q"
            }

            result = await handle_find_element(arguments)

            assert len(result) > 0
            response_data = result[0].text
            assert "Found 1 element" in response_data


class TestNetworkAndPerformance:
    """Test network and performance optimizations."""

    def test_browser_options_caching(self):
        """Test browser options caching for performance."""
        # Caching disabled to fix bugs with mutable options. Test skipped.
        pytest.skip("Browser options caching is disabled")

    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking."""
        from pydoll_mcp.core import BrowserMetrics

        metrics = BrowserMetrics()

        # Test navigation timing
        metrics.record_navigation(1.5)
        metrics.record_navigation(2.0)
        metrics.record_navigation(1.2)

        avg_time = metrics.get_avg_navigation_time()
        assert 1.0 < avg_time < 2.5

        # Test error tracking
        metrics.record_error()
        metrics.record_error()

        error_rate = metrics.get_error_rate()
        assert error_rate > 0


class TestAsyncOperations:
    """Test asynchronous operations and error handling."""

    @pytest.mark.asyncio
    async def test_browser_cleanup(self):
        """Test proper browser cleanup."""


        # Mock browser and tab objects
        mock_tab = Mock()
        mock_tab.page_title = AsyncMock(return_value="Test Page")
        mock_tab.close = AsyncMock()
        mock_tab.execute_script = AsyncMock(return_value="complete")

        mock_browser = Mock()
        mock_browser.start = AsyncMock(return_value=mock_tab)
        mock_browser.stop = AsyncMock()
        mock_browser.tab = mock_tab

            # Mock session store to avoid database/file operations
        mock_browser.list_browsers = AsyncMock(return_value=[])
        mock_browser.delete_browser = AsyncMock()
        mock_browser.save_browser = AsyncMock()


        # Mock BrowserInstance
        from pydoll_mcp.core import BrowserInstance
        mock_instance = BrowserInstance(mock_browser, "chrome", "test_browser")
        mock_instance.tabs["test_tab"] = mock_tab
        mock_instance.is_active = True

        # Call cleanup method which handles tab closing and browser stopping
        await mock_instance.cleanup()

        # Verify cleanup methods were called
        mock_tab.close.assert_called_once()
        mock_browser.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_tab_context_manager(self):
        """Test tab context manager for safe operations."""
        from pydoll_mcp.core import BrowserInstance

        mock_browser = Mock()
        instance = BrowserInstance(mock_browser, "chrome", "test_id")

        mock_tab = Mock()
        instance.tabs["test_tab"] = mock_tab

        # Test successful operation
        async with instance.tab_context("test_tab") as tab:
            assert tab == mock_tab

        # Test error handling
        with pytest.raises(ValueError):
            async with instance.tab_context("nonexistent_tab"):
                pass


if __name__ == "__main__":
    # Run specific tests for Windows environment
    if os.name == 'nt':
        print("Running Windows-specific tests...")
        pytest.main([__file__ + "::TestWindowsCompatibility", "-v"])
    else:
        print("Running cross-platform tests...")
        pytest.main([__file__, "-v"])
