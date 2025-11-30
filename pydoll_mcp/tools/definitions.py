"""Unified Tool Definitions for PyDoll MCP Server.

This module defines Pydantic models for the "Fat Tools" - unified,
high-level tools that consolidate multiple granular operations.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

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
    CREATE_CONTEXT = "create_context"
    LIST_CONTEXTS = "list_contexts"
    DELETE_CONTEXT = "delete_context"
    GRANT_PERMISSIONS = "grant_permissions"
    RESET_PERMISSIONS = "reset_permissions"


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

    # Browser context and permissions fields
    context_name: Optional[str] = Field(None, description="Context name (for create_context action)")
    context_id: Optional[str] = Field(None, description="Context ID (for delete_context action)")
    origin: Optional[str] = Field(None, description="URL origin (for grant_permissions and reset_permissions actions)")
    permissions: Optional[list] = Field(None, description="List of permissions (for grant_permissions action)")


class ExecuteCDPInput(BaseModel):
    """Input model for CDP command execution tool."""

    domain: str = Field(description="CDP domain (e.g., 'Page', 'Network', 'DOM')")
    method: str = Field(description="CDP method name (e.g., 'printToPDF', 'navigate')")
    params: Dict[str, Any] = Field(default_factory=dict, description="CDP method parameters")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")


class NavigationAction(str, Enum):
    """Page navigation actions."""
    NAVIGATE = "navigate"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    GET_URL = "get_url"
    GET_TITLE = "get_title"
    GET_SOURCE = "get_source"
    WAIT_LOAD = "wait_load"
    WAIT_NETWORK_IDLE = "wait_network_idle"
    SET_VIEWPORT = "set_viewport"
    GET_INFO = "get_info"


class NavigatePageInput(BaseModel):
    """Input model for unified page navigation tool."""

    action: NavigationAction = Field(description="Navigation action to perform")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")
    url: Optional[str] = Field(None, description="URL for navigate action")
    wait_for_load: Optional[bool] = Field(True, description="Wait for page to load")
    timeout: Optional[int] = Field(30, description="Timeout in seconds")
    referrer: Optional[str] = Field(None, description="Referrer URL for navigate action")
    width: Optional[int] = Field(None, description="Viewport width for set_viewport action")
    height: Optional[int] = Field(None, description="Viewport height for set_viewport action")


class ScreenshotAction(str, Enum):
    """Screenshot and media capture actions."""
    SCREENSHOT = "screenshot"
    ELEMENT_SCREENSHOT = "element_screenshot"
    GENERATE_PDF = "generate_pdf"
    SAVE_PAGE_AS_PDF = "save_page_as_pdf"
    SAVE_PDF = "save_pdf"


class CaptureMediaInput(BaseModel):
    """Input model for unified screenshot/media capture tool."""

    action: ScreenshotAction = Field(description="Media capture action to perform")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")
    selector: Optional[Dict[str, Any]] = Field(None, description="Element selector for element_screenshot action")
    format: Optional[str] = Field("png", description="Image format: png, jpeg, jpg")
    quality: Optional[int] = Field(None, description="JPEG quality (1-100)")
    full_page: Optional[bool] = Field(False, description="Capture full page")
    file_name: Optional[str] = Field(None, description="Output filename")
    save_to_file: Optional[bool] = Field(True, description="Save to file")
    return_base64: Optional[bool] = Field(False, description="Return as base64")
    # PDF options
    pdf_format: Optional[str] = Field("A4", description="PDF format: A4, A3, A5, Letter, Legal, Tabloid")
    orientation: Optional[str] = Field("portrait", description="PDF orientation: portrait, landscape")
    include_background: Optional[bool] = Field(True, description="Include background in PDF")
    file_path: Optional[str] = Field(None, description="File path to save PDF (for save_pdf action)")
    print_background: Optional[bool] = Field(True, description="Print background graphics (for save_pdf action)")


class ScriptAction(str, Enum):
    """Script execution actions."""
    EXECUTE = "execute"
    EVALUATE = "evaluate"
    INJECT = "inject"
    GET_CONSOLE_LOGS = "get_console_logs"


class ExecuteScriptInput(BaseModel):
    """Input model for unified script execution tool."""

    action: ScriptAction = Field(description="Script action to perform")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")
    script: Optional[str] = Field(None, description="JavaScript code to execute")
    expression: Optional[str] = Field(None, description="Expression to evaluate (for evaluate action)")
    library: Optional[str] = Field(None, description="Library to inject: jquery, lodash, axios, moment, custom")
    custom_url: Optional[str] = Field(None, description="Custom library URL (for inject action with custom library)")
    wait_for_execution: Optional[bool] = Field(True, description="Wait for execution to complete")
    return_result: Optional[bool] = Field(True, description="Return execution result")
    timeout: Optional[int] = Field(30, description="Execution timeout in seconds")
    context: Optional[str] = Field("page", description="Execution context: page, isolated")


class FileAction(str, Enum):
    """File operation actions."""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    MANAGE_DOWNLOADS = "manage_downloads"


class ManageFileInput(BaseModel):
    """Input model for unified file operations tool."""

    action: FileAction = Field(description="File operation action to perform")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")
    file_path: Optional[str] = Field(None, description="File path for upload/download")
    input_selector: Optional[Dict[str, Any]] = Field(None, description="File input selector for upload action")
    url: Optional[str] = Field(None, description="URL for download action")
    save_path: Optional[str] = Field(None, description="Save path for download action")
    download_action: Optional[str] = Field(None, description="Download management action: list, pause, resume, cancel")
    download_id: Optional[str] = Field(None, description="Download ID for manage_downloads action")
    wait_for_completion: Optional[bool] = Field(True, description="Wait for operation to complete")
    timeout: Optional[int] = Field(30, description="Operation timeout in seconds")


class ElementFindAction(str, Enum):
    """Element finding actions."""
    FIND = "find"
    FIND_ALL = "find_all"
    QUERY = "query"
    WAIT_FOR = "wait_for"
    GET_TEXT = "get_text"
    GET_ATTRIBUTE = "get_attribute"
    CHECK_VISIBILITY = "check_visibility"
    GET_PARENT = "get_parent"


class FindElementInput(BaseModel):
    """Input model for unified element finding tool."""

    action: ElementFindAction = Field(description="Element finding action to perform")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")
    selector: Dict[str, Any] = Field(description="Element selector dictionary")
    css_selector: Optional[str] = Field(None, description="CSS selector for query action")
    xpath: Optional[str] = Field(None, description="XPath for query action")
    find_all: Optional[bool] = Field(False, description="Find all matching elements")
    timeout: Optional[int] = Field(10, description="Timeout in seconds for wait_for action")
    wait_for_visible: Optional[bool] = Field(True, description="Wait for element to be visible")
    attribute_name: Optional[str] = Field(None, description="Attribute name for get_attribute action")
    search_shadow_dom: Optional[bool] = Field(False, description="Search within shadow DOM")


class DialogAction(str, Enum):
    """Page dialog interaction actions."""
    HANDLE_DIALOG = "handle_dialog"
    HANDLE_ALERT = "handle_alert"


class InteractPageInput(BaseModel):
    """Input model for unified page interaction tool (dialogs)."""

    action: DialogAction = Field(description="Dialog action to perform")
    browser_id: str = Field(description="Browser instance ID")
    tab_id: Optional[str] = Field(None, description="Tab ID, uses active tab if not specified")
    accept: Optional[bool] = Field(True, description="Whether to accept or dismiss the dialog")
    prompt_text: Optional[str] = Field(None, description="Text to enter into prompt dialog (for handle_dialog action)")

