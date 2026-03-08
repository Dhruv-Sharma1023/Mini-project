"""
Unit Tests
-----------
Tests for all core NLP modules.

Run with:
    python -m pytest tests/ -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.modules.preprocessor import TextPreprocessor
from app.modules.classifier import EmailClassifier
from app.modules.sentiment import SentimentAnalyzer
from app.modules.priority import PriorityDetector
from app.modules.responder import ResponseSuggester


# ── Preprocessor Tests ───────────────────────────────

class TestPreprocessor:
    def setup_method(self):
        self.pp = TextPreprocessor()

    def test_lowercase(self):
        result = self.pp.lowercase("Hello WORLD")
        assert result == "hello world"

    def test_remove_urls(self):
        result = self.pp.remove_urls("Visit https://example.com for info")
        assert "https://" not in result

    def test_tokenize(self):
        tokens = self.pp.tokenize("hello world today")
        assert tokens == ["hello", "world", "today"]

    def test_remove_stop_words(self):
        tokens = ["i", "am", "very", "happy", "today"]
        filtered = self.pp.remove_stop_words(tokens)
        assert "i" not in filtered
        assert "am" not in filtered
        assert "happy" in filtered

    def test_full_pipeline(self):
        text = "I am very ANGRY about my order https://example.com"
        result = self.pp.preprocess(text)
        assert "original" in result
        assert "cleaned_text" in result
        assert "tokens" in result
        assert isinstance(result["tokens"], list)
        assert result["token_count"] >= 0

    def test_empty_input(self):
        result = self.pp.preprocess("")
        assert result["token_count"] == 0
        assert result["tokens"] == []


# ── Classifier Tests ─────────────────────────────────

class TestClassifier:
    def setup_method(self):
        self.clf = EmailClassifier()

    def test_returns_valid_category(self):
        from app.modules.classifier import CATEGORIES
        result = self.clf.classify("I want a refund for my broken product")
        assert result["category"] in CATEGORIES

    def test_refund_classification(self):
        result = self.clf.classify("Please refund my money. I want a refund immediately.")
        assert result["category"] == "Refund Request"

    def test_complaint_classification(self):
        result = self.clf.classify("I am furious and disgusted with your terrible service")
        assert result["category"] == "Complaint"

    def test_inquiry_classification(self):
        result = self.clf.classify("I have a question about pricing and delivery times")
        assert result["category"] == "Inquiry"

    def test_confidence_range(self):
        result = self.clf.classify("Test email")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_result_structure(self):
        result = self.clf.classify("Hello, I need help")
        assert "category" in result
        assert "confidence" in result
        assert "method" in result


# ── Sentiment Tests ───────────────────────────────────

class TestSentiment:
    def setup_method(self):
        self.sa = SentimentAnalyzer()

    def test_positive_sentiment(self):
        result = self.sa.analyze("I love your service. It is excellent and amazing!")
        assert result["sentiment"] == "Positive"

    def test_negative_sentiment(self):
        result = self.sa.analyze("Terrible service. I hate this. Worst experience ever!")
        assert result["sentiment"] == "Negative"

    def test_result_has_emoji(self):
        result = self.sa.analyze("This is okay")
        assert result["label_emoji"] in ["😊", "😐", "😠"]

    def test_confidence_range(self):
        result = self.sa.analyze("Some email text here")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_result_structure(self):
        result = self.sa.analyze("Test text")
        assert "sentiment" in result
        assert "score" in result
        assert "confidence" in result
        assert "label_emoji" in result


# ── Priority Tests ────────────────────────────────────

class TestPriority:
    def setup_method(self):
        self.pd = PriorityDetector()

    def test_high_priority_keywords(self):
        result = self.pd.detect("I will take legal action and sue your company immediately")
        assert result["priority"] == "High"

    def test_low_priority_feedback(self):
        result = self.pd.detect("Just a quick question about delivery times", sentiment="Neutral", category="Inquiry")
        assert result["priority"] in ["Low", "Medium"]

    def test_negative_sentiment_raises_priority(self):
        result_neg = self.pd.detect("broken product", sentiment="Negative", category="Complaint")
        result_pos = self.pd.detect("broken product", sentiment="Positive", category="Feedback")
        assert result_neg["priority_score"] > result_pos["priority_score"]

    def test_result_structure(self):
        result = self.pd.detect("Test email")
        assert "priority" in result
        assert "priority_score" in result
        assert "triggers" in result
        assert "badge_color" in result

    def test_score_range(self):
        result = self.pd.detect("URGENT!!! FRAUD!!! LEGAL ACTION NOW!!!")
        assert 0 <= result["priority_score"] <= 100


# ── Responder Tests ───────────────────────────────────

class TestResponder:
    def setup_method(self):
        self.rs = ResponseSuggester()

    def test_returns_suggestions(self):
        suggestions = self.rs.suggest("Complaint", "High")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_suggestion_structure(self):
        suggestions = self.rs.suggest("Inquiry", "Medium")
        for s in suggestions:
            assert "title" in s
            assert "body" in s
            assert "tone_note" in s

    def test_all_categories(self):
        from app.modules.classifier import CATEGORIES
        for cat in CATEGORIES:
            for priority in ["High", "Medium", "Low"]:
                suggestions = self.rs.suggest(cat, priority)
                assert len(suggestions) > 0, f"No suggestions for {cat}/{priority}"

    def test_body_not_empty(self):
        suggestions = self.rs.suggest("Refund Request", "High")
        for s in suggestions:
            assert len(s["body"]) > 20


# ── Integration Test ──────────────────────────────────

class TestIntegration:
    """End-to-end test of the full analysis pipeline."""

    def test_full_pipeline(self):
        from app.routes import analyze_email
        result = analyze_email(
            subject="I demand a refund for my broken laptop",
            body="The product I received is completely broken. I am very angry and want my money back immediately. This is unacceptable!",
            sender="test@example.com"
        )

        assert result["id"]
        assert result["timestamp"]
        assert result["classification"]["category"] in [
            "Complaint", "Inquiry", "Refund Request", "Technical Support", "Feedback"
        ]
        assert result["sentiment"]["sentiment"] in ["Positive", "Neutral", "Negative"]
        assert result["priority"]["priority"] in ["High", "Medium", "Low"]
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0


if __name__ == "__main__":
    import traceback

    test_classes = [
        TestPreprocessor,
        TestClassifier,
        TestSentiment,
        TestPriority,
        TestResponder,
        TestIntegration,
    ]

    passed = 0
    failed = 0

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(cls) if m.startswith("test_")]
        print(f"\n{'─' * 50}")
        print(f"  {cls.__name__}")
        print(f"{'─' * 50}")
        for method in methods:
            try:
                if hasattr(instance, "setup_method"):
                    instance.setup_method()
                getattr(instance, method)()
                print(f"  ✅  {method}")
                passed += 1
            except Exception as e:
                print(f"  ❌  {method}")
                print(f"       {e}")
                failed += 1

    print(f"\n{'═' * 50}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'═' * 50}\n")
