# Unified Tools Coverage

## Overview

Unified tools **do NOT replace all tools**. They consolidate a subset of related tools into 9 powerful endpoints. Many tool categories remain as legacy tools.

## What Unified Tools Replace

### 1. `interact_element` - Replaces Element Interaction Tools
**Replaces:**
- `click_element`
- `type_text`
- `hover_element`
- `press_key`
- `drag_and_drop`
- `scroll_to_element`
- `double_click`
- `right_click`

**Does NOT replace:**
- `select_option` (still available as legacy)

### 2. `manage_tab` - Replaces Tab Management Tools
**Replaces:**
- `new_tab`
- `close_tab`
- `refresh_page`
- `set_active_tab`
- `list_tabs`
- `get_tab_info`

**Does NOT replace:**
- `bring_tab_to_front` (still available as legacy)

### 3. `browser_control` - Replaces Browser Lifecycle Tools
**Replaces:**
- `start_browser`
- `stop_browser`
- `list_browsers`
- `get_browser_status`
- `create_browser_context` (logical consolidation - browser configuration)
- `list_browser_contexts` (logical consolidation - browser configuration)
- `delete_browser_context` (logical consolidation - browser configuration)
- `grant_permissions` (logical consolidation - browser configuration)
- `reset_permissions` (logical consolidation - browser configuration)

**Does NOT replace:**
- `set_download_behavior`
- `set_download_path`
- `enable_file_chooser_interception`
- `disable_file_chooser_interception`

### 4. `execute_cdp_command` - Provides CDP Access
**Does NOT replace anything** - this is a new capability that provides direct Chrome DevTools Protocol access.

### 5. `navigate_page` - Replaces Navigation Tools
**Replaces:**
- `navigate_to`
- `go_back`
- `go_forward`
- `get_current_url`
- `get_page_title`
- `get_page_source`
- `wait_for_page_load`
- `wait_for_network_idle`
- `set_viewport_size`
- `get_page_info`

**Does NOT replace:**
- `fetch_domain_commands` (still available as legacy)

### 6. `capture_media` - Replaces Screenshot & Media Tools
**Replaces:**
- `take_screenshot`
- `take_element_screenshot`
- `generate_pdf`
- `save_page_as_pdf` (logical consolidation - PDF generation)
- `save_pdf` (logical consolidation - PDF generation)

**Does NOT replace:**
- `save_page_content` (if exists)
- `capture_video` (if exists)
- `extract_images` (if exists)

### 7. `execute_script` - Replaces Script Execution Tools
**Replaces:**
- `execute_script` (legacy version)
- `evaluate_expression`
- `inject_script`
- `get_console_logs`

**Does NOT replace:**
- `execute_script_on_element` (still available as legacy)
- `manipulate_cookies`
- `local_storage_operations`

### 8. `manage_file` - Replaces File Operation Tools
**Replaces:**
- `upload_file`
- `download_file`
- `manage_downloads`

**Does NOT replace:**
- `extract_page_data`
- `export_data`
- `import_configuration`
- `manage_sessions`
- `backup_browser_state`
- `restore_browser_state`

### 9. `find_element` - Replaces Element Finding Tools
**Replaces:**
- `find_element` (legacy version)
- `find_elements`
- `find_or_wait_element`
- `query` / `query_all`
- `get_element_text`
- `get_element_attribute`
- `wait_for_element`
- `check_element_visibility`
- `get_parent_element`

**Does NOT replace:**
- `select_option` (still available as legacy)

## What Remains as Legacy Tools

### ✅ Still Available (Not Replaced)

1. **Navigation Tools** (Legacy)
   - `fetch_domain_commands`

2. **Screenshot & Media Tools** (Active)
   - `save_page_content` (if exists)
   - `capture_video` (if exists)
   - `extract_images` (if exists)

3. **Script Execution Tools** (Active)
   - `execute_automation_script`
   - `inject_script_library`

4. **Page Interaction Tools** (Legacy)
   - `handle_dialog` / `handle_alert` (could be consolidated - both handle dialogs)
   - `select_option` (if exists)

5. **Network Monitoring Tools** (Active)
   - `network_monitoring`
   - `intercept_network_requests`
   - `extract_api_responses`
   - `modify_request_headers`
   - `block_requests`
   - `get_network_logs`
   - `get_network_response_body`
   - `monitor_websockets`
   - `throttle_network`
   - `clear_cache`
   - `save_har`
   - All event monitoring tools (DOM, network, page, fetch, runtime)

6. **Protection & Stealth Tools** (Active)
   - `bypass_cloudflare`
   - `bypass_recaptcha`
   - `enable_stealth_mode`
   - `simulate_human_behavior`
   - `randomize_fingerprint`
   - `handle_bot_detection`
   - `evade_detection`
   - `check_protection_status`
   - `rotate_proxy`
   - `set_user_agent`
   - `spoof_headers`
   - `randomize_timing`
   - `enable_cloudflare_auto_solve`
   - `disable_cloudflare_auto_solve`

7. **File Operations Tools** (Active)
   - `extract_page_data`
   - `export_data`
   - `import_configuration`
   - `manage_sessions`
   - `backup_browser_state`
   - `restore_browser_state`

8. **Advanced Tools** (Active)
   - `analyze_performance`
   - `analyze_content_with_ai`
   - Various advanced automation features

9. **Search Automation Tools** (Active)
    - `intelligent_search`

10. **Browser Configuration** (Legacy)
    - `set_download_behavior`
    - `set_download_path`
    - `enable_file_chooser_interception`
    - `disable_file_chooser_interception`
    - `bring_tab_to_front`

## Summary

| Category | Status | Count |
|----------|--------|-------|
| **Unified Tools** | ⭐ Recommended | 9 |
| **Replaced by Unified** | Legacy (deprecated) | ~40-50 |
| **Still Active** | Available | ~20-30 |
| **Consolidation Opportunities** | Could be unified | ~5-10 |

## Recommendation

- **Use Unified Tools** for: element interactions, element finding, tab management, browser lifecycle, navigation, screenshots/PDFs, script execution, file operations
- **Use Legacy Tools** for: specialized operations (network monitoring, protection/stealth, advanced features, browser context, etc.)

## Logical Consolidation Opportunities

The following legacy tools could be logically consolidated into existing unified tools:

1. **PDF Tools** → `capture_media`
   - `save_page_as_pdf` and `save_pdf` are PDF-related and could be added as actions to `capture_media` (which already has `generate_pdf`)

2. **Dialog Handling** → New unified tool or `interact_element`
   - `handle_dialog` and `handle_alert` are very similar (handle_alert is a simplified version) and could be consolidated into a single page interaction tool

3. **Browser Context & Permissions** → `browser_control`
   - `create_browser_context`, `list_browser_contexts`, `delete_browser_context`, `grant_permissions`, `reset_permissions` are all browser configuration operations and could logically be part of `browser_control`

## Future Plans

Future versions may add more unified tools to consolidate:
- Network monitoring operations
- Protection/stealth operations
- Advanced automation features
- Page interaction operations (dialogs, alerts)

The current unified tools cover the most common operations: element interaction, element finding, tab management, browser control, navigation, screenshots/PDFs, script execution, and file operations.

