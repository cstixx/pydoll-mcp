# Unimplemented PyDoll Features in pydoll-mcp

This document lists all features from the PyDoll library that are available but not yet implemented as MCP tools in pydoll-mcp.

**Last Updated**: Based on PyDoll 2.12.4+ and pydoll-mcp v1.5.18
**Status**: All high and medium priority features have been implemented. Remaining features are low priority.

---

## 📊 Summary

### Implementation Status
- ✅ **High Priority Features**: All implemented (v1.5.17 & v1.5.18)
- ✅ **Medium Priority Features**: All implemented (v1.5.18)
- ⚠️ **Low Priority Features**: 8 features remaining (Window Management, Callbacks, Browser Info)

### Total Unimplemented Features: 8

---

## 🪟 1. Window Management Features (5 features)

All window management features are marked as **Low Priority** because they're primarily useful for multi-window scenarios and non-headless automation. The current focus is on single-window, multi-tab workflows.

### 1.1 `set_window_bounds()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Window positioning, multi-window automation, multi-monitor setups

**PyDoll API**:
```python
await browser.set_window_bounds(window_id, x, y, width, height)
```

**Suggested MCP Tool**: `set_window_position` or `set_window_bounds`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Position browser windows at specific screen coordinates
- Set custom window sizes for testing responsive designs
- Arrange multiple browser windows in specific layouts
- Control window positioning for screenshots/video recording
- Multi-monitor setups

**Current Limitation**: Window size can only be set at browser creation via `--window-size` Chrome argument. Window position cannot be controlled.

---

### 1.2 `set_window_maximized()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Window state management

**PyDoll API**:
```python
await browser.set_window_maximized(window_id, maximized=True)
```

**Suggested MCP Tool**: `maximize_window` or `set_window_state`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Maximize window for full-screen automation
- Ensure maximum screen real estate for screenshots
- Standardize window state across different environments
- Testing full-screen UI elements

**Current Limitation**: Window state cannot be changed after browser creation.

---

### 1.3 `set_window_minimized()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Low (Very Low)
**Use Case**: Window state management during background automation

**PyDoll API**:
```python
await browser.set_window_minimized(window_id, minimized=True)
```

**Suggested MCP Tool**: `minimize_window` or `set_window_state`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Minimize window during background automation
- Reduce visual clutter during long-running tasks
- Hide browser window while still running automation
- Resource management (minimized windows may use less resources)

**Current Limitation**: Window state cannot be changed after browser creation.

---

### 1.4 `get_window_id()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Window tracking, debugging

**PyDoll API**:
```python
window_id = await browser.get_window_id()
```

**Suggested MCP Tool**: `get_window_info` or `get_browser_window_id`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Identify browser windows for window management operations
- Track multiple browser instances
- Debugging window-related issues
- Window state management

**Current Limitation**: Window IDs are not currently tracked or exposed.

---

### 1.5 `get_window_id_for_tab()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Low (Very Low)
**Use Case**: Multi-window browser automation

**PyDoll API**:
```python
window_id = await browser.get_window_id_for_tab(tab_id)
```

**Suggested MCP Tool**: `get_tab_window` or `get_window_for_tab`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Determine which window a tab belongs to
- Multi-window browser automation
- Window-tab relationship tracking
- Advanced tab management across windows

**Current Limitation**: Window-tab relationships are not tracked. The project currently focuses on single-window, multi-tab workflows.

---

### 1.6 `get_window_id_for_target()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Very Low
**Use Case**: Advanced browser target management

**PyDoll API**:
```python
window_id = await browser.get_window_id_for_target(target_id)
```

**Suggested MCP Tool**: `get_target_window`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Get window ID for any browser target (not just tabs)
- Service worker management
- Web worker tracking
- Advanced browser target management

**Current Limitation**: Not needed for typical automation scenarios.

---

## 🎣 2. Event Callback System (3 features)

The callback system allows event-driven automation with custom event handlers. Currently marked as **Low Priority** because the MCP protocol already provides a request-response model for automation.

### 2.1 `on()` - Tab/Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Event-driven automation, custom event handlers

**PyDoll API**:
```python
# Tab-level events
await tab.on('event_name', callback_function)

# Browser-level events
await browser.on('event_name', callback_function)
```

**Suggested Implementation**: Event callback management system
**File Location**: `pydoll_mcp/browser_manager.py` or new event system module

**Use Cases**:
- Register custom event handlers for browser events
- Event-driven automation workflows
- React to page load events
- Handle network events asynchronously
- Custom error handling

**Current Limitation**: MCP tools use a synchronous request-response model. Event callbacks would require a different architecture (e.g., streaming responses or event notifications).

**Implementation Notes**:
- Would require MCP protocol extensions for event streaming
- Could be implemented as background event handlers that store results
- May conflict with MCP's request-response paradigm

---

### 2.2 `remove_callback()` - Tab/Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Cleanup of event callbacks

**PyDoll API**:
```python
await tab.remove_callback('event_name', callback_function)
```

**Suggested Implementation**: Part of callback management system
**File Location**: `pydoll_mcp/browser_manager.py` or event system module

**Use Cases**:
- Remove specific event callbacks
- Clean up event handlers
- Manage callback lifecycle

**Current Limitation**: Requires callback system (`on()`) to be implemented first.

---

### 2.3 `clear_callbacks()` - Tab/Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Cleanup of all event callbacks

**PyDoll API**:
```python
await tab.clear_callbacks()
await tab.clear_callbacks('event_name')  # Clear callbacks for specific event
```

**Suggested Implementation**: Part of callback management system
**File Location**: `pydoll_mcp/browser_manager.py` or event system module

**Use Cases**:
- Remove all event callbacks
- Clean up all event handlers
- Reset event system state

