"""Unified Tool Definitions for PyDoll MCP Server.

This module defines Pydantic models for the "Fat Tools" - unified,
high-level tools that consolidate multiple granular operations.
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ElementAction(str, Enum):
    """Element interaction actions."""
    CLICK = "click"
    TYPE = "type"
    HOVER = "hover"
    PRESS_KEY = "press_key"
    DRAG = "drag"
    SCROLL = "scroll"


class TabAction(str, Enum):
    """Tab management actions."""
    CREATE = "create"
    CLOSE = "close"
    REFRESH = "refresh"
    ACTIVATE = "activate"
    LIST = "list"


class BrowserAction(str, Enum):
    """Browser control actions."""
    START = "start"
    STOP = "stop"
    GET_STATE = "get_state"
    LIST = "list"


class ElementSelector(BaseModel):
    """Element selector model - supports all selector types."""

    # Natural attribute selectors
    id: Optional[str] = Field(None, description="Element ID attribute")
    class_name: Optional[str] = Field(None, description="CSS class name")
    tag_name: Optional[str] = Field(None, description="HTML tag name")
    text: Optional[str] = Field(None, description="Element text content")
    name: Optional[str] = Field(None, description="Element name attribute")
    type: Optional[str] = Field(None, description="Element type attribute")
    placeholder: Optional[str] = Field(None, description="Input placeholder text")
    value: Optional[str] = Field(None, description="Element value attribute")

    # Data attributes
    data_testid: Optional[str] = Field(None, description="data-testid attribute")
    data_id: Optional[str] = Field(None, description="data-id attribute")

    # Accessibility attributes
    aria_label: Optional[str] = Field(None, description="aria-label attribute")
    aria_role: Optional[str] = Field(None, description="aria-role attribute")

    # Traditional selectors
    css_selector: Optional[str] = Field(None, description="CSS selector string")
    xpath: Optional[str] = Field(None, description="XPath expression")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, removing None values."""
        return {k: v for k, v in self.dict().items() if v is not None}


class InteractElementInput(BaseModel):
    """Input model for unified element interaction tool."""

    action: ElementAction = Field(description="Action to perform on the element")
    selector: Dict[str, Any] = Field(description="Element selector dictionary")
    value: Optional[str] = Field(None, description="Value for type action")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")

    # Additional options
    click_type: Optional[str] = Field("left", description="Click type: left, right, double, middle")
    scroll_to_element: Optional[bool] = Field(True, description="Scroll element into view before action")
    human_like: Optional[bool] = Field(True, description="Use human-like behavior")
    typing_speed: Optional[str] = Field("normal", description="Typing speed: slow, normal, fast, instant")
    clear_first: Optional[bool] = Field(True, description="Clear existing text before typing")


class ManageTabInput(BaseModel):
    """Input model for unified tab management tool."""

    action: TabAction = Field(description="Action to perform")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID (required for close, refresh, activate)")
    url: Optional[str] = Field(None, description="URL for create action")

    # Additional options
    background: Optional[bool] = Field(False, description="Open tab in background")
    wait_for_load: Optional[bool] = Field(True, description="Wait for page to load")
    ignore_cache: Optional[bool] = Field(False, description="Ignore cache on refresh")


class BrowserControlInput(BaseModel):
    """Input model for unified browser control tool."""

    action: BrowserAction = Field(description="Action to perform")
    browser_id: Optional[str] = Field(None, description="Browser ID (required for stop, get_state)")
    config: Optional[Dict[str, Any]] = Field(None, description="Browser configuration (for start action)")

    # Browser configuration fields (for start action)
    browser_type: Optional[str] = Field("chrome", description="Browser type: chrome or edge")
    headless: Optional[bool] = Field(False, description="Run in headless mode")
    window_width: Optional[int] = Field(1920, description="Window width")
    window_height: Optional[int] = Field(1080, description="Window height")
    stealth_mode: Optional[bool] = Field(True, description="Enable stealth mode")
    proxy_server: Optional[str] = Field(None, description="Proxy server")
    user_agent: Optional[str] = Field(None, description="Custom user agent")


class ExecuteCDPInput(BaseModel):
    """Input model for CDP command execution tool."""

    domain: str = Field(description="CDP domain (e.g., 'Page', 'Network', 'DOM')")
    method: str = Field(description="CDP method name (e.g., 'printToPDF', 'navigate')")
    params: Dict[str, Any] = Field(default_factory=dict, description="CDP method parameters")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")

