"""
Email Classification Module
-----------------------------
Classifies customer emails into predefined categories using
TF-IDF vectorization + Logistic Regression (primary) and
Naive Bayes (secondary/fallback).

Categories:
    - Complaint
    - Inquiry
    - Refund Request
    - Technical Support
    - Feedback
"""

import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from app.modules.preprocessor import TextPreprocessor

# Category labels
CATEGORIES = [
    "Complaint",
    "Inquiry",
    "Refund Request",
    "Technical Support",
    "Feedback",
]

# Keyword heuristics used as fallback when no trained model is found
CATEGORY_KEYWORDS = {
    "Complaint": [
        "complaint", "complain", "disappointed", "unacceptable", "terrible",
        "awful", "horrible", "disgusted", "furious", "angry", "upset",
        "worst", "never again", "demand", "incompetent", "failure", "broken",
        "damaged", "wrong", "missing", "lost", "delayed", "late", "rude",
    ],
    "Inquiry": [
        "inquiry", "question", "wondering", "would like to know", "information",
        "details", "how does", "how do", "what is", "can you explain", "pricing",
        "availability", "hours", "location", "tell me about", "help me understand",
    ],
    "Refund Request": [
        "refund", "money back", "return", "reimburse", "reimbursement",
        "cancel", "cancellation", "chargeback", "overpaid", "overcharged",
        "credit", "compensation", "pay back", "give back",
    ],
    "Technical Support": [
        "technical", "error", "bug", "crash", "not working", "broken",
        "issue", "problem", "glitch", "fix", "install", "setup", "configure",
        "connect", "wifi", "password", "login", "account", "access", "reset",
        "update", "upgrade", "slow", "freeze", "hang",
    ],
    "Feedback": [
        "feedback", "suggestion", "recommend", "improve", "idea", "feature",
        "love", "great", "excellent", "amazing", "satisfied", "happy",
        "appreciate", "thank", "congratulations", "well done", "good job",
    ],
}


class EmailClassifier:
    """
    Classifies emails using a trained ML pipeline or keyword heuristics.

    Usage:
        classifier = EmailClassifier()
        result = classifier.classify("I want a refund for my broken product.")
        # {'category': 'Refund Request', 'confidence': 0.87, 'method': 'ml_model'}
    """

    def __init__(self, model_path: str = None):
        self.preprocessor = TextPreprocessor()
        self.model = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "../../models/classifier.pkl"
        )
        self._load_model()

    def _load_model(self):
        """Load trained model from disk if available."""
        abs_path = os.path.abspath(self.model_path)
        if os.path.exists(abs_path):
            with open(abs_path, "rb") as f:
                self.model = pickle.load(f)

    def _keyword_classify(self, text: str) -> dict:
        """
        Fallback classification using keyword matching.
        Returns the category with the highest keyword hit count.
        """
        text_lower = text.lower()
        scores = {cat: 0 for cat in CATEGORIES}

        for category, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[category] += 1

        best_category = max(scores, key=scores.get)
        total_hits = sum(scores.values())
        confidence = scores[best_category] / total_hits if total_hits > 0 else 0.2
        confidence = min(round(confidence, 2), 0.95)

        if scores[best_category] == 0:
            best_category = "Inquiry"
            confidence = 0.3

        return {
            "category": best_category,
            "confidence": confidence,
            "method": "keyword_heuristic",
            "all_scores": scores,
        }

    def classify(self, text: str) -> dict:
        """
        Classify a single email text.

        Args:
            text: Raw or cleaned email text

        Returns:
            dict with keys: category, confidence, method, all_scores
        """
        preprocessed = self.preprocessor.preprocess(text)
        cleaned = preprocessed["cleaned_text"]

        if self.model is not None:
            try:
                proba = self.model.predict_proba([cleaned])[0]
                category_idx = proba.argmax()
                category = CATEGORIES[category_idx]
                confidence = round(float(proba[category_idx]), 2)
                all_scores = {CATEGORIES[i]: round(float(p), 3) for i, p in enumerate(proba)}
                return {
                    "category": category,
                    "confidence": confidence,
                    "method": "ml_model",
                    "all_scores": all_scores,
                }
            except Exception:
                pass  # Fall through to keyword method

        return self._keyword_classify(text)

    @staticmethod
    def get_categories() -> list:
        """Return list of all possible categories."""
        return CATEGORIES
