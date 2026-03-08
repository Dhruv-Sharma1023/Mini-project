"""
Response Suggestion Module
----------------------------
Generates professional email reply templates based on:
    - Email category (Complaint, Inquiry, etc.)
    - Sentiment (Positive, Neutral, Negative)
    - Priority level (High, Medium, Low)

Each category has multiple response variants to choose from.
"""


RESPONSE_TEMPLATES = {
    "Complaint": {
        "High": [
            (
                "Urgent Acknowledgment",
                """Dear Customer,

Thank you for bringing this critical matter to our attention. We sincerely apologize for the experience you have had, and we take issues of this nature very seriously.

We have escalated your case to our senior support team and a dedicated specialist will contact you within the next 2 hours. Your reference number is [REF-XXXXX].

We are committed to resolving this matter urgently and to your full satisfaction. Please do not hesitate to call our priority helpline at [PHONE NUMBER] if you need immediate assistance.

Warm regards,
[Agent Name]
Senior Customer Support Team"""
            ),
        ],
        "Medium": [
            (
                "Standard Complaint Response",
                """Dear Customer,

Thank you for reaching out to us. We are truly sorry to hear about your experience and understand how frustrating this must be.

We have reviewed your complaint and are actively working to resolve it. A member of our support team will follow up with you within 24 hours with an update.

Your reference number for this case is [REF-XXXXX]. Please keep this for future correspondence.

We value your business and are committed to making this right.

Best regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
        "Low": [
            (
                "General Complaint Acknowledgment",
                """Dear Customer,

Thank you for taking the time to share your feedback with us. We are sorry to learn that your experience did not meet your expectations.

We have logged your complaint (Reference: [REF-XXXXX]) and our team will investigate the matter. We will get back to you within 2–3 business days.

We appreciate your patience and the opportunity to improve our service.

Kind regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
    },

    "Inquiry": {
        "High": [
            (
                "Priority Inquiry Response",
                """Dear Customer,

Thank you for contacting us. We are happy to assist you with your inquiry.

[ANSWER TO SPECIFIC INQUIRY]

If you need further clarification or have additional questions, please do not hesitate to reply to this email or contact us at [SUPPORT EMAIL / PHONE].

We are here to help and aim to respond to all follow-up questions within 4 hours.

Best regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
        "Medium": [
            (
                "Standard Inquiry Response",
                """Dear Customer,

Thank you for your inquiry. We are happy to provide you with the information you requested.

[ANSWER TO SPECIFIC INQUIRY]

For more information, you can also visit our Help Center at [HELP CENTER URL] where you will find detailed guides and FAQs.

Please feel free to reach out if you have any additional questions.

Kind regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
        "Low": [
            (
                "General Inquiry Response",
                """Dear Customer,

Thank you for getting in touch with us. We appreciate your interest.

[ANSWER TO SPECIFIC INQUIRY]

You may also find the following resources helpful:
- Help Center: [HELP CENTER URL]
- FAQs: [FAQ URL]

Feel free to contact us anytime if you need further assistance.

Best regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
    },

    "Refund Request": {
        "High": [
            (
                "Priority Refund Acknowledgment",
                """Dear Customer,

Thank you for contacting us regarding your refund request. We understand the urgency of this matter and sincerely apologize for any inconvenience caused.

We are processing your refund request immediately. Your reference number is [REF-XXXXX].

Refund Details:
- Amount: [AMOUNT]
- Method: [ORIGINAL PAYMENT METHOD]
- Expected Timeline: 3–5 business days

You will receive a confirmation email once the refund has been processed. If you do not see the refund within 5 business days, please contact us with your reference number.

Warm regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
        "Medium": [
            (
                "Standard Refund Response",
                """Dear Customer,

Thank you for your refund request. We have received your request and are reviewing your case.

Once verified, your refund will be processed within 5–7 business days and credited back to your original payment method. Your reference number is [REF-XXXXX].

Please note that processing times may vary depending on your bank or card provider.

We will send you a confirmation once the refund is issued.

Best regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
        "Low": [
            (
                "General Refund Information",
                """Dear Customer,

Thank you for reaching out about a refund. We have received your request (Reference: [REF-XXXXX]).

Our refund policy allows returns within [X] days of purchase. Once your request is approved, the refund will be processed within 7–10 business days to your original payment method.

If you have not heard back within 3 business days, please do not hesitate to follow up.

Kind regards,
[Agent Name]
Customer Support Team"""
            ),
        ],
    },

    "Technical Support": {
        "High": [
            (
                "Critical Technical Issue Response",
                """Dear Customer,

Thank you for reporting this critical technical issue. We understand how disruptive this must be and we are treating this as a high-priority case.

Our senior technical team has been notified and will reach out to you within 1 hour. Your case number is [CASE-XXXXX].

In the meantime, please try the following steps:
1. Restart the application / device
2. Clear your browser cache (if applicable)
3. Ensure your software is updated to the latest version

If these steps do not resolve the issue, please do not attempt further troubleshooting — our technician will guide you through the process.

Regards,
[Agent Name]
Technical Support Team"""
            ),
        ],
        "Medium": [
            (
                "Standard Technical Support Response",
                """Dear Customer,

Thank you for contacting our technical support team. We are sorry to hear you are experiencing an issue.

Please try the following troubleshooting steps:
1. [STEP 1 SPECIFIC TO ISSUE]
2. [STEP 2 SPECIFIC TO ISSUE]
3. Restart your device and try again

If the issue persists after these steps, please reply to this email with:
- Your device/OS version
- A screenshot or description of any error messages

Your case number is [CASE-XXXXX] for reference.

Best regards,
[Agent Name]
Technical Support Team"""
            ),
        ],
        "Low": [
            (
                "General Technical Guidance",
                """Dear Customer,

Thank you for contacting us. We are happy to assist you with the technical query you have raised.

[ANSWER / TECHNICAL GUIDANCE]

You may also find helpful guides in our Knowledge Base at [KB URL]. Most common issues are covered there with step-by-step instructions.

If you continue to experience problems, please reply with more details and we will investigate further.

Kind regards,
[Agent Name]
Technical Support Team"""
            ),
        ],
    },

    "Feedback": {
        "High": [
            (
                "Urgent Feedback Follow-up",
                """Dear Customer,

Thank you for sharing your feedback with us — we truly appreciate it.

We have taken note of your comments and have escalated them to the relevant team for immediate review. Your input directly shapes the improvements we make to our products and services.

We will follow up with you within 48 hours regarding any actions taken based on your feedback.

Thank you for being a valued customer.

Warm regards,
[Agent Name]
Customer Experience Team"""
            ),
        ],
        "Medium": [
            (
                "Standard Feedback Response",
                """Dear Customer,

Thank you so much for taking the time to share your feedback with us. Your opinion is extremely valuable and helps us continuously improve our service.

We have forwarded your comments to the relevant department. While we may not be able to respond individually to all feedback, please know that every piece of input is reviewed and taken seriously.

We look forward to serving you better in the future.

Best regards,
[Agent Name]
Customer Experience Team"""
            ),
        ],
        "Low": [
            (
                "General Feedback Thank You",
                """Dear Customer,

Thank you for your feedback! We truly appreciate you taking the time to share your thoughts with us.

Your comments have been logged and will be shared with our product/service team. We are always working to improve, and feedback like yours helps us do that.

Thank you for being a valued customer. We hope to continue exceeding your expectations.

Kind regards,
[Agent Name]
Customer Experience Team"""
            ),
        ],
    },
}


class ResponseSuggester:
    """
    Suggests reply templates for customer emails.

    Usage:
        suggester = ResponseSuggester()
        templates = suggester.suggest(category="Complaint", priority="High")
    """

    def suggest(self, category: str, priority: str, sentiment: str = None) -> list:
        """
        Get suggested response templates.

        Args:
            category:  Email category
            priority:  Priority level
            sentiment: Sentiment (optional, used for tone guidance)

        Returns:
            List of dicts: [{'title': str, 'body': str, 'tone_note': str}]
        """
        category_templates = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES["Inquiry"])
        priority_templates = category_templates.get(priority, category_templates.get("Medium", []))

        results = []
        for title, body in priority_templates:
            tone_note = self._tone_guidance(sentiment, priority)
            results.append({
                "title": title,
                "body": body,
                "tone_note": tone_note,
            })

        # Always add a generic fallback if nothing matched
        if not results:
            results.append({
                "title": "General Response",
                "body": self._generic_response(),
                "tone_note": "Neutral and professional tone recommended.",
            })

        return results

    @staticmethod
    def _tone_guidance(sentiment: str, priority: str) -> str:
        """Return a brief tone recommendation for the support agent."""
        if sentiment == "Negative" and priority == "High":
            return "⚠️ Customer is upset. Use empathetic, apologetic tone. Avoid defensive language."
        elif sentiment == "Negative":
            return "Customer expressed frustration. Acknowledge feelings before providing solutions."
        elif sentiment == "Positive":
            return "Customer is satisfied. Maintain warm, appreciative tone."
        elif priority == "High":
            return "High-priority issue. Be concise, action-focused, and provide clear timelines."
        else:
            return "Maintain professional and helpful tone throughout."

    @staticmethod
    def _generic_response() -> str:
        return """Dear Customer,

Thank you for contacting us. We have received your message and our team is reviewing it.

We will get back to you as soon as possible. Your reference number is [REF-XXXXX].

Best regards,
Customer Support Team"""
