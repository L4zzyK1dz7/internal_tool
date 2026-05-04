"""seed.py — Database bootstrap and synthetic data generator.

This module is responsible for initialising the application database with a
clean, reproducible state.  It is executed during local development and as
part of the CI/CD build phase on Render, where it runs against the live
Neon PostgreSQL instance.

Responsibilities:
    - Drop and recreate all SQLAlchemy-managed tables.
    - Insert reference data (Teams, Languages, Categories).
    - Create two default users: one admin and one standard user.
    - Populate 50 synthetic Tool records for development and testing.

Usage::

    python seed.py

The module also exposes ``seed_database()`` so that the pytest suite can
invoke it programmatically against an isolated in-memory test database.
"""

from __future__ import annotations

from itertools import cycle

from sqlalchemy import select

from app import create_app
from models import Category, Language, Team, Tool, User, db


TEAM_NAMES = [
    "Platform Engineering",
    "Data Operations",
    "Risk & Compliance",
    "Customer Success",
    "Finance Systems",
]

LANGUAGE_NAMES = [
    "Python",
    "SQL",
    "JavaScript",
    "TypeScript",
    "R",
]

CATEGORY_NAMES = [
    "Analytics",
    "Automation",
    "Compliance",
    "Reporting",
    "Monitoring",
]

DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "Admin123!",
        "role": "admin",
        "team_name": "Platform Engineering",
    },
    {
        "username": "analyst",
        "password": "User123!",
        "role": "user",
        "team_name": "Data Operations",
    },
]


def _create_reference_data() -> tuple[list[Team], list[Language], list[Category]]:
    """Create and flush all normalised reference-data records.

    Builds ``Team``, ``Language``, and ``Category`` ORM objects from the
    module-level name lists, adds them to the current session, and flushes
    so that their primary keys are available before any foreign-key
    references are made.

    Returns:
        A three-tuple of ``(teams, languages, categories)`` — the
        newly created lists in insertion order.
    """
    teams = [Team(name=name) for name in TEAM_NAMES]
    languages = [Language(name=name) for name in LANGUAGE_NAMES]
    categories = [Category(name=name) for name in CATEGORY_NAMES]

    db.session.add_all([*teams, *languages, *categories])
    db.session.flush()
    return teams, languages, categories


def _create_users(teams: list[Team]) -> list[User]:
    """Create the default application users and hash their passwords.

    Iterates over ``DEFAULT_USERS``, resolves each user's team from the
    supplied list, sets a bcrypt-hashed password via ``User.set_password``,
    and flushes the session so that generated IDs are available for
    downstream tool creation.

    Args:
        teams: The persisted ``Team`` records returned by
            ``_create_reference_data``.

    Returns:
        The list of newly created ``User`` objects in definition order.
    """
    teams_by_name = {team.name: team for team in teams}
    users = []
    for user_data in DEFAULT_USERS:
        user = User(
            username=user_data["username"],
            password_hash="",
            role=user_data["role"],
            team=teams_by_name[user_data["team_name"]],
        )
        user.set_password(user_data["password"])
        users.append(user)

    db.session.add_all(users)
    db.session.flush()
    return users


def _create_tools(users: list[User], categories: list[Category], languages: list[Language]) -> list[Tool]:
    """Generate 50 synthetic Tool records distributed across reference data.

    Uses ``itertools.cycle`` to evenly distribute creators, categories, and
    languages across all 50 tools so that every combination appears in the
    seed dataset.  Each tool gets a deterministic name, description, and
    data link, making the output predictable for test assertions.

    Args:
        users:      Persisted ``User`` records to assign as tool creators.
        categories: Persisted ``Category`` records to assign to tools.
        languages:  Persisted ``Language`` records to assign to tools.

    Returns:
        The list of 50 newly created ``Tool`` objects (not yet committed).
    """
    user_iterator = cycle(users)
    category_iterator = cycle(categories)
    language_iterator = cycle(languages)

    tools = []
    for index in range(1, 51):
        owner = next(user_iterator)
        category = next(category_iterator)
        language = next(language_iterator)
        tools.append(
            Tool(
                name=f"Internal Tool {index:02d}",
                description=(
                    f"{category.name} workflow utility built by the {owner.team.name} team "
                    f"using {language.name}."
                ),
                data_link=f"https://internal.example.com/tools/{index:02d}",
                creator=owner,
                category=category,
                language=language,
                is_active=True,
            )
        )

    db.session.add_all(tools)
    db.session.flush()
    return tools


def seed_database(app=None) -> dict[str, int]:
    """Orchestrate a full destructive reseed of the database.

    Drops all existing tables and recreates them from the current
    SQLAlchemy model definitions, then delegates to the private helpers
    to insert reference data, users, and tools in a single transaction.

    This function is intentionally destructive — it is designed for use
    during CI/CD build phases and local development resets where a clean,
    known state is required.

    Args:
        app: An optional Flask application instance.  When ``None``, a
            new instance is created via ``create_app()``.  Pass an
            existing test-app instance from ``conftest.py`` to avoid
            creating a second app during testing.

    Returns:
        A summary dictionary with row counts for each seeded table::

            {
                "teams": 5,
                "languages": 5,
                "categories": 5,
                "users": 2,
                "tools": 50,
            }
    """
    application = app or create_app()

    with application.app_context():
        db.drop_all()
        db.create_all()

        teams, languages, categories = _create_reference_data()
        users = _create_users(teams)
        _create_tools(users, categories, languages)

        db.session.commit()

        return {
            "teams": len(db.session.scalars(select(Team.id)).all()),
            "languages": len(db.session.scalars(select(Language.id)).all()),
            "categories": len(db.session.scalars(select(Category.id)).all()),
            "users": len(db.session.scalars(select(User.id)).all()),
            "tools": len(db.session.scalars(select(Tool.id)).all()),
        }


if __name__ == "__main__":
    summary = seed_database()
    print(
        "Seed complete: "
        f"{summary['teams']} teams, "
        f"{summary['languages']} languages, "
        f"{summary['categories']} categories, "
        f"{summary['users']} users, "
        f"{summary['tools']} tools"
    )
