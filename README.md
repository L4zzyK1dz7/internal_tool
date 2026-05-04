# Internal Tool Directory

A secure Flask web application for discovering and managing internal tools.
It replaces spreadsheet-based tracking with structured metadata, RBAC-protected administration, and tested backend workflows.

## Overview

This project is built around a strict engineering workflow:

- **Tech stack:** Python, Flask, SQLAlchemy 2.0, WTForms, Flask-Login
- **Security first:** no raw SQL, password hashing, and admin-only CRUD routes
- **TDD slices:** incremental delivery with `pytest` coverage per vertical slice
- **Environment portability:** SQLite for local development, PostgreSQL-ready via `DATABASE_URL`

## Current Scope (Implemented)

### Slice 1 — Foundation
- Flask app factory with instance-based SQLite default
- SQLAlchemy models for `User`, `Tool`, `Team`, `Category`, and `Language`
- Seed script creating reference data, 2 users, and 50 synthetic tools

### Slice 2 — Authentication & Access Control
- Local authentication via `Flask-Login`
- Password hashing via `werkzeug.security`
- Custom `@admin_required` decorator for RBAC enforcement
- Explicit `403` security view for blocked admin access

### Slice 3 — Admin CRUD (Soft Delete)
- Protected admin dashboard at `/admin`
- Add/edit tool forms with WTForms validation
- Soft delete implemented with `Tool.is_active = False`

## Security & Architecture Constraints

The repository enforces the following non-negotiable rules:

- **No raw SQL:** all database interactions must use SQLAlchemy ORM
- **SQLAlchemy 2.0 style only:** e.g. `db.session.execute(select(...))`
- **RBAC required:** admin routes must be wrapped with `@admin_required`
- **Validation required:** backend forms must use WTForms validators

## Tech Stack

- Python 3.11+
- Flask 3+
- Flask-SQLAlchemy 3.1+
- SQLAlchemy 2+
- Flask-WTF / WTForms
- Flask-Login
- Pytest

See `requirements.txt` for full dependency pins.

## Project Structure

```text
.
├── app.py                  # Flask app factory and config
├── models.py               # SQLAlchemy models
├── forms.py                # WTForms definitions
├── seed.py                 # Database bootstrap and synthetic data
├── routes/
│   ├── main.py             # Public routes
│   ├── auth.py             # Login/logout + admin_required decorator
│   └── admin.py            # Protected CRUD routes
├── templates/              # Jinja templates (base, auth, admin, errors)
├── tests/                  # Pytest slices for foundation/auth/admin CRUD
├── docs/
│   └── tdd.md              # Technical design document
└── Makefile                # Common local commands
```

## Getting Started

### 1) Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Seed the database
```bash
python seed.py
```

### 4) Run the app
```bash
flask --app app run --debug
```

The app will start on `http://127.0.0.1:5000`.

## Default Seeded Accounts

After running `python seed.py`:

- **Admin:** `admin` / `Admin123!`
- **Standard user:** `analyst` / `User123!`

Use the admin account to access `/admin` and perform CRUD operations.

## Environment Configuration

- `SECRET_KEY` (optional in local dev; should be set in production)
- `DATABASE_URL` (optional in local dev)

Behavior:

- If `DATABASE_URL` is set, the app uses it.
- If it starts with `postgres://`, it is normalized to `postgresql://`.
- If not set, local SQLite is used at `instance/app.db`.

## Testing

Run the full suite:

```bash
pytest -q
```

Or via Makefile:

```bash
make test
```

The tests currently verify:

- App/database configuration
- Model/table setup and seeding
- Password hashing and login/logout flow
- RBAC blocking for non-admin users
- Admin add/edit/soft-delete CRUD behavior

## Useful Commands

```bash
make install   # install dependencies
make seed      # seed database
make run       # run flask dev server
make test      # run tests
make build     # compile sanity check
make lint      # python compile checks
make clean     # remove __pycache__ folders
```

## Route Summary

- `GET /` — Home page
- `GET|POST /login` — User login
- `GET /logout` — User logout
- `GET /admin` — Admin dashboard (protected)
- `GET|POST /admin/add` — Create tool (protected)
- `GET|POST /admin/edit/<tool_id>` — Update tool (protected)
- `POST /admin/delete/<tool_id>` — Soft delete tool (protected)
- `GET /health` — Health check endpoint

## Engineering Workflow

This project follows an "agentic engineering" workflow emphasizing:

- TDD (red → green → refactor)
- Vertical slices over horizontal build phases
- Deep module boundaries with clear interfaces
- Security and quality gates before completion

Reference docs:

- `PROJECT_CONTEXT.md` — Product Requirements Document
- `docs/tdd.md` — Technical Design Document
- `.github/copilot-instructions.md` — Engineering and security directives

## Planned Next Slices

- **Slice 4:** user-facing tool discovery/search with backend limits
- **Slice 5:** CI/CD pipeline and deployment automation

