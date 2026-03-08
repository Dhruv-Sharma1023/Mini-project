"""
Sentiment Analysis Module
---------------------------
Determines the emotional tone of a customer email.

Sentiments: Positive | Neutral | Negative

Uses a lexicon-based approach with intensity scoring,
or a trained ML model if available.
"""

import os
import pickle

# Sentiment word lexicons
POSITIVE_WORDS = {
    "happy", "great", "excellent", "amazing", "wonderful", "fantastic",
    "love", "loved", "good", "best", "awesome", "superb", "perfect",
    "satisfied", "pleased", "delighted", "impressed", "appreciate",
    "appreciated", "thankful", "grateful", "glad", "enjoy", "enjoyed",
    "helpful", "friendly", "fast", "quick", "easy", "smooth", "outstanding",
    "brilliant", "remarkable", "exceptional", "recommend", "recommended",
    "resolved", "fixed", "working", "solved", "thank", "thanks",
}

NEGATIVE_WORDS = {
    "bad", "terrible", "horrible", "awful", "disgusting", "hate",
    "angry", "furious", "upset", "disappointed", "frustrated", "annoyed",
    "worst", "useless", "broken", "defective", "damaged", "failed",
    "failure", "error", "problem", "issue", "complaint", "complain",
    "never", "refuse", "refused", "wrong", "incorrect", "unacceptable",
    "poor", "slow", "delayed", "missing", "lost", "rude", "incompetent",
    "scam", "fraud", "lie", "lied", "cheat", "cheated", "waste",
    "wasted", "disgrace", "disgraceful", "ridiculous", "absurd", "outrageous",
}

# Intensifiers that boost sentiment score
INTENSIFIERS = {
    "very", "extremely", "absolutely", "totally", "completely",
    "utterly", "incredibly", "really", "so", "quite", "highly",
}

# Negation words that flip sentiment
NEGATION_WORDS = {"not", "no", "never", "neither", "nor", "without", "barely", "hardly"}


class SentimentAnalyzer:
    """
    Analyzes the sentiment of email text.

    Usage:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze("I am very happy with the service!")
        # {'sentiment': 'Positive', 'score': 0.72, 'label_emoji': '😊'}
    """

    def __init__(self, model_path: str = None):
        self.model = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "../../models/sentiment.pkl"
        )
        self._load_model()

    def _load_model(self):
        """Load trained sentiment model if available."""
        abs_path = os.path.abspath(self.model_path)
        if os.path.exists(abs_path):
            with open(abs_path, "rb") as f:
                self.model = pickle.load(f)

    def _lexicon_sentiment(self, text: str) -> dict:
        """
        Score sentiment using word lexicons with negation handling.
        Returns a score in [-1.0, +1.0].
        """
        tokens = text.lower().split()
        pos_score = 0
        neg_score = 0
        i = 0

        while i < len(tokens):
            token = tokens[i]
            # Look ahead for intensifier
            multiplier = 1.0
            if i > 0 and tokens[i - 1] in INTENSIFIERS:
                multiplier = 1.5
            # Check negation in a window of 3 preceding words
            negated = any(tokens[max(0, i - 3): i].__contains__(n) for n in NEGATION_WORDS)

            if token in POSITIVE_WORDS:
                if negated:
                    neg_score += 1 * multiplier
                else:
                    pos_score += 1 * multiplier
            elif token in NEGATIVE_WORDS:
                if negated:
                    pos_score += 0.5 * multiplier  # Negated negative = mild positive
                else:
                    neg_score += 1 * multiplier
            i += 1

        total = pos_score + neg_score
        if total == 0:
            return {"raw_score": 0.0, "pos": 0, "neg": 0}

        # Normalize to [-1, +1]
        raw_score = (pos_score - neg_score) / total
        return {
            "raw_score": round(raw_score, 3),
            "pos": pos_score,
            "neg": neg_score,
        }

    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of email text.

        Args:
            text: Raw email text

        Returns:
            dict with:
                - sentiment: 'Positive', 'Neutral', or 'Negative'
                - score: float in [-1.0, 1.0], positive = more positive
                - confidence: 0.0–1.0
                - label_emoji: visual indicator
                - method: 'ml_model' or 'lexicon'
        """
        if self.model is not None:
            try:
                proba = self.model.predict_proba([text.lower()])[0]
                labels = ["Negative", "Neutral", "Positive"]
                idx = proba.argmax()
                sentiment = labels[idx]
                confidence = round(float(proba[idx]), 2)
                score = round(float(proba[2]) - float(proba[0]), 2)
                return {
                    "sentiment": sentiment,
                    "score": score,
                    "confidence": confidence,
                    "label_emoji": self._emoji(sentiment),
                    "method": "ml_model",
                }
            except Exception:
                pass

        # Lexicon fallback
        lexicon = self._lexicon_sentiment(text)
        raw = lexicon["raw_score"]

        if raw > 0.15:
            sentiment = "Positive"
        elif raw < -0.15:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        confidence = round(min(abs(raw) * 1.5 + 0.4, 0.95), 2)

        return {
            "sentiment": sentiment,
            "score": raw,
            "confidence": confidence,
            "label_emoji": self._emoji(sentiment),
            "method": "lexicon",
        }

    @staticmethod
    def _emoji(sentiment: str) -> str:
        mapping = {"Positive": "😊", "Neutral": "😐", "Negative": "😠"}
        return mapping.get(sentiment, "😐")
