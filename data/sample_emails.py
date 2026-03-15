"""
Sample Emails Dataset
-----------------------
25 diverse sample customer service emails for demo and training.
"""

SAMPLE_EMAILS = [
    # ── COMPLAINTS ──────────────────────────────────────────────
    {
        "sender": "john.smith@gmail.com",
        "subject": "Absolutely disgusted with your service",
        "body": (
            "I am absolutely furious. I ordered a laptop three weeks ago and it has still "
            "not arrived. I have contacted your support team FOUR times and nobody can give "
            "me a straight answer. This is completely unacceptable. I demand a full refund "
            "immediately or I will be forced to take legal action. This is the WORST customer "
            "service I have ever experienced. I will never buy from you again!"
        ),
        "label": "Complaint",
    },
    {
        "sender": "sara.jones@yahoo.com",
        "subject": "Damaged product received",
        "body": (
            "I received my order today but the product arrived damaged. The box was completely "
            "crushed and the item inside was broken. I paid full price for this and I expect "
            "either a replacement or a refund. This is not acceptable and very disappointing."
        ),
        "label": "Complaint",
    },
    {
        "sender": "mike.brown@hotmail.com",
        "subject": "Wrong item sent",
        "body": (
            "I ordered a blue hoodie in size Large but received a red t-shirt in size Small. "
            "This is clearly a packing error. I need the correct item sent as soon as possible. "
            "I am quite frustrated with this situation as it is an anniversary gift."
        ),
        "label": "Complaint",
    },
    {
        "sender": "angry.customer@email.com",
        "subject": "FRAUD ALERT - Unauthorized charges on my account",
        "body": (
            "I just checked my bank account and found THREE unauthorized charges from your company. "
            "I never authorized these transactions. This looks like fraud or a security breach. "
            "I am contacting my bank and consumer affairs immediately. I need an urgent response "
            "from a senior manager ASAP!"
        ),
        "label": "Complaint",
    },
    {
        "sender": "unhappy@customer.com",
        "subject": "Rude staff complaint",
        "body": (
            "I wanted to report the behavior of one of your staff members. The representative "
            "I spoke to yesterday was dismissive, rude, and unhelpful. When I asked to speak "
            "to a manager, I was put on hold for 45 minutes and then disconnected. I deserve "
            "to be treated with respect as a paying customer."
        ),
        "label": "Complaint",
    },

    # ── INQUIRIES ────────────────────────────────────────────────
    {
        "sender": "curious.buyer@gmail.com",
        "subject": "Question about your subscription plans",
        "body": (
            "Hello, I am interested in signing up for one of your subscription plans. "
            "Could you please provide more details about the pricing, features included, "
            "and whether there is a free trial period? I would also like to know if the "
            "subscription can be cancelled at any time."
        ),
        "label": "Inquiry",
    },
    {
        "sender": "new.customer@email.com",
        "subject": "Delivery time inquiry",
        "body": (
            "Hi there, I was wondering what your standard delivery times are for orders "
            "to the UK. Also, do you offer express shipping? I need the item by next Friday "
            "if possible. Thank you for your help."
        ),
        "label": "Inquiry",
    },
    {
        "sender": "business.owner@company.com",
        "subject": "Bulk order discount information",
        "body": (
            "Good afternoon, I run a small business and I am considering placing a bulk order "
            "of approximately 200 units. I would like to know if you offer any discounts for "
            "large quantity orders and what the lead time would be. Please also send me your "
            "product catalog if available."
        ),
        "label": "Inquiry",
    },
    {
        "sender": "parent@family.com",
        "subject": "Product age suitability question",
        "body": (
            "Hello, I wanted to ask if the educational tablet you sell is suitable for a "
            "5-year-old child. What age range is it designed for? Are there parental controls? "
            "I am looking for a safe and educational device for my daughter. Thank you."
        ),
        "label": "Inquiry",
    },

    # ── REFUND REQUESTS ──────────────────────────────────────────
    {
        "sender": "refund.please@gmail.com",
        "subject": "Refund request - Order #45231",
        "body": (
            "Dear support team, I would like to request a refund for my recent order #45231. "
            "The product did not match the description on your website and is not suitable for "
            "my needs. I have not opened the package and it is still in its original condition. "
            "Please advise on how to proceed with the return and refund."
        ),
        "label": "Refund Request",
    },
    {
        "sender": "double.charged@outlook.com",
        "subject": "Overcharged twice - need refund urgently",
        "body": (
            "I have been charged twice for the same order. My bank statement shows two identical "
            "charges of $89.99 on the same date. Please refund the duplicate charge immediately. "
            "This is very frustrating and I need this resolved urgently as I am on a tight budget."
        ),
        "label": "Refund Request",
    },
    {
        "sender": "cancel.subscription@user.com",
        "subject": "Cancel subscription and refund",
        "body": (
            "I would like to cancel my annual subscription and request a partial refund for the "
            "remaining months. I signed up 2 months ago on a 12-month plan. I am not using the "
            "service as much as expected and I would appreciate a prorated refund. Thank you."
        ),
        "label": "Refund Request",
    },

    # ── TECHNICAL SUPPORT ────────────────────────────────────────
    {
        "sender": "tech.problem@user.com",
        "subject": "App keeps crashing on iPhone",
        "body": (
            "Hi, your mobile app keeps crashing every time I try to open it on my iPhone 14. "
            "I have tried restarting the phone, reinstalling the app, and clearing the cache "
            "but nothing works. The error message says 'Unable to connect to server'. I am "
            "running iOS 17.2. Please help urgently as I need the app for work."
        ),
        "label": "Technical Support",
    },
    {
        "sender": "login.issue@email.com",
        "subject": "Cannot log into my account",
        "body": (
            "I am unable to log into my account. I have reset my password three times but still "
            "get the error message 'Invalid credentials'. I have checked and I am using the "
            "correct email address. My account is very important and contains data I need. "
            "Please resolve this as soon as possible."
        ),
        "label": "Technical Support",
    },
    {
        "sender": "wifi.problem@home.com",
        "subject": "Smart device not connecting to WiFi",
        "body": (
            "I recently purchased your smart thermostat and I cannot get it to connect to my "
            "WiFi network. I have followed the setup guide but the device shows a red blinking "
            "light and does not appear in the app. I have a dual-band router. Is there a "
            "compatibility issue? I need help setting this up."
        ),
        "label": "Technical Support",
    },
    {
        "sender": "software.error@company.com",
        "subject": "Critical software bug affecting production",
        "body": (
            "URGENT: We are experiencing a critical bug in version 3.2.1 of your software that "
            "is affecting our entire production environment. The issue causes data exports to fail "
            "silently with no error message. This is causing significant business disruption. "
            "We need an immediate hotfix or patch. Please escalate to your engineering team now."
        ),
        "label": "Technical Support",
    },
    {
        "sender": "slow.performance@user.com",
        "subject": "Website extremely slow to load",
        "body": (
            "Your website has been extremely slow for the past week. Pages take over 30 seconds "
            "to load and sometimes time out completely. I have tested on multiple devices and "
            "internet connections so the issue is on your end. Please investigate."
        ),
        "label": "Technical Support",
    },

    # ── FEEDBACK ─────────────────────────────────────────────────
    {
        "sender": "happy.customer@gmail.com",
        "subject": "Excellent customer service experience",
        "body": (
            "I just wanted to say how impressed I am with your customer service team. "
            "Sarah from your support team went above and beyond to help me resolve an issue "
            "with my order. She was professional, friendly, and resolved everything within "
            "minutes. This is what great customer service looks like! Keep up the amazing work."
        ),
        "label": "Feedback",
    },
    {
        "sender": "product.lover@email.com",
        "subject": "Love your new product range",
        "body": (
            "I recently purchased several items from your new eco-friendly product range and "
            "I absolutely love them. The quality is outstanding and the packaging is beautifully "
            "minimal. I have already recommended your brand to all of my friends. You should "
            "consider expanding this range further!"
        ),
        "label": "Feedback",
    },
    {
        "sender": "suggestion.box@user.com",
        "subject": "Suggestion: dark mode for your app",
        "body": (
            "Hello, I have been using your app for about six months now and I really enjoy it. "
            "One feature I would love to see is a dark mode option. Many apps offer this now and "
            "it would be much better for use at night. Just a suggestion — overall the app is "
            "great! Thank you."
        ),
        "label": "Feedback",
    },
    {
        "sender": "loyal.customer@email.com",
        "subject": "Feedback on recent purchase",
        "body": (
            "I have been a customer for over three years now and I have always been satisfied. "
            "My most recent purchase arrived quickly and was exactly as described. However, I "
            "noticed the packaging has become less eco-friendly compared to before. I appreciate "
            "your products but would love to see a return to sustainable packaging."
        ),
        "label": "Feedback",
    },
    {
        "sender": "positive.feedback@yahoo.com",
        "subject": "Thank you for a great experience",
        "body": (
            "Thank you so much for the wonderful experience from start to finish. The ordering "
            "process was simple, delivery was fast, and the product exceeded my expectations. "
            "I will definitely be ordering again and highly recommend your store to others."
        ),
        "label": "Feedback",
    },
    {
        "sender": "mixed.review@gmail.com",
        "subject": "Mixed feedback on recent service",
        "body": (
            "I have mixed feelings about my recent experience. The product itself is great and "
            "arrived quickly, but the checkout process was confusing and I nearly abandoned my "
            "cart. I think simplifying the payment steps would help a lot. Overall satisfied but "
            "there is room for improvement."
        ),
        "label": "Feedback",
    },
    {
        "sender": "billing.query@email.com",
        "subject": "Billing statement unclear",
        "body": (
            "I received my monthly invoice and I am struggling to understand some of the line "
            "items. Could someone explain what the 'platform fee' and 'usage surcharge' charges "
            "are? They were not mentioned when I signed up. I want to make sure I am being "
            "charged correctly before making payment."
        ),
        "label": "Inquiry",
    },
]

# Labels for training ML models
TRAINING_LABELS = [email["label"] for email in SAMPLE_EMAILS]
TRAINING_TEXTS = [f"{email['subject']} {email['body']}" for email in SAMPLE_EMAILS]
