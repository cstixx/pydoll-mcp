# Release Notes - PyDoll MCP Server v1.5.17

**Release Date**: November 29, 2025
**PyDoll Version**: 2.12.4+
**Total Tools**: 84 (up from 79)

## 🚀 Major Update: PyDoll 2.12.4+ Full Integration

This release brings comprehensive integration with PyDoll 2.12.4+ APIs, replacing all simulation-based implementations with real browser automation capabilities. All new tools use native PyDoll APIs for authentic browser control.

## ✨ New Features

### Page Interaction Tools

#### `handle_alert` (NEW)
Simplified alert and dialog handler with automatic detection capabilities.

**Features**:
- Automatic dialog detection using `has_dialog()` API
- Dialog message retrieval with `get_dialog_message()` API
- Simple accept/dismiss interface
- Works with alerts, confirms, and prompts

**Usage Example**:
```
"Handle any alert that appears on the page"
"Dismiss the confirmation dialog"
```

#### `save_pdf` (ENHANCED)
Enhanced PDF saving with file system support and formatting options.

**New Features**:
- Save PDFs directly to file system
- Format options (A4, Letter, etc.)
- Print background graphics control
- Base64 encoding fallback

**Usage Example**:
```
"Save the current page as a PDF to /path/to/output.pdf"
"Generate a PDF with A4 format and background graphics"
```

### Browser Management Tools

#### `bring_tab_to_front` (NEW)
Multi-tab focus management for better tab control.

**Features**:
- Brings specified tab to front in browser window
- Updates active tab tracking
- Works with multiple open tabs

**Usage Example**:
```
"Bring the tab with ID 'tab-123' to the front"
"Switch focus to the search results tab"
```

#### `set_download_behavior` (NEW)
Configure browser download behavior (allow/deny/prompt).

**Features**:
- Control download behavior per browser instance
- Support for allow, deny, and prompt modes
- Optional download path configuration

**Usage Example**:
```
"Set download behavior to allow for this browser"
"Configure downloads to prompt user for each file"
```

#### `set_download_path` (NEW)
Set default download directory for browser.

**Features**:
- Configure download directory per browser
- Automatic directory creation
- Path validation and error handling

**Usage Example**:
```
"Set download path to /path/to/downloads"
"Configure downloads to save to the desktop"
```

#### `enable_file_chooser_interception` / `disable_file_chooser_interception` (NEW)
Control file chooser dialog interception for upload automation.

**Features**:
- Enable/disable file chooser automation
- Works with `upload_file` tool
- Per-tab configuration

**Usage Example**:
```
"Enable file chooser interception for upload automation"
"Disable file chooser interception on this tab"
```

### Network Monitoring Tools

#### `get_network_response_body` (NEW)
Retrieve response bodies for specific network requests.

**Features**:
- Get response body by request ID or URL
- Support for all request types
- Proper error handling

**Usage Example**:
```
"Get the response body for request ID 'req-123'"
"Retrieve the API response for this URL"
```

### Protection Tools

#### `enable_cloudflare_auto_solve` / `disable_cloudflare_auto_solve` (NEW)
Control automatic Cloudflare captcha solving.

**Features**:
- Enable/disable automatic captcha solving
- Per-tab configuration
- Works with `bypass_cloudflare` tool

**Usage Example**:
```
"Enable automatic Cloudflare captcha solving"
"Disable auto-solve for this tab"
```

## 🔧 Enhanced Features

### File Operations

#### `upload_file` (ENHANCED)
Now uses real PyDoll API (`expect_file_chooser`) instead of simulation.

**Improvements**:
- Real file chooser interception
- Support for multiple file uploads
- Proper async generator handling
- Better error messages

#### `download_file` (ENHANCED)
Now uses real PyDoll API (`expect_download`) with download path configuration.

**Improvements**:
- Real download tracking
- Download path configuration
- Wait for completion option
- Download status reporting

### Dialog Handling

#### `handle_dialog` (ENHANCED)
Enhanced with native PyDoll APIs.

**Improvements**:
- Uses `has_dialog()` for detection
- Uses `get_dialog_message()` for message retrieval
- Uses `handle_dialog()` for handling
- Better error handling

### Network Monitoring

#### `get_network_logs` (ENHANCED)
Now uses real `tab.get_network_logs()` API.

**Improvements**:
- Real network log retrieval
- Proper log entry processing
- Enhanced filtering capabilities
- Better attribute extraction

### Cloudflare Bypass

#### `bypass_cloudflare` (ENHANCED)
Uses `expect_and_bypass_cloudflare_captcha` API.

**Improvements**:
- Real captcha bypass
- Automatic solving integration
- Better success tracking
- Enhanced error handling

## 🐛 Bug Fixes

### DownloadBehavior Import
- **Fixed**: Import path corrected to `pydoll.protocol.browser.types` (was incorrectly `pydoll.browser`)
- **Impact**: Download configuration tools now work correctly

### File Upload Implementation
- **Fixed**: Async generator usage for `expect_file_chooser` API
- **Impact**: File uploads now work reliably

### Network Logs Processing
- **Fixed**: Improved network log entry processing with proper attribute extraction
- **Impact**: Network logs now display correctly with all attributes

### Tab Activation
- **Fixed**: Enhanced `set_active_tab` to use native `bring_to_front()` API
- **Impact**: Tab switching now works correctly in browser window

## 📊 Tool Count Updates

| Category | Previous | Current | Change |
|----------|----------|---------|--------|
| Browser Management | 8 | 13 | +5 |
| Protection Tools | 12 | 14 | +2 |
| Network Tools | 10 | 11 | +1 |
| Page Tools | 2 | 4 | +2 |
| **Total** | **79** | **84** | **+5** |

## 🧪 Testing

### New Test Coverage
- Added 21 new tests in `test_new_features.py`
- Comprehensive coverage for all new tools
- Integration tests for enhanced features
- Error handling and edge case testing

### Test Results
- All existing tests: ✅ 144 passed
- New feature tests: ✅ 21 passed
- Total: ✅ 165 tests passing

## 📦 Migration Guide

### For Existing Users

No breaking changes! All existing tools continue to work as before. New tools are additive.

### Upgrading

```bash
pip install --upgrade pydoll-mcp
```

### New Tool Usage

All new tools are immediately available after upgrade. No configuration changes required.

## 🔗 Related Documentation

- [README.md](../README.md) - Complete tool documentation
- [CHANGELOG.md](../CHANGELOG.md) - Full changelog
- [PyDoll Documentation](https://github.com/autoscrape-labs/pydoll) - PyDoll library docs

## 🙏 Acknowledgments

- PyDoll team for the excellent 2.12.4+ API
- Community contributors for feedback and testing
- All users who reported issues and suggested improvements

---

**Upgrade Now**: `pip install --upgrade pydoll-mcp`

