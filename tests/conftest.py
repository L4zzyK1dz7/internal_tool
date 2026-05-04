"""tests/conftest.py — Shared pytest fixtures for the test suite.

Provides two session-scoped fixtures used across all test slices:

- ``app``    — An isolated Flask application instance backed by a
               temporary SQLite database.  CSRF is disabled and the
               database is created/torn down around each test.
- ``client`` — A Flask test client bound to the ``app`` fixture,
               enabling HTTP-level integration tests without a real server.
"""

from pathlib import Path

import pytest

from app import create_app
from models import db


@pytest.fixture()
def app(tmp_path: Path):
    """Create an isolated Flask app instance for a single test.

    Configures the app with:
    - ``TESTING = True`` to propagate exceptions to the test runner.
    - ``WTF_CSRF_ENABLED = False`` to allow form POSTs without tokens.
    - A fresh SQLite database in pytest's ``tmp_path`` directory so that
      each test starts with a clean schema.

    Yields:
        A :class:`flask.Flask` instance within an active app context.
        All tables are dropped on teardown.
    """
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
    """Return a Flask test client bound to the ``app`` fixture.

    Resolves the ``app`` fixture via ``request.getfixturevalue`` so that
    both fixtures share the same application instance within a test.

    Returns:
        A :class:`flask.testing.FlaskClient` for issuing test HTTP requests.
    """
    return request.getfixturevalue("app").test_client()
