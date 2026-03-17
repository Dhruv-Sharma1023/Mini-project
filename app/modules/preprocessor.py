"""
Text Preprocessing Module
--------------------------
Handles all text cleaning, normalization, tokenization,
and stop-word removal before NLP analysis.
"""

import re
import string

# Common English stop words (no NLTK dependency)
STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
    "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself",
    "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
    "their", "theirs", "themselves", "what", "which", "who", "whom", "this",
    "that", "these", "those", "am", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "to",
    "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "s", "t", "can", "will", "just", "don", "should", "now", "d", "ll",
    "m", "o", "re", "ve", "y", "ain", "aren", "couldn", "didn", "doesn",
    "hadn", "hasn", "haven", "isn", "ma", "mightn", "mustn", "needn",
    "shan", "shouldn", "wasn", "weren", "won", "wouldn"
}


class TextPreprocessor:
    """
    Preprocesses raw email text for NLP analysis.

    Steps:
        1. Lowercase conversion
        2. Remove email headers, URLs, and special characters
        3. Tokenization
        4. Stop-word removal
        5. Return cleaned text and tokens
    """

    def __init__(self):
        self.stop_words = STOP_WORDS

    def lowercase(self, text: str) -> str:
        """Convert text to lowercase."""
        return text.lower()

    def remove_email_headers(self, text: str) -> str:
        """Remove common email header patterns (Subject:, From:, To:, Date:)."""
        patterns = [
            r"^(from|to|cc|bcc|subject|date|reply-to)\s*:.*$",
            r"^-{2,}.*$",           # Separator lines
            r"<[^>]+>",             # HTML tags
        ]
        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
        return text

    def remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        return re.sub(r"https?://\S+|www\.\S+", "", text)

    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation, keeping spaces."""
        return text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))

    def remove_extra_whitespace(self, text: str) -> str:
        """Collapse multiple spaces/newlines into a single space."""
        return re.sub(r"\s+", " ", text).strip()

    def tokenize(self, text: str) -> list:
        """Split cleaned text into individual word tokens."""
        return text.split()

    def remove_stop_words(self, tokens: list) -> list:
        """Filter out common stop words from token list."""
        return [t for t in tokens if t not in self.stop_words and len(t) > 1]

    def preprocess(self, text: str) -> dict:
        """
        Full preprocessing pipeline.

        Args:
            text: Raw email text

        Returns:
            dict with keys:
                - original: original text
                - cleaned_text: fully cleaned text string
                - tokens: list of meaningful tokens
                - token_count: number of tokens after cleaning
        """
        if not text or not isinstance(text, str):
            return {
                "original": "",
                "cleaned_text": "",
                "tokens": [],
                "token_count": 0,
            }

        cleaned = self.lowercase(text)
        cleaned = self.remove_email_headers(cleaned)
        cleaned = self.remove_urls(cleaned)
        cleaned = self.remove_punctuation(cleaned)
        cleaned = self.remove_extra_whitespace(cleaned)

        tokens = self.tokenize(cleaned)
        tokens = self.remove_stop_words(tokens)

        return {
            "original": text,
            "cleaned_text": cleaned,
            "tokens": tokens,
            "token_count": len(tokens),
        }
