# FolioPress — Flask Blog Management System

A complete, production-ready editorial Blog Management System built with **Python Flask**, **Flask-SQLAlchemy**, **Flask-Migrate**, **Flask-Login**, **Flask-WTF**, **Bootstrap 5**, **Quill.js**, **Pytest**, **Gunicorn**, and **Docker**.

---

## Features

- **Modular Architecture**: Application factory pattern (`create_app`) organized with Flask Blueprints (`main`, `auth`, `posts`, `comments`, `profile`) and environment-specific configurations (`development`, `testing`, `production`).
- **User Authentication & Profiles**: Registration, login (by email or username), logout, Werkzeug password hashing, uniqueness validation, session protection via Flask-Login, and public author profile pages with editable bio, location, and website.
- **Blog Posts CRUD & Rich Text**: Create, read, edit, and delete blog posts using the **Quill.js** rich text editor with server-side HTML sanitization (`bleach`), featured image uploads (validated via Pillow), categories, comma-separated tags, draft/publish toggles, and strict author-only edit/delete authorization (`403` enforcement).
- **Comments System**: Authenticated commenting below blog posts, total comment counts, and inline edit/delete actions protected by ownership checks.
- **Search, Filtering & Pagination**: Full-text search across post titles, descriptions, and content; filtering by category and tag; combined search + category filters; clear-filter reset; empty-state feedback; and consistent **6 posts per page** pagination across home and profile views.
- **Testing & Production Deployment**: Comprehensive **Pytest** suite covering models, auth, CRUD, authorization, comments, search, filtering, and pagination, plus Gunicorn (`wsgi.py`), `Dockerfile`, and `docker-compose.yml`.

---

## Project Structure

```text
flask-blog-management-system/
├── app/
│   ├── __init__.py
│   ├── seed.py
│   ├── utils.py
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── comment_forms.py
│   │   └── post_forms.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── comment.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── comments.py
│   │   ├── main.py
│   │   ├── posts.py
│   │   └── profile.py
│   ├── static/
│   │   ├── css/style.css
│   │   ├── images/
│   │   ├── js/
│   │   │   ├── editor.js
│   │   │   └── main.js
│   │   └── uploads/
│   └── templates/
│       ├── base.html
│       ├── auth/
│       ├── components/
│       ├── errors/
│       ├── main/
│       ├── posts/
│       └── profile/
├── migrations/
├── tests/
├── config.py
├── run.py
├── wsgi.py
├── requirements.txt
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Local Setup & Installation

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd flask-blog-management-system

python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY` before deploying to production.

### 4. Initialize the database & run migrations

```bash
flask --app run.py db upgrade
```

*(If creating a fresh migration history from scratch:)*

```bash
flask --app run.py db init
flask --app run.py db migrate -m "Initial schema"
flask --app run.py db upgrade
```

### 5. Seed sample editorial content (optional)

```bash
flask --app run.py seed
```

### 6. Run the development server

```bash
python run.py
```

Open `http://127.0.0.1:5000` in your browser and click **Create Account** to register your author profile.

---

## Running Unit Tests

Run the full Pytest suite:

```bash
pytest
```

---

## Production Deployment

### With Gunicorn

```bash
export FLASK_CONFIG=production
export SECRET_KEY="your-secure-random-secret-key"
gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:app
```

### With Docker & Docker Compose

```bash
SECRET_KEY="your-secure-random-secret-key" docker compose up --build -d
```

The application will be served on `http://localhost:8000`.
