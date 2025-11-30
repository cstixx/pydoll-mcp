# PyDoll Tools Guide

This guide provides a comprehensive overview of all available tools in the PyDoll MCP Server.

## Table of Contents

1.  [Unified Tools (Recommended)](#unified-tools-recommended) ⭐ NEW
2.  [Browser Management](#browser-management)
3.  [Navigation](#navigation)
4.  [Page Interaction](#page-interaction)
5.  [Element Interaction](#element-interaction)
6.  [Scripting & Automation](#scripting--automation)
7.  [Screenshots & PDF](#screenshots--pdf)
8.  [Network Control](#network-control)
9.  [Protection & Evasion](#protection--evasion)
10. [Advanced Tools](#advanced-tools)

---

## Unified Tools (Recommended) ⭐

**NEW in v1.6.0+**: PyDoll MCP Server now features **Unified Tools** - a streamlined architecture that consolidates ~50-60 granular tools into 10 powerful, action-based endpoints. These are **recommended for LLM usage** as they provide a cleaner, more intuitive API.

### Why Unified Tools?

- **Reduced Complexity**: 10 tools instead of 60+
- **Action-Based API**: Clear action parameter instead of separate tools
- **Better Error Context**: Rich debugging information with DOM snapshots
- **Backward Compatible**: Legacy tools remain available

### Available Unified Tools

1. **[`interact_element`](#interact_element)** - Element interactions (click, type, hover, press_key, drag, scroll)
2. **[`manage_tab`](#manage_tab)** - Tab management (create, close, refresh, activate, list, get_info)
3. **[`browser_control`](#browser_control)** - Browser lifecycle (start, stop, list, get_state, create_context, list_contexts, delete_context, grant_permissions, reset_permissions)
4. **[`execute_cdp_command`](#execute_cdp_command)** - Direct Chrome DevTools Protocol access
5. **[`navigate_page`](#navigate_page)** - Page navigation (navigate, go_back, go_forward, get_url, get_title, get_source, wait_load, wait_network_idle, set_viewport, get_info)
6. **[`capture_media`](#capture_media)** - Screenshots and PDFs (screenshot, element_screenshot, generate_pdf, save_page_as_pdf, save_pdf)
7. **[`execute_script`](#execute_script)** - Script execution (execute, evaluate, inject, get_console_logs)
8. **[`manage_file`](#manage_file)** - File operations (upload, download, manage_downloads)
9. **[`find_element`](#find_element)** - Element finding (find, find_all, query, wait_for, get_text, get_attribute, check_visibility, get_parent)
10. **[`interact_page`](#interact_page)** - Page dialogs (handle_dialog, handle_alert)

---

### `interact_element`

Unified tool for all element interactions. Consolidates click, type, hover, press_key, drag, and scroll operations.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Action to perform. Enum: `click`, `type`, `hover`, `press_key`, `drag`, `scroll` |
| `browser_id` | string | Yes | Browser instance ID |
| `tab_id` | string | No | Tab ID (uses active tab if not specified) |
| `selector` | object | Yes | Element selector dictionary (see below) |
| `value` | string | No | Value for `type` action or key for `press_key` action |
| `key` | string | No | Key for `press_key` action (e.g., 'Enter', 'Escape', 'Control+c') |
| `click_type` | string | No | Click type: `left`, `right`, `double`, `middle` (default: `left`) |
| `scroll_to_element` | boolean | No | Scroll element into view before action (default: `true`) |
| `human_like` | boolean | No | Use human-like behavior (default: `true`) |
| `typing_speed` | string | No | Typing speed: `slow`, `normal`, `fast`, `instant` (default: `normal`) |
| `clear_first` | boolean | No | Clear existing text before typing (default: `true`) |

**Selector Object:**

The `selector` parameter accepts various ways to identify elements:

```json
{
  "id": "submit-button",
  "class_name": "btn-primary",
  "tag_name": "button",
  "text": "Submit",
  "name": "submitBtn",
  "type": "submit",
  "placeholder": "Enter text",
  "value": "Click me",
  "data_testid": "submit-btn",
  "data_id": "submit-123",
  "aria_label": "Submit form",
  "aria_role": "button",
  "css_selector": "button.submit",
  "xpath": "//button[@class='submit']"
}
```

**Action Examples:**

**Click Action:**
```json
{
  "tool": "interact_element",
  "arguments": {
    "action": "click",
    "browser_id": "browser-1",
    "selector": {"css_selector": "button.submit"},
    "click_type": "left"
  }
}
```

**Type Action:**
```json
{
  "tool": "interact_element",
  "arguments": {
    "action": "type",
    "browser_id": "browser-1",
    "selector": {"id": "search-input"},
    "value": "Hello, World!",
    "clear_first": true,
    "typing_speed": "normal"
  }
}
```

**Hover Action:**
```json
{
  "tool": "interact_element",
  "arguments": {
    "action": "hover",
    "browser_id": "browser-1",
    "selector": {"class_name": "dropdown-trigger"}
  }
}
```

**Press Key Action:**
```json
{
  "tool": "interact_element",
  "arguments": {
    "action": "press_key",
    "browser_id": "browser-1",
    "key": "Enter"
  }
}
```

**Returns:**
An `OperationResult` object with success status and operation details.

---

### `manage_tab`

Unified tool for tab management operations. Consolidates create, close, refresh, activate, list, and get_info operations.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Action to perform. Enum: `create`, `close`, `refresh`, `activate`, `list`, `get_info` |
| `browser_id` | string | Yes | Browser instance ID |
| `tab_id` | string | No | Tab ID (required for close, refresh, activate, get_info) |
| `url` | string | No | URL for `create` action |
| `background` | boolean | No | Open tab in background (default: `false`) |
| `wait_for_load` | boolean | No | Wait for page to load (default: `true`) |
| `ignore_cache` | boolean | No | Ignore cache on refresh (default: `false`) |

**Action Examples:**

**Create Tab:**
```json
{
  "tool": "manage_tab",
  "arguments": {
    "action": "create",
    "browser_id": "browser-1",
    "url": "https://example.com",
    "background": false
  }
}
```

**Close Tab:**
```json
{
  "tool": "manage_tab",
  "arguments": {
    "action": "close",
    "browser_id": "browser-1",
    "tab_id": "tab-123"
  }
}
```

**Refresh Tab:**
```json
{
  "tool": "manage_tab",
  "arguments": {
    "action": "refresh",
    "browser_id": "browser-1",
    "tab_id": "tab-123",
    "ignore_cache": true
  }
}
```

**Activate Tab:**
```json
{
  "tool": "manage_tab",
  "arguments": {
    "action": "activate",
    "browser_id": "browser-1",
    "tab_id": "tab-123"
  }
}
```

**List Tabs:**
```json
{
  "tool": "manage_tab",
  "arguments": {
    "action": "list",
    "browser_id": "browser-1"
  }
}
```

**Get Tab Info:**
```json
{
  "tool": "manage_tab",
  "arguments": {
    "action": "get_info",
    "browser_id": "browser-1",
    "tab_id": "tab-123"
  }
}
```

**Returns:**
An `OperationResult` object with tab information or operation status.

---

### `browser_control`

Unified tool for browser lifecycle management. Consolidates start, stop, list, get_state, and reattach operations.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Action to perform. Enum: `start`, `stop`, `list`, `get_state`, `reattach` |
| `browser_id` | string | No | Browser ID (required for stop, get_state, reattach) |
| `config` | object | No | Browser configuration for `start` action (see below) |

**Browser Config Object (for `start` action):**

```json
{
  "browser_type": "chrome",
  "headless": false,
  "window_width": 1920,
  "window_height": 1080,
  "stealth_mode": true,
  "proxy_server": "host:port",
  "user_agent": "Custom User Agent"
}
```

**Action Examples:**

**Start Browser:**
```json
{
  "tool": "browser_control",
  "arguments": {
    "action": "start",
    "config": {
      "browser_type": "chrome",
      "headless": false,
      "stealth_mode": true
    }
  }
}
```

**Stop Browser:**
```json
{
  "tool": "browser_control",
  "arguments": {
    "action": "stop",
    "browser_id": "browser-1"
  }
}
```

**List Browsers:**
```json
{
  "tool": "browser_control",
  "arguments": {
    "action": "list"
  }
}
```

**Get Browser State:**
```json
{
  "tool": "browser_control",
  "arguments": {
    "action": "get_state",
    "browser_id": "browser-1"
  }
}
```

**Returns:**
An `OperationResult` object with browser information or operation status.

---

### `execute_cdp_command`

Direct access to Chrome DevTools Protocol (CDP) commands. Provides an "escape hatch" for advanced operations not covered by other tools.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `browser_id` | string | Yes | Browser instance ID |
| `tab_id` | string | No | Tab ID (uses active tab if not specified) |
| `domain` | string | Yes | CDP domain (e.g., 'Page', 'Network', 'DOM', 'Runtime') |
| `method` | string | Yes | CDP method within the domain (e.g., 'navigate', 'enable') |
| `params` | object | No | Parameters for the CDP method (default: `{}`) |

**Example:**

**Navigate using CDP:**
```json
{
  "tool": "execute_cdp_command",
  "arguments": {
    "browser_id": "browser-1",
    "domain": "Page",
    "method": "navigate",
    "params": {
      "url": "https://example.com"
    }
  }
}
```

**Enable Network Domain:**
```json
{
  "tool": "execute_cdp_command",
  "arguments": {
    "browser_id": "browser-1",
    "domain": "Network",
    "method": "enable",
    "params": {}
  }
}
```

**Execute JavaScript:**
```json
{
  "tool": "execute_cdp_command",
  "arguments": {
    "browser_id": "browser-1",
    "domain": "Runtime",
    "method": "evaluate",
    "params": {
      "expression": "document.title"
    }
  }
}
```

**Returns:**
An `OperationResult` object with the CDP command result.

**Available CDP Domains:**
- `Page` - Page navigation and lifecycle
- `Network` - Network monitoring and control
- `DOM` - DOM manipulation and querying
- `Runtime` - JavaScript execution
- `Debugger` - Debugging support
- `Performance` - Performance metrics
- And many more... (see [Chrome DevTools Protocol documentation](https://chromedevtools.github.io/devtools-protocol/))

---

## Legacy Tools

The following sections document the legacy granular tools. These remain available for backward compatibility, but **we recommend using the Unified Tools** for new implementations.

---

## Browser Management

Tools for managing browser instances, tabs, and contexts.

### `start_browser`
Start a new browser instance with specified configuration.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `block_ads` | boolean | No | `true` | Block advertisement requests. |
| `browser_type` | string | No | `chrome` | Type of browser to start. Enum: `chrome`, `edge`. |
| `custom_args` | array | No | | Additional browser command line arguments. |
| `disable_images` | boolean | No | `false` | Disable image loading for faster browsing. |
| `headless` | boolean | No | `false` | Run browser in headless mode. |
| `proxy_server` | string | No | | Proxy server in format host:port. |
| `start_timeout` | integer | No | `30` | Browser startup timeout in seconds. |
| `stealth_mode` | boolean | No | `true` | Enable stealth mode to avoid detection. |
| `user_agent` | string | No | | Custom user agent string. |
| `window_height`| integer | No | `1080` | Browser window height in pixels. |
| `window_width` | integer | No | `1920` | Browser window width in pixels. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains:
- `browser_id`: ID of the new browser instance.
- `browser_type`: Type of browser started.
- `created_at`: Timestamp of browser creation.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_start_browser

result = await handle_start_browser({
    "browser_type": "chrome",
    "headless": True,
    "stealth_mode": True
})
# result is an OperationResult object
if result.success:
    print("Browser started:", result.data["browser_id"])
```

### `stop_browser`
Stop a browser instance and clean up resources.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID to stop. |
| `force` | boolean | No | `false` | Force stop even if tabs are open. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `browser_id` of the stopped instance.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_stop_browser

result = await handle_stop_browser({
    "browser_id": "your-browser-id",
    "force": True
})
if result.success:
    print("Browser stopped:", result.data["browser_id"])
```

### `list_browsers`
List all active browser instances with their status.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `include_stats`| boolean | No | `true` | Include performance statistics. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains:
- `browsers`: A list of browser instance details.
- `count`: The number of active browsers.
- `global_stats`: Global performance statistics if `include_stats` is true.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_list_browsers

result = await handle_list_browsers({
    "include_stats": True
})
if result.success:
    print(f"Found {result.data['count']} browsers.")
    for browser in result.data['browsers']:
        print(f"- {browser['browser_id']} ({browser['status']})")
```

### `get_browser_status`
Get detailed status information for a specific browser.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains a dictionary with the detailed status of the browser instance.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_get_browser_status

result = await handle_get_browser_status({
    "browser_id": "your-browser-id"
})
if result.success:
    print("Browser status:", result.data)
```

### `new_tab`
Create a new tab in a browser instance.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `background` | boolean | No | `false` | Open tab in background. |
| `url` | string | No | | Optional URL to navigate to immediately. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `tab_id` of the newly created tab.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_new_tab

result = await handle_new_tab({
    "browser_id": "your-browser-id",
    "url": "https://example.com",
    "background": False
})
if result.success:
    print("New tab created:", result.data["tab_id"])
```

### `close_tab`
Close a specific tab in a browser.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | Yes | | Tab ID to close. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `tab_id` of the closed tab.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_close_tab

result = await handle_close_tab({
    "browser_id": "your-browser-id",
    "tab_id": "your-tab-id"
})
if result.success:
    print("Tab closed:", result.data["tab_id"])
```

### `list_tabs`
List all tabs in a browser instance.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `include_content` | boolean | No | `false` | Include page content information. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains:
- `tabs`: A list of tab information objects.
- `count`: The number of open tabs.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_list_tabs

result = await handle_list_tabs({
    "browser_id": "your-browser-id"
})
if result.success:
    print(f"Found {result.data['count']} tabs.")
    for tab in result.data['tabs']:
        print(f"- {tab['tab_id']}: {tab['title']}")
```

### `set_active_tab`
Switch to a specific tab in a browser.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | Yes | | Tab ID to activate. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `tab_id` that was activated.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_set_active_tab

result = await handle_set_active_tab({
    "browser_id": "your-browser-id",
    "tab_id": "your-tab-id"
})
if result.success:
    print("Active tab set to:", result.data["tab_id"])
```

### `bring_tab_to_front`
Bring a tab to the front (activate it) in the browser window for multi-tab focus management.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | Yes | | Tab ID to bring to front. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `tab_id` and `browser_id`.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_bring_tab_to_front

result = await handle_bring_tab_to_front({
    "browser_id": "your-browser-id",
    "tab_id": "your-tab-id"
})
if result.success:
    print("Tab brought to front:", result.data["tab_id"])
```

### `set_download_behavior`
Set browser download behavior (allow, deny, or prompt).

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `behavior` | string | Yes | | Download behavior: `allow`, `deny`, or `prompt`. |
| `download_path`| string | No | | Optional default download directory path. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `browser_id`, `behavior`, and `download_path`.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_set_download_behavior

result = await handle_set_download_behavior({
    "browser_id": "your-browser-id",
    "behavior": "allow",
    "download_path": "/path/to/downloads"
})
if result.success:
    print("Download behavior set:", result.data)
```

### `set_download_path`
Set default download directory for browser.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `path` | string | Yes | | Directory path for downloads. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `browser_id` and the absolute `path` that was set.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_set_download_path

result = await handle_set_download_path({
    "browser_id": "your-browser-id",
    "path": "/path/to/downloads"
})
if result.success:
    print("Download path set to:", result.data["path"])
```

### `enable_file_chooser_interception`
Enable file chooser dialog interception for file upload automation.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object confirming the action, with `browser_id` and `tab_id` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_enable_file_chooser_interception

result = await handle_enable_file_chooser_interception({
    "browser_id": "your-browser-id"
})
if result.success:
    print("File chooser interception enabled.")
```

### `disable_file_chooser_interception`
Disable file chooser dialog interception.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object confirming the action, with `browser_id` and `tab_id` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_disable_file_chooser_interception

result = await handle_disable_file_chooser_interception({
    "browser_id": "your-browser-id"
})
if result.success:
    print("File chooser interception disabled.")
```

### `create_browser_context`
Create a new browser context (isolated profile) for multi-profile automation.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `context_name` | string | No | | Optional name for the context. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `context_id`, and `context_name`.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_create_browser_context

result = await handle_create_browser_context({
    "browser_id": "your-browser-id",
    "context_name": "MyTestContext"
})
if result.success:
    print("Browser context created:", result.data["context_id"])
```

### `list_browser_contexts`
List all browser contexts for a browser instance.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, a `contexts` list, and `count`.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_list_browser_contexts

result = await handle_list_browser_contexts({
    "browser_id": "your-browser-id"
})
if result.success:
    print(f"Found {result.data['count']} browser contexts.")
```

### `delete_browser_context`
Delete a browser context.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `context_id` | string | Yes | | Context ID to delete. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id` and `context_id`.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_delete_browser_context

result = await handle_delete_browser_context({
    "browser_id": "your-browser-id",
    "context_id": "your-context-id"
})
if result.success:
    print("Browser context deleted:", result.data["context_id"])
```

### `grant_permissions`
Grant browser permissions (camera, microphone, geolocation, etc.) to a specific origin.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `origin` | string | Yes | | URL origin to grant permissions for. |
| `permissions`| array | Yes | | List of permissions to grant. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `origin`, and the list of `permissions` granted.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_grant_permissions

result = await handle_grant_permissions({
    "browser_id": "your-browser-id",
    "origin": "https://example.com",
    "permissions": ["geolocation", "camera"]
})
if result.success:
    print("Permissions granted for:", result.data["origin"])
```

### `reset_permissions`
Reset browser permissions for a specific origin or all origins.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `origin` | string | No | | Optional URL origin to reset permissions for. If not provided, resets all permissions. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id` and the `origin` affected.

**Python Example:**
```python
from pydoll_mcp.tools.browser_tools import handle_reset_permissions

result = await handle_reset_permissions({
    "browser_id": "your-browser-id",
    "origin": "https://example.com"
})
if result.success:
    print("Permissions reset for:", result.data["origin"])
```

### Usage Examples

**AI Assistant Prompts:**

> "Start a new Chrome browser instance in headless mode"
> "List all currently running browsers and their status"
> "Create a new tab in the browser"
> "Close the current tab and stop the browser"

**Python (Programmatic Usage):**

```python
# Start browser
browser_result = await handle_start_browser({
    "browser_type": "chrome",
    "headless": True
})
browser_data = json.loads(browser_result[0].text)
if browser_data["success"]:
    browser_id = browser_data["data"]["browser_id"]
    print(f"Browser started: {browser_id}")

    # Stop browser
    stop_result = await handle_stop_browser({
        "browser_id": browser_id
    })
    if json.loads(stop_result[0].text)["success"]:
        print("Browser stopped successfully")
```

---

## Navigation

Tools for controlling browser navigation.

### `navigate_to`
Navigate to a specific URL in a browser tab.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `url` | string | Yes | | URL to navigate to. |
| `referrer` | string | No | | Optional referrer URL. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |
| `timeout` | integer | No | `30` | Navigation timeout in seconds. |
| `wait_for_load`| boolean | No | `true` | Wait for page to fully load. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains:
- `browser_id`, `tab_id`, `requested_url`, `final_url`, `page_title`, and a `redirected` boolean.

**Python Example:**
```python
from pydoll_mcp.tools.navigation_tools import handle_navigate_to

result = await handle_navigate_to({
    "browser_id": "your-browser-id",
    "url": "https://example.com",
    "wait_for_load": True
})
if result.success:
    print("Navigated to:", result.data["final_url"])
```

### `refresh_page`
Refresh the current page in a browser tab.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `ignore_cache` | boolean | No | `false` | Force refresh ignoring cache. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |
| `wait_for_load`| boolean | No | `true` | Wait for page to reload. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `tab_id`, `url`, `title`, and `ignore_cache`.

**Python Example:**
```python
from pydoll_mcp.tools.navigation_tools import handle_refresh_page

result = await handle_refresh_page({
    "browser_id": "your-browser-id",
    "ignore_cache": True
})
if result.success:
    print("Page refreshed:", result.data["url"])
```

### `go_back`
Navigate back in browser history.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `steps` | integer | No | `1` | Number of steps to go back. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `tab_id`, `steps`, `current_url`, and `current_title`.

**Python Example:**
```python
from pydoll_mcp.tools.navigation_tools import handle_go_back

result = await handle_go_back({
    "browser_id": "your-browser-id",
    "steps": 1
})
if result.success:
    print("Navigated back to:", result.data["current_url"])
```

### Usage Examples

**AI Assistant Prompts:**

> "Navigate to https://example.com"
> "Go to the GitHub homepage and wait for it to load completely"
> "Refresh the current page"
> "Go back to the previous page in browser history"

**Python (Programmatic Usage):**

```python
# Navigate to page
nav_result = await handle_navigate_to({
    "browser_id": browser_id,
    "url": "https://example.com"
})

if json.loads(nav_result[0].text)["success"]:
    print("Navigation successful")
```

---

## Page Interaction

Tools for interacting with and getting information from web pages.

### `get_current_url`
Get the current URL of a browser tab.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `tab_id`, and the current `url`.

**Python Example:**
```python
from pydoll_mcp.tools.page_tools import handle_get_current_url

result = await handle_get_current_url({
    "browser_id": "your-browser-id"
})
if result.success:
    print("Current URL:", result.data["url"])
```

### `get_page_title`
Get the title of the current page.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `tab_id`, `title`, and `url`.

**Python Example:**
```python
from pydoll_mcp.tools.page_tools import handle_get_page_title

result = await handle_get_page_title({
    "browser_id": "your-browser-id"
})
if result.success:
    print("Page title:", result.data["title"])
```

### `get_page_source`
Get the HTML source code of the current page.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `include_resources` | boolean | No | `false` | Include information about page resources. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `tab_id`, `url`, `title`, `source`, `length`, and optional `resources` info.

**Python Example:**
```python
from pydoll_mcp.tools.page_tools import handle_get_page_source

result = await handle_get_page_source({
    "browser_id": "your-browser-id"
})
if result.success:
    print(f"Page source length: {result.data['length']} characters")
```

### `scroll`
Scroll the page in various directions or to specific positions/elements.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `direction` | string | Yes | `down` | Scroll direction or mode. |
| `amount` | integer | No | | Number of pixels to scroll (for up/down/left/right). |
| `behavior` | string | No | `smooth` | Scroll behavior: `auto`, `smooth`, `instant`. |
| `element_selector` | object | No | | Element selector for `to_element`. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |
| `x` | integer | No | | X coordinate for `to_position`. |
| `y` | integer | No | | Y coordinate for `to_position`. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `tab_id`, `direction`, `amount`, `scroll_position`, and `behavior`.

**Python Example:**
```python
from pydoll_mcp.tools.page_tools import handle_scroll

result = await handle_scroll({
    "browser_id": "your-browser-id",
    "direction": "to_bottom"
})
if result.success:
    print("Scrolled to position:", result.data["scroll_position"])
```

### `get_frame`
Get access to an iframe/frame element for operations within the frame.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `frame_selector` | string | Yes | | Frame selector: CSS selector, XPath, name attribute, or id attribute. |
| `selector_type` | string | No | `css` | Type of frame selector: `css`, `xpath`, `name`, `id`. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `browser_id`, `tab_id`, `frame_selector`, and `frame` info.

**Python Example:**
```python
from pydoll_mcp.tools.page_tools import handle_get_frame

result = await handle_get_frame({
    "browser_id": "your-browser-id",
    "frame_selector": "#my-iframe",
    "selector_type": "css"
})
if result.success:
    print("Got frame:", result.data["frame"])
```

### `handle_dialog`
Handle JavaScript dialogs like alert, confirm, or prompt.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID |
| `tab_id` | string | No | | Optional tab ID |
| `accept` | boolean | No | true | Whether to accept or dismiss the dialog. |
| `prompt_text` | string | No | | Text to enter into the prompt dialog. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains details of the handled dialog.

**Python Example:**
```python
from pydoll_mcp.tools.page_tools import handle_handle_dialog

# This should be called when a dialog is expected
result = await handle_handle_dialog({
    "browser_id": "your-browser-id",
    "accept": True,
    "prompt_text": "Optional text for prompt dialogs"
})
if result.success:
    print("Dialog handled successfully.")
```

### Usage Examples

**AI Assistant Prompts:**

> "Get the current page URL and title"
> "Extract all the text content from the page"
> "Get all image URLs from the current page"
> "Scroll down to the bottom of the page"

---

## Element Interaction

Tools for finding and interacting with elements on a page.

### `find_element`
Find a web element using natural attributes or traditional selectors.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `aria_label` | string | No | | aria-label attribute. |
| `aria_role` | string | No | | aria-role attribute. |
| `class_name` | string | No | | CSS class name. |
| `css_selector` | string | No | | CSS selector string. |
| `data_id` | string | No | | data-id attribute. |
| `data_testid` | string | No | | data-testid attribute. |
| `find_all` | boolean | No | `false` | Find all matching elements. |
| `id` | string | No | | Element ID attribute. |
| `name` | string | No | | Element name attribute. |
| `placeholder` | string | No | | Input placeholder text. |
| `search_shadow_dom`| boolean | No | `false` | Search within shadow DOM elements. |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |
| `tag_name` | string | No | | HTML tag name. |
| `text` | string | No | | Element text content. |
| `timeout` | integer | No | `10` | Element search timeout in seconds. |
| `type` | string | No | | Element type attribute (for inputs). |
| `value` | string | No | | Element value attribute. |
| `wait_for_visible` | boolean | No | `true` | Wait for element to be visible. |
| `xpath` | string | No | | XPath expression. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains a list of found `elements` and their details.

**Python Example:**
```python
from pydoll_mcp.tools.element_tools import handle_find_element

result = await handle_find_element({
    "browser_id": "your-browser-id",
    "css_selector": "button.submit",
    "find_all": False
})
if result.success:
    print(f"Found {result.data['count']} element(s).")
```

### `click_element`
Click on a web element with human-like behavior.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `element_selector` | object | Yes | | Element selector. |
| `click_type` | string | No | `left` | Type of click: `left`, `right`, `double`, `middle`. |
| `force` | boolean | No | `false` | Force click even if element is not clickable. |
| `human_like` | boolean | No | `true` | Use human-like click behavior. |
| `offset_x` | integer | No | | X offset from element center. |
| `offset_y` | integer | No | | Y offset from element center. |
| `scroll_to_element` | boolean | No | `true` | Scroll element into view before clicking. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object confirming the click, with details of the clicked `element` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.element_tools import handle_click_element

result = await handle_click_element({
    "browser_id": "your-browser-id",
    "element_selector": {"text": "Submit"}
})
if result.success:
    print("Element clicked:", result.data["element"])
```

### `type_text`
Type text into an input element with realistic human typing.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `element_selector` | object | Yes | | Element selector. |
| `text` | string | Yes | | Text to type. |
| `clear_first` | boolean | No | `true` | Clear existing text before typing. |
| `human_like` | boolean | No | `true` | Use human-like typing. |
| `tab_id` | string | No | | Optional tab ID. |
| `typing_speed` | string | No | `normal` | Typing speed: `slow`, `normal`, `fast`, `instant`. |

**Returns:**
An `OperationResult` object confirming the text was typed, with details of the `element` and `text` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.element_tools import handle_type_text

result = await handle_type_text({
    "browser_id": "your-browser-id",
    "element_selector": {"name": "username"},
    "text": "testuser"
})
if result.success:
    print("Text typed into element:", result.data["element"])
```

### `get_parent_element`
Get the parent element of a specific element with its attributes.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `element_selector` | object | Yes | | Element selector. |
| `include_attributes` | boolean | No | `true` | Include all attributes of the parent element. |
| `include_bounds` | boolean | No | `true` | Include bounding box information. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains information about the parent element.

**Python Example:**
```python
from pydoll_mcp.tools.element_tools import handle_get_parent_element

result = await handle_get_parent_element({
    "browser_id": "your-browser-id",
    "element_selector": {"id": "child-element"}
})
if result.success:
    print("Parent element:", result.data)
```

### `find_or_wait_element`
Find an element with automatic waiting and polling until it appears or timeout.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `poll_interval` | number | No | `0.5` | Time between polling attempts in seconds. |
| `tab_id` | string | No | | Optional tab ID. |
| `timeout` | integer | No | `30` | Maximum time to wait for element in seconds. |
| `wait_for_visible` | boolean | No | `true` | Wait for element to be visible. |
| *Other params* | | | | Accepts same selector params as `find_element`. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the found `element`'s details.

**Python Example:**
```python
from pydoll_mcp.tools.element_tools import handle_find_or_wait_element

result = await handle_find_or_wait_element({
    "browser_id": "your-browser-id",
    "css_selector": "#dynamic-content",
    "timeout": 15
})
if result.success:
    print("Dynamically loaded element found:", result.data["element"])
```

### `query`
Query elements using CSS selector or XPath.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `css_selector` | string | No | | CSS selector string. |
| `find_all` | boolean | No | `false` | Find all matching elements. |
| `tab_id` | string | No | | Optional tab ID. |
| `xpath` | string | No | | XPath expression. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains a list of found `elements` and their details.

**Python Example:**
```python
from pydoll_mcp.tools.element_tools import handle_query

result = await handle_query({
    "browser_id": "your-browser-id",
    "css_selector": "div.item",
    "find_all": True
})
if result.success:
    print(f"Query found {result.data['count']} elements.")
```

### `press_key`
Press keyboard keys or key combinations.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `key` | string | Yes | | Key to press (e.g., 'Enter', 'Control+c'). |
| `element_selector` | object | No | | Optional element selector to focus before pressing key. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object confirming the key press, with `key` and whether an `element_focused` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.element_tools import handle_press_key

result = await handle_press_key({
    "browser_id": "your-browser-id",
    "key": "Enter",
    "element_selector": {"name": "search"}
})
if result.success:
    print("Pressed 'Enter' key.")
```

### Usage Examples

**AI Assistant Prompts:**

> "Find the search box on the page and type 'PyDoll MCP'"
> "Click the submit button on the form"
> "Find all links on the page and show their text and URLs"
> "Hover over the navigation menu"

---

## Scripting & Automation

Tools for executing scripts and managing automation.

### `execute_javascript`
Execute JavaScript code in the browser context.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `script` | string | Yes | | JavaScript code to execute. |
| `context` | string | No | `page` | Execution context: `page` or `isolated`. |
| `return_result` | boolean | No | `true` | Return the result of script execution. |
| `tab_id` | string | No | | Optional tab ID. |
| `timeout` | integer | No | `30` | Execution timeout in seconds. |
| `wait_for_execution` | boolean | No | `true` | Wait for script execution to complete. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `result` of the script, its `result_type`, and execution context details.

**Python Example:**
```python
from pydoll_mcp.tools.script_tools import handle_execute_javascript

result = await handle_execute_javascript({
    "browser_id": "your-browser-id",
    "script": "return document.title;"
})
if result.success:
    print("Script result (page title):", result.data["result"])
```

### `execute_automation_script`
Execute predefined automation scripts.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `script_name` | string | Yes | | Name of the predefined automation script. |
| `parameters` | object | No | | Parameters to pass to the automation script. |
| `step_by_step` | boolean | No | `false` | Execute automation step by step with confirmations. |
| `tab_id` | string | No | | Optional tab ID. |
| `wait_for_completion` | boolean | No | `true` | Wait for automation to complete. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `script_name`, `parameters`, and a `result` object from the script.

**Python Example:**
```python
from pydoll_mcp.tools.script_tools import handle_execute_automation_script

result = await handle_execute_automation_script({
    "browser_id": "your-browser-id",
    "script_name": "login_workflow",
    "parameters": {"username": "test", "password": "password"}
})
if result.success:
    print("Automation script executed:", result.data["result"])
```

### `inject_script_library`
Inject JavaScript libraries into the page.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `library` | string | Yes | | JS library to inject: `jquery`, `lodash`, `axios`, `moment`, `custom`. |
| `custom_url` | string | No | | Custom URL for library injection (if library is 'custom'). |
| `tab_id` | string | No | | Optional tab ID. |
| `version` | string | No | | Specific version of the library. |
| `wait_for_load`| boolean | No | `true` | Wait for library to load completely. |

**Returns:**
An `OperationResult` object confirming injection, with `library`, `version`, and `url` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.script_tools import handle_inject_script_library

result = await handle_inject_script_library({
    "browser_id": "your-browser-id",
    "library": "jquery",
    "version": "3.6.0"
})
if result.success:
    print("jQuery injected successfully.")
```

### Usage Examples

**AI Assistant Prompts:**

> "Execute JavaScript to modify the page content"
> "Fill out the contact form with test data and submit it"
> "Perform a search on Google for 'browser automation'"

**Python (Programmatic Usage):**

```python
# Extract table data using JavaScript
js_script = """
    const tables = document.querySelectorAll('table');
    const data = [];
    tables.forEach(table => {
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        rows.forEach(row => {
            const cells = Array.from(row.querySelectorAll('td'));
            const rowData = {};
            cells.forEach((cell, index) => {
                if (headers[index]) {
                    rowData[headers[index]] = cell.textContent.trim();
                }
            });
            data.push(rowData);
        });
    });
    return data;
"""
table_data_result = await execute_javascript({
    "browser_id": browser_id,
    "script": js_script
})
```

---

## Screenshots & PDF

Tools for capturing screenshots and generating PDFs.

### `take_screenshot`
Take a screenshot of the current page or viewport.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `clip_area` | object | No | | Specific area to capture (x, y, width, height). |
| `file_name` | string | No | | Custom filename for saved screenshot. |
| `format` | string | No | `png` | Image format: `png`, `jpeg`, `jpg`. |
| `full_page` | boolean | No | `false` | Capture entire page content, not just viewport. |
| `hide_scrollbars` | boolean | No | `true` | Hide scrollbars in screenshot. |
| `quality` | integer | No | | JPEG quality (1-100). |
| `return_base64`| boolean | No | `false` | Return screenshot as base64 encoded string. |
| `save_to_file` | boolean | No | `true` | Save screenshot to file. |
| `tab_id` | string | No | | Optional tab ID. |
| `viewport_only`| boolean | No | `true` | Capture only the current viewport. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains screenshot metadata like `file_path`, `file_size`, dimensions, and optionally the `base64_data`.

**Python Example:**
```python
from pydoll_mcp.tools.screenshot_tools import handle_take_screenshot

result = await handle_take_screenshot({
    "browser_id": "your-browser-id",
    "full_page": True,
    "save_to_file": True
})
if result.success:
    print("Screenshot saved to:", result.data["file_path"])
```

### `take_element_screenshot`
Take a screenshot of a specific element.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `element_selector` | object | Yes | | Element selector. |
| `file_name` | string | No | | Custom filename for saved screenshot. |
| `format` | string | No | `png` | Image format. |
| `padding` | integer | No | `0` | Extra padding around element in pixels. |
| `quality` | integer | No | | JPEG quality (1-100). |
| `return_base64`| boolean | No | `false` | Return screenshot as base64 encoded string. |
| `save_to_file` | boolean | No | `true` | Save screenshot to file. |
| `scroll_into_view` | boolean | No | `true` | Scroll element into view before capturing. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains screenshot metadata including `file_path` and `element_bounds`.

**Python Example:**
```python
from pydoll_mcp.tools.screenshot_tools import handle_take_element_screenshot

result = await handle_take_element_screenshot({
    "browser_id": "your-browser-id",
    "element_selector": {"css_selector": "#main-banner"}
})
if result.success:
    print("Element screenshot saved to:", result.data["file_path"])
```

### `generate_pdf`
Generate a PDF of the current page.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `display_header_footer` | boolean | No | `false` | Display header and footer. |
| `file_name` | string | No | | Custom filename for PDF. |
| `footer_template` | string | No | | HTML template for page footer. |
| `format` | string | No | `A4` | Page format. |
| `header_template` | string | No | | HTML template for page header. |
| `include_background` | boolean | No | `true` | Include background graphics. |
| `margins` | object | No | | Page margins. |
| `orientation` | string | No | `portrait`| Page orientation. |
| `print_media` | boolean | No | `false` | Use print media CSS. |
| `scale` | number | No | `1` | Scale factor for PDF generation. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains PDF metadata including `file_path`, `file_size`, and `pages`.

**Python Example:**
```python
from pydoll_mcp.tools.screenshot_tools import handle_generate_pdf

result = await handle_generate_pdf({
    "browser_id": "your-browser-id",
    "file_name": "mypage.pdf",
    "orientation": "landscape"
})
if result.success:
    print("PDF saved to:", result.data["file_path"])
```

### Usage Examples

**AI Assistant Prompts:**

> "Take a screenshot of the entire page"
> "Capture a screenshot of just the header section"
> "Generate a PDF of the current page"

**Python (Programmatic Usage):**

```python
# Take screenshot
screenshot_result = await handle_take_screenshot({
    "browser_id": browser_id,
    "format": "png",
    "save_to_file": True
})

screenshot_data = json.loads(screenshot_result[0].text)
if screenshot_data["success"]:
    print(f"Screenshot saved: {screenshot_data['data'].get('file_path')}")
```

---

## Network Control

Tools for monitoring and manipulating network activity.

### `get_network_logs`
Retrieve detailed network activity logs.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `filter` | object | No | | Filter logs by `resource_type` or `status_code`. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains a `logs` list and `count`.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_get_network_logs

result = await handle_get_network_logs({
    "browser_id": "your-browser-id",
    "filter": {"resource_type": "xhr"}
})
if result.success:
    print(f"Found {result.data['count']} XHR requests.")
```

### `get_network_response_body`
Get the response body for a specific network request.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `request_id` | string | No | | Request ID from network logs. |
| `tab_id` | string | No | | Optional tab ID. |
| `url` | string | No | | URL of the request (alternative to `request_id`). |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `response_body` and `body_size`.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_get_network_response_body

# request_id is obtained from get_network_logs
result = await handle_get_network_response_body({
    "browser_id": "your-browser-id",
    "request_id": "your-request-id"
})
if result.success:
    print("Response body size:", result.data["body_size"])
```

### `block_requests`
Block specific network requests.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `patterns` | array | No | | URL patterns to block. |
| `resource_types` | array | No | | Resource types to block. |

**Returns:**
An `OperationResult` object confirming the block rules, with `patterns` and `resource_types` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_block_requests

result = await handle_block_requests({
    "browser_id": "your-browser-id",
    "patterns": ["*.google-analytics.com", "*.doubleclick.net"],
    "resource_types": ["image", "script"]
})
if result.success:
    print("Request blocking rules applied.")
```

### `modify_request_headers`
Modify HTTP request headers.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `headers` | object | No | | Headers to add or modify. |
| `remove_headers` | array | No | | Headers to remove. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `modified_headers` and `removed_headers`.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_modify_request_headers

result = await handle_modify_request_headers({
    "browser_id": "your-browser-id",
    "headers": {"X-Custom-Header": "PyDoll-Test"},
    "remove_headers": ["X-Powered-By"]
})
if result.success:
    print("Request headers modification rules applied.")
```

### `extract_api_responses`
Extract and save API responses.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `api_patterns` | array | No | | API URL patterns to monitor. |
| `save_to_file` | boolean | No | `false` | Save responses to files. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `extracted_count`, `saved_to_file`, and a list of `responses`.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_extract_api_responses

result = await handle_extract_api_responses({
    "browser_id": "your-browser-id",
    "api_patterns": ["/api/v1/*"],
    "save_to_file": True
})
if result.success:
    print(f"Extracted {result.data['extracted_count']} API responses.")
```

### `monitor_websockets`
Monitor WebSocket connections and messages.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `action` | string | Yes | | Action: `start`, `stop`, `get_messages`. |
| `filter_pattern` | string | No | | Filter messages by pattern. |

**Returns:**
An `OperationResult` object. The `data` field varies by action, providing status or a list of `messages`.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_monitor_websockets

# Start monitoring
await handle_monitor_websockets({"browser_id": "your-browser-id", "action": "start"})

# Get messages
result = await handle_monitor_websockets({"browser_id": "your-browser-id", "action": "get_messages"})
if result.success:
    print("WebSocket messages:", result.data["messages"])
```

### `throttle_network`
Simulate different network conditions.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `preset` | string | Yes | | Preset: `offline`, `slow-3g`, `fast-3g`, `4g`, `wifi`, `custom`. |
| `custom_settings` | object | No | | Custom settings for `download_throughput`, `upload_throughput`, `latency`. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `preset` and applied `settings`.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_throttle_network

result = await handle_throttle_network({
    "browser_id": "your-browser-id",
    "preset": "slow-3g"
})
if result.success:
    print("Network throttled to Slow 3G.")
```

### `clear_cache`
Clear browser cache and storage.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `cache_types` | array | No | `[all]` | Types of cache to clear. |

**Returns:**
An `OperationResult` object. On success, the `data` field lists the `cleared` cache types.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_clear_cache

result = await handle_clear_cache({
    "browser_id": "your-browser-id",
    "cache_types": ["all"]
})
if result.success:
    print("Browser cache cleared.")
```

### `save_har`
Save HTTP Archive (HAR) file of network activity.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `file_name` | string | Yes | | HAR file name. |
| `include_content` | boolean | No | `true` | Include response content in HAR. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `file_name`, `size`, and `include_content`.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_save_har

result = await handle_save_har({
    "browser_id": "your-browser-id",
    "file_name": "network_log.har"
})
if result.success:
    print("HAR file saved:", result.data["file_name"])
```

### `intercept_network_requests`
Intercept and modify network requests and responses.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `action` | string | Yes | | Interception action: `start`, `stop`, `configure`. |
| `block_patterns` | array | No | | Patterns to block completely. |
| `log_requests` | boolean | No | `true` | Log intercepted requests. |
| `modification_rules` | array | No | | Rules for modifying requests/responses. |
| `modify_requests` | boolean | No | `false` | Enable request modification. |
| `modify_responses` | boolean | No | `false` | Enable response modification. |
| `patterns` | array | No | | URL patterns to intercept. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object confirming the action (`started`, `stopped`, or `configured`) and current settings in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_intercept_network_requests

result = await handle_intercept_network_requests({
    "browser_id": "your-browser-id",
    "action": "start",
    "patterns": ["/api/*"]
})
if result.success:
    print("Network interception started for /api/*")
```

### `modify_request`
Modify an intercepted network request.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `request_id` | string | Yes | | Request ID from intercepted request. |
| `headers` | object | No | | New or modified headers. |
| `method` | string | No | | New HTTP method. |
| `post_data` | string | No | | New POST data. |
| `tab_id` | string | No | | Optional tab ID. |
| `url` | string | No | | New URL for the request. |

**Returns:**
An `OperationResult` object confirming the modification, with details of the `modifications` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_modify_request

# request_id from an intercepted request event
result = await handle_modify_request({
    "browser_id": "your-browser-id",
    "request_id": "intercepted-request-id",
    "headers": {"Authorization": "Bearer my-token"}
})
if result.success:
    print("Intercepted request modified.")
```

### `fulfill_request`
Fulfill an intercepted request with a custom response (mock response).

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `request_id` | string | Yes | | Request ID from intercepted request. |
| `status` | integer | Yes | | HTTP status code for the response. |
| `body` | string | No | | Response body. |
| `headers` | object | No | | Response headers. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object confirming fulfillment, with details of the response provided in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_fulfill_request

result = await handle_fulfill_request({
    "browser_id": "your-browser-id",
    "request_id": "intercepted-request-id",
    "status": 200,
    "body": "{\"mock\": \"response\"}",
    "headers": {"Content-Type": "application/json"}
})
if result.success:
    print("Request fulfilled with mock response.")
```

### `continue_with_auth`
Continue an intercepted request with HTTP authentication.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `request_id` | string | Yes | | Request ID from intercepted request. |
| `username` | string | Yes | | HTTP authentication username. |
| `password` | string | Yes | | HTTP authentication password. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object confirming the action, with `request_id` and `username` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_continue_with_auth

result = await handle_continue_with_auth({
    "browser_id": "your-browser-id",
    "request_id": "auth-request-id",
    "username": "user",
    "password": "pass"
})
if result.success:
    print("Request continued with authentication.")
```

### Event Monitoring
Tools to enable/disable DOM, network, page, fetch, and runtime events.

- **`enable_dom_events`** / **`disable_dom_events`**
- **`enable_network_events`** / **`disable_network_events`**
- **`enable_page_events`** / **`disable_page_events`**
- **`enable_fetch_events`** / **`disable_fetch_events`**
- **`enable_runtime_events`** / **`disable_runtime_events`**

All event monitoring tools take `browser_id` (required) and `tab_id` (optional).

**Returns:**
An `OperationResult` object confirming the action.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_enable_dom_events

result = await handle_enable_dom_events({
    "browser_id": "your-browser-id"
})
if result.success:
    print("DOM events enabled.")
```

### `get_event_status`
Get the current status of all event monitoring.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains an `event_status` object with the current state of all event monitors.

**Python Example:**
```python
from pydoll_mcp.tools.network_tools import handle_get_event_status

result = await handle_get_event_status({
    "browser_id": "your-browser-id"
})
if result.success:
    print("Event status:", result.data["event_status"])
```

### Usage Examples

**AI Assistant Prompts:**

> "Monitor all network requests while browsing"
> "Block all ad requests"
> "Throttle the network to simulate a slow 3G connection"

---

## Protection & Evasion

Tools for bypassing bot detection and appearing more human-like.

### `enable_stealth_mode`
Enable advanced stealth mode to avoid bot detection.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `level` | string | No | `advanced` | Stealth level: `basic`, `advanced`, `maximum`. |

**Returns:**
An `OperationResult` object confirming the action, with `stealth_level` and `enabled` status in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_enable_stealth_mode

result = await handle_enable_stealth_mode({
    "browser_id": "your-browser-id",
    "level": "maximum"
})
if result.success:
    print("Stealth mode enabled at maximum level.")
```

### `bypass_cloudflare`
Attempt to bypass Cloudflare Turnstile protection.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `auto_solve` | boolean | No | `true` | Enable automatic Cloudflare captcha solving. |
| `max_attempts` | integer | No | `3` | Maximum bypass attempts. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. The `data` field indicates `success`, `attempts`, and the `bypass_method` used.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_bypass_cloudflare

result = await handle_bypass_cloudflare({
    "browser_id": "your-browser-id",
    "max_attempts": 5
})
if result.success and result.data["success"]:
    print("Cloudflare bypassed successfully.")
```

### `enable_cloudflare_auto_solve` / `disable_cloudflare_auto_solve`
Enable or disable automatic Cloudflare captcha solving for a browser/tab.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object confirming the action.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_enable_cloudflare_auto_solve

result = await handle_enable_cloudflare_auto_solve({
    "browser_id": "your-browser-id"
})
if result.success:
    print("Cloudflare auto-solve enabled.")
```

### `bypass_recaptcha`
Attempt to bypass reCAPTCHA v3 protection.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `action` | string | No | `homepage`| reCAPTCHA action. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the bypass `score`, `action`, and a simulated `token`.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_bypass_recaptcha

result = await handle_bypass_recaptcha({
    "browser_id": "your-browser-id",
    "action": "login"
})
if result.success:
    print(f"reCAPTCHA bypass score: {result.data['score']}")
```

### `simulate_human_behavior`
Simulate realistic human interaction patterns.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `actions` | array | No | | Human behaviors to simulate. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains a list of `simulated_actions` and their outcomes.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_simulate_human_behavior

result = await handle_simulate_human_behavior({
    "browser_id": "your-browser-id",
    "actions": ["mouse_move", "scroll", "random_delay"]
})
if result.success:
    print("Human behavior simulation complete.")
```

### `randomize_fingerprint`
Randomize browser fingerprint to avoid tracking.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `components` | array | No | | Fingerprint components to randomize. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains a dictionary of the `randomized_components`.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_randomize_fingerprint

result = await handle_randomize_fingerprint({
    "browser_id": "your-browser-id",
    "components": ["canvas", "webgl", "fonts"]
})
if result.success:
    print("Browser fingerprint randomized.")
```

### `set_user_agent`
Set a custom or random user agent string.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `random` | boolean | No | `false` | Use random user agent. |
| `user_agent` | string | No | | Custom user agent string. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the new `user_agent`.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_set_user_agent

result = await handle_set_user_agent({
    "browser_id": "your-browser-id",
    "random": True
})
if result.success:
    print("Using random user agent:", result.data["user_agent"])
```

### `handle_bot_detection`
Handle generic bot detection challenges.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `detection_type` | string | No | | Type of detection to handle. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object confirming the handling, with `detection_type`, `handled` status, and `method` in the `data` field.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_handle_bot_detection

result = await handle_handle_bot_detection({
    "browser_id": "your-browser-id"
})
if result.success and result.data["handled"]:
    print("Bot detection challenge was handled.")
```

### `evade_detection`
Apply comprehensive evasion techniques.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `techniques` | array | No | | Evasion techniques to apply. |

**Returns:**
An `OperationResult` object. On success, the `data` field lists the `applied_techniques` and their status.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_evade_detection

result = await handle_evade_detection({
    "browser_id": "your-browser-id",
    "techniques": ["all"]
})
if result.success:
    print("Applied detection evasion techniques.")
```

### `rotate_proxy`
Rotate to a new proxy server.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `country` | string | No | | Preferred proxy country code. |
| `proxy_type` | string | No | | Type of proxy to use. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains details of the `new_proxy`.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_rotate_proxy

result = await handle_rotate_proxy({
    "browser_id": "your-browser-id",
    "country": "US"
})
if result.success:
    print("Rotated to new proxy:", result.data["new_proxy"])
```

### `check_protection_status`
Check current protection and detection status.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains a dictionary of the current protection status.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_check_protection_status

result = await handle_check_protection_status({
    "browser_id": "your-browser-id"
})
if result.success:
    print("Protection status:", result.data)
```

### `spoof_headers`
Spoof HTTP headers to appear more legitimate.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `headers` | object | No | | Headers to spoof. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `spoofed_headers`.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_spoof_headers

result = await handle_spoof_headers({
    "browser_id": "your-browser-id",
    "headers": {"Accept-Language": "en-US,en;q=0.9"}
})
if result.success:
    print("Headers spoofed.")
```

### `randomize_timing`
Add random delays and timing variations.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `max_delay` | number | No | `3` | Maximum delay in seconds. |
| `min_delay` | number | No | `0.5` | Minimum delay in seconds. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `applied_delay`.

**Python Example:**
```python
from pydoll_mcp.tools.protection_tools import handle_randomize_timing

result = await handle_randomize_timing({
    "browser_id": "your-browser-id",
    "min_delay": 1.0,
    "max_delay": 5.0
})
if result.success:
    print(f"Applied random delay of {result.data['applied_delay']:.2f}s")
```

### Usage Examples

**AI Assistant Prompts:**

> "Bypass any captcha challenges that appear"
> "Enable stealth mode and anti-detection features"
> "Simulate human-like browsing patterns with random delays"

---

## Advanced Tools

Advanced tools for performance analysis and AI-powered content analysis.

### `fetch_domain_commands`
Fetch all possible commands available for the current domain from Chrome DevTools Protocol.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `domain` | string | No | | Chrome DevTools Protocol domain (e.g., 'Page', 'Network', 'DOM'). |
| `tab_id` | string | No | | Optional tab ID, uses active tab if not specified. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the list of `commands` and `command_count`.

**Python Example:**
```python
from pydoll_mcp.tools.advanced_tools import handle_fetch_domain_commands

result = await handle_fetch_domain_commands({
    "browser_id": "your-browser-id",
    "domain": "Network"
})
if result.success:
    print(f"Found {result.data['command_count']} commands in the Network domain.")
```

### `analyze_performance`
Analyze page performance metrics and provide optimization suggestions.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `export_format` | string | No | `json` | Export format for performance data. |
| `include_suggestions`| boolean | No | `true` | Include optimization suggestions. |
| `metrics_to_collect` | array | No | `[timing, navigation, paint]` | Performance metrics to collect. |
| `save_report` | boolean | No | `false` | Save performance report to file. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains `performance_data`, a `performance_score`, and a list of `suggestions`.

**Python Example:**
```python
from pydoll_mcp.tools.advanced_tools import handle_analyze_performance

result = await handle_analyze_performance({
    "browser_id": "your-browser-id",
    "save_report": True
})
if result.success:
    print(f"Page performance score: {result.data['performance_score']}/100")
```

### `analyze_content_with_ai`
Analyze page content using AI for insights and recommendations.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `browser_id` | string | Yes | | Browser instance ID. |
| `analysis_type` | string | Yes | | Type of AI analysis to perform. |
| `content_selector` | string | No | | CSS selector for specific content to analyze. |
| `custom_prompt` | string | No | | Custom prompt for AI analysis. |
| `generate_report`| boolean | No | `true` | Generate a comprehensive analysis report. |
| `include_images` | boolean | No | `false` | Include image analysis in content analysis. |
| `language` | string | No | `auto` | Language of the content. |
| `tab_id` | string | No | | Optional tab ID. |

**Returns:**
An `OperationResult` object. On success, the `data` field contains the `analysis_type` and the `results` of the analysis.

**Python Example:**
```python
from pydoll_mcp.tools.advanced_tools import handle_analyze_content_with_ai

result = await handle_analyze_content_with_ai({
    "browser_id": "your-browser-id",
    "analysis_type": "sentiment",
    "generate_report": True
})
if result.success:
    print("AI analysis results:", result.data["results"])
```

### Usage Examples

**AI Assistant Prompts:**

> "Test the page performance and load times"
> "Analyze the content of the page for sentiment"
> "Discover all available API endpoints by monitoring network traffic"
