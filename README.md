# Customer Service Email Intelligence System

An NLP-powered Flask application that automatically classifies customer emails, detects sentiment, assigns priority, and suggests responses.

## Project Structure

```
email_intelligence/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes.py                # All route handlers
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── preprocessor.py      # Text cleaning & tokenization
│   │   ├── classifier.py        # Email category classification
│   │   ├── sentiment.py         # Sentiment analysis
│   │   ├── priority.py          # Priority detection
│   │   └── responder.py         # Response suggestion generator
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   └── analyze.html
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── data/
│   └── sample_emails.py         # Sample dataset
├── models/
│   └── model_trainer.py         # ML model training script
├── tests/
│   └── test_modules.py          # Unit tests
├── config.py                    # App configuration
├── run.py                       # App entry point
└── requirements.txt
```

## Setup & Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the models
python models/model_trainer.py

# 4. Run the application
python run.py
```

Then open: http://localhost:5000

## Features

- **Email Classification**: Complaint, Inquiry, Refund Request, Technical Support, Feedback
- **Sentiment Analysis**: Positive, Neutral, Negative
- **Priority Detection**: High, Medium, Low
- **Response Suggestions**: Auto-generated reply templates
- **Dashboard**: View all analyzed emails with filters
