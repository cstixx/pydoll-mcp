# High Priority PyDoll 2.12.4 Features - Implementation Plan

## Executive Summary

This plan implements high-priority features from pydoll-python 2.12.4 and critical tool enhancements. The implementation is organized into 5 phases, prioritizing critical functionality first.

**Target**: pydoll-python 2.12.4
**Estimated Duration**: 3-4 days
**Priority Order**: Critical → High → Medium

---

## Phase 1: Critical Tool Enhancements (Day 1)

### 1.1 Enhance Alert/Dialog Handling

**Tool**: `handle_alert` (new) + enhance `handle_dialog`
**File**: `pydoll_mcp/tools/page_tools.py`
**Priority**: CRITICAL

**Tasks**:
1. Update `handle_handle_dialog()` to use native `tab.handle_dialog()` instead of `_execute_command`
2. Add `handle_alert` tool as simplified alias for alert dialogs
3. Integrate `has_dialog()` and `get_dialog_message()` for better detection
4. Add auto-detection of dialog type (alert/confirm/prompt)

**Implementation**:
```python
# Replace low-level API call
await tab._execute_command(PageCommands.handle_javascript_dialog(...))
# With native PyDoll method
await tab.handle_dialog(accept=accept, prompt_text=prompt_text)

# Add dialog detection
if await tab.has_dialog():
    message = await tab.get_dialog_message()
```

**Testing**: Alert, confirm, prompt dialogs; error handling

---

### 1.2 Enhance File Upload

**Tool**: `upload_file` (enhance existing)
**File**: `pydoll_mcp/tools/file_tools.py`
**Priority**: CRITICAL

**Tasks**:
1. Replace simulated upload with `expect_file_chooser()` API
2. Enable file chooser interception before upload
3. Support single and multiple file uploads
4. Add proper file validation and error handling

**Implementation**:
```python
# Enable interception
await tab.enable_intercept_file_chooser_dialog()

# Find and click file input
element = await tab.find(**selector_params)
await element.click()

# Handle file chooser
async for _ in tab.expect_file_chooser(files=[file_path]):
    pass  # File uploaded
```

**Testing**: Single/multiple files, various file types, error scenarios

---

### 1.3 Enhance File Download

**Tool**: `download_file` (enhance existing)
**File**: `pydoll_mcp/tools/file_tools.py`
**Priority**: CRITICAL

**Tasks**:
1. Replace simulated download with `expect_download()` API
2. Implement download path configuration
3. Add download progress tracking
4. Handle download completion and errors

**Implementation**:
```python
# Configure download path
await browser.set_download_path(save_path)
await browser.set_download_behavior("allow")

# Trigger download (navigate or click)
await tab.go_to(download_url)

# Wait for download
async for download in tab.expect_download(keep_file_at=save_path, timeout=30):
    return {
        "filename": download.filename,
        "path": download.path,
        "size": download.size
    }
```

**Testing**: Various file types, timeout handling, download cancellation

---

### 1.4 Enhance PDF Generation

**Tool**: `save_pdf` (new alias) + enhance `save_page_as_pdf`
**File**: `pydoll_mcp/tools/page_tools.py`
**Priority**: HIGH

**Tasks**:
1. Add `save_pdf` as alias to `save_page_as_pdf`
2. Add file path saving option (not just base64)
3. Add PDF options (margins, format, scale)
4. Support full-page and viewport modes

**Implementation**:
```python
# Enhanced PDF with options
pdf_data = await tab.print_to_pdf(
    as_base64=not file_path,
    format="A4",
    margin={"top": 0, "right": 0, "bottom": 0, "left": 0},
    print_background=True
)

# Save to file if path provided
if file_path:
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(pdf_data))
```

**Testing**: File saving, various PDF options, different page sizes

---

### 1.5 Implement Tab Focus Management

**Tool**: `bring_tab_to_front` (new)
**File**: `pydoll_mcp/tools/browser_tools.py`
**Priority**: MEDIUM

**Tasks**:
1. Add `bring_tab_to_front` tool
2. Enhance `handle_set_active_tab()` to also call `bring_to_front()`
3. Update tab tracking to reflect browser state

**Implementation**:
```python
async def handle_bring_tab_to_front(arguments: Dict[str, Any]):
    tab, tab_id = await browser_manager.get_tab_with_fallback(...)
    await tab.bring_to_front()
    # Update active tab tracking
```

**Testing**: Multi-tab scenarios, tab activation, visual verification

---

## Phase 2: Download Management Infrastructure (Day 2)

### 2.1 Download Configuration Tools

**Tools**: `set_download_behavior`, `set_download_path`
**File**: `pydoll_mcp/tools/browser_tools.py`
**Priority**: HIGH

**Tasks**:
1. Add `set_download_behavior` tool (allow/deny/prompt)
2. Add `set_download_path` tool
3. Integrate with browser creation process
4. Add download path validation

