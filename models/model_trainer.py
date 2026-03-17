"""
Model Trainer
--------------
Trains and saves the email classification and sentiment ML models.

Run this script before starting the Flask server to enable
ML-based classification instead of keyword heuristics.

Usage:
    python models/model_trainer.py
"""

import os
import sys
import pickle

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
import numpy as np

from data.sample_emails import TRAINING_TEXTS, TRAINING_LABELS, SAMPLE_EMAILS

MODEL_DIR = os.path.dirname(__file__)


def train_classifier():
    """Train the email category classifier (Logistic Regression + TF-IDF)."""
    print("\n── Training Email Category Classifier ──")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            random_state=42,
        )),
    ])

    # Cross-validation
    scores = cross_val_score(pipeline, TRAINING_TEXTS, TRAINING_LABELS, cv=3, scoring="accuracy")
    print(f"  Cross-validation accuracy: {np.mean(scores):.2%} ± {np.std(scores):.2%}")

    # Fit on all data
    pipeline.fit(TRAINING_TEXTS, TRAINING_LABELS)

    # Save
    path = os.path.join(MODEL_DIR, "classifier.pkl")
    with open(path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"  Saved classifier → {path}")

    return pipeline


def train_naive_bayes():
    """Train a secondary Naive Bayes classifier."""
    print("\n── Training Naive Bayes Classifier ──")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 1),
            max_features=3000,
            sublinear_tf=True,
        )),
        ("clf", MultinomialNB(alpha=0.5)),
    ])

    pipeline.fit(TRAINING_TEXTS, TRAINING_LABELS)

    path = os.path.join(MODEL_DIR, "classifier_nb.pkl")
    with open(path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"  Saved Naive Bayes → {path}")
    return pipeline


def train_sentiment():
    """Train a basic sentiment classifier."""
    print("\n── Training Sentiment Classifier ──")

    # Build sentiment labels from email content heuristics
    # (In production you'd use a labeled sentiment dataset)
    sentiment_texts = []
    sentiment_labels = []

    positive_texts = [
        "I love your service it is amazing and wonderful",
        "Excellent customer support thank you so much",
        "Great product fast delivery very satisfied",
        "Outstanding quality I am very happy",
        "Perfect experience highly recommend this",
        "Thank you for the wonderful assistance",
        "Fantastic service exceeded my expectations",
        "Really happy with my purchase great work",
    ]
    negative_texts = [
        "Terrible service I am furious and disgusted",
        "Worst experience ever completely unacceptable",
        "Very disappointed with this broken product",
        "Angry about the delayed shipment and rude staff",
        "Awful quality never buying again waste of money",
        "Completely frustrated with your incompetent team",
        "This is fraud and scam I demand a refund now",
        "Horrible broken damaged product arrived late",
    ]
    neutral_texts = [
        "I have a question about my order status",
        "Please provide information about your delivery times",
        "I would like to know the return policy details",
        "Can you tell me about pricing and availability",
        "I need help with my account settings configuration",
        "What are the technical specifications of this product",
    ]

    for text in positive_texts:
        sentiment_texts.append(text)
        sentiment_labels.append("Positive")
    for text in negative_texts:
        sentiment_texts.append(text)
        sentiment_labels.append("Negative")
    for text in neutral_texts:
        sentiment_texts.append(text)
        sentiment_labels.append("Neutral")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=2000)),
        ("clf", LogisticRegression(max_iter=500, random_state=42)),
    ])

    pipeline.fit(sentiment_texts, sentiment_labels)

    path = os.path.join(MODEL_DIR, "sentiment.pkl")
    with open(path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"  Saved sentiment model → {path}")
    return pipeline


def evaluate_models(classifier_pipeline):
    """Quick evaluation on training data."""
    print("\n── Evaluation on Training Data ──")
    from sklearn.metrics import classification_report

    predictions = classifier_pipeline.predict(TRAINING_TEXTS)
    print(classification_report(TRAINING_LABELS, predictions))


if __name__ == "__main__":
    print("=" * 50)
    print("  Customer Service Email Intelligence System")
    print("           Model Training Script")
    print("=" * 50)

    clf = train_classifier()
    train_naive_bayes()
    train_sentiment()
    evaluate_models(clf)

    print("\n✅ All models trained and saved successfully!")
    print("   You can now run: python run.py")
