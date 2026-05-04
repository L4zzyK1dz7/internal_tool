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
    teams = [Team(name=name) for name in TEAM_NAMES]
    languages = [Language(name=name) for name in LANGUAGE_NAMES]
    categories = [Category(name=name) for name in CATEGORY_NAMES]

    db.session.add_all([*teams, *languages, *categories])
    db.session.flush()
    return teams, languages, categories


def _create_users(teams: list[Team]) -> list[User]:
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
