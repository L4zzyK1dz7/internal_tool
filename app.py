"""app.py — Flask application factory.

This module is the entry point for the Internal Tool Directory application.
It uses the application-factory pattern so that the app can be instantiated
with different configurations (e.g. testing vs production) without importing
a module-level singleton.

Environment variables:
    SECRET_KEY:    Flask session secret.  Defaults to ``"dev"`` locally.
    DATABASE_URL:  Full database connection URI.  When absent the app falls
                   back to a local SQLite file at ``instance/app.db``.
"""

import os
from pathlib import Path

from flask import Flask, render_template

from models import db
from routes.admin import admin_bp
from routes.auth import auth_bp, login_manager
from routes.main import main_bp


def _normalise_database_url(database_url: str | None) -> str | None:
    """Normalise a Heroku/Render-style ``postgres://`` URI to ``postgresql://``.

    SQLAlchemy 2.0 dropped support for the legacy ``postgres://`` scheme.
    Render and some other cloud providers still emit the old scheme, so this
    helper performs the substitution transparently before the URI reaches
    SQLAlchemy.

    Args:
        database_url: The raw ``DATABASE_URL`` string from the environment,
            or ``None`` if the variable is not set.

    Returns:
        The corrected URI string, or ``None`` if the input was ``None``.
    """
    if not database_url:
        return None
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def create_app(test_config: dict | None = None) -> Flask:
    """Construct and configure the Flask application instance.

    Registers all SQLAlchemy models, Flask-Login, and the three route
    blueprints (main, auth, admin).  Also registers a ``/health`` endpoint
    and a custom 403 error handler that renders the explicit security-alert
    template required for OWASP video evidence.

    Args:
        test_config: An optional dictionary of configuration overrides.
            When provided (e.g. from ``conftest.py``), these values are
            merged on top of the default configuration, allowing tests to
            inject an in-memory SQLite URI or disable CSRF.

    Returns:
        A fully configured :class:`flask.Flask` instance ready to serve
        requests.
    """
    flask_app = Flask(__name__, instance_relative_config=True)

    instance_path = Path(flask_app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)
    default_database_path = instance_path / "app.db"

    flask_app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=_normalise_database_url(os.getenv("DATABASE_URL"))
        or f"sqlite:///{default_database_path.as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        flask_app.config.update(test_config)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)

    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(admin_bp)

    @flask_app.get("/health")
    def healthcheck() -> tuple[dict[str, str], int]:
        """Return a simple JSON liveness probe used by the hosting platform.

        Returns:
            A ``200 OK`` response with ``{"status": "ok"}`` confirming the
            app process is running.
        """
        return {"status": "ok"}, 200

    @flask_app.errorhandler(403)
    def forbidden(error):
        """Render the explicit security-alert view for 403 Forbidden errors.

        Uses the ``errors/403.html`` template which displays a prominent
        "Security Alert: Broken Access Control" message.  This satisfies the
        OWASP video-evidence requirement for clearly visible access-control
        blocks.

        Args:
            error: The :class:`werkzeug.exceptions.Forbidden` exception
                instance raised by ``abort(403)``.

        Returns:
            A rendered 403 response with the security-alert template.
        """
        return render_template(
            "errors/403.html",
            message=getattr(error, "description", "Admin access required"),
        ), 403

    return flask_app


app = create_app()
