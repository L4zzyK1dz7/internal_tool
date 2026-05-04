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
    return db.session.get(User, int(user_id))


ViewFunction = TypeVar("ViewFunction", bound=Callable[..., object])
logger = logging.getLogger(__name__)


def admin_required(view: ViewFunction) -> ViewFunction:
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
    if current_user.is_authenticated:
        logout_user()
        flash("Logged out successfully.", "success")
    return redirect(url_for("main.index"))
