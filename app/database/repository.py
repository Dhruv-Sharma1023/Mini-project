"""
Repository — all database read/write for emails AND users.
No raw SQL anywhere outside this file.
"""

import json, hashlib
from datetime import datetime
from typing import Optional
from app.database.connection import db_session


# ── User Repository ───────────────────────────────────────────────────────────

class UserRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def get_by_id(self, user_id: int) -> Optional[dict]:
        with db_session(self.db_path) as conn:
            row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def get_by_username(self, username: str) -> Optional[dict]:
        with db_session(self.db_path) as conn:
            row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None

    def verify_password(self, username: str, password: str) -> Optional[dict]:
        """Return user dict if credentials match, else None."""
        user = self.get_by_username(username)
        if user and user["password_hash"] == self._hash(password):
            return user
        return None

    def update_last_login(self, user_id: int) -> None:
        with db_session(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET last_login=? WHERE id=?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id)
            )

    def get_all(self) -> list:
        with db_session(self.db_path) as conn:
            rows = conn.execute("SELECT id,username,role,full_name,created_at,last_login FROM users ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def create(self, username: str, password: str, role: str = "agent", full_name: str = "") -> int:
        with db_session(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO users (username,password_hash,role,full_name) VALUES (?,?,?,?)",
                (username, self._hash(password), role, full_name)
            )
        return cur.lastrowid

    def change_password(self, user_id: int, new_password: str) -> None:
        with db_session(self.db_path) as conn:
            conn.execute("UPDATE users SET password_hash=? WHERE id=?",
                         (self._hash(new_password), user_id))

    def delete(self, user_id: int) -> bool:
        with db_session(self.db_path) as conn:
            cur = conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        return cur.rowcount > 0


# ── Email Repository ──────────────────────────────────────────────────────────

class EmailRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def save(self, result: dict, user_id: int = None) -> str:
        eid = result["id"]
        with db_session(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO emails
                   (id,sender,subject,body,cleaned_text,token_count,created_by,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (eid, result.get("sender",""), result.get("subject",""),
                 result.get("body",""), result["preprocessed"]["cleaned_text"],
                 result["preprocessed"]["token_count"], user_id,
                 result["timestamp"], result["timestamp"])
            )
            clf = result["classification"]
            conn.execute(
                "INSERT INTO classifications (email_id,category,confidence,method,all_scores) VALUES (?,?,?,?,?)",
                (eid, clf["category"], clf["confidence"], clf["method"], json.dumps(clf.get("all_scores",{})))
            )
            sent = result["sentiment"]
            conn.execute(
                "INSERT INTO sentiments (email_id,sentiment,score,confidence,label_emoji,method) VALUES (?,?,?,?,?,?)",
                (eid, sent["sentiment"], sent["score"], sent["confidence"], sent["label_emoji"], sent["method"])
            )
            pri = result["priority"]
            conn.execute(
                "INSERT INTO priorities (email_id,priority,priority_score,triggers,badge_color) VALUES (?,?,?,?,?)",
                (eid, pri["priority"], pri["priority_score"], json.dumps(pri.get("triggers",[])), pri["badge_color"])
            )
            for i, s in enumerate(result.get("suggestions",[])):
                conn.execute(
                    "INSERT INTO suggestions (email_id,title,body,tone_note,sort_order) VALUES (?,?,?,?,?)",
                    (eid, s["title"], s["body"], s.get("tone_note",""), i)
                )
            self._log(conn, "INSERT", eid, user_id, f"Saved: {result.get('subject','')[:60]}")
        return eid

    def delete(self, email_id: str, user_id: int = None) -> bool:
        with db_session(self.db_path) as conn:
            cur = conn.execute("DELETE FROM emails WHERE id=?", (email_id,))
            if cur.rowcount:
                self._log(conn, "DELETE", email_id, user_id, "Deleted")
        return cur.rowcount > 0

    def delete_all(self, user_id: int = None) -> int:
        with db_session(self.db_path) as conn:
            n = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
            conn.execute("DELETE FROM emails")
            self._log(conn, "CLEAR", None, user_id, f"Cleared {n} emails")
        return n

    def get_by_id(self, email_id: str) -> Optional[dict]:
        with db_session(self.db_path) as conn:
            row = conn.execute("SELECT * FROM emails WHERE id=?", (email_id,)).fetchone()
            if not row: return None
            return self._assemble(conn, dict(row))

    def get_all(self, category=None, priority=None, sentiment=None,
                sort_by="priority", limit=500, offset=0) -> list:
        where, params = [], []
        if category:  where.append("c.category=?");  params.append(category)
        if priority:  where.append("p.priority=?");  params.append(priority)
        if sentiment: where.append("s.sentiment=?"); params.append(sentiment)
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""
        order = {
            "priority":  "CASE p.priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END ASC, e.created_at DESC",
            "date_desc": "e.created_at DESC",
            "date_asc":  "e.created_at ASC",
        }.get(sort_by, "e.created_at DESC")
        sql = f"""SELECT e.* FROM emails e
                  JOIN classifications c ON c.email_id=e.id
                  JOIN sentiments      s ON s.email_id=e.id
                  JOIN priorities      p ON p.email_id=e.id
                  {where_sql} ORDER BY {order} LIMIT ? OFFSET ?"""
        params.extend([limit, offset])
        with db_session(self.db_path) as conn:
            rows = conn.execute(sql, params).fetchall()
            return [self._assemble(conn, dict(r)) for r in rows]

    def count(self, category=None, priority=None, sentiment=None) -> int:
        where, params = [], []
        if category:  where.append("c.category=?");  params.append(category)
        if priority:  where.append("p.priority=?");  params.append(priority)
        if sentiment: where.append("s.sentiment=?"); params.append(sentiment)
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""
        sql = f"""SELECT COUNT(DISTINCT e.id) FROM emails e
                  LEFT JOIN classifications c ON c.email_id=e.id
                  LEFT JOIN sentiments      s ON s.email_id=e.id
                  LEFT JOIN priorities      p ON p.email_id=e.id
                  {where_sql}"""
        with db_session(self.db_path) as conn:
            return conn.execute(sql, params).fetchone()[0]

    def search(self, query: str, limit: int = 100) -> list:
        pat = f"%{query}%"
        with db_session(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM emails WHERE subject LIKE ? OR body LIKE ? OR sender LIKE ? ORDER BY created_at DESC LIMIT ?",
                (pat, pat, pat, limit)
            ).fetchall()
            return [self._assemble(conn, dict(r)) for r in rows]

    def get_stats(self) -> dict:
        with db_session(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
            if not total:
                return {"total":0,"high":0,"medium":0,"low":0,"positive":0,"neutral":0,"negative":0,"categories":{}}
            pri   = {r["priority"]: r["cnt"] for r in conn.execute("SELECT priority,COUNT(*) cnt FROM priorities GROUP BY priority").fetchall()}
            sent  = {r["sentiment"]: r["cnt"] for r in conn.execute("SELECT sentiment,COUNT(*) cnt FROM sentiments GROUP BY sentiment").fetchall()}
            cats  = {r["category"]: r["cnt"] for r in conn.execute("SELECT category,COUNT(*) cnt FROM classifications GROUP BY category ORDER BY cnt DESC").fetchall()}
        return {"total":total,"high":pri.get("High",0),"medium":pri.get("Medium",0),"low":pri.get("Low",0),
                "positive":sent.get("Positive",0),"neutral":sent.get("Neutral",0),"negative":sent.get("Negative",0),
                "categories":cats}

    def get_audit_log(self, limit=50, user_id=None) -> list:
        """
        If user_id is given, return only that user's entries (agent view).
        If user_id is None, return all entries (admin view).
        """
        with db_session(self.db_path) as conn:
            if user_id is not None:
                rows = conn.execute(
                    """SELECT a.*, u.username FROM audit_log a
                       LEFT JOIN users u ON u.id=a.user_id
                       WHERE a.user_id = ?
                       ORDER BY a.created_at DESC LIMIT ?""",
                    (user_id, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT a.*, u.username FROM audit_log a
                       LEFT JOIN users u ON u.id=a.user_id
                       ORDER BY a.created_at DESC LIMIT ?""",
                    (limit,)
                ).fetchall()
        return [dict(r) for r in rows]

    def _assemble(self, conn, row: dict) -> dict:
        eid = row["id"]
        clf  = conn.execute("SELECT * FROM classifications WHERE email_id=? LIMIT 1", (eid,)).fetchone()
        sent = conn.execute("SELECT * FROM sentiments     WHERE email_id=? LIMIT 1", (eid,)).fetchone()
        pri  = conn.execute("SELECT * FROM priorities     WHERE email_id=? LIMIT 1", (eid,)).fetchone()
        sugs = conn.execute("SELECT * FROM suggestions    WHERE email_id=? ORDER BY sort_order", (eid,)).fetchall()
        return {
            "id": eid, "timestamp": row["created_at"], "sender": row["sender"],
            "subject": row["subject"], "body": row["body"],
            "preprocessed": {"cleaned_text": row["cleaned_text"], "token_count": row["token_count"]},
            "classification": {
                "category": clf["category"], "confidence": clf["confidence"],
                "method": clf["method"], "all_scores": json.loads(clf["all_scores"])
            } if clf else {},
            "sentiment": {
                "sentiment": sent["sentiment"], "score": sent["score"],
                "confidence": sent["confidence"], "label_emoji": sent["label_emoji"],
                "method": sent["method"]
            } if sent else {},
            "priority": {
                "priority": pri["priority"], "priority_score": pri["priority_score"],
                "triggers": json.loads(pri["triggers"]), "badge_color": pri["badge_color"]
            } if pri else {},
            "suggestions": [{"title":s["title"],"body":s["body"],"tone_note":s["tone_note"]} for s in sugs],
        }

    @staticmethod
    def _log(conn, action, email_id, user_id, details):
        conn.execute("INSERT INTO audit_log (action,email_id,user_id,details) VALUES (?,?,?,?)",
                     (action, email_id, user_id, details))
