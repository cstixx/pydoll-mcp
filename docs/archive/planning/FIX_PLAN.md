# Fix Plan for Test Failures

## Overview
This document outlines the changes made to resolve test failures in the PyDoll MCP Server codebase. The failures were primarily due to API mismatches between tests and implementation, missing mock configurations for Windows compatibility, and issues with test data expectations.

## 1. BrowserManager Initialization & API Mismatches
**Issue:** `AttributeError: 'BrowserManager' object has no attribute 'browsers'` (masked error) and `AttributeError: 'BrowserManager' object has no attribute 'next_browser_id'`.
**Resolution:**
- Updated `tests/test_basic.py` to match the current `BrowserManager` implementation:
    - Renamed `start_browser` calls to `create_browser`.
    - Removed assertions for `next_browser_id` (implementation uses UUIDs).
    - Updated `BrowserConfig` usage to use `custom_args` instead of `args`.
- Updated `tests/test_browser_manager.py`:
    - Disabled `test_get_browser_options_caching` as caching was disabled to prevent bugs.
    - Fixed `test_ensure_tab_methods` to properly test attribute injection by deleting attributes before assertion.

## 2. Integration Tests
**Issue:** Failures due to missing real browser in the test environment (`InvalidBrowserPath`) and API mismatches (`start_browser` vs `create_browser`).
**Resolution:**
- Updated `tests/test_integration.py` to:
    - Use `create_browser` instead of `start_browser`.
    - Use `pytest.mark.skipif` with `_is_browser_available()` helper to skip tests when no real browser is present (e.g., in CI/CD or sandbox environments).
    - Updated test logic to work with `BrowserInstance` returned by `create_browser`.

## 3. Tool Definitions and Schemas
**Issue:** `TypeError: 'Tool' object is not subscriptable` and incorrect tool counts.
**Resolution:**
- Updated `tests/test_tools.py` to:
    - Access tool attributes using dot notation (e.g., `tool.name`) instead of dictionary access (`tool["name"]`), reflecting the change to Pydantic models for Tools.
    - Updated expected tool counts to match `pydoll_mcp/tools/__init__.py` (Total 61).
    - Updated category counts and added missing imports (`ADVANCED_TOOLS`, `PAGE_TOOLS`, `SEARCH_AUTOMATION_TOOLS`).
    - Removed obsolete schema assertions (e.g., `user_data_dir` in `start_browser`, `wait_until` in `navigate_to`).

## 4. Windows Compatibility & Mocking
**Issue:** `ValueError: Circular reference detected` during JSON serialization and `object Mock can't be used in 'await' expression`.
**Resolution:**
- Updated `tests/test_windows_compatibility.py`:
    - Fixed circular reference in `test_intelligent_search_multiple_strategies` by configuring `execute_script` mock to return independent objects via `side_effect`.
    - Fixed `test_element_finding_fallback_strategies` by mocking `find` and `query` methods on the tab mock (as the implementation uses native methods).
    - Updated `test_browser_cleanup` to use `browser_manager.stop()` to ensure proper cleanup cycle.

## 5. Browser Option Caching Bug
**Issue:** `ArgumentAlreadyExistsInOptions: Argument already exists: --no-first-run`.
**Resolution:**
- Disabled caching of `ChromiumOptions` in `pydoll_mcp/browser_manager.py`. The `Chrome` class modifies options in-place (adding default args), making cached options invalid for reuse.

## Verification
All tests have been run and passed (111 passed, 14 skipped).
