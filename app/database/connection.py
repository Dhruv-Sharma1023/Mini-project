"""
Database Connection Manager
-----------------------------
Manages SQLite connections using a thread-safe approach.
Provides a context manager for clean connection handling.

All database files are stored in the `instance/` folder
at the project root (created automatically).
"""

import sqlite3
import os
from contextlib import contextmanager

# Resolve the instance directory relative to project root
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INSTANCE_DIR = os.path.join(_BASE_DIR, "instance")
DEFAULT_DB_PATH = os.path.join(INSTANCE_DIR, "emailiq.db")


def get_db_path(db_path: str = None) -> str:
    """Return the active database path, creating the instance dir if needed."""
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """
    Open and return a new SQLite connection.
    Row factory is set so rows behave like dicts.
    """
    conn = sqlite3.connect(get_db_path(db_path))
    conn.row_factory = sqlite3.Row          # access columns by name
    conn.execute("PRAGMA journal_mode=WAL")  # better concurrent read performance
    conn.execute("PRAGMA foreign_keys=ON")   # enforce FK constraints
    return conn


@contextmanager
def db_session(db_path: str = None):
    """
    Context manager for a database session.

    Usage:
        with db_session() as conn:
            conn.execute("SELECT ...")

    Commits on clean exit, rolls back on exception, always closes.
    """
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
