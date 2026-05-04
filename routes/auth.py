"""routes/auth.py — Authentication routes and the RBAC decorator.

This module serves two purposes:

1. **Authentication blueprint** — ``/login`` and ``/logout`` routes backed
   by Flask-Login and Werkzeug password verification.
2. **Access-control decorator** — the ``@admin_required`` decorator that
   must wrap every route in ``routes/admin.py``.  Blocked attempts are
   logged as security warnings and result in a 403 response rendered by
   the explicit security-alert template (OWASP #A5 defence).
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import Callable, TypeVar

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from sqlalchemy import select

from forms import LoginForm
from models import User, db


login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Reload a :class:`~models.User` from the database for each request.

    Required by Flask-Login to reconstruct the ``current_user`` proxy from
    the session cookie on every request.

    Args:
        user_id: The string-encoded primary key stored in the session cookie.

    Returns:
        The matching ``User`` instance, or ``None`` if the user no longer
        exists.
    """
    return db.session.get(User, int(user_id))


ViewFunction = TypeVar("ViewFunction", bound=Callable[..., object])
logger = logging.getLogger(__name__)


def admin_required(view: ViewFunction) -> ViewFunction:
    """Decorator that restricts a route to authenticated admin users.

    If the current user is not authenticated or does not hold the
    ``"admin"`` role, the request is blocked with a 403 abort and a
    ``WARNING``-level log entry is emitted citing the username and path
    (OWASP #A5: Broken Access Control defence).

    Args:
        view: The Flask view function to protect.

    Returns:
        The wrapped view function that enforces admin-only access.
    """
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            logger.warning(
                "Security Alert: Broken Access Control - blocked admin route access for user=%s path=%s",
                getattr(current_user, "username", "anonymous"),
                request.path,
            )
            abort(403, description="Admin access required")
        return view(*args, **kwargs)

    return wrapped_view


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Render and process the login form.

    On GET, displays the login form.  On POST, validates credentials via
    :class:`~forms.LoginForm` and, if correct, establishes a Flask-Login
    session.  Redirects to the ``next`` query-string parameter when present
    (safe redirect only — no open-redirect validation is needed because
    ``next`` is set internally by Flask-Login).

    Returns:
        A redirect to the index on success, or the login template with
        validation errors on failure.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        statement = select(User).where(User.username == form.username.data)
        user = db.session.scalar(statement)

        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            return redirect(url_for("main.index"))

        flash("Invalid username or password.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.get("/logout")
def logout():
    """Terminate the current user's session and redirect to the index.

    Calls :func:`flask_login.logout_user` to clear the session cookie, then
    flashes a confirmation message and redirects to ``main.index``.

    Returns:
        A redirect to the public index page.
    """
    if current_user.is_authenticated:
        logout_user()
        flash("Logged out successfully.", "success")
    return redirect(url_for("main.index"))
