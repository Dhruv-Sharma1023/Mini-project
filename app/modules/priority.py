"""
Priority Detection Module
---------------------------
Assigns a priority level (High / Medium / Low) to each email
based on keyword signals, sentiment, and urgency indicators.
"""


# Keywords that signal HIGH urgency
HIGH_PRIORITY_KEYWORDS = [
    "urgent", "immediately", "asap", "emergency", "critical", "severe",
    "legal action", "lawsuit", "sue", "lawyer", "attorney", "court",
    "fraud", "scam", "stolen", "hacked", "unauthorized", "security breach",
    "life threatening", "danger", "injury", "accident", "broken immediately",
    "demand refund", "final warning", "last chance", "escalate", "manager",
    "supervisor", "ceo", "never buy again", "social media", "news",
    "regulatory", "report to", "consumer affairs",
]

# Keywords that signal MEDIUM urgency
MEDIUM_PRIORITY_KEYWORDS = [
    "soon", "please help", "need assistance", "waiting", "still waiting",
    "follow up", "follow-up", "still no response", "days ago", "week ago",
    "not working", "broken", "defective", "incorrect", "wrong item",
    "cancel", "cancellation", "overcharged", "duplicate charge",
]

# Keywords that suggest LOW urgency (routine)
LOW_PRIORITY_KEYWORDS = [
    "question", "wondering", "curious", "information", "feedback",
    "suggestion", "love", "great", "happy", "satisfied", "inquiry",
    "just wanted", "when you have time",
]


class PriorityDetector:
    """
    Determines email priority based on content and sentiment.

    Priority Rules (applied in order):
        HIGH   → Contains legal threats, security issues, or high-urgency keywords
        HIGH   → Negative sentiment + high negative keyword density
        MEDIUM → Contains medium urgency keywords or neutral sentiment + complaints
        LOW    → Positive sentiment or routine inquiry keywords
    """

    def detect(self, text: str, sentiment: str = None, category: str = None) -> dict:
        """
        Detect priority level for an email.

        Args:
            text:      Raw or cleaned email text
            sentiment: Sentiment label ('Positive', 'Neutral', 'Negative')
            category:  Classified category ('Complaint', 'Inquiry', etc.)

        Returns:
            dict with:
                - priority: 'High', 'Medium', or 'Low'
                - priority_score: 0–100 numeric score
                - triggers: list of matched keywords/rules that raised priority
                - badge_color: CSS color name for UI display
        """
        text_lower = text.lower()
        triggers = []
        score = 0  # 0–100

        # --- HIGH priority keyword check ---
        for kw in HIGH_PRIORITY_KEYWORDS:
            if kw in text_lower:
                score += 30
                triggers.append(f'keyword: "{kw}"')
                if score >= 60:
                    break

        # --- MEDIUM priority keyword check ---
        if score < 60:
            for kw in MEDIUM_PRIORITY_KEYWORDS:
                if kw in text_lower:
                    score += 12
                    triggers.append(f'keyword: "{kw}"')

        # --- Sentiment adjustment ---
        if sentiment == "Negative":
            score += 20
            triggers.append("negative sentiment")
        elif sentiment == "Positive":
            score = max(0, score - 15)

        # --- Category adjustment ---
        if category == "Complaint":
            score += 15
            triggers.append("complaint category")
        elif category == "Refund Request":
            score += 10
            triggers.append("refund category")
        elif category == "Technical Support":
            score += 5
        elif category == "Feedback":
            score = max(0, score - 10)

        # --- Capitalization / exclamation emphasis ---
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamations = text.count("!")
        if caps_ratio > 0.25:
            score += 10
            triggers.append("excessive caps")
        if exclamations >= 3:
            score += 8
            triggers.append("multiple exclamation marks")

        score = min(score, 100)

        # --- Assign priority level ---
        if score >= 55:
            priority = "High"
        elif score >= 25:
            priority = "Medium"
        else:
            priority = "Low"

        return {
            "priority": priority,
            "priority_score": score,
            "triggers": list(set(triggers)),  # deduplicate
            "badge_color": self._badge_color(priority),
        }

    @staticmethod
    def _badge_color(priority: str) -> str:
        colors = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}
        return colors.get(priority, "#6b7280")
