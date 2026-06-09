# Login-First Access Fix

## Problem Statement
At application startup, users can access the tool directory without authenticating first.

Current behavior:
- GET / returns the internal tools list.
- GET /tools/<id> returns tool details.
- Anonymous users can browse internal resources before login.

Expected behavior:
- Anonymous users should be redirected to /login first.
- Only authenticated users should view internal tools and tool details.

## Root Cause
The main directory routes were implemented as open routes in routes/main.py:
- index() bound to /
- tool_detail() bound to /tools/<id>

These routes did not use Flask-Login protection, so they stayed publicly accessible.

## Solution Implemented
A minimal, standards-aligned fix was applied:

1. Add Flask-Login route protection to directory views
- Import login_required in routes/main.py.
- Add @login_required to:
  - index()
  - tool_detail()

2. Keep admin RBAC unchanged
- Admin-only routes still use @admin_required.
- This preserves separation of concerns:
  - Authentication gate for viewing internal tools.
  - Authorization gate for privileged admin actions.

## Why This Matches Project Constraints
- Uses Flask-Login as required by PRD/TDD.
- Does not introduce raw SQL or bypass ORM patterns.
- Preserves deep module boundaries (auth concerns remain in auth module; main routes only declare access requirement).
- Keeps the solution simple (KISS/YAGNI), with smallest safe change.

## Test Impact and Updates
Because / and /tools/<id> are now authenticated routes, tests were updated to reflect new behavior:

- tests/test_slice2_auth.py
  - Anonymous GET / now expects 302 redirect to /login.

- tests/test_slice4_directory.py
  - Directory and detail tests now log in before calling protected routes.

- tests/test_security_owasp.py
  - Injection search test now authenticates first, then verifies payload is safely handled.

## Security Outcome
- Anonymous browsing of internal tool metadata is blocked.
- Users must establish a valid session before discovery access.
- Existing OWASP protections remain intact:
  - A1 injection defense through ORM + parameterized SQLAlchemy queries.
  - A5 access control defense through admin_required for admin routes.

## Optional Hardening (Next Step)
If you want stricter startup behavior and clearer UX evidence:
- Set LoginManager login message/category explicitly in routes/auth.py.
- Add a dedicated test asserting anonymous GET /tools/<id> redirects to /login.
- Add a short note in README.md under Security Behavior: "All directory views require authentication."
