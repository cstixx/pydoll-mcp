"""Browser Manager for PyDoll MCP Server.

This module provides centralized browser instance management, including:
- Browser lifecycle management
- Resource cleanup and monitoring
- Configuration management
- Performance optimization
"""

import asyncio
import logging
import os
import time
import weakref
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from collections import deque
from contextlib import asynccontextmanager

from ..config import get_settings
from .session_store import SessionStore

try:
    from pydoll.browser import Chrome, Edge
    from pydoll.browser.options import ChromiumOptions
    from pydoll.browser.tab import Tab
    PYDOLL_AVAILABLE = True
except ImportError:
    PYDOLL_AVAILABLE = False
    Chrome = None
    Edge = None
    ChromiumOptions = None
    Tab = None

logger = logging.getLogger(__name__)


class BrowserMetrics:
    """Track browser performance metrics."""

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.navigation_times = deque(maxlen=max_history)
        self.memory_usage = deque(maxlen=max_history)
        self.cpu_usage = deque(maxlen=max_history)
        self.error_count = 0
        self.total_operations = 0

    def record_navigation(self, duration: float):
        """Record navigation timing."""
        self.navigation_times.append(duration)
        self.total_operations += 1

    def get_avg_navigation_time(self) -> float:
        """Get average navigation time."""
        if not self.navigation_times:
            return 0.0
        return sum(self.navigation_times) / len(self.navigation_times)

    def record_error(self):
        """Record an error occurrence."""
        self.error_count += 1

    def get_error_rate(self) -> float:
        """Get error rate as percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.error_count / self.total_operations) * 100


class BrowserInstance:
    """Represents a managed browser instance with metadata."""

    def __init__(self, browser, browser_type: str, instance_id: str):
        from datetime import datetime
        self.browser = browser
        self.browser_type = browser_type
        self.instance_id = instance_id
        self.created_at = datetime.now()
        self.tabs: Dict[str, Tab] = {}
        self.active_tab_id: Optional[str] = None
        self.is_active = True
        self.last_activity = time.time()
        self.metrics = BrowserMetrics()

        # Browser contexts tracking
        self.contexts: Dict[str, Dict[str, Any]] = {}

        # Event states tracking
        self.event_states: Dict[str, bool] = {}

        # Performance metrics
        self.stats = {
            "total_tabs_created": 0,
            "total_navigations": 0,
            "total_screenshots": 0,
            "total_scripts_executed": 0,
        }

    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = time.time()

    def get_uptime(self) -> float:
        """Get browser instance uptime in seconds."""
        from datetime import datetime
        return (datetime.now() - self.created_at).total_seconds()

    def get_idle_time(self) -> float:
        """Get time since last activity in seconds."""
        return time.time() - self.last_activity

    def to_dict(self) -> dict:
        """Convert browser instance to serializable dictionary."""
        return {
            "instance_id": self.instance_id,
            "browser_type": self.browser_type,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "uptime": self.get_uptime(),
            "idle_time": self.get_idle_time(),
            "tabs_count": len(self.tabs),
            "contexts_count": len(self.contexts) if hasattr(self, 'contexts') else 0,
            "event_states": self.event_states if hasattr(self, 'event_states') else {},
            "stats": self.stats,
            "error_rate": self.metrics.get_error_rate(),
            "avg_navigation_time": self.metrics.get_avg_navigation_time()
        }

    @asynccontextmanager
    async def tab_context(self, tab_id: str):
        """Context manager for safe tab operations."""
        tab = self.tabs.get(tab_id)
        if not tab:
            raise ValueError(f"Tab {tab_id} not found")

        try:
            yield tab
            self.update_activity()
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"Error in tab operation: {e}")
            raise

    async def cleanup(self):
        """Clean up browser instance and all associated resources."""
        try:
            logger.info(f"Cleaning up browser instance {self.instance_id}")

            # Close all tabs with timeout
            for tab_id, tab in list(self.tabs.items()):
                try:
                    await asyncio.wait_for(
                        tab.close(),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Tab {tab_id} close timed out")
                except Exception as e:
                    logger.warning(f"Error closing tab {tab_id}: {e}")

            self.tabs.clear()

            # Stop browser with timeout
            if self.browser and hasattr(self.browser, 'stop'):
                try:
                    await asyncio.wait_for(
                        self.browser.stop(),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Browser stop timed out for {self.instance_id}")
                except Exception as e:
                    logger.warning(f"Error stopping browser: {e}")

            self.is_active = False
            logger.info(f"Browser instance {self.instance_id} cleaned up successfully")

        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")


class BrowserPool:
    """Pool of browser instances for improved resource management."""

    def __init__(self, max_size: int = 3):
        self.max_size = max_size
        self.available = deque()
        self.in_use = set()
        self._lock = asyncio.Lock()

    async def acquire(self) -> Optional[BrowserInstance]:
        """Acquire a browser instance from the pool."""
        async with self._lock:
            if self.available:
                instance = self.available.popleft()
                self.in_use.add(instance)
                return instance
            return None

    async def release(self, instance: BrowserInstance):
        """Release a browser instance back to the pool."""
        async with self._lock:
            if instance in self.in_use:
                self.in_use.remove(instance)
                if len(self.available) < self.max_size and instance.is_active:
                    self.available.append(instance)
                else:
                    await instance.cleanup()

    async def clear(self):
        """Clear all instances from the pool."""
        async with self._lock:
            # Cleanup available instances
            while self.available:
                instance = self.available.popleft()
                await instance.cleanup()

            # Cleanup in-use instances
            for instance in list(self.in_use):
                await instance.cleanup()
            self.in_use.clear()


class BrowserManager:
    """Centralized browser management for PyDoll MCP Server.

    This class is now stateless - all persistent state is managed by SessionStore.
    BrowserInstance objects are kept as temporary operation contexts.
    """

    def __init__(self, session_store: Optional[SessionStore] = None):
        """Initialize BrowserManager.

        Args:
            session_store: Optional SessionStore instance. If None, creates a new one.
        """
        self.session_store = session_store or SessionStore()
        self.settings = get_settings()
        # pylint: disable=no-member
        self.default_browser_type = self.settings.browser_type.lower()
        self.max_browsers = self.settings.max_browsers
        self.max_tabs_per_browser = self.settings.max_tabs_per_browser
        self.cleanup_interval = self.settings.cleanup_interval
        self.idle_timeout = self.settings.idle_timeout

        # Temporary cache for active BrowserInstance objects (not persisted)
        # These are loaded on-demand and kept in memory for active operations
        self._active_browsers: Dict[str, BrowserInstance] = {}

        # Browser pool for better resource management
        self.browser_pool = BrowserPool(max_size=self.max_browsers)

        # Global statistics
        self.global_stats = {
            "total_browsers_created": 0,
            "total_browsers_destroyed": 0,
            "total_errors": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # Cleanup task
        self._cleanup_task = None
        self._is_running = False

        # Performance optimization: Browser option cache
        self._options_cache = {}

        logger.info(f"BrowserManager initialized with max_browsers={self.max_browsers}")

    async def start(self):
        """Start the browser manager and background tasks."""
        if self._is_running:
            return

        self._is_running = True

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("BrowserManager started")

    async def stop(self):
        """Stop the browser manager and cleanup all resources."""
        self._is_running = False

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Cleanup all browsers
        await self.cleanup_all()
        await self.browser_pool.clear()
        logger.info("BrowserManager stopped")

    def _generate_browser_id(self) -> str:
        """Generate a unique browser instance ID."""
        import uuid
        return f"browser_{uuid.uuid4().hex[:8]}"

    def _generate_tab_id(self) -> str:
        """Generate a unique tab ID."""
        import uuid
        return f"tab_{uuid.uuid4().hex[:8]}"

    async def _check_existing_chrome_processes(self):
        """Check for existing Chrome processes and warn user."""
        import psutil
        chrome_processes = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if chrome_processes:
                logger.warning(f"Found {len(chrome_processes)} existing Chrome processes. "
                             "This may cause conflicts. Consider closing Chrome or using a custom user data directory.")
                # Add a unique user data directory to avoid conflicts
                import tempfile
                temp_dir = tempfile.mkdtemp(prefix="pydoll_chrome_")
                logger.info(f"Using temporary user data directory: {temp_dir}")
                return temp_dir
        except ImportError:
            logger.debug("psutil not available, skipping Chrome process check")
        except Exception as e:
            logger.debug(f"Error checking Chrome processes: {e}")

        return None

    def _get_browser_options(self, **kwargs) -> ChromiumOptions:
        """Create browser options based on configuration and parameters."""
        if not ChromiumOptions:
            raise RuntimeError("PyDoll not available - ChromiumOptions not imported")

        # Create cache key from kwargs (convert lists to tuples for hashability)
        def make_hashable(obj):
            if isinstance(obj, list):
                return tuple(obj)
            elif isinstance(obj, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
            return obj

        hashable_kwargs = {k: make_hashable(v) for k, v in kwargs.items()}
        cache_key = hash(frozenset(hashable_kwargs.items()))

        # Check cache first
        if cache_key in self._options_cache:
            self.global_stats["cache_hits"] += 1
            return self._options_cache[cache_key]

        self.global_stats["cache_misses"] += 1

        options = ChromiumOptions()

        # Environment-based defaults
        settings = get_settings()
        headless = kwargs.get("headless", settings.headless_mode)
        window_width = int(kwargs.get("window_width", settings.window_width))
        window_height = int(kwargs.get("window_height", settings.window_height))

        # Configure options
        if headless:
            try:
                options.add_argument("--headless=new")  # Use new headless mode
            except Exception:
                pass

        try:
            options.add_argument(f"--window-size={window_width},{window_height}")
        except Exception:
            pass

        # Stealth and performance options (Chrome compatible)
        settings = get_settings()
        if settings.stealth_mode:
            # Enhanced stealth options for modern Chrome
            # Note: --no-first-run and --no-default-browser-check are already added by PyDoll
            stealth_args = [
                # "--no-default-browser-check",  # Already added by PyDoll
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-ipc-flooding-protection",
                "--disable-component-extensions-with-background-pages",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-background-networking",
                "--disable-client-side-phishing-detection",
            ]

            for arg in stealth_args:
                try:
                    options.add_argument(arg)
                except Exception:
                    # Skip if argument already exists
                    pass

        # Additional stability options (removed --disable-gpu-sandbox for security)
        stability_args = [
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]

        for arg in stability_args:
            try:
                options.add_argument(arg)
            except Exception:
                # Skip if argument already exists
                pass

        # Enhanced performance optimizations
        settings = get_settings()
        if settings.disable_images:
            try:
                options.add_argument("--disable-images")
            except Exception:
                pass

        # Windows-specific optimizations for better compatibility
        if os.name == 'nt':  # Windows
            try:
                # Windows-specific Chrome arguments for better stability
                options.add_argument("--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--force-device-scale-factor=1")
            except Exception:
                pass

        # Memory and CPU optimizations
        performance_args = [
            "--memory-pressure-off",
            "--max_old_space_size=4096",
            "--aggressive-cache-discard",
            "--disable-background-mode",
            "--disable-hang-monitor",
            "--disable-prompt-on-repost",
            "--disable-domain-reliability",
        ]

        for arg in performance_args:
            try:
                options.add_argument(arg)
            except Exception:
                # Skip if argument already exists
                pass

        # User data directory configuration
        user_data_dir = kwargs.get("user_data_dir")
        if user_data_dir:
            try:
                options.add_argument(f"--user-data-dir={user_data_dir}")
                logger.debug(f"Using custom user data directory: {user_data_dir}")
            except Exception:
                pass

        # Proxy configuration
        settings = get_settings()
        proxy = kwargs.get("proxy", settings.default_proxy)
        if proxy:
            try:
                options.add_argument(f"--proxy-server={proxy}")
            except Exception:
                pass

        # Custom binary path
        binary_path = kwargs.get("binary_path", settings.binary_path)
        if binary_path:
            options.binary_location = binary_path

        # Custom user data directory
        user_data_dir = kwargs.get("user_data_dir", settings.user_data_dir)
        if user_data_dir:
            try:
                options.add_argument(f"--user-data-dir={user_data_dir}")
            except Exception:
                pass

        # Additional custom arguments
        custom_args = kwargs.get("custom_args", [])
        for arg in custom_args:
            try:
                options.add_argument(arg)
            except Exception:
                # Skip if argument already exists
                pass

        # Cache the options
        # Note: We must NOT cache mutable ChromiumOptions objects because they are modified in-place
        # by the Chrome class (e.g., adding default arguments).
        # We can cache the configuration logic if needed, but for now, disabling cache to fix bugs.
        # self._options_cache[cache_key] = options



        return options

    async def create_browser(self, browser_type: Optional[str] = None, **kwargs) -> BrowserInstance:
        """Create a new browser instance with optimized settings."""
        if not PYDOLL_AVAILABLE:
            raise RuntimeError("PyDoll library is not available. Please install with: pip install pydoll-python")

        # Check pool first
        pooled_instance = await self.browser_pool.acquire()
        if pooled_instance:
            logger.info(f"Reusing pooled browser instance {pooled_instance.instance_id}")
            return pooled_instance

        # Check browser limit from SessionStore
        active_browsers = await self.session_store.list_browsers(active_only=True)
        if len(active_browsers) >= self.max_browsers:
            # Try to cleanup idle browsers
            await self._cleanup_idle_browsers()

            # Re-check after cleanup
            active_browsers = await self.session_store.list_browsers(active_only=True)
            if len(active_browsers) >= self.max_browsers:
                raise RuntimeError(f"Maximum browser limit ({self.max_browsers}) reached")

        browser_type = browser_type or self.default_browser_type
        browser_id = self._generate_browser_id()

        try:
            logger.info(f"Creating new {browser_type} browser instance {browser_id}")

            # Check for existing Chrome processes if user data dir is default
            temp_user_data_dir = None
            if browser_type == "chrome" and not kwargs.get("user_data_dir"):
                temp_user_data_dir = await self._check_existing_chrome_processes()
                if temp_user_data_dir:
                    kwargs["user_data_dir"] = temp_user_data_dir

            # Get browser options
            options = self._get_browser_options(**kwargs)

            # Create browser based on type
            if browser_type == "chrome":
                browser = Chrome(options=options)
            elif browser_type == "edge":
                browser = Edge(options=options)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

            # Start browser - browser.start() returns the initial Tab
            # Add timeout to prevent hanging if browser doesn't start
            start_time = time.time()
            try:
                initial_tab = await asyncio.wait_for(
                    browser.start(),
                    timeout=30.0  # 30 second timeout for browser startup
                )
            except asyncio.TimeoutError:
                logger.error(f"Browser startup timed out after 30 seconds for {browser_id}")
                raise RuntimeError(f"Browser startup timed out after 30 seconds")
            startup_time = time.time() - start_time

            # Create browser instance
            instance = BrowserInstance(browser, browser_type, browser_id)
            instance.metrics.record_navigation(startup_time)

            # IMPORTANT: PyDoll's browser.start() ALWAYS returns the initial Tab object
            # We must register this tab immediately
            if initial_tab:
                default_tab_id = self._generate_tab_id()
                instance.tabs[default_tab_id] = initial_tab
                instance.active_tab_id = default_tab_id
                # Store the tab reference in browser object for compatibility
                instance.browser.tab = initial_tab
                logger.info(f"Registered initial tab from browser.start(): {default_tab_id}")

                # Enhanced Windows compatibility: Wait for tab to be fully ready
                # Run readiness check in background to avoid blocking browser creation
                async def check_tab_readiness():
                    try:
                        await asyncio.sleep(0.5)  # Give tab time to initialize
                        # Try to get tab title to ensure it's ready (with timeout)
                        await asyncio.wait_for(
                            self._ensure_tab_ready(initial_tab, default_tab_id, timeout=3.0),
                            timeout=4.0  # Slightly longer than _ensure_tab_ready timeout
                        )
                    except (asyncio.TimeoutError, Exception) as e:
                        logger.debug(f"Tab initialization check completed with: {e}")

                # Don't wait for readiness check - let it run in background
                # This prevents hanging if the tab isn't ready yet
                asyncio.create_task(check_tab_readiness())
            else:
                # This should never happen with PyDoll
                logger.error("CRITICAL: No initial tab returned from browser.start() - this is unexpected!")
                raise RuntimeError("PyDoll browser.start() did not return a tab")

            # Try to extract debug_port from browser connection if available
            debug_port = None
            pid = None
            try:
                # PyDoll may expose connection info - check for common attributes
                # pylint: disable=no-member,protected-access
                if hasattr(browser, '_connection') and hasattr(browser._connection, 'port'):
                    debug_port = browser._connection.port  # type: ignore
                elif hasattr(browser, 'port'):
                    debug_port = browser.port
                # Try to get PID if available
                if hasattr(browser, 'process') and hasattr(browser.process, 'pid'):
                    pid = browser.process.pid  # type: ignore
            except Exception as e:
                logger.debug(f"Could not extract debug_port/pid: {e}")

            # Save to SessionStore
            await self.session_store.save_browser(
                browser_id=browser_id,
                browser_type=browser_type,
                debug_port=debug_port,
                pid=pid,
                config=kwargs
            )

            # Save initial tab to SessionStore
            if initial_tab:
                try:
                    url = None
                    title = None
                    if hasattr(initial_tab, 'current_url') and callable(initial_tab.current_url):
                        url = await initial_tab.current_url()
                    if hasattr(initial_tab, 'page_title') and callable(initial_tab.page_title):
                        title = await initial_tab.page_title()
                except Exception:
                    url = None
                    title = None

                await self.session_store.save_tab(
                    tab_id=default_tab_id,
                    browser_id=browser_id,
                    url=url,
                    title=title
                )

            # Store in active cache for immediate use
            self._active_browsers[browser_id] = instance
            self.global_stats["total_browsers_created"] += 1

            logger.info(f"Browser {browser_id} created successfully in {startup_time:.2f}s with {len(instance.tabs)} initial tab(s)")
            return instance

        except Exception as e:
            self.global_stats["total_errors"] += 1
            logger.error(f"Failed to create browser: {e}")
            raise

    async def get_browser(self, browser_id: str) -> Optional[BrowserInstance]:
        """Get a browser instance by ID.

        First checks active cache, then tries to reattach from SessionStore.

        Args:
            browser_id: Unique browser identifier

        Returns:
            BrowserInstance if found, None otherwise
        """
        # Check active cache first (fast path, no timeout needed)
        if browser_id in self._active_browsers:
            return self._active_browsers[browser_id]

        # Try to reattach from SessionStore with timeout
        try:
            return await asyncio.wait_for(
                self.reattach_browser(browser_id),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            logger.debug(f"get_browser timed out for {browser_id}")
            return None

    async def get_tab(self, browser_id: str, tab_id: str):
        """Get a tab from a browser instance."""
        instance = await self.get_browser(browser_id)
        if not instance:
            raise ValueError(f"Browser {browser_id} not found")

        tab = instance.tabs.get(tab_id)
        if not tab:
            raise ValueError(f"Tab {tab_id} not found in browser {browser_id}")

        return await self.ensure_tab_methods(tab)

    async def get_active_tab_id(self, browser_id: str) -> Optional[str]:
        """Get the active tab ID for a browser instance."""
        instance = await self.get_browser(browser_id)
        if not instance:
            return None

        # Return cached active tab if available
        if instance.active_tab_id and instance.active_tab_id in instance.tabs:
            return instance.active_tab_id

        # If no active tab cached, try to find one
        if instance.tabs:
            # Return the first available tab
            first_tab_id = next(iter(instance.tabs.keys()))
            instance.active_tab_id = first_tab_id
            return first_tab_id

        return None

    async def get_tab_with_fallback(self, browser_id: str, tab_id: Optional[str] = None):
        """Get a tab with automatic fallback to active tab if tab_id is None."""
        instance = await self.get_browser(browser_id)
        if not instance:
            raise ValueError(f"Browser {browser_id} not found")

        # If no tab_id provided, get the active tab
        if tab_id is None:
            tab_id = await self.get_active_tab_id(browser_id)
            if tab_id is None:
                raise ValueError(f"No active tab found in browser {browser_id}")

        # Get the specific tab
        tab = instance.tabs.get(tab_id)
        if not tab:
            # Try to get active tab as fallback
            active_tab_id = await self.get_active_tab_id(browser_id)
            if active_tab_id and active_tab_id != tab_id:
                tab = instance.tabs.get(active_tab_id)
                if tab:
                    logger.warning(f"Tab {tab_id} not found, using active tab {active_tab_id}")
                    tab_id = active_tab_id

            if not tab:
                raise ValueError(f"Tab {tab_id} not found in browser {browser_id}")

        return await self.ensure_tab_methods(tab), tab_id

    async def destroy_browser(self, browser_id: str):
        """Destroy a browser instance and cleanup resources."""
        instance = self._active_browsers.get(browser_id)

        try:
            logger.info(f"Destroying browser {browser_id}")

            # Cleanup browser instance if in cache
            if instance:
                # Release to pool first
                await self.browser_pool.release(instance)
                # Cleanup browser resources
                await instance.cleanup()
                # Remove from active cache
                del self._active_browsers[browser_id]

            # Mark as inactive in SessionStore
            await self.session_store.delete_browser(browser_id)
            self.global_stats["total_browsers_destroyed"] += 1

            logger.info(f"Browser {browser_id} destroyed successfully")

        except Exception as e:
            self.global_stats["total_errors"] += 1
            logger.error(f"Failed to destroy browser {browser_id}: {e}")
            raise

    async def cleanup_all(self):
        """Cleanup all browser instances."""
        logger.info("Cleaning up all browser instances")

        # Get all active browsers from SessionStore
        active_browsers = await self.session_store.list_browsers(active_only=True)
        browser_ids = [b["browser_id"] for b in active_browsers]

        for browser_id in browser_ids:
            try:
                await self.destroy_browser(browser_id)
            except Exception as e:
                logger.error(f"Failed to destroy browser {browser_id}: {e}")

        # Clear active cache
        self._active_browsers.clear()
        logger.info("All browser instances cleaned up")

    async def _cleanup_idle_browsers(self):
        """Cleanup browsers that have been idle for too long."""
        from datetime import datetime

        active_browsers = await self.session_store.list_browsers(active_only=True)
        idle_browsers = []

        current_time = datetime.utcnow()

        for browser_data in active_browsers:
            last_activity_str = browser_data.get("last_activity")
            if last_activity_str:
                try:
                    last_activity = datetime.fromisoformat(last_activity_str)
                    idle_seconds = (current_time - last_activity).total_seconds()
                    if idle_seconds > self.idle_timeout:
                        idle_browsers.append(browser_data["browser_id"])
                except Exception as e:
                    logger.debug(f"Error parsing last_activity for {browser_data['browser_id']}: {e}")

        for browser_id in idle_browsers:
            logger.info(f"Cleaning up idle browser {browser_id}")
            try:
                await self.destroy_browser(browser_id)
            except Exception as e:
                logger.error(f"Failed to cleanup idle browser {browser_id}: {e}")

    async def _periodic_cleanup(self):
        """Periodically cleanup idle resources."""
        while self._is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_idle_browsers()

                # Log statistics
                active_browsers = await self.session_store.list_browsers(active_only=True)
                logger.info(f"Browser stats: Active={len(active_browsers)}, "
                          f"Created={self.global_stats['total_browsers_created']}, "
                          f"Destroyed={self.global_stats['total_browsers_destroyed']}, "
                          f"Errors={self.global_stats['total_errors']}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get browser manager statistics."""
        active_browsers = await self.session_store.list_browsers(active_only=True)
        stats = {
            "active_browsers": len(active_browsers),
            "max_browsers": self.max_browsers,
            "global_stats": self.global_stats.copy(),
            "browser_details": [],
        }

        # Get details from active cache and SessionStore
        for browser_data in active_browsers:
            browser_id = browser_data["browser_id"]
            instance = self._active_browsers.get(browser_id)

            if instance:
                stats["browser_details"].append({
                    "id": browser_id,
                    "type": instance.browser_type,
                    "uptime": instance.get_uptime(),
                    "idle_time": instance.get_idle_time(),
                    "tabs": len(instance.tabs),
                    "stats": instance.stats.copy(),
                    "avg_navigation_time": instance.metrics.get_avg_navigation_time(),
                    "error_rate": instance.metrics.get_error_rate(),
                })
            else:
                # Browser exists in store but not in cache (not reattached)
                stats["browser_details"].append({
                    "id": browser_id,
                    "type": browser_data.get("browser_type", "unknown"),
                    "status": "not_attached",
                })

        return stats

    async def reattach_browser(self, browser_id: str) -> Optional[BrowserInstance]:
        """Attempt to reattach to an existing browser from SessionStore.

        This method tries to reconnect to a browser that was persisted
        in SessionStore, typically after a server restart.

        Args:
            browser_id: Unique browser identifier

        Returns:
            BrowserInstance if reattachment successful, None otherwise
        """
        try:
            browser_data = await asyncio.wait_for(
                self.session_store.get_browser(browser_id),
                timeout=5.0  # Quick timeout for database query
            )
        except asyncio.TimeoutError:
            logger.warning(f"Session store query timed out for browser {browser_id}")
            return None
        except Exception as e:
            logger.debug(f"Error querying session store for {browser_id}: {e}")
            return None

        if not browser_data:
            return None

        # For now, we can't actually reattach to existing Chrome instances
        # without additional PyDoll API support. This is a placeholder for
        # future implementation when PyDoll supports reconnection via debug_port.
        #
        # The browser would need to be started with --remote-debugging-port
        # and we'd need PyDoll API to connect to existing instances.

        logger.debug(f"Browser {browser_id} found in SessionStore but reattachment not yet implemented")
        return None

    async def _ensure_tab_ready(self, tab, tab_id: str, timeout: float = 5.0):
        """Enhanced tab readiness check for Windows compatibility.

        Args:
            tab: Tab object to check
            tab_id: Tab identifier for logging
            timeout: Maximum time to wait for tab readiness (default: 5 seconds)
        """
        try:
            # Try multiple methods to ensure tab is ready with timeout
            max_attempts = 5
            attempt_timeout = timeout / max_attempts

            for attempt in range(max_attempts):
                try:
                    # Check if tab has basic properties with timeout
                    if hasattr(tab, 'page_title'):
                        title = await asyncio.wait_for(
                            tab.page_title(),
                            timeout=attempt_timeout
                        )
                        logger.debug(f"Tab {tab_id} title: {title}")
                        break
                    elif hasattr(tab, 'execute_script'):
                        # Try to execute a simple script to verify tab is ready
                        result = await asyncio.wait_for(
                            tab.execute_script('return document.readyState;'),
                            timeout=attempt_timeout
                        )
                        if result:
                            logger.debug(f"Tab {tab_id} ready state check passed")
                            break
                    else:
                        # Basic existence check
                        logger.debug(f"Tab {tab_id} basic existence check passed")
                        break
                except asyncio.TimeoutError:
                    if attempt == max_attempts - 1:
                        logger.warning(f"Tab readiness check timed out after {max_attempts} attempts")
                    else:
                        await asyncio.sleep(0.5)  # Wait before retry
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.warning(f"Tab readiness check failed after {max_attempts} attempts: {e}")
                    else:
                        await asyncio.sleep(0.5)  # Wait before retry
        except Exception as e:
            logger.warning(f"Tab readiness check error: {e}")

    # Backward compatibility methods
    async def ensure_tab_methods(self, tab):
        """Ensure tab has all required methods for compatibility."""
        if not hasattr(tab, 'fetch_domain_commands'):
            # Add stub method for older PyDoll versions
            async def fetch_domain_commands_stub(domain: Optional[str] = None):
                return {"error": "fetch_domain_commands not available in this PyDoll version"}
            tab.fetch_domain_commands = fetch_domain_commands_stub

        if not hasattr(tab, 'get_parent_element'):
            # Add stub method for older PyDoll versions
            async def get_parent_element_stub(selector: str):
                return {"error": "get_parent_element not available in this PyDoll version"}
            tab.get_parent_element = get_parent_element_stub

        return tab


# Global browser manager instance
_browser_manager: Optional[BrowserManager] = None


def get_browser_manager(session_store: Optional[SessionStore] = None) -> BrowserManager:
    """Get the global browser manager instance.

    Args:
        session_store: Optional SessionStore instance. If provided, uses it.
                      If None and no manager exists, creates a new SessionStore.

    Returns:
        BrowserManager: The global browser manager instance
    """
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager(session_store=session_store)
    return _browser_manager


async def cleanup_browser_manager():
    """Cleanup the global browser manager."""
    global _browser_manager
    if _browser_manager:
        await _browser_manager.stop()
        _browser_manager = None


# Create global browser manager instance for easy access
browser_manager = get_browser_manager()
