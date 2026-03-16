"""
Database Schema
----------------
Defines all tables and handles schema creation / migration.

Tables:
    emails          — core email record (sender, subject, body, timestamps)
    classifications — ML classification result per email
    sentiments      — sentiment analysis result per email
    priorities      — priority detection result per email
    suggestions     — response suggestion templates per email
    audit_log       — audit trail for all write operations

Run standalone to initialise (or re-initialise) the database:
    python app/database/schema.py
"""

import os
import sys
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.database.connection import db_session, get_db_path

# ── DDL Statements ────────────────────────────────────────────────────────────

CREATE_EMAILS = """
CREATE TABLE IF NOT EXISTS emails (
    id              TEXT PRIMARY KEY,          -- short UUID e.g. "A3F9B1C2"
    sender          TEXT NOT NULL,
    subject         TEXT NOT NULL DEFAULT '',
    body            TEXT NOT NULL DEFAULT '',
    cleaned_text    TEXT NOT NULL DEFAULT '',
    token_count     INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_CLASSIFICATIONS = """
CREATE TABLE IF NOT EXISTS classifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id        TEXT NOT NULL,
    category        TEXT NOT NULL,
    confidence      REAL NOT NULL DEFAULT 0.0,
    method          TEXT NOT NULL DEFAULT 'keyword_heuristic',
    all_scores      TEXT NOT NULL DEFAULT '{}',  -- JSON string
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_SENTIMENTS = """
CREATE TABLE IF NOT EXISTS sentiments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id        TEXT NOT NULL,
    sentiment       TEXT NOT NULL,               -- Positive|Neutral|Negative
    score           REAL NOT NULL DEFAULT 0.0,
    confidence      REAL NOT NULL DEFAULT 0.0,
    label_emoji     TEXT NOT NULL DEFAULT '😐',
    method          TEXT NOT NULL DEFAULT 'lexicon',
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_PRIORITIES = """
CREATE TABLE IF NOT EXISTS priorities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id        TEXT NOT NULL,
    priority        TEXT NOT NULL,               -- High|Medium|Low
    priority_score  INTEGER NOT NULL DEFAULT 0,
    triggers        TEXT NOT NULL DEFAULT '[]',  -- JSON array string
    badge_color     TEXT NOT NULL DEFAULT '#6b7280',
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_SUGGESTIONS = """
CREATE TABLE IF NOT EXISTS suggestions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id        TEXT NOT NULL,
    title           TEXT NOT NULL,
    body            TEXT NOT NULL,
    tone_note       TEXT NOT NULL DEFAULT '',
    sort_order      INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_AUDIT_LOG = """
CREATE TABLE IF NOT EXISTS audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    action          TEXT NOT NULL,               -- INSERT|DELETE|CLEAR|LOAD_SAMPLES
    email_id        TEXT,                        -- NULL for bulk ops
    details         TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# Indexes for common query patterns
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_emails_created   ON emails(created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_clf_email_id     ON classifications(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_clf_category     ON classifications(category);",
    "CREATE INDEX IF NOT EXISTS idx_sent_email_id    ON sentiments(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_sent_sentiment   ON sentiments(sentiment);",
    "CREATE INDEX IF NOT EXISTS idx_pri_email_id     ON priorities(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_pri_priority     ON priorities(priority);",
    "CREATE INDEX IF NOT EXISTS idx_sugg_email_id    ON suggestions(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_audit_action     ON audit_log(action);",
    "CREATE INDEX IF NOT EXISTS idx_audit_created    ON audit_log(created_at DESC);",
]

ALL_DDL = [
    CREATE_EMAILS,
    CREATE_CLASSIFICATIONS,
    CREATE_SENTIMENTS,
    CREATE_PRIORITIES,
    CREATE_SUGGESTIONS,
    CREATE_AUDIT_LOG,
] + CREATE_INDEXES


def init_db(db_path: str = None) -> None:
    """
    Create all tables and indexes if they do not already exist.
    Safe to call on every startup (idempotent).
    """
    with db_session(db_path) as conn:
        for statement in ALL_DDL:
            conn.execute(statement)
    print(f"[DB] Schema initialised at: {get_db_path(db_path)}")


def drop_all(db_path: str = None) -> None:
    """
    DROP all application tables. DESTRUCTIVE — use only in testing.
    """
    tables = ["suggestions", "priorities", "sentiments", "classifications", "audit_log", "emails"]
    with db_session(db_path) as conn:
        for t in tables:
            conn.execute(f"DROP TABLE IF EXISTS {t}")
    print("[DB] All tables dropped.")


def get_schema_info(db_path: str = None) -> list:
    """Return a list of (table_name, column_info) tuples for inspection."""
    with db_session(db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        info = []
        for row in tables:
            name = row["name"]
            cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
            info.append({
                "table": name,
                "columns": [dict(c) for c in cols],
            })
    return info


if __name__ == "__main__":
    init_db()
    info = get_schema_info()
    print(f"\n[DB] Tables created: {[t['table'] for t in info]}")
