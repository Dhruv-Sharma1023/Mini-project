"""
Routes Module
--------------
Defines all URL routes for the Flask application.

Routes:
    GET  /               → Landing page
    GET  /dashboard      → Email dashboard (view all analyzed emails)
    GET  /analyze        → Analyze email form
    POST /analyze        → Submit email for analysis
    POST /api/analyze    → JSON API endpoint for single email analysis
    GET  /api/emails     → JSON API: list all stored emails
    POST /api/clear      → Clear all stored emails
"""

import json
import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session

from app.modules.preprocessor import TextPreprocessor
from app.modules.classifier import EmailClassifier
from app.modules.sentiment import SentimentAnalyzer
from app.modules.priority import PriorityDetector
from app.modules.responder import ResponseSuggester

main_bp = Blueprint("main", __name__)

# In-memory email store (replace with DB in production)
email_store = []

# Initialize NLP modules once (module-level singletons)
preprocessor = TextPreprocessor()
classifier = EmailClassifier()
sentiment_analyzer = SentimentAnalyzer()
priority_detector = PriorityDetector()
responder = ResponseSuggester()


def analyze_email(subject: str, body: str, sender: str = "") -> dict:
    """
    Core analysis pipeline. Runs all NLP modules on the email.

    Returns:
        Full analysis result dict ready for storage and display.
    """
    full_text = f"{subject} {body}".strip()

    # 1. Preprocess
    preprocessed = preprocessor.preprocess(full_text)

    # 2. Classify
    classification = classifier.classify(full_text)

    # 3. Sentiment
    sentiment = sentiment_analyzer.analyze(full_text)

    # 4. Priority
    priority = priority_detector.detect(
        text=full_text,
        sentiment=sentiment["sentiment"],
        category=classification["category"],
    )

    # 5. Response suggestions
    suggestions = responder.suggest(
        category=classification["category"],
        priority=priority["priority"],
        sentiment=sentiment["sentiment"],
    )

    return {
        "id": str(uuid.uuid4())[:8].upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sender": sender or "unknown@email.com",
        "subject": subject,
        "body": body,
        "preprocessed": {
            "cleaned_text": preprocessed["cleaned_text"],
            "token_count": preprocessed["token_count"],
        },
        "classification": classification,
        "sentiment": sentiment,
        "priority": priority,
        "suggestions": suggestions,
    }


# ──────────────────────────────────────────
#  Page Routes
# ──────────────────────────────────────────

@main_bp.route("/")
def index():
    """Landing / home page."""
    stats = _compute_stats()
    return render_template("index.html", stats=stats)


@main_bp.route("/dashboard")
def dashboard():
    """Dashboard showing all analyzed emails."""
    filter_category = request.args.get("category", "All")
    filter_priority = request.args.get("priority", "All")
    filter_sentiment = request.args.get("sentiment", "All")

    filtered = email_store.copy()
    if filter_category != "All":
        filtered = [e for e in filtered if e["classification"]["category"] == filter_category]
    if filter_priority != "All":
        filtered = [e for e in filtered if e["priority"]["priority"] == filter_priority]
    if filter_sentiment != "All":
        filtered = [e for e in filtered if e["sentiment"]["sentiment"] == filter_sentiment]

    # Sort: High priority first, then by timestamp desc
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    filtered.sort(key=lambda x: (
        priority_order.get(x["priority"]["priority"], 3),
        x["timestamp"]
    ), reverse=False)

    from app.modules.classifier import CATEGORIES
    return render_template(
        "dashboard.html",
        emails=filtered,
        total=len(email_store),
        stats=_compute_stats(),
        categories=CATEGORIES,
        filter_category=filter_category,
        filter_priority=filter_priority,
        filter_sentiment=filter_sentiment,
    )


@main_bp.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Email analysis form page."""
    result = None
    error = None

    if request.method == "POST":
        sender = request.form.get("sender", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()

        if not body and not subject:
            error = "Please enter an email subject or body to analyze."
        else:
            result = analyze_email(subject=subject, body=body, sender=sender)
            email_store.append(result)

    # Load sample emails for the "Try Sample" buttons
    from data.sample_emails import SAMPLE_EMAILS
    return render_template(
        "analyze.html",
        result=result,
        error=error,
        samples=SAMPLE_EMAILS[:6],
    )


# ──────────────────────────────────────────
#  JSON API Routes
# ──────────────────────────────────────────

@main_bp.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    JSON API: Analyze a single email.

    Request body (JSON):
        { "sender": str, "subject": str, "body": str }

    Response:
        Full analysis result as JSON.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    subject = data.get("subject", "")
    body = data.get("body", "")
    sender = data.get("sender", "api@user.com")

    if not subject and not body:
        return jsonify({"error": "subject or body is required"}), 400

    result = analyze_email(subject=subject, body=body, sender=sender)
    email_store.append(result)
    return jsonify(result), 200


@main_bp.route("/api/emails", methods=["GET"])
def api_emails():
    """JSON API: Return all stored analyzed emails."""
    return jsonify({
        "total": len(email_store),
        "emails": email_store,
    }), 200


@main_bp.route("/api/clear", methods=["POST"])
def api_clear():
    """JSON API: Clear all stored emails."""
    email_store.clear()
    return jsonify({"message": "All emails cleared.", "total": 0}), 200


@main_bp.route("/api/load-samples", methods=["POST"])
def api_load_samples():
    """Load sample emails into the store for demo purposes."""
    from data.sample_emails import SAMPLE_EMAILS
    count = 0
    for sample in SAMPLE_EMAILS:
        result = analyze_email(
            subject=sample["subject"],
            body=sample["body"],
            sender=sample.get("sender", "customer@example.com"),
        )
        email_store.append(result)
        count += 1
    return jsonify({"message": f"Loaded {count} sample emails.", "total": len(email_store)}), 200


# ──────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────

def _compute_stats() -> dict:
    """Compute summary statistics for the dashboard."""
    total = len(email_store)
    if total == 0:
        return {"total": 0, "high": 0, "medium": 0, "low": 0,
                "positive": 0, "neutral": 0, "negative": 0,
                "categories": {}}

    stats = {
        "total": total,
        "high": sum(1 for e in email_store if e["priority"]["priority"] == "High"),
        "medium": sum(1 for e in email_store if e["priority"]["priority"] == "Medium"),
        "low": sum(1 for e in email_store if e["priority"]["priority"] == "Low"),
        "positive": sum(1 for e in email_store if e["sentiment"]["sentiment"] == "Positive"),
        "neutral": sum(1 for e in email_store if e["sentiment"]["sentiment"] == "Neutral"),
        "negative": sum(1 for e in email_store if e["sentiment"]["sentiment"] == "Negative"),
        "categories": {},
    }
    for e in email_store:
        cat = e["classification"]["category"]
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1

    return stats
