from sqlalchemy import select

from models import Category, Language, Team, Tool, User, db


ADMIN_PASSWORD = "AdminPass123!"
USER_PASSWORD = "UserPass123!"
SQL_INJECTION_PAYLOAD = "' OR 1=1 --"


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


def _create_user(username: str, password: str, role: str = "user") -> User:
    team, _, _ = _get_or_create_reference_data()
    user = User(username=username, password_hash="", role=role, team=team)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def _create_tool(name: str, creator: User, category_name: str = "Analytics") -> Tool:
    _, category, language = _get_or_create_reference_data(category_name)
    tool = Tool(
        name=name,
        description=f"{name} description",
        data_link=f"https://internal.example.com/{name.lower().replace(' ', '-')}",
        creator=creator,
        category=category,
        language=language,
        is_active=True,
    )
    db.session.add(tool)
    db.session.commit()
    return tool


def _login(client, username: str, password: str):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_admin_routes_reject_unauthenticated_get_and_post_requests(client, app):
    with app.app_context():
        creator = _create_user("security-user", USER_PASSWORD)
        tool = _create_tool("Protected Directory Tool", creator)
        tool_id = tool.id

    responses = [
        client.get("/admin"),
        client.get("/admin/add"),
        client.post("/admin/add", data={}),
        client.get(f"/admin/edit/{tool_id}"),
        client.post(f"/admin/edit/{tool_id}", data={}),
        client.post(f"/admin/delete/{tool_id}"),
    ]

    assert all(response.status_code == 403 for response in responses)
    assert all(b"Security Alert: Broken Access Control" in response.data for response in responses)


def test_admin_routes_reject_standard_user_get_and_post_requests(client, app):
    with app.app_context():
        creator = _create_user("standard-user", USER_PASSWORD)
        tool = _create_tool("Protected Tool", creator)
        tool_id = tool.id

    login_response = _login(client, "standard-user", USER_PASSWORD)
    assert login_response.status_code == 200

    responses = [
        client.get("/admin"),
        client.get("/admin/add"),
        client.post("/admin/add", data={}),
        client.get(f"/admin/edit/{tool_id}"),
        client.post(f"/admin/edit/{tool_id}", data={}),
        client.post(f"/admin/delete/{tool_id}"),
    ]

    assert all(response.status_code == 403 for response in responses)
    assert all(b"Security Alert: Broken Access Control" in response.data for response in responses)


def test_search_rejects_sql_injection_payload_without_exposing_records(client, app):
    with app.app_context():
        creator = _create_user("search-owner", USER_PASSWORD)
        _create_tool("Revenue Forecaster", creator, category_name="Analytics")
        _create_tool("Compliance Lens", creator, category_name="Compliance")

    response = client.get(f"/?q={SQL_INJECTION_PAYLOAD}")

    assert response.status_code == 200
    assert b"No matching tools found." in response.data
    assert b"Revenue Forecaster" not in response.data
    assert b"Compliance Lens" not in response.data
