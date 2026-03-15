"""
Database Schema
----------------
Tables:
    users           — login accounts (username, password hash, role)
    emails          — analyzed email records
    classifications — ML classification result
    sentiments      — sentiment analysis result
    priorities      — priority detection result
    suggestions     — response suggestion templates
    audit_log       — every write operation logged

Run standalone:  python app/database/schema.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.database.connection import db_session, get_db_path

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role         TEXT NOT NULL DEFAULT 'agent',   -- 'admin' | 'agent'
    full_name    TEXT NOT NULL DEFAULT '',
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login   TIMESTAMP
);
"""

CREATE_EMAILS = """
CREATE TABLE IF NOT EXISTS emails (
    id           TEXT PRIMARY KEY,
    sender       TEXT NOT NULL,
    subject      TEXT NOT NULL DEFAULT '',
    body         TEXT NOT NULL DEFAULT '',
    cleaned_text TEXT NOT NULL DEFAULT '',
    token_count  INTEGER NOT NULL DEFAULT 0,
    created_by   INTEGER,                         -- FK → users.id (nullable for API)
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
"""

CREATE_CLASSIFICATIONS = """
CREATE TABLE IF NOT EXISTS classifications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id   TEXT NOT NULL,
    category   TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.0,
    method     TEXT NOT NULL DEFAULT 'keyword_heuristic',
    all_scores TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_SENTIMENTS = """
CREATE TABLE IF NOT EXISTS sentiments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id    TEXT NOT NULL,
    sentiment   TEXT NOT NULL,
    score       REAL NOT NULL DEFAULT 0.0,
    confidence  REAL NOT NULL DEFAULT 0.0,
    label_emoji TEXT NOT NULL DEFAULT '😐',
    method      TEXT NOT NULL DEFAULT 'lexicon',
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_PRIORITIES = """
CREATE TABLE IF NOT EXISTS priorities (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id       TEXT NOT NULL,
    priority       TEXT NOT NULL,
    priority_score INTEGER NOT NULL DEFAULT 0,
    triggers       TEXT NOT NULL DEFAULT '[]',
    badge_color    TEXT NOT NULL DEFAULT '#6b7280',
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_SUGGESTIONS = """
CREATE TABLE IF NOT EXISTS suggestions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id   TEXT NOT NULL,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    tone_note  TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);
"""

CREATE_AUDIT_LOG = """
CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    action     TEXT NOT NULL,
    email_id   TEXT,
    user_id    INTEGER,
    details    TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_users_username   ON users(username);",
    "CREATE INDEX IF NOT EXISTS idx_emails_created   ON emails(created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_emails_user      ON emails(created_by);",
    "CREATE INDEX IF NOT EXISTS idx_clf_email_id     ON classifications(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_clf_category     ON classifications(category);",
    "CREATE INDEX IF NOT EXISTS idx_sent_email_id    ON sentiments(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_sent_sentiment   ON sentiments(sentiment);",
    "CREATE INDEX IF NOT EXISTS idx_pri_email_id     ON priorities(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_pri_priority     ON priorities(priority);",
    "CREATE INDEX IF NOT EXISTS idx_sugg_email_id    ON suggestions(email_id);",
    "CREATE INDEX IF NOT EXISTS idx_audit_created    ON audit_log(created_at DESC);",
]

ALL_DDL = [
    CREATE_USERS, CREATE_EMAILS, CREATE_CLASSIFICATIONS,
    CREATE_SENTIMENTS, CREATE_PRIORITIES, CREATE_SUGGESTIONS,
    CREATE_AUDIT_LOG,
] + CREATE_INDEXES


def init_db(db_path: str = None) -> None:
    """Create all tables/indexes (idempotent — safe to call on every start)."""
    with db_session(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        for stmt in ALL_DDL:
            conn.execute(stmt)
        _seed_default_users(conn)
    print(f"[DB] Schema ready: {get_db_path(db_path)}")


def _seed_default_users(conn) -> None:
    """Insert default admin + agent accounts if users table is empty."""
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        import hashlib
        def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()
        conn.executemany(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (?,?,?,?)",
            [
                ("admin",  _hash("admin123"),  "admin", "System Administrator"),
                ("agent1", _hash("agent123"),  "agent", "Support Agent One"),
                ("agent2", _hash("agent456"),  "agent", "Support Agent Two"),
            ]
        )
        print("[DB] Default users seeded  (admin/admin123 · agent1/agent123 · agent2/agent456)")


def get_schema_info(db_path: str = None) -> list:
    with db_session(db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        return [{"table": r["name"],
                 "columns": [dict(c) for c in conn.execute(f"PRAGMA table_info({r['name']})").fetchall()]}
                for r in tables]


if __name__ == "__main__":
    init_db()
    print([t["table"] for t in get_schema_info()])