**Implementation**:
```python
# Tool: set_download_behavior
await browser.set_download_behavior(
    behavior="allow",  # or "deny", "prompt"
    download_path=path
)

# Tool: set_download_path
await browser.set_download_path(path)
```

**Testing**: Path validation, behavior settings, integration with downloads

---

### 2.2 Download Tracking System

**Enhancement**: `handle_manage_downloads`
**File**: `pydoll_mcp/tools/file_tools.py` + `browser_manager.py`
**Priority**: HIGH

**Tasks**:
1. Implement real download tracking in browser manager
2. Update `handle_manage_downloads()` to work with real downloads
3. Add download state management (pending, in-progress, completed, failed)
4. Support download cancellation and status queries

**Implementation**:
```python
# In browser_manager.py
class BrowserInstance:
    def __init__(self):
        self.active_downloads: Dict[str, DownloadInfo] = {}

# Track downloads
async def track_download(download):
    self.active_downloads[download.id] = {
        "id": download.id,
        "filename": download.filename,
        "status": "in_progress",
        "progress": 0
    }
```

**Testing**: Download tracking, status queries, cancellation

---

## Phase 3: File Chooser Infrastructure (Day 2)

### 3.1 File Chooser Control Tools

**Tools**: `enable_file_chooser_interception`, `disable_file_chooser_interception`
**File**: `pydoll_mcp/tools/browser_tools.py`
**Priority**: HIGH

**Tasks**:
1. Add enable/disable file chooser interception tools
2. Integrate with browser/tab lifecycle
3. Add state tracking for interception status

**Implementation**:
```python
# Tool: enable_file_chooser_interception
await tab.enable_intercept_file_chooser_dialog()

# Tool: disable_file_chooser_interception
await tab.disable_intercept_file_chooser_dialog()
```

**Testing**: Enable/disable functionality, state persistence

---

## Phase 4: Network Monitoring Enhancements (Day 3)

### 4.1 Network Logs Tool

**Tool**: `get_network_logs` (new)
**File**: `pydoll_mcp/tools/network_tools.py`
**Priority**: HIGH

**Tasks**:
1. Add `get_network_logs` tool
2. Implement filtering (URL pattern, method, status code, resource type)
3. Add pagination support
4. Format logs for easy consumption

**Implementation**:
```python
# Get network logs
logs = await tab.get_network_logs()

# Filter logs
filtered = [
    log for log in logs
    if matches_filter(log, filter_params)
]

# Return formatted logs
return {
    "logs": filtered[:limit],
    "total": len(filtered),
    "filtered": len(filtered)
}
```

**Testing**: Log retrieval, filtering, pagination, various network activity

---

### 4.2 Network Response Body Tool

**Tool**: `get_network_response_body` (new)
**File**: `pydoll_mcp/tools/network_tools.py`
**Priority**: HIGH

**Tasks**:
1. Add `get_network_response_body` tool
2. Support request identification by ID or URL
3. Handle different response types (JSON, text, binary)
4. Add response caching

**Implementation**:
```python
# Get response body
body = await tab.get_network_response_body(request_id)

# Handle different types
if content_type == "application/json":
    return json.loads(body)
elif content_type.startswith("text/"):
    return body.decode("utf-8")
else:
    return base64.b64encode(body).decode()
```

**Testing**: JSON/text/binary responses, request identification, caching

---

## Phase 5: Captcha & Element Finding (Day 3-4)

### 5.1 Cloudflare Captcha Auto-Solve

**Tools**: `enable_auto_solve_cloudflare`, `disable_auto_solve_cloudflare`, `expect_and_bypass_cloudflare`
**File**: `pydoll_mcp/tools/protection_tools.py`
**Priority**: HIGH

**Tasks**:
1. Add enable/disable auto-solve tools
2. Add `expect_and_bypass_cloudflare_captcha` tool
3. Integrate with existing protection tools
4. Add captcha detection and status reporting

**Implementation**:
```python
# Enable auto-solve
await tab.enable_auto_solve_cloudflare_captcha()

# Wait and bypass
await tab.expect_and_bypass_cloudflare_captcha()

# Disable when done
await tab.disable_auto_solve_cloudflare_captcha()
```

**Testing**: Captcha detection, auto-solving, success rates

---

### 5.2 Enhanced Element Finding

**Tool**: `find_or_wait_element` (new)
**File**: `pydoll_mcp/tools/element_tools.py`
**Priority**: HIGH

**Tasks**:
1. Add `find_or_wait_element` tool
2. Support all selector types (CSS, XPath, natural attributes)
3. Add configurable timeout and polling
4. Improve error messages

**Implementation**:
```python
# Find with automatic waiting
element = await tab.find_or_wait_element(
    selector=selector,
    timeout=30,
    poll_interval=0.5
)

# Returns element when found or raises timeout error
```

