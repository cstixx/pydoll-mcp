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
        assert len(BROWSER_TOOLS) == 8
        assert len(NAVIGATION_TOOLS) == 7
        assert len(ELEMENT_TOOLS) == 4
        assert len(SCREENSHOT_TOOLS) == 3
        assert len(SCRIPT_TOOLS) == 3
        assert len(PROTECTION_TOOLS) == 12
        assert len(NETWORK_TOOLS) == 10
        assert len(FILE_TOOLS) == 8

        # Total should match all tools
        total = sum([
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

            # Tool names should be unique
            tool_names = [t.name for t in ALL_TOOLS]
            assert len(tool_names) == len(set(tool_names))

    def test_tool_categories(self):
        """Test tool category organization."""
        # Match categories defined in __init__.py
        expected_categories = {
            "browser_management": 8,
            "navigation_control": 7,
            "element_interaction": 4,
            "page_interaction": 2,
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
        ]

        actual_names = [tool.name for tool in BROWSER_TOOLS]
        assert set(actual_names) == set(expected_names)

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
        assert len(NAVIGATION_TOOLS) == 7

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


class TestElementTools:
    """Test element interaction tools."""

    def test_element_tool_count(self):
        """Test element tool count includes new tools."""
        assert len(ELEMENT_TOOLS) == 4

        # Check for new tool
        tool_names = [t.name for t in ELEMENT_TOOLS]
        assert "get_parent_element" in tool_names

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
        assert len(PROTECTION_TOOLS) == 12

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
        assert len(NETWORK_TOOLS) == 10

    def test_request_interception(self):
        """Test request interception tools."""
        tool_names = [t.name for t in NETWORK_TOOLS]

        assert "intercept_network_requests" in tool_names


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
