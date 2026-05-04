from sqlalchemy import inspect, select
from sqlalchemy.orm import joinedload

from app import create_app
from models import Category, Language, Team, Tool, User, db
from seed import seed_database


EXPECTED_TABLES = {"users", "teams", "languages", "categories", "tools"}


def test_create_app_defaults_to_local_sqlite_when_database_url_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    app = create_app({"TESTING": True})

    database_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    assert database_uri.startswith("sqlite:///")
    assert database_uri.endswith("app.db")



def test_create_app_uses_database_url_when_present(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:password@localhost:5432/tool_directory")

    app = create_app({"TESTING": True})

    assert (
        app.config["SQLALCHEMY_DATABASE_URI"]
        == "postgresql://user:password@localhost:5432/tool_directory"
    )



def test_models_create_expected_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)

    assert EXPECTED_TABLES.issubset(set(inspector.get_table_names()))



def test_seed_database_creates_reference_data_users_and_tools(app):
    seed_database(app)

    with app.app_context():
        team_count = len(db.session.scalars(select(Team.id)).all())
        language_count = len(db.session.scalars(select(Language.id)).all())
        category_count = len(db.session.scalars(select(Category.id)).all())
        user_count = len(db.session.scalars(select(User.id)).all())
        tool_count = len(db.session.scalars(select(Tool.id)).all())
        admin_user = db.session.scalar(select(User).where(User.role == "admin"))
        sample_tool = db.session.scalar(
            select(Tool)
            .options(
                joinedload(Tool.creator),
                joinedload(Tool.category),
                joinedload(Tool.language),
            )
            .order_by(Tool.id)
        )

        assert sample_tool is not None
        assert sample_tool.creator is not None
        assert sample_tool.category is not None
        assert sample_tool.language is not None

    assert team_count == 5
    assert language_count == 5
    assert category_count == 5
    assert user_count == 2
    assert tool_count == 50
    assert admin_user is not None
    assert admin_user.password_hash != "Admin123!"
