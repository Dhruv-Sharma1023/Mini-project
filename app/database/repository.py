"""
Email Repository (Data Access Object)
---------------------------------------
All database read/write operations for emails and related data.
Routes and services interact ONLY through this repository —
no raw SQL outside this module.

Public API:
    EmailRepository.save(result_dict)         → str  (email_id)
    EmailRepository.get_by_id(email_id)       → dict | None
    EmailRepository.get_all(filters, sort)    → list[dict]
    EmailRepository.delete(email_id)          → bool
    EmailRepository.delete_all()              → int  (rows deleted)
    EmailRepository.get_stats()               → dict
    EmailRepository.search(query)             → list[dict]
    EmailRepository.get_recent(limit)         → list[dict]
    EmailRepository.count()                   → int
"""

import json
from datetime import datetime
from typing import Optional

from app.database.connection import db_session


class EmailRepository:
    """
    Handles all persistence for analyzed emails.

    All methods accept an optional `db_path` kwarg for testing
    against an isolated in-memory / temp database.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path

    # ── Write Operations ──────────────────────────────────────────────────────

    def save(self, result: dict) -> str:
        """
        Persist a full email analysis result to the database.

        Args:
            result: Dict produced by routes.analyze_email()

        Returns:
            The email id (str)
        """
        email_id = result["id"]
        with db_session(self.db_path) as conn:
            # 1. emails table
            conn.execute(
                """INSERT OR REPLACE INTO emails
                   (id, sender, subject, body, cleaned_text, token_count, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    email_id,
                    result.get("sender", ""),
                    result.get("subject", ""),
                    result.get("body", ""),
                    result["preprocessed"]["cleaned_text"],
                    result["preprocessed"]["token_count"],
                    result["timestamp"],
                    result["timestamp"],
                ),
            )

            # 2. classifications table
            clf = result["classification"]
            conn.execute(
                """INSERT INTO classifications
                   (email_id, category, confidence, method, all_scores)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    email_id,
                    clf["category"],
                    clf["confidence"],
                    clf["method"],
                    json.dumps(clf.get("all_scores", {})),
                ),
            )

            # 3. sentiments table
            sent = result["sentiment"]
            conn.execute(
                """INSERT INTO sentiments
                   (email_id, sentiment, score, confidence, label_emoji, method)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    email_id,
                    sent["sentiment"],
                    sent["score"],
                    sent["confidence"],
                    sent["label_emoji"],
                    sent["method"],
                ),
            )

            # 4. priorities table
            pri = result["priority"]
            conn.execute(
                """INSERT INTO priorities
                   (email_id, priority, priority_score, triggers, badge_color)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    email_id,
                    pri["priority"],
                    pri["priority_score"],
                    json.dumps(pri.get("triggers", [])),
                    pri["badge_color"],
                ),
            )

            # 5. suggestions table
            for i, sug in enumerate(result.get("suggestions", [])):
                conn.execute(
                    """INSERT INTO suggestions
                       (email_id, title, body, tone_note, sort_order)
                       VALUES (?, ?, ?, ?, ?)""",
                    (email_id, sug["title"], sug["body"], sug.get("tone_note", ""), i),
                )

            # 6. audit log
            self._log_action(conn, "INSERT", email_id, f"Saved email: {result.get('subject','')[:60]}")

        return email_id

    def delete(self, email_id: str) -> bool:
        """
        Delete a single email and all related records (cascade).

        Returns:
            True if a row was deleted, False if not found.
        """
        with db_session(self.db_path) as conn:
            cur = conn.execute("DELETE FROM emails WHERE id = ?", (email_id,))
            deleted = cur.rowcount > 0
            if deleted:
                self._log_action(conn, "DELETE", email_id, "Single email deleted")
        return deleted

    def delete_all(self) -> int:
        """
        Delete ALL emails and related records.

        Returns:
            Number of emails deleted.
        """
        with db_session(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
            conn.execute("DELETE FROM emails")  # cascade deletes related rows
            self._log_action(conn, "CLEAR", None, f"Cleared {count} emails")
        return count

    # ── Read Operations ───────────────────────────────────────────────────────

    def get_by_id(self, email_id: str) -> Optional[dict]:
        """Fetch a single fully-assembled email dict by ID."""
        with db_session(self.db_path) as conn:
            row = conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
            if not row:
                return None
            return self._assemble(conn, dict(row))

    def get_all(
        self,
        category: str = None,
        priority: str = None,
        sentiment: str = None,
        sort_by: str = "priority",   # "priority" | "date_desc" | "date_asc"
        limit: int = 500,
        offset: int = 0,
    ) -> list:
        """
        Fetch all emails with optional filters and sorting.

        Args:
            category:  Filter by category string (exact match)
            priority:  Filter by priority string (exact match)
            sentiment: Filter by sentiment string (exact match)
            sort_by:   Sorting strategy
            limit:     Max rows to return
            offset:    Pagination offset

        Returns:
            List of fully-assembled email dicts
        """
        # Build JOIN query with optional WHERE clauses
        where_clauses = []
        params = []

        if category:
            where_clauses.append("c.category = ?")
            params.append(category)
        if priority:
            where_clauses.append("p.priority = ?")
            params.append(priority)
        if sentiment:
            where_clauses.append("s.sentiment = ?")
            params.append(sentiment)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        sort_map = {
            "priority": "CASE p.priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END ASC, e.created_at DESC",
            "date_desc": "e.created_at DESC",
            "date_asc":  "e.created_at ASC",
        }
        order_sql = sort_map.get(sort_by, sort_map["priority"])

        sql = f"""
            SELECT e.*
            FROM emails e
            JOIN classifications c ON c.email_id = e.id
            JOIN sentiments      s ON s.email_id = e.id
            JOIN priorities      p ON p.email_id = e.id
            {where_sql}
            ORDER BY {order_sql}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        with db_session(self.db_path) as conn:
            rows = conn.execute(sql, params).fetchall()
            return [self._assemble(conn, dict(row)) for row in rows]

    def get_recent(self, limit: int = 10) -> list:
        """Return the most recently added emails."""
        return self.get_all(sort_by="date_desc", limit=limit)

    def search(self, query: str, limit: int = 100) -> list:
        """
        Full-text search across subject, body, and sender fields.

        Args:
            query: Search string (case-insensitive)
            limit: Max results

        Returns:
            List of matching email dicts
        """
        pattern = f"%{query}%"
        sql = """
            SELECT e.*
            FROM emails e
            WHERE e.subject LIKE ? OR e.body LIKE ? OR e.sender LIKE ?
            ORDER BY e.created_at DESC
            LIMIT ?
        """
        with db_session(self.db_path) as conn:
            rows = conn.execute(sql, (pattern, pattern, pattern, limit)).fetchall()
            return [self._assemble(conn, dict(row)) for row in rows]

    def count(self, category: str = None, priority: str = None, sentiment: str = None) -> int:
        """Return total email count with optional filters."""
        where_parts = []
        params = []

        if category:
            where_parts.append("c.category = ?")
            params.append(category)
        if priority:
            where_parts.append("p.priority = ?")
            params.append(priority)
        if sentiment:
            where_parts.append("s.sentiment = ?")
            params.append(sentiment)

        where_sql = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
        sql = f"""
            SELECT COUNT(DISTINCT e.id)
            FROM emails e
            LEFT JOIN classifications c ON c.email_id = e.id
            LEFT JOIN sentiments      s ON s.email_id = e.id
            LEFT JOIN priorities      p ON p.email_id = e.id
            {where_sql}
        """
        with db_session(self.db_path) as conn:
            return conn.execute(sql, params).fetchone()[0]

    def get_stats(self) -> dict:
        """
        Compute summary statistics for the dashboard.
        All aggregations done in a single DB pass using SQL.
        """
        with db_session(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]

            if total == 0:
                return {
                    "total": 0, "high": 0, "medium": 0, "low": 0,
                    "positive": 0, "neutral": 0, "negative": 0,
                    "categories": {}, "recent_high": [],
                }

            # Priority counts
            pri_rows = conn.execute("""
                SELECT priority, COUNT(*) as cnt
                FROM priorities GROUP BY priority
            """).fetchall()
            pri_counts = {r["priority"]: r["cnt"] for r in pri_rows}

            # Sentiment counts
            sent_rows = conn.execute("""
                SELECT sentiment, COUNT(*) as cnt
                FROM sentiments GROUP BY sentiment
            """).fetchall()
            sent_counts = {r["sentiment"]: r["cnt"] for r in sent_rows}

            # Category counts
            cat_rows = conn.execute("""
                SELECT category, COUNT(*) as cnt
                FROM classifications GROUP BY category ORDER BY cnt DESC
            """).fetchall()
            categories = {r["category"]: r["cnt"] for r in cat_rows}

            # Most recent high-priority emails (for home page alert)
            recent_high_rows = conn.execute("""
                SELECT e.id, e.subject, e.sender, e.created_at
                FROM emails e
                JOIN priorities p ON p.email_id = e.id
                WHERE p.priority = 'High'
                ORDER BY e.created_at DESC LIMIT 3
            """).fetchall()

        return {
            "total": total,
            "high": pri_counts.get("High", 0),
            "medium": pri_counts.get("Medium", 0),
            "low": pri_counts.get("Low", 0),
            "positive": sent_counts.get("Positive", 0),
            "neutral": sent_counts.get("Neutral", 0),
            "negative": sent_counts.get("Negative", 0),
            "categories": categories,
            "recent_high": [dict(r) for r in recent_high_rows],
        }

    def get_audit_log(self, limit: int = 50) -> list:
        """Return recent audit log entries."""
        with db_session(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _assemble(self, conn: object, email_row: dict) -> dict:
        """
        Given a raw emails row, fetch related rows and assemble a
        full result dict matching the format returned by analyze_email().
        """
        eid = email_row["id"]

        clf_row = conn.execute(
            "SELECT * FROM classifications WHERE email_id = ? LIMIT 1", (eid,)
        ).fetchone()
        sent_row = conn.execute(
            "SELECT * FROM sentiments WHERE email_id = ? LIMIT 1", (eid,)
        ).fetchone()
        pri_row = conn.execute(
            "SELECT * FROM priorities WHERE email_id = ? LIMIT 1", (eid,)
        ).fetchone()
        sug_rows = conn.execute(
            "SELECT * FROM suggestions WHERE email_id = ? ORDER BY sort_order", (eid,)
        ).fetchall()

        classification = {}
        if clf_row:
            clf = dict(clf_row)
            classification = {
                "category": clf["category"],
                "confidence": clf["confidence"],
                "method": clf["method"],
                "all_scores": json.loads(clf.get("all_scores", "{}")),
            }

        sentiment = {}
        if sent_row:
            s = dict(sent_row)
            sentiment = {
                "sentiment": s["sentiment"],
                "score": s["score"],
                "confidence": s["confidence"],
                "label_emoji": s["label_emoji"],
                "method": s["method"],
            }

        priority = {}
        if pri_row:
            p = dict(pri_row)
            priority = {
                "priority": p["priority"],
                "priority_score": p["priority_score"],
                "triggers": json.loads(p.get("triggers", "[]")),
                "badge_color": p["badge_color"],
            }

        suggestions = [
            {"title": s["title"], "body": s["body"], "tone_note": s["tone_note"]}
            for s in sug_rows
        ]

        return {
            "id": eid,
            "timestamp": email_row["created_at"],
            "sender": email_row["sender"],
            "subject": email_row["subject"],
            "body": email_row["body"],
            "preprocessed": {
                "cleaned_text": email_row["cleaned_text"],
                "token_count": email_row["token_count"],
            },
            "classification": classification,
            "sentiment": sentiment,
            "priority": priority,
            "suggestions": suggestions,
        }

    @staticmethod
    def _log_action(conn, action: str, email_id: str = None, details: str = None):
        """Write an entry to the audit_log table (within existing transaction)."""
        conn.execute(
            "INSERT INTO audit_log (action, email_id, details) VALUES (?, ?, ?)",
            (action, email_id, details),
        )
