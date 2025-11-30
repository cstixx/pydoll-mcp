# PyDoll MCP Server Architecture

This document describes the architecture of PyDoll MCP Server, including the unified tools system, session persistence, and error handling.

## Overview

PyDoll MCP Server has been refactored to provide a streamlined, LLM-friendly interface while maintaining backward compatibility with existing tools. The architecture emphasizes:

- **Unified Tools**: Consolidation of granular tools into powerful, action-based endpoints
- **Session Persistence**: SQLite-based state management for resilience and recovery
- **Stateless Design**: Decoupled state management for better scalability
- **Smart Error Handling**: Context-aware error responses for better debugging

## Directory Structure

```
pydoll_mcp/
├── core/                    # Core functionality
│   ├── browser_manager.py   # Stateless browser management
│   └── session_store.py     # SQLite-based session persistence
├── tools/                   # Tool definitions and handlers
│   ├── definitions.py       # Pydantic models for unified tools
│   ├── handlers.py          # Tool handler implementations
│   └── registry.py          # Tool registration and discovery
├── utils/                   # Utility functions
│   ├── error_handler.py     # Error enrichment decorator
│   └── dom_helper.py        # DOM snapshot utilities
└── config.py                # Centralized Pydantic settings
```

## Unified Tools Architecture

### Design Philosophy

The unified tools ("Fat Tools") consolidate **a subset** of granular tools into 4 powerful endpoints. They focus on the most common operations: element interaction, tab management, and browser control.

1. **`interact_element`** - Element interactions (click, type, hover, press_key, drag, scroll)
2. **`manage_tab`** - Tab management (create, close, refresh, activate, list, get_info)
3. **`browser_control`** - Browser lifecycle (start, stop, list, get_state, reattach)
4. **`execute_cdp_command`** - Direct Chrome DevTools Protocol access

### What They Replace

Unified tools replace approximately **20-30 legacy tools** in these categories:
- Element interaction tools (click, type, hover, etc.)
- Tab management tools (new_tab, close_tab, refresh, etc.)
- Basic browser lifecycle tools (start, stop, list, etc.)

### What They Don't Replace

Many tool categories remain as legacy tools:
- **Screenshot & Media** - Still use legacy tools
- **Script Execution** - Still use legacy tools
- **Network Monitoring** - Still use legacy tools
- **Protection & Stealth** - Still use legacy tools
- **File Operations** - Still use legacy tools
- **Element Finding** - Still use legacy tools (find_element, query, etc.)
- **Navigation** - Still use legacy tools
- **Advanced Features** - Still use legacy tools

See [Unified Tools Coverage](UNIFIED_TOOLS_COVERAGE.md) for complete details.

### Benefits

- **Reduced Complexity**: 4 unified tools for common operations instead of 20-30 separate tools
- **Action-Based API**: Clear action parameter instead of separate tools
- **Better Error Context**: Unified error handling with rich context
- **Backward Compatibility**: Legacy tools remain available for all other operations

### Example Usage

```python
# Unified tool approach
{
    "tool": "interact_element",
    "arguments": {
        "action": "click",
        "browser_id": "browser-1",
        "selector": {"css_selector": "button.submit"}
    }
}

# vs. legacy approach
{
    "tool": "click_element",
    "arguments": {
        "browser_id": "browser-1",
        "selector": {"css_selector": "button.submit"}
    }
}
```

## Session Persistence

### SessionStore

The `SessionStore` class provides SQLite-based persistence for browser and tab state:

- **Database Location**: `~/.local/share/pydoll-mcp/sessions.db`
- **Schema**: Separate tables for browsers, tabs, and session metadata
- **Features**:
  - Browser state persistence (type, debug_port, PID, config)
  - Tab state tracking (URL, title, activity)
  - Activity timestamps for cleanup
  - Foreign key relationships for data integrity

### Benefits

- **Resilience**: Browser state survives server restarts
- **Recovery**: Ability to reattach to existing browser instances
- **Cleanup**: Automatic cleanup of idle browsers and tabs
- **Debugging**: Historical state for troubleshooting

## Stateless BrowserManager

### Design

The `BrowserManager` has been refactored to be stateless:

- **State Storage**: Uses `SessionStore` for persistence
- **Active Cache**: `_active_browsers` dictionary for temporary operation contexts
- **Session Integration**: All state operations go through `SessionStore`

### Benefits

- **Scalability**: No in-memory state limits
- **Resilience**: State survives process restarts
- **Separation of Concerns**: Clear separation between logic and state
- **Testability**: Easier to test with mocked SessionStore

## Error Handling

### Error Enrichment Decorator

The `@enrich_errors` decorator provides context-aware error responses:

- **DOM Snapshots**: Captures DOM state for element errors
- **Page Context**: Includes URL and title for timeout errors
- **Structured Responses**: Consistent error format for LLMs

### Example Error Response

```json
{
    "success": false,
    "error": "ElementNotFound",
    "message": "Element not found with selector: {'css_selector': 'button.submit'}",
    "context": {
        "dom_snapshot": "...",
        "current_url": "https://example.com",
        "page_title": "Example Page"
    }
}
```

## Configuration Management

### Pydantic Settings

Centralized configuration using Pydantic Settings:

- **Environment Variables**: Automatic loading from `.env` files
- **Type Safety**: Strong typing and validation
- **Defaults**: Sensible defaults for all settings
- **Documentation**: Self-documenting configuration schema

### Configuration Options

- `headless_mode`: Browser headless mode
- `default_proxy`: Default proxy configuration
- `user_agent`: Default user agent string
- `download_path`: Default download directory
- `window_width` / `window_height`: Browser window dimensions
- `max_browsers`: Maximum concurrent browsers
- `max_tabs_per_browser`: Maximum tabs per browser
- `stealth_mode`: Enable stealth mode by default
- `browser_type`: Default browser type (chrome/edge)
- `cleanup_interval`: Idle browser cleanup interval
- `idle_timeout`: Browser idle timeout

## Tool Registry

### Dynamic Registration

The `ToolRegistry` class manages tool registration:

- **Unified Tools**: Automatically registers unified tools
- **Legacy Tools**: Maintains backward compatibility
- **Handler Mapping**: Maps tool names to handler functions
- **Error Enrichment**: Applies error enrichment to all handlers

## CDP Command Dispatcher

### Direct Protocol Access

The `execute_cdp_command` tool provides direct access to Chrome DevTools Protocol:

- **Domain Support**: All CDP domains (Page, Network, DOM, Runtime, etc.)
- **Method Execution**: Execute any CDP method
- **Parameter Passing**: Full parameter support
- **Response Handling**: Structured response format

### Example

```python
{
    "tool": "execute_cdp_command",
    "arguments": {
        "browser_id": "browser-1",
        "domain": "Page",
        "method": "navigate",
        "params": {"url": "https://example.com"}
    }
}
```

## Migration Guide

### For LLM Users

**Recommended**: Use unified tools for new implementations:
- `interact_element` instead of `click_element`, `type_text`, etc.
- `manage_tab` instead of `new_tab`, `close_tab`, etc.
- `browser_control` instead of `start_browser`, `stop_browser`, etc.

**Legacy Tools**: Still available for backward compatibility.

### For Developers

**New Code**: Use unified tool handlers and SessionStore
**Existing Code**: Legacy tools continue to work
**Testing**: Update tests to use new import paths (`pydoll_mcp.core`)

## Future Enhancements

- **Browser Reattachment**: Full support for reattaching to existing browsers
- **State Migration**: Tools for migrating between session stores
- **Performance Metrics**: Enhanced metrics collection and reporting
- **Plugin System**: Extensible tool registration system

