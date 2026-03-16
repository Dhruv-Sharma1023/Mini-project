"""
Main Routes — all page + API endpoints.
All routes (except / redirect) require login via @login_required.
"""

import uuid
from datetime import datetime
from flask import (Blueprint, current_app, render_template,
                   request, jsonify, redirect, url_for, session, flash)

from app.modules.preprocessor import TextPreprocessor
from app.modules.classifier    import EmailClassifier
from app.modules.sentiment     import SentimentAnalyzer
from app.modules.priority      import PriorityDetector
from app.modules.responder     import ResponseSuggester
from app.database              import EmailRepository
from app.auth                  import login_required, admin_required

main_bp = Blueprint("main", __name__)

_preprocessor = TextPreprocessor()
_classifier   = EmailClassifier()
_sentiment    = SentimentAnalyzer()
_priority     = PriorityDetector()
_responder    = ResponseSuggester()


def _repo() -> EmailRepository:
    return EmailRepository(db_path=current_app.config["DB_PATH"])

def _uid() -> int | None:
    return session.get("user_id")

def analyze_email(subject: str, body: str, sender: str = "") -> dict:
    full = f"{subject} {body}".strip()
    pre  = _preprocessor.preprocess(full)
    clf  = _classifier.classify(full)
    sent = _sentiment.analyze(full)
    pri  = _priority.detect(text=full, sentiment=sent["sentiment"], category=clf["category"])
    sugs = _responder.suggest(category=clf["category"], priority=pri["priority"], sentiment=sent["sentiment"])
    return {
        "id": str(uuid.uuid4())[:8].upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sender": sender or "unknown@email.com",
        "subject": subject, "body": body,
        "preprocessed": {"cleaned_text": pre["cleaned_text"], "token_count": pre["token_count"]},
        "classification": clf, "sentiment": sent, "priority": pri, "suggestions": sugs,
    }


# ── Page Routes ───────────────────────────────────────────────────────────────

@main_bp.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("index.html", stats=_repo().get_stats())


@main_bp.route("/dashboard")
@login_required
def dashboard():
    repo = _repo()
    fc = request.args.get("category",  "All")
    fp = request.args.get("priority",  "All")
    fs = request.args.get("sentiment", "All")
    sb = request.args.get("sort", "priority")
    pg = max(int(request.args.get("page", 1)), 1)
    per = 25

    emails = repo.get_all(
        category  = fc if fc != "All" else None,
        priority  = fp if fp != "All" else None,
        sentiment = fs if fs != "All" else None,
        sort_by=sb, limit=per, offset=(pg-1)*per,
    )
    total_f = repo.count(
        category  = fc if fc != "All" else None,
        priority  = fp if fp != "All" else None,
        sentiment = fs if fs != "All" else None,
    )
    from app.modules.classifier import CATEGORIES
    return render_template("dashboard.html",
        emails=emails, total=repo.count(), total_filtered=total_f,
        stats=repo.get_stats(), categories=CATEGORIES,
        filter_category=fc, filter_priority=fp, filter_sentiment=fs,
        sort_by=sb, page=pg, total_pages=max((total_f+per-1)//per, 1), per_page=per,
    )


@main_bp.route("/analyze", methods=["GET","POST"])
@login_required
def analyze():
    result = error = None
    if request.method == "POST":
        sender  = request.form.get("sender","").strip()
        subject = request.form.get("subject","").strip()
        body    = request.form.get("body","").strip()
        if not body and not subject:
            error = "Please enter an email subject or body."
        else:
            result = analyze_email(subject=subject, body=body, sender=sender)
            _repo().save(result, user_id=_uid())
            flash("Email analyzed and saved to database.", "success")
    from data.sample_emails import SAMPLE_EMAILS
    return render_template("analyze.html", result=result, error=error, samples=SAMPLE_EMAILS[:6])


@main_bp.route("/email/<email_id>")
@login_required
def email_detail(email_id):
    email = _repo().get_by_id(email_id)
    if not email:
        return render_template("404.html"), 404
    return render_template("email_detail.html", email=email)


@main_bp.route("/audit-log")
@login_required
def audit_log_page():
    is_admin = session.get("role") == "admin"
    uid  = None if is_admin else session["user_id"]
    logs = _repo().get_audit_log(limit=100, user_id=uid)
    return render_template("audit_log.html", logs=logs, is_admin=is_admin)


# ── JSON API ──────────────────────────────────────────────────────────────────

@main_bp.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    data = request.get_json()
    if not data: return jsonify({"error":"JSON required"}), 400
    if not data.get("subject") and not data.get("body"):
        return jsonify({"error":"subject or body required"}), 400
    result = analyze_email(data.get("subject",""), data.get("body",""), data.get("sender","api@user.com"))
    _repo().save(result, user_id=_uid())
    return jsonify(result), 201


@main_bp.route("/api/emails")
@login_required
def api_emails():
    repo = _repo()
    emails = repo.get_all(
        category=request.args.get("category"),
        priority=request.args.get("priority"),
        sentiment=request.args.get("sentiment"),
        limit=min(int(request.args.get("limit",100)),500),
        offset=int(request.args.get("offset",0)),
    )
    return jsonify({"total": repo.count(), "count": len(emails), "emails": emails}), 200


@main_bp.route("/api/emails/<email_id>")
@login_required
def api_email_detail(email_id):
    e = _repo().get_by_id(email_id)
    return (jsonify(e), 200) if e else (jsonify({"error":"Not found"}), 404)


@main_bp.route("/api/emails/<email_id>", methods=["DELETE"])
@login_required
def api_delete_email(email_id):
    ok = _repo().delete(email_id, user_id=_uid())
    return (jsonify({"message":f"Deleted {email_id}"}), 200) if ok else (jsonify({"error":"Not found"}), 404)


@main_bp.route("/api/clear", methods=["POST"])
@login_required
def api_clear():
    n = _repo().delete_all(user_id=_uid())
    return jsonify({"message":f"Cleared {n} emails.", "deleted":n}), 200


@main_bp.route("/api/load-samples", methods=["POST"])
@login_required
def api_load_samples():
    from data.sample_emails import SAMPLE_EMAILS
    repo = _repo()
    for s in SAMPLE_EMAILS:
        repo.save(analyze_email(s["subject"], s["body"], s.get("sender","customer@example.com")), user_id=_uid())
    return jsonify({"message":f"Loaded {len(SAMPLE_EMAILS)} sample emails.", "total":repo.count()}), 200


@main_bp.route("/api/stats")
@login_required
def api_stats():
    return jsonify(_repo().get_stats()), 200


@main_bp.route("/api/search")
@login_required
def api_search():
    q = request.args.get("q","").strip()
    if not q: return jsonify({"error":"q required"}), 400
    results = _repo().search(q)
    return jsonify({"query":q, "total":len(results), "emails":results}), 200


@main_bp.route("/api/audit-log")
@login_required
def api_audit_log():
    is_admin = session.get("role") == "admin"
    uid  = None if is_admin else session["user_id"]
    logs = _repo().get_audit_log(limit=min(int(request.args.get("limit",50)),200), user_id=uid)
    return jsonify({"total":len(logs),"logs":logs}), 200
