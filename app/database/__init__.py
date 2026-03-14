"""
Database package.

Exports the main objects needed by the rest of the application.

Usage:
    from app.database import init_db, EmailRepository
"""

from app.database.connection import db_session, get_connection, get_db_path
from app.database.schema import init_db, get_schema_info
from app.database.repository import EmailRepository

__all__ = [
    "db_session",
    "get_connection",
    "get_db_path",
    "init_db",
    "get_schema_info",
    "EmailRepository",
]
