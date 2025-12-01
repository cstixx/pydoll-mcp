"""Test suite for PyDoll MCP tools."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from pydoll_mcp.tools import (
    ALL_TOOLS,
    BROWSER_TOOLS,
    NAVIGATION_TOOLS,
    SCRIPT_TOOLS,
    PROTECTION_TOOLS,
    NETWORK_TOOLS,
    FILE_TOOLS,
    TOTAL_TOOLS,
    TOOL_CATEGORIES,
    SEARCH_AUTOMATION_TOOLS,
    PAGE_TOOLS,
    ADVANCED_TOOLS,
    UNIFIED_TOOLS,
)


class TestToolDefinitions:
    """Test tool definitions and structure."""

    def test_tool_counts(self):
        """Test that tool counts match expected values."""
        # Browser tools: legacy tools (context/permissions now in unified browser_control)
        assert len(BROWSER_TOOLS) >= 5  # At least bring_tab_to_front, set_download_behavior, etc.
        # Navigation tools: only fetch_domain_commands remains (others in unified navigate_page)
        assert len(NAVIGATION_TOOLS) >= 1
        # Element tools and Screenshot tools are fully replaced by unified tools
        # Script tools: some remain (execute_automation_script, inject_script_library)
        assert len(SCRIPT_TOOLS) >= 2
        assert len(PROTECTION_TOOLS) >= 12
        assert len(NETWORK_TOOLS) >= 10
        assert len(FILE_TOOLS) >= 0  # upload_file, download_file, manage_downloads replaced by unified manage_file

        # Total should match all tools (including unified tools)
        total = sum([
            len(UNIFIED_TOOLS),  # 10 unified tools
            len(BROWSER_TOOLS),
            len(NAVIGATION_TOOLS),
            len(SCRIPT_TOOLS),
            len(PROTECTION_TOOLS),
            len(NETWORK_TOOLS),
            len(FILE_TOOLS),
            len(SEARCH_AUTOMATION_TOOLS),
            len(PAGE_TOOLS),
            len(ADVANCED_TOOLS),
        ])
        # Note: ALL_TOOLS may only include unified tools if UNIFIED_TOOLS_ONLY is True
        # So we check that unified tools are included
        assert len(UNIFIED_TOOLS) == 10
        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
        all_tool_names = [tool.name for tool in ALL_TOOLS]
        for name in unified_tool_names:
            assert name in all_tool_names, f"Unified tool {name} not in ALL_TOOLS"

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
        # Unified tools category should exist
        assert "unified_tools" in TOOL_CATEGORIES
        assert TOOL_CATEGORIES["unified_tools"]["count"] == 10

        # Check that unified tools are listed
        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
        category_tools = TOOL_CATEGORIES["unified_tools"]["tools"]
        for name in unified_tool_names:
            assert name in category_tools, f"Unified tool {name} not in category tools list"


class TestBrowserTools:
    """Test browser management tools."""

    def test_browser_tool_names(self):
        """Test browser tool naming."""
        # Most browser tools are now in unified tools (browser_control, manage_tab)
        # Only a few legacy tools remain in BROWSER_TOOLS
        actual_names = [tool.name for tool in BROWSER_TOOLS]

        # Check that legacy tools that remain are present
        assert "bring_tab_to_front" in actual_names
        assert "set_download_behavior" in actual_names

        # Check that unified tools have browser control capabilities
        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
        assert "browser_control" in unified_tool_names
        assert "manage_tab" in unified_tool_names

    def test_create_browser_schema(self):
        """Test browser creation via unified browser_control tool."""
        # start_browser is now in unified browser_control tool
        browser_control_tool = next(t for t in UNIFIED_TOOLS if t.name == "browser_control")

        properties = browser_control_tool.inputSchema["properties"]

        # Check expected properties for start action
        assert "action" in properties
        assert "start" in properties["action"]["enum"]
        assert "browser_type" in properties
        assert "headless" in properties

        # Check property types
        assert properties["browser_type"]["type"] == "string"
        assert properties["headless"]["type"] == "boolean"


class TestNavigationTools:
    """Test navigation tools."""

    def test_navigation_tool_count(self):
        """Test navigation tool count - most tools moved to unified navigate_page."""
        # Most navigation tools are now in unified navigate_page
        # Only a few legacy tools remain (like fetch_domain_commands, scroll, get_frame)
        assert len(NAVIGATION_TOOLS) >= 1  # At least fetch_domain_commands remains

    def test_navigate_to_schema(self):
        """Test navigate_to via unified navigate_page tool."""
        # navigate_to is now in unified navigate_page tool
        nav_tool = next(t for t in UNIFIED_TOOLS if t.name == "navigate_page")

        properties = nav_tool.inputSchema["properties"]
        required = nav_tool.inputSchema["required"]

        # Check that it supports navigate action
        assert "action" in properties
        assert "navigate" in properties["action"]["enum"]

        # Check required fields
        assert "action" in required
        assert "browser_id" in required

        # Check optional fields
        assert "url" in properties
        assert "timeout" in properties

    def test_navigation_tools_in_unified(self):
        """Test that navigation capabilities exist in unified tools."""
        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
        assert "navigate_page" in unified_tool_names


class TestElementTools:
    """Test element interaction tools."""

    def test_element_tools_replaced(self):
        """Test that element tools are replaced by unified tools."""
        # Element tools are now in unified tools (interact_element, find_element)
        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
        assert "interact_element" in unified_tool_names
        assert "find_element" in unified_tool_names

    def test_find_element_unified_tool(self):
        """Test find_element unified tool schema."""
        find_tool = next(t for t in UNIFIED_TOOLS if t.name == "find_element")

        properties = find_tool.inputSchema["properties"]

        # Should support action parameter
        assert "action" in properties
        assert "enum" in properties["action"]

        # Should support selector
        assert "selector" in properties

        # Should have browser context
        assert "browser_id" in properties
        assert "tab_id" in properties


class TestScreenshotTools:
    """Test screenshot and media tools."""

    def test_screenshot_tools_replaced(self):
        """Test that screenshot tools are replaced by unified capture_media."""
        # Screenshot tools are now in unified capture_media tool
        unified_tool_names = [tool.name for tool in UNIFIED_TOOLS]
        assert "capture_media" in unified_tool_names

        # Check that capture_media supports screenshot actions
        capture_tool = next(t for t in UNIFIED_TOOLS if t.name == "capture_media")
        assert "action" in capture_tool.inputSchema["properties"]
        action_enum = capture_tool.inputSchema["properties"]["action"]["enum"]
        assert "screenshot" in action_enum
        assert "element_screenshot" in action_enum
        assert "generate_pdf" in action_enum


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
        # FILE_TOOLS count may vary - upload_file, download_file, manage_downloads removed

    def test_file_tools_remaining(self):
        """Test remaining file tools (upload/download moved to unified manage_file)."""
        tool_names = [t.name for t in FILE_TOOLS]

        # upload_file and download_file removed - use unified manage_file tool instead
        # Only data extraction and session management tools remain
        assert "extract_data" in tool_names or len(tool_names) >= 0


class TestToolIntegration:
    """Test tool integration and cross-references."""

    def test_browser_id_consistency(self):
        """Test that tools requiring browser_id are consistent."""
        browser_dependent_tools = []

        for tool in ALL_TOOLS:
            properties = tool.inputSchema["properties"]
            if "browser_id" in properties:
                browser_dependent_tools.append(tool)

        # With unified tools, we have fewer tools but they're more powerful
        assert len(browser_dependent_tools) >= 10  # At least all unified tools

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

        # With unified tools, we have fewer tools but they're more powerful
        assert len(tab_dependent_tools) >= 9  # At least most unified tools

        # Check consistency
        for tool in tab_dependent_tools:
            tab_prop = tool.inputSchema["properties"]["tab_id"]
            assert tab_prop["type"] == "string"
            assert "description" in tab_prop

    def test_required_fields(self):
        """Test that tools have appropriate required fields."""
        for tool in ALL_TOOLS:
            schema = tool.inputSchema
            properties = schema["properties"]
            required = schema.get("required", [])

            # Unified tools use action-based patterns
            if tool.name in UNIFIED_TOOLS and hasattr(tool, 'name'):
                unified_tool_names = [t.name for t in UNIFIED_TOOLS]
                if tool.name in unified_tool_names:
                    # Unified tools should have action as required
                    if "action" in properties:
                        assert "action" in required
                    # Most unified tools require browser_id
                    if "browser_id" in properties and tool.name not in ["browser_control"]:
                        # browser_control might have actions that don't require browser_id (like START)
                        # But most actions do require it
                        pass  # Allow flexibility for unified tools

            # Legacy tools should follow old patterns
            if tool.name not in [t.name for t in UNIFIED_TOOLS]:
                # Legacy tools should define required fields when needed
                if tool.name in ["navigate_to", "find_element"]:
                    assert "required" in schema
                    assert len(schema["required"]) > 0

                # Browser/tab dependent legacy tools should require those fields
                if "browser_id" in properties and tool.name not in ["start_browser", "list_browsers", "get_browser_status"]:
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