**Current Limitation**: Requires callback system to be implemented first.

---

## 🔍 3. Browser Information & Target Management (2 features)

These features provide introspection and debugging capabilities for the browser instance.

### 3.1 `get_version()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Browser version detection, compatibility checks

**PyDoll API**:
```python
version_info = await browser.get_version()
```

**Suggested MCP Tool**: `get_browser_version` or enhance `get_browser_status`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Browser version detection
- Compatibility checks
- Debugging browser-specific issues
- Version reporting in automation logs

**Current Alternative**: Browser version can sometimes be inferred from Chrome user agent or command-line arguments, but there's no direct API.

**Implementation Notes**:
- Could enhance existing `get_browser_status` tool to include version
- Simple to implement as a wrapper around PyDoll API
- Low priority because version info is rarely needed in automation

---

### 3.2 `get_targets()` - Browser Method

**Status**: ❌ Not implemented
**Priority**: Low
**Use Case**: Advanced browser state inspection

**PyDoll API**:
```python
targets = await browser.get_targets()
```

**Suggested MCP Tool**: `list_browser_targets` or enhance `get_browser_status`
**File Location**: `pydoll_mcp/tools/browser_tools.py`

**Use Cases**:
- Get all browser targets (tabs, workers, etc.)
- Advanced browser state inspection
- Debugging browser instance state
- Service worker detection
- Web worker tracking

**Current Alternative**: Tabs can be listed via `list_tabs`, but other targets (workers, etc.) are not exposed.

**Implementation Notes**:
- Useful for debugging and advanced scenarios
- Not commonly needed for typical automation tasks
- Could provide insights into browser internals

---

## 📋 Implementation Priority Summary

### Low Priority Features (8 total)

1. **Window Management (5 features)** - Low priority
   - `set_window_bounds()` - Useful for multi-window/multi-monitor scenarios
   - `set_window_maximized()` - Convenience feature
   - `set_window_minimized()` - Rarely needed
   - `get_window_id()` - Mainly for debugging
   - `get_window_id_for_tab()` / `get_window_id_for_target()` - Multi-window scenarios only

2. **Event Callback System (3 features)** - Low priority
   - `on()` - Would require MCP protocol extensions
   - `remove_callback()` - Requires `on()` first
   - `clear_callbacks()` - Requires `on()` first

3. **Browser Information (2 features)** - Low priority
   - `get_version()` - Rarely needed, could enhance existing status tool
   - `get_targets()` - Advanced debugging only

---

## 🎯 Implementation Recommendations

### If Implementing Window Management

**Suggested Order**:
1. `set_window_bounds()` - Most versatile (can achieve maximize/minimize)
2. `get_window_id()` - Needed for window management operations
3. `set_window_maximized()` / `set_window_minimized()` - Convenience wrappers
4. Window ID for tab/target methods - Only if multi-window support is added

**Estimated Effort**: 1-2 days for all window management features

### If Implementing Callback System

**Requirements**:
- MCP protocol extensions for event streaming/notifications
- Event handler storage and management
- Lifecycle management (registration, cleanup)
- Integration with browser manager

**Estimated Effort**: 3-5 days (requires architectural changes)

### If Implementing Browser Information

**Suggested Order**:
1. `get_version()` - Simple wrapper, could enhance `get_browser_status`
2. `get_targets()` - More complex, useful for debugging

**Estimated Effort**: 1-2 hours for both

---

## 📝 Notes

### Why These Features Are Low Priority

1. **Window Management**:
   - Most automation runs in headless mode (windows not visible)
   - Single-window, multi-tab workflows are more common than multi-window
   - Window size can be set at creation time

2. **Event Callbacks**:
   - MCP uses request-response model (not event-driven)
   - Would require protocol extensions
   - Current tools can poll/check state as needed

3. **Browser Information**:
   - Rarely needed in automation workflows
   - Version info can be inferred from other sources
   - Target inspection is advanced debugging only

### When These Features Become Higher Priority

- **Window Management**: If multi-window automation workflows become common
- **Event Callbacks**: If MCP protocol adds event streaming support
- **Browser Information**: If debugging/version checking becomes critical

---

## 🔗 Related Documentation

- `PYDOLL_UPGRADE_FEATURES.md` - Comprehensive feature implementation status
- `HIGH_PRIORITY_IMPLEMENTATION_PLAN.md` - Implementation plans for completed features
- `TAB_WINDOW_MANAGEMENT_FEATURES.md` - Detailed window management feature specs

---

## ✅ Recently Implemented Features (for reference)

The following features were previously unimplemented but have been added:

- ✅ `bring_to_front()` - Tab activation (v1.5.17)
- ✅ `expect_download()` - Download handling (v1.5.17)
- ✅ `expect_file_chooser()` - File upload handling (v1.5.17)
- ✅ `get_network_logs()` - Network monitoring (v1.5.17)
- ✅ `get_network_response_body()` - Network response inspection (v1.5.17)
- ✅ `create_browser_context()` - Browser context management (v1.5.18)
- ✅ `grant_permissions()` / `reset_permissions()` - Permission management (v1.5.18)
- ✅ Event system control (enable/disable DOM, network, page, fetch, runtime events) (v1.5.18)
- ✅ Request interception enhancements (`modify_request`, `fulfill_request`, `continue_with_auth`) (v1.5.18)
- ✅ `find_or_wait_element()` - Element finding with waiting (v1.5.18)
- ✅ `query()` - Advanced querying (v1.5.18)
- ✅ `keyboard` API - Advanced keyboard control (v1.5.18)
- ✅ `scroll()` - Programmatic scrolling (v1.5.18)
- ✅ `get_frame()` - Frame/iframe access (v1.5.18)

**All high and medium priority features from PyDoll 2.12.4+ have been successfully implemented!**