**Testing**: Dynamic elements, timeout behavior, various selectors

---

## Implementation Checklist

### Phase 1: Critical Tools
- [ ] Enhance `handle_alert` / `handle_dialog`
- [ ] Enhance `upload_file` with real API
- [ ] Enhance `download_file` with real API
- [ ] Enhance `save_pdf`
- [ ] Implement `bring_tab_to_front`
- [ ] Update tool registrations
- [ ] Write tests

### Phase 2: Download Management
- [ ] Add `set_download_behavior` tool
- [ ] Add `set_download_path` tool
- [ ] Implement download tracking
- [ ] Update `handle_manage_downloads`
- [ ] Write tests

### Phase 3: File Chooser
- [ ] Add enable/disable file chooser tools
- [ ] Integrate with upload workflow
- [ ] Write tests

### Phase 4: Network Monitoring
- [ ] Add `get_network_logs` tool
- [ ] Add `get_network_response_body` tool
- [ ] Implement filtering and caching
- [ ] Write tests

### Phase 5: Captcha & Elements
- [ ] Add Cloudflare captcha tools
- [ ] Add `find_or_wait_element` tool
- [ ] Write tests

### Final Steps
- [ ] Update all tool registrations
- [ ] Update documentation
- [ ] Update CHANGELOG.md
- [ ] Update README.md
- [ ] Run full test suite
- [ ] Code review

---

## File Modification Summary

### Files to Modify

1. **`pydoll_mcp/tools/page_tools.py`**
   - Enhance `handle_handle_dialog()` → use native API
   - Add `handle_alert` tool
   - Enhance `save_page_as_pdf` → add `save_pdf` alias and file saving

2. **`pydoll_mcp/tools/file_tools.py`**
   - Replace simulated `upload_file` → use `expect_file_chooser()`
   - Replace simulated `download_file` → use `expect_download()`
   - Update `handle_manage_downloads()` → real download tracking

3. **`pydoll_mcp/tools/browser_tools.py`**
   - Add `bring_tab_to_front` tool
   - Add `set_download_behavior` tool
   - Add `set_download_path` tool
   - Add `enable_file_chooser_interception` tool
   - Add `disable_file_chooser_interception` tool

4. **`pydoll_mcp/tools/network_tools.py`**
   - Add `get_network_logs` tool
   - Add `get_network_response_body` tool

5. **`pydoll_mcp/tools/protection_tools.py`**
   - Add `enable_auto_solve_cloudflare` tool
   - Add `disable_auto_solve_cloudflare` tool
   - Add `expect_and_bypass_cloudflare_captcha` tool

6. **`pydoll_mcp/tools/element_tools.py`**
   - Add `find_or_wait_element` tool

7. **`pydoll_mcp/browser_manager.py`**
   - Add download tracking to `BrowserInstance`
   - Add download path configuration support
   - Add file chooser state tracking

8. **`pydoll_mcp/tools/__init__.py`**
   - Register all new tools
   - Update tool counts and categories

9. **`tests/test_tools.py`**
   - Add tests for all new tools

10. **`tests/test_integration.py`**
    - Add integration tests for new features

---

## Testing Strategy

### Unit Tests
- Each tool handler tested independently
- Error handling and edge cases
- Parameter validation
- Mock PyDoll API responses

### Integration Tests
- Real browser workflows
- File upload/download end-to-end
- Network monitoring with actual requests
- Captcha bypass on test sites
- Element finding with dynamic content

### Manual Testing
- Test with real websites
- Verify file operations work correctly
- Test network monitoring accuracy
- Verify captcha bypass success rates

---

## Success Criteria

- ✅ All critical tools enhanced and working
- ✅ All high-priority features implemented
- ✅ Real PyDoll 2.12.4 APIs integrated (no simulations)
- ✅ 100% test coverage for new code
- ✅ No breaking changes to existing functionality
- ✅ Documentation updated
- ✅ All tests passing

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API changes in PyDoll 2.12.4 | Test each API call before implementation |
| Breaking existing functionality | Comprehensive testing, maintain backward compatibility |
| Performance degradation | Profile and optimize, use async properly |
| Browser compatibility issues | Test with Chrome and Edge, document limitations |

---

## Timeline

- **Day 1**: Phase 1 (Critical Tools) - 6-8 hours
- **Day 2**: Phase 2 & 3 (Download & File Chooser) - 6-8 hours
- **Day 3**: Phase 4 (Network Monitoring) - 4-6 hours
- **Day 4**: Phase 5 (Captcha & Elements) + Testing - 4-6 hours

**Total**: 20-28 hours (3-4 days)

---

## Next Steps

1. Review and approve plan
2. Create feature branch: `feature/pydoll-2.12.4-high-priority`
3. Start Phase 1 implementation
4. Implement incrementally with tests
5. Review and merge each phase
6. Final integration testing
7. Update documentation and release
