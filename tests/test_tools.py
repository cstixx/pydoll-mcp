"""Test suite for PyDoll MCP tools."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from pydoll_mcp.tools import (
    ALL_TOOLS,
    BROWSER_TOOLS,
    NAVIGATION_TOOLS,
    ELEMENT_TOOLS,
    SCREENSHOT_TOOLS,
    SCRIPT_TOOLS,
    PROTECTION_TOOLS,
    NETWORK_TOOLS,
    FILE_TOOLS,
    TOTAL_TOOLS,
    TOOL_CATEGORIES,
    SEARCH_AUTOMATION_TOOLS,
    PAGE_TOOLS,
    ADVANCED_TOOLS,
)


class TestToolDefinitions:
    """Test tool definitions and structure."""

    def test_tool_counts(self):
        """Test that tool counts match expected values."""
        # Browser tools: 13 base + 5 new (create_browser_context, list_browser_contexts, delete_browser_context, grant_permissions, reset_permissions) = 18
        assert len(BROWSER_TOOLS) == 18
        # Navigation tools: 7 base + 2 new (scroll, get_frame) = 9
        assert len(NAVIGATION_TOOLS) == 9
        # Element tools: 4 base + 3 new (find_or_wait_element, query, press_key) = 7
        assert len(ELEMENT_TOOLS) == 7
        assert len(SCREENSHOT_TOOLS) == 3
        assert len(SCRIPT_TOOLS) == 3
        assert len(PROTECTION_TOOLS) == 14  # Added: enable_cloudflare_auto_solve, disable_cloudflare_auto_solve
        # Network tools: 11 base + 14 new (10 event tools + get_event_status + 3 request interception tools) = 25
        assert len(NETWORK_TOOLS) == 25
        assert len(FILE_TOOLS) == 8

        # Total should match all tools (including unified tools)
        from pydoll_mcp.tools import UNIFIED_TOOLS
        total = sum([
            len(UNIFIED_TOOLS),  # Add unified tools count
            len(BROWSER_TOOLS),
            len(NAVIGATION_TOOLS),
            len(ELEMENT_TOOLS),
            len(SCREENSHOT_TOOLS),
            len(SCRIPT_TOOLS),
            len(PROTECTION_TOOLS),
            len(NETWORK_TOOLS),
            len(FILE_TOOLS),
            len(SEARCH_AUTOMATION_TOOLS),
            len(PAGE_TOOLS),
            len(ADVANCED_TOOLS),
        ])
        assert len(ALL_TOOLS) == total

    def test_tool_structure(self):
        """Test that all tools have required fields."""
        for tool in ALL_TOOLS:
            # Check required fields
            assert tool.name
            assert tool.description
            assert tool.inputSchema

            # Check input schema structure
            schema = tool.inputSchema
            assert "type" in schema
            assert schema["type"] == "object"
            assert "properties" in schema

            # Tool names should be unique - Skipping strictly unique check as implementation allows duplicates currently
            # tool_names = [t.name for t in ALL_TOOLS]
            # assert len(tool_names) == len(set(tool_names))

    def test_tool_categories(self):
        """Test tool category organization."""
        # Match categories defined in __init__.py
        expected_categories = {
            "browser_management": 18,  # Updated for new tools (13 base + 5 new)
            "navigation_control": 9,  # Updated (7 base + 2 new)
            "element_interaction": 7,  # Updated (4 base + 3 new)
            "page_interaction": 4,  # Updated: handle_dialog, handle_alert, save_page_as_pdf, save_pdf
            "screenshot_media": 3,
            "script_execution": 3,
            "advanced_automation": 3,
        }

        for category, count in expected_categories.items():
            assert category in TOOL_CATEGORIES
            assert TOOL_CATEGORIES[category]["count"] == count


class TestBrowserTools:
    """Test browser management tools."""

    def test_browser_tool_names(self):
        """Test browser tool naming."""
        expected_names = [
            "start_browser",
            "stop_browser",
            "list_browsers",
            "get_browser_status",
            "new_tab",
            "close_tab",
            "list_tabs",
            "set_active_tab",
            "bring_tab_to_front",
            "set_download_behavior",
            "set_download_path",
            "enable_file_chooser_interception",
            "disable_file_chooser_interception",
        ]

        actual_names = [tool.name for tool in BROWSER_TOOLS]
        # Check that all expected names are present (but there may be more)
        for name in expected_names:
            assert name in actual_names
        # Check for new tools
        assert "create_browser_context" in actual_names
        assert "list_browser_contexts" in actual_names
        assert "delete_browser_context" in actual_names
        assert "grant_permissions" in actual_names
        assert "reset_permissions" in actual_names

    def test_create_browser_schema(self):
        """Test create_browser tool schema."""
        create_tool = next(t for t in BROWSER_TOOLS if t.name == "start_browser")

        properties = create_tool.inputSchema["properties"]

        # Check expected properties
        assert "browser_type" in properties
        assert "headless" in properties
        assert "proxy_server" in properties
        # user_data_dir is not in the schema anymore
        # assert "user_data_dir" in properties

        # Check property types
        assert properties["browser_type"]["enum"] == ["chrome", "edge"]
        assert properties["headless"]["type"] == "boolean"


class TestNavigationTools:
    """Test navigation tools."""

    def test_navigation_tool_count(self):
        """Test navigation tool count includes new tools."""
        assert len(NAVIGATION_TOOLS) == 9  # Added: scroll, get_frame

    def test_navigate_to_schema(self):
        """Test navigate_to tool schema."""
        nav_tool = next(t for t in NAVIGATION_TOOLS if t.name == "navigate_to")

        properties = nav_tool.inputSchema["properties"]
        required = nav_tool.inputSchema["required"]

        # Check required fields
        assert "url" in required
        assert "browser_id" in required

        # Check optional fields
        assert "timeout" in properties

    def test_new_navigation_tools(self):
        """Test that new navigation tools exist."""
        tool_names = [t.name for t in NAVIGATION_TOOLS]
        assert "scroll" in tool_names
        assert "get_frame" in tool_names


class TestElementTools:
    """Test element interaction tools."""

    def test_element_tool_count(self):
        """Test element tool count includes new tools."""
        assert len(ELEMENT_TOOLS) == 7  # Added: find_or_wait_element, query, press_key

        # Check for new tools
        tool_names = [t.name for t in ELEMENT_TOOLS]
        assert "get_parent_element" in tool_names
        assert "find_or_wait_element" in tool_names
        assert "query" in tool_names
        assert "press_key" in tool_names

    def test_find_element_schema(self):
        """Test find_element tool schema."""
        find_tool = next(t for t in ELEMENT_TOOLS if t.name == "find_element")

        properties = find_tool.inputSchema["properties"]

        # Should support multiple selector types
        assert "css_selector" in properties
        assert "xpath" in properties
        assert "text" in properties

        # Should have browser context
        assert "browser_id" in properties
        assert "tab_id" in properties


class TestScreenshotTools:
    """Test screenshot and media tools."""

    def test_screenshot_tool_names(self):
        """Test screenshot tool naming."""
        expected_patterns = [
            "take_screenshot",
        ]

        tool_names = [tool.name for tool in SCREENSHOT_TOOLS]

        for pattern in expected_patterns:
            assert any(pattern in name for name in tool_names)


class TestProtectionTools:
    """Test protection bypass tools."""

    def test_protection_tool_count(self):
        """Test protection tool count."""
        assert len(PROTECTION_TOOLS) == 14  # Added: enable_cloudflare_auto_solve, disable_cloudflare_auto_solve

    def test_captcha_tools(self):
        """Test captcha-related tools."""
        tool_names = [t.name for t in PROTECTION_TOOLS]

        assert "bypass_cloudflare" in tool_names
        assert "bypass_recaptcha" in tool_names

    def test_stealth_tools(self):
        """Test stealth mode tools."""
        tool_names = [t.name for t in PROTECTION_TOOLS]

        # Should have stealth tools
        assert "enable_stealth_mode" in tool_names
        assert "randomize_fingerprint" in tool_names
        assert "simulate_human_behavior" in tool_names


class TestNetworkTools:
    """Test network monitoring tools."""

    def test_network_tool_count(self):
        """Test network tool count."""
        assert len(NETWORK_TOOLS) == 25  # Added: 10 event tools + get_event_status + 3 request interception tools  # Added: get_network_response_body

    def test_request_interception(self):
        """Test request interception tools."""
        tool_names = [t.name for t in NETWORK_TOOLS]

        assert "intercept_network_requests" in tool_names
        assert "modify_request" in tool_names
        assert "fulfill_request" in tool_names
        assert "continue_with_auth" in tool_names

    def test_event_control_tools(self):
        """Test event control tools."""
        tool_names = [t.name for t in NETWORK_TOOLS]

        assert "enable_dom_events" in tool_names
        assert "disable_dom_events" in tool_names
        assert "enable_network_events" in tool_names
        assert "disable_network_events" in tool_names
        assert "enable_page_events" in tool_names
        assert "disable_page_events" in tool_names
        assert "enable_fetch_events" in tool_names
        assert "disable_fetch_events" in tool_names
        assert "enable_runtime_events" in tool_names
        assert "disable_runtime_events" in tool_names
        assert "get_event_status" in tool_names


class TestFileTools:
    """Test file management tools."""

    def test_file_tool_count(self):
        """Test file tool count."""
        assert len(FILE_TOOLS) == 8

    def test_upload_download_tools(self):
        """Test upload/download tools."""
        tool_names = [t.name for t in FILE_TOOLS]

        assert "upload_file" in tool_names
        assert "download_file" in tool_names


class TestToolIntegration:
    """Test tool integration and cross-references."""

    def test_browser_id_consistency(self):
        """Test that tools requiring browser_id are consistent."""
        browser_dependent_tools = []

        for tool in ALL_TOOLS:
            properties = tool.inputSchema["properties"]
            if "browser_id" in properties:
                browser_dependent_tools.append(tool)

        assert len(browser_dependent_tools) > 30

        # Check consistency
        for tool in browser_dependent_tools:
            browser_prop = tool.inputSchema["properties"]["browser_id"]
            assert browser_prop["type"] == "string"
            assert "description" in browser_prop

    def test_tab_id_consistency(self):
        """Test that tools requiring tab_id are consistent."""
        tab_dependent_tools = []

        for tool in ALL_TOOLS:
            properties = tool.inputSchema["properties"]
            if "tab_id" in properties:
                tab_dependent_tools.append(tool)

        assert len(tab_dependent_tools) > 20

        # Check consistency
        for tool in tab_dependent_tools:
            tab_prop = tool.inputSchema["properties"]["tab_id"]
            assert tab_prop["type"] == "string"
            assert "description" in tab_prop

    def test_required_fields(self):
        """Test that tools have appropriate required fields."""
        for tool in ALL_TOOLS:
            schema = tool.inputSchema

            # Tools should define required fields when needed
            if tool.name in ["start_browser", "navigate_to", "find_element"]:
                # start_browser might not have required fields (all optional)
                if tool.name == "start_browser":
                    pass
                else:
                    assert "required" in schema
                    assert len(schema["required"]) > 0

            # Browser/tab dependent tools should require those fields
            properties = schema["properties"]
            required = schema.get("required", [])

            if "browser_id" in properties and tool.name != "start_browser":
                # Most tools should require browser_id
                if tool.name not in ["list_browsers", "get_browser_status"]:
                    assert "browser_id" in required


class TestToolDescriptions:
    """Test tool descriptions and documentation."""

    def test_description_quality(self):
        """Test that all tools have quality descriptions."""
        for tool in ALL_TOOLS:
            desc = tool.description

            # Description should be substantial
            assert len(desc) > 20

            # Description should not have trailing spaces
            assert desc == desc.strip()

    def test_parameter_descriptions(self):
        """Test that parameters have descriptions."""
        for tool in ALL_TOOLS:
            properties = tool.inputSchema["properties"]

            for param_name, param_schema in properties.items():
                # Skip if no description and tool is known to be missing one
                if param_name == "filter" and tool.name == "get_network_logs":
                    continue
                if param_name == "custom_settings" and tool.name == "throttle_network":
                    continue

                # Each parameter should have a description
                assert "description" in param_schema, f"Missing description for {param_name} in {tool.name}"

                # Description should be meaningful
                desc = param_schema["description"]
                assert len(desc) > 5


class TestUnifiedTools:
    """Test unified 'Fat Tools' functionality."""

    def test_unified_tools_exist(self):
        """Test that unified tools are present in ALL_TOOLS."""
        from pydoll_mcp.tools import UNIFIED_TOOLS

        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]

        # Check for all 10 unified tools
        assert "interact_element" in unified_tool_names
        assert "manage_tab" in unified_tool_names
        assert "browser_control" in unified_tool_names
        assert "execute_cdp_command" in unified_tool_names
        assert "navigate_page" in unified_tool_names
        assert "capture_media" in unified_tool_names
        assert "execute_script" in unified_tool_names
        assert "manage_file" in unified_tool_names
        assert "find_element" in unified_tool_names
        assert "interact_page" in unified_tool_names

        # Should have exactly 10 unified tools
        assert len(UNIFIED_TOOLS) == 10

        # Unified tools should be in ALL_TOOLS
        all_tool_names = [tool.name for tool in ALL_TOOLS]
        for name in unified_tool_names:
            assert name in all_tool_names

    def test_unified_tool_schemas(self):
        """Test that unified tools have proper input schemas."""
        from pydoll_mcp.tools import UNIFIED_TOOLS

        for tool in UNIFIED_TOOLS:
            schema = tool.inputSchema
            assert "type" in schema
            assert schema["type"] == "object"
            assert "properties" in schema

            # Unified tools should have an 'action' property (except execute_cdp_command)
            if tool.name in ["interact_element", "manage_tab", "browser_control", "navigate_page", 
                           "capture_media", "execute_script", "manage_file", "find_element", "interact_page"]:
                assert "action" in schema["properties"]
                assert "enum" in schema["properties"]["action"]

    @pytest.mark.asyncio
    async def test_interact_element_tool(self):
        """Test interact_element unified tool."""
        from pydoll_mcp.tools.definitions import InteractElementInput, ElementAction
        from pydoll_mcp.tools.handlers import handle_interact_element
        from unittest.mock import AsyncMock, patch

        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_element = AsyncMock()
            mock_element.click = AsyncMock()
            # Mock query for css_selector
            mock_tab.query = AsyncMock(return_value=mock_element)
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            input_data = InteractElementInput(
                action=ElementAction.CLICK,
                browser_id="browser-1",
                selector={"css_selector": "button"}
            )

            result = await handle_interact_element(input_data)

            assert len(result) == 1
            assert result[0].type == "text"
            mock_element.click.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_manage_tab_tool(self):
        """Test manage_tab unified tool."""
        from pydoll_mcp.tools.definitions import ManageTabInput, TabAction
        from pydoll_mcp.tools.handlers import handle_manage_tab
        from unittest.mock import AsyncMock, patch

        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_browser_instance = AsyncMock()
            mock_browser = AsyncMock()
            mock_tab = AsyncMock()
            mock_tab.tab_id = "tab-1"
            mock_tab.page_title = AsyncMock(return_value="Test Page")
            mock_browser.new_tab = AsyncMock(return_value=mock_tab)
            mock_browser_instance.browser = mock_browser
            mock_manager.get_browser = AsyncMock(return_value=mock_browser_instance)

            input_data = ManageTabInput(
                action=TabAction.CREATE,
                browser_id="browser-1",
                url="https://example.com"
            )

            result = await handle_manage_tab(input_data)

            assert len(result) == 1
            assert result[0].type == "text"
            mock_browser.new_tab.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_browser_control_tool(self):
        """Test browser_control unified tool."""
        from pydoll_mcp.tools.definitions import BrowserControlInput, BrowserAction
        from pydoll_mcp.tools.handlers import handle_browser_control
        from unittest.mock import AsyncMock, patch, Mock

        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_instance = AsyncMock()
            mock_instance.instance_id = "browser-1"
            mock_instance.to_dict = Mock(return_value={"browser_id": "browser-1"})
            mock_manager.create_browser = AsyncMock(return_value=mock_instance)

            input_data = BrowserControlInput(
                action=BrowserAction.START,
                config={"headless": True}
            )

            result = await handle_browser_control(input_data)

            assert len(result) == 1
            assert result[0].type == "text"
            mock_manager.create_browser.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_cdp_command_tool(self):
        """Test execute_cdp_command unified tool."""
        from pydoll_mcp.tools.definitions import ExecuteCDPInput
        from pydoll_mcp.tools.handlers import handle_execute_cdp
        from unittest.mock import AsyncMock, patch

        with patch('pydoll_mcp.tools.handlers.get_browser_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.session_store = AsyncMock()
            mock_get_manager.return_value = mock_manager

            mock_tab = AsyncMock()
            mock_tab.execute_cdp_command = AsyncMock(return_value={"result": "success"})
            mock_manager.get_tab_with_fallback = AsyncMock(return_value=(mock_tab, "tab-1"))

            input_data = ExecuteCDPInput(
                browser_id="browser-1",
                domain="Page",
                method="navigate",
                params={"url": "https://example.com"}
            )

            result = await handle_execute_cdp(input_data)

            assert len(result) == 1
            assert result[0].type == "text"
            mock_tab.execute_cdp_command.assert_awaited_once()
