# EmailIQ — Customer Service Email Intelligence System

A full-stack Flask application with complete authentication, SQLite persistence,
NLP-powered email analysis, role-based access control, and a polished dark-themed UI.

---

## Quick Start

```bash
# 1. Create & activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python run.py
# → http://localhost:5000
```

The database (`instance/emailiq_dev.db`) and default admin account are created
**automatically** on first run.

---

## Default Admin Account

| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | Admin |

All other users must **self-register** at `/register` and receive the **Agent** role.

---

## Project Structure

```
emailiq_final/
├── run.py                          ← Entry point
├── config.py                       ← Dev / Prod / Test configs
├── requirements.txt
│
├── instance/                       ← Auto-created; holds DB files (gitignore)
│   └── emailiq_dev.db              ← SQLite database
│
├── app/
│   ├── __init__.py                 ← App factory: init DB, register blueprints
│   ├── routes.py                   ← Main routes (all @login_required)
│   ├── auth.py                     ← Auth blueprint (login/register/logout/profile/admin)
│   │
│   ├── database/
│   │   ├── connection.py           ← SQLite connection + db_session() context manager
│   │   ├── schema.py               ← 7-table DDL, indexes, default admin seed
│   │   └── repository.py          ← UserRepository + EmailRepository (all CRUD)
│   │
│   ├── modules/
│   │   ├── preprocessor.py         ← Tokenize, clean, stop-word removal
│   │   ├── classifier.py           ← TF-IDF + Logistic Regression
│   │   ├── sentiment.py            ← Lexicon-based sentiment analysis
│   │   ├── priority.py             ← Keyword + rule-based priority scoring
│   │   └── responder.py            ← 15 professional response templates
│   │
│   ├── templates/
│   │   ├── base.html               ← Shared layout, navbar, user menu
│   │   ├── index.html              ← Home dashboard
│   │   ├── analyze.html            ← Email analysis form + results
│   │   ├── dashboard.html          ← Filterable table: search, sort, paginate, delete
│   │   ├── email_detail.html       ← Full detail view per email
│   │   ├── audit_log.html          ← Activity log (scoped by role)
│   │   ├── 404.html
│   │   └── auth/
│   │       ├── login.html          ← Clean login form (no credentials shown)
│   │       ├── register.html       ← Self-registration with validation + PW strength
│   │       ├── profile.html        ← Change password + display name
│   │       └── admin_users.html    ← Admin: create / delete / reset-password users
│   │
│   └── static/
│       ├── css/style.css           ← Complete dark theme stylesheet
│       └── js/main.js              ← Dropdown, confidence bars, flash auto-dismiss
│
├── data/sample_emails.py           ← 25 labelled sample emails
├── models/model_trainer.py         ← Optional: train ML .pkl models
└── tests/test_modules.py           ← Unit tests for all NLP modules
```

---

## Authentication

### Self-Registration (`/register`)
- Anyone can register at `/register`
- Required: full name, username (3–30 alphanumeric chars), password (min 6 chars)
- Passwords must match; live strength meter shown
- All self-registered accounts receive **Agent** role automatically
- No demo credentials are shown anywhere

### Login (`/login`)
- Session-based with `session.permanent = True`
- Redirects to original destination after login (`?next=` param preserved)
- No credentials or hints shown on the page

### Roles & Permissions

| Feature                   | Agent | Admin |
|---------------------------|-------|-------|
| Analyze emails            | ✅    | ✅    |
| View dashboard            | ✅    | ✅    |
| View own audit log        | ✅    | ✅    |
| View ALL users' audit log | ❌    | ✅    |
| User management page      | ❌    | ✅    |
| Create / delete users     | ❌    | ✅    |
| Reset any password        | ❌    | ✅    |

### Audit Log Scoping
- **Admin** → sees `Full Audit Log` — every entry from every user, with a User column
- **Agent** → sees `My Activity Log` — only their own entries, with a scope notice
- Applies to both the `/audit-log` page and the `/api/audit-log` API endpoint

---

## Database Schema

```
users           id · username · password_hash (SHA-256) · role · full_name · created_at · last_login
emails          id · sender · subject · body · cleaned_text · token_count · created_by(FK) · timestamps
classifications email_id(FK+cascade) · category · confidence · method · all_scores(JSON)
sentiments      email_id(FK+cascade) · sentiment · score · confidence · label_emoji · method
priorities      email_id(FK+cascade) · priority · priority_score · triggers(JSON) · badge_color
suggestions     email_id(FK+cascade) · title · body · tone_note · sort_order
audit_log       action · email_id · user_id(FK) · details · created_at
```

All related tables cascade-delete when an email is removed.

---

## API Reference (all require active session)

| Method   | Endpoint                   | Description                              |
|----------|----------------------------|------------------------------------------|
| POST     | `/api/analyze`             | Analyze & save one email (JSON body)     |
| GET      | `/api/emails`              | List emails (filter by cat/pri/sent)     |
| GET      | `/api/emails/<id>`         | Get one email by ID                      |
| DELETE   | `/api/emails/<id>`         | Delete one email                         |
| POST     | `/api/clear`               | Delete all emails                        |
| POST     | `/api/load-samples`        | Load 25 demo emails                      |
| GET      | `/api/stats`               | Dashboard statistics                     |
| GET      | `/api/search?q=...`        | Full-text search across subject/body     |
| GET      | `/api/audit-log`           | Activity log (scoped by role)            |
| GET      | `/api/users`               | User list (admin: all · agent: self)     |
| GET      | `/api/users/<id>`          | Single user detail (no password hash)    |
