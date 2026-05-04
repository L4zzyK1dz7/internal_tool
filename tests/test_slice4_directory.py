from sqlalchemy import select

from models import Category, Language, Team, Tool, User, db


USER_PASSWORD = "UserPass123!"


def _get_or_create_reference_data(category_name: str = "Analytics") -> tuple[Team, Category, Language]:
    team = db.session.scalar(select(Team).where(Team.name == "Platform Engineering"))
    if team is None:
        team = Team(name="Platform Engineering")
        db.session.add(team)

    category = db.session.scalar(select(Category).where(Category.name == category_name))
    if category is None:
        category = Category(name=category_name)
        db.session.add(category)

    language = db.session.scalar(select(Language).where(Language.name == "Python"))
    if language is None:
        language = Language(name="Python")
        db.session.add(language)

    db.session.flush()
    return team, category, language


def _create_user(username: str) -> User:
    team, _, _ = _get_or_create_reference_data()
    user = User(username=username, password_hash="", role="user", team=team)
    user.set_password(USER_PASSWORD)
    db.session.add(user)
    db.session.commit()
    return user


def _create_tool(name: str, creator: User, category_name: str = "Analytics", is_active: bool = True) -> Tool:
    _, category, language = _get_or_create_reference_data(category_name)
    tool = Tool(
        name=name,
        description=f"{name} description",
        data_link=f"https://internal.example.com/{name.lower().replace(' ', '-')}",
        creator=creator,
        category=category,
        language=language,
        is_active=is_active,
    )
    db.session.add(tool)
    db.session.commit()
    return tool


def test_directory_home_limits_results_to_20_and_excludes_archived(client, app):
    with app.app_context():
        creator = _create_user("directory-user")
        for index in range(1, 23):
            _create_tool(f"Directory Tool {index:02d}", creator)
        _create_tool("Archived Tool", creator, is_active=False)

    response = client.get("/")

    assert response.status_code == 200
    assert b"Directory Tool 01" in response.data
    assert b"Directory Tool 20" in response.data
    assert b"Directory Tool 21" not in response.data
    assert b"Archived Tool" not in response.data
    assert b"Load More" in response.data


def test_directory_search_filters_by_name_and_category_case_insensitively(client, app):
    with app.app_context():
        creator = _create_user("search-user")
        _create_tool("Revenue Forecaster", creator, category_name="Analytics")
        _create_tool("Alert Hub", creator, category_name="Compliance")

    name_response = client.get('/?q=foreCASTER')
    category_response = client.get('/?q=compliance')

    assert name_response.status_code == 200
    assert b"Revenue Forecaster" in name_response.data
    assert b"Alert Hub" not in name_response.data

    assert category_response.status_code == 200
    assert b"Alert Hub" in category_response.data
    assert b"Revenue Forecaster" not in category_response.data


def test_directory_load_more_shows_next_page(client, app):
    with app.app_context():
        creator = _create_user("paging-user")
        for index in range(1, 23):
            _create_tool(f"Paged Tool {index:02d}", creator)

    response = client.get("/?page=2")

    assert response.status_code == 200
    assert b"Paged Tool 01" not in response.data
    assert b"Paged Tool 20" not in response.data
    assert b"Paged Tool 21" in response.data
    assert b"Paged Tool 22" in response.data
    assert b"Load More" not in response.data


def test_tool_detail_page_shows_metadata_and_data_link(client, app):
    with app.app_context():
        creator = _create_user("detail-user")
        tool = _create_tool("Insight Console", creator, category_name="Monitoring")
        tool_id = tool.id

    response = client.get(f"/tools/{tool_id}")

    assert response.status_code == 200
    assert b"Insight Console" in response.data
    assert b"Monitoring" in response.data
    assert b"Platform Engineering" in response.data
    assert b"https://internal.example.com/insight-console" in response.data
