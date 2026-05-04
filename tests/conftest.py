from pathlib import Path

import pytest

from app import create_app
from models import db


@pytest.fixture()
def app(tmp_path: Path):
    database_path = tmp_path / "test.db"
    flask_app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
        }
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(request):
    return request.getfixturevalue("app").test_client()
