"""Session Store for PyDoll MCP Server.

This module provides persistent session storage using SQLite,
allowing the server to reattach to existing browser sessions after restart.
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import get_settings

logger = logging.getLogger(__name__)


class SessionStore:
    """SQLite-based session store for browser and tab persistence.

    This class manages the persistent state of browsers and tabs,
    allowing the server to recover sessions after restart.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the session store.

        Args:
            db_path: Optional path to SQLite database. If None, uses default from settings.
        """
        settings = get_settings()
        self.db_path = db_path or settings.session_db_path
        self._lock = asyncio.Lock()
        self._init_lock = asyncio.Lock()  # Separate lock for initialization
        self._connection: Optional[sqlite3.Connection] = None
        self._initialized = False
        self._initializing = False  # Track if initialization is in progress

        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"SessionStore initialized with database: {self.db_path}")

    async def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection.

        Returns:
            sqlite3.Connection: Database connection
        """
        # Fast path: connection already exists
        if self._connection is not None:
            return self._connection

        # Use lock to prevent race condition in connection creation
        async with self._init_lock:
            # Double-check after acquiring lock
            if self._connection is not None:
                return self._connection

            # Create connection
            try:
                self._connection = sqlite3.connect(
                    str(self.db_path),
                    check_same_thread=False,
                    timeout=5.0  # Reduced timeout to prevent hanging
                )
                self._connection.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                logger.error(f"Failed to create database connection: {e}")
                self._connection = None
                raise

            # Initialize schema after connection is created (only once)
            if not self._initialized and not self._initializing:
                self._initializing = True
                try:
                    await self._initialize_schema()
                finally:
                    self._initializing = False

        return self._connection

    async def _initialize_schema(self):
        """Initialize database schema if not already initialized.

        This method should only be called while holding _init_lock.
        """
        if self._initialized:
            return

        # Use existing connection, don't call _get_connection to avoid recursion
        if self._connection is None:
            logger.error("Cannot initialize schema: connection is None")
            return

        conn = self._connection
        cursor = conn.cursor()

        # Create browsers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS browsers (
                browser_id TEXT PRIMARY KEY,
                browser_type TEXT NOT NULL,
                debug_port INTEGER,
                pid INTEGER,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                config_json TEXT
            )
        """)

        # Create tabs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tabs (
                tab_id TEXT PRIMARY KEY,
                browser_id TEXT NOT NULL,
                url TEXT,
                title TEXT,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (browser_id) REFERENCES browsers(browser_id) ON DELETE CASCADE
            )
        """)

        # Create session_metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_browsers_active
            ON browsers(is_active, last_activity)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tabs_browser_id
            ON tabs(browser_id, is_active)
        """)

        conn.commit()
        self._initialized = True
        logger.debug("Database schema initialized")

    async def save_browser(
        self,
        browser_id: str,
        browser_type: str,
        debug_port: Optional[int] = None,
        pid: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Save browser instance to database.

        Args:
            browser_id: Unique browser identifier
            browser_type: Type of browser (chrome, edge)
            debug_port: Chrome DevTools Protocol debug port
            pid: Process ID of the browser
            config: Browser configuration dictionary
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()
            config_json = json.dumps(config) if config else None

            cursor.execute("""
                INSERT OR REPLACE INTO browsers
                (browser_id, browser_type, debug_port, pid, created_at, last_activity, is_active, config_json)
                VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM browsers WHERE browser_id = ?), ?), ?, 1, ?)
            """, (browser_id, browser_type, debug_port, pid, browser_id, now, now, config_json))

            conn.commit()
            logger.debug(f"Saved browser {browser_id} to database")

    async def get_browser(self, browser_id: str) -> Optional[Dict[str, Any]]:
        """Get browser instance from database.

        Args:
            browser_id: Unique browser identifier

        Returns:
            Dictionary with browser data or None if not found
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM browsers WHERE browser_id = ? AND is_active = 1
            """, (browser_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def list_browsers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all browsers from database.

        Args:
            active_only: If True, only return active browsers

        Returns:
            List of browser dictionaries
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            if active_only:
                cursor.execute("""
                    SELECT * FROM browsers WHERE is_active = 1 ORDER BY last_activity DESC
                """)
            else:
                cursor.execute("""
                    SELECT * FROM browsers ORDER BY last_activity DESC
                """)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def save_tab(
        self,
        tab_id: str,
        browser_id: str,
        url: Optional[str] = None,
        title: Optional[str] = None
    ):
        """Save tab instance to database.

        Args:
            tab_id: Unique tab identifier
            browser_id: Parent browser identifier
            url: Current tab URL
            title: Current tab title
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO tabs
                (tab_id, browser_id, url, title, created_at, last_activity, is_active)
                VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM tabs WHERE tab_id = ?), ?), ?, 1)
            """, (tab_id, browser_id, url, title, tab_id, now, now))

            conn.commit()
            logger.debug(f"Saved tab {tab_id} to database")

    async def get_tab(self, tab_id: str) -> Optional[Dict[str, Any]]:
        """Get tab instance from database.

        Args:
            tab_id: Unique tab identifier

        Returns:
            Dictionary with tab data or None if not found
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tabs WHERE tab_id = ? AND is_active = 1
            """, (tab_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def list_tabs(self, browser_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all tabs for a browser.

        Args:
            browser_id: Parent browser identifier
            active_only: If True, only return active tabs

        Returns:
            List of tab dictionaries
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            if active_only:
                cursor.execute("""
                    SELECT * FROM tabs
                    WHERE browser_id = ? AND is_active = 1
                    ORDER BY last_activity DESC
                """, (browser_id,))
            else:
                cursor.execute("""
                    SELECT * FROM tabs
                    WHERE browser_id = ?
                    ORDER BY last_activity DESC
                """, (browser_id,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_browser(self, browser_id: str):
        """Mark browser as inactive (soft delete).

        Args:
            browser_id: Unique browser identifier
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE browsers SET is_active = 0 WHERE browser_id = ?
            """, (browser_id,))

            # Also mark all tabs as inactive
            cursor.execute("""
                UPDATE tabs SET is_active = 0 WHERE browser_id = ?
            """, (browser_id,))

            conn.commit()
            logger.debug(f"Deleted browser {browser_id} from database")

    async def delete_tab(self, tab_id: str):
        """Mark tab as inactive (soft delete).

        Args:
            tab_id: Unique tab identifier
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE tabs SET is_active = 0 WHERE tab_id = ?
            """, (tab_id,))

            conn.commit()
            logger.debug(f"Deleted tab {tab_id} from database")

    async def update_activity(self, browser_id: str, tab_id: Optional[str] = None):
        """Update last activity timestamp.

        Args:
            browser_id: Unique browser identifier
            tab_id: Optional tab identifier to update
        """
        async with self._lock:
            conn = await self._get_connection()
            cursor = conn.cursor()

            now = datetime.utcnow().isoformat()

            # Update browser activity
            cursor.execute("""
                UPDATE browsers SET last_activity = ? WHERE browser_id = ?
            """, (now, browser_id))

            # Update tab activity if provided
            if tab_id:
                cursor.execute("""
                    UPDATE tabs SET last_activity = ? WHERE tab_id = ?
                """, (now, tab_id))

            conn.commit()

    async def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._initialized = False
            logger.debug("Database connection closed")

