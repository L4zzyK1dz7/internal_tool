import os
from pathlib import Path

from flask import Flask, render_template

from models import db
from routes.admin import admin_bp
from routes.auth import auth_bp, login_manager
from routes.main import main_bp


def _normalise_database_url(database_url: str | None) -> str | None:
    if not database_url:
        return None
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def create_app(test_config: dict | None = None) -> Flask:
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
        return {"status": "ok"}, 200

    @flask_app.errorhandler(403)
    def forbidden(error):
        return render_template(
            "errors/403.html",
            message=getattr(error, "description", "Admin access required"),
        ), 403

    return flask_app


app = create_app()
