from sqlalchemy import select

from models import Category, Language, Team, Tool, User, db


ADMIN_PASSWORD = "AdminPass123!"
USER_PASSWORD = "UserPass123!"


def _get_or_create_reference_data() -> tuple[Team, Category, Language]:
    team = db.session.scalar(select(Team).where(Team.name == "Platform Engineering"))
    if team is None:
        team = Team(name="Platform Engineering")
        db.session.add(team)

    category = db.session.scalar(select(Category).where(Category.name == "Analytics"))
    if category is None:
        category = Category(name="Analytics")
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


def _create_tool(name: str, creator: User) -> Tool:
    _, category, language = _get_or_create_reference_data()
    tool = Tool(
        name=name,
        description="Initial description",
        data_link="https://internal.example.com/original",
        creator=creator,
        category=category,
        language=language,
        is_active=True,
    )
    db.session.add(tool)
    db.session.commit()
    return tool


def _login_as_admin(client, app) -> User:
    with app.app_context():
        admin = _create_user("admin-user", ADMIN_PASSWORD, role="admin")
        username = admin.username

    response = client.post(
        "/login",
        data={"username": username, "password": ADMIN_PASSWORD},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return admin


def test_admin_routes_reject_unauthenticated_requests(client, app):
    with app.app_context():
        creator = _create_user("creator-user", USER_PASSWORD)
        tool = _create_tool("Protected Tool", creator)
        tool_id = tool.id

    add_response = client.get("/admin/add")
    edit_response = client.get(f"/admin/edit/{tool_id}")
    delete_response = client.post(f"/admin/delete/{tool_id}")

    assert add_response.status_code == 403
    assert edit_response.status_code == 403
    assert delete_response.status_code == 403
    assert b"Security Alert: Broken Access Control" in add_response.data


def test_admin_can_create_and_view_tool(client, app):
    _login_as_admin(client, app)

    with app.app_context():
        creator = _create_user("tool-owner", USER_PASSWORD)
        category = db.session.scalar(select(Category).where(Category.name == "Analytics"))
        language = db.session.scalar(select(Language).where(Language.name == "Python"))
        creator_id = creator.id
        category_id = category.id
        language_id = language.id

    response = client.post(
        "/admin/add",
        data={
            "name": "Revenue Forecaster",
            "description": "Projects quarterly revenue trends.",
            "data_link": "https://internal.example.com/revenue-forecaster",
            "creator_id": str(creator_id),
            "category_id": str(category_id),
            "language_id": str(language_id),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Revenue Forecaster" in response.data
    assert b"Tool created successfully." in response.data

    with app.app_context():
        created_tool = db.session.scalar(select(Tool).where(Tool.name == "Revenue Forecaster"))
        assert created_tool is not None
        assert created_tool.is_active is True


def test_admin_can_edit_existing_tool(client, app):
    _login_as_admin(client, app)

    with app.app_context():
        creator = _create_user("editor-user", USER_PASSWORD)
        tool = _create_tool("Legacy Dashboard", creator)
        category = db.session.scalar(select(Category).where(Category.name == "Analytics"))
        language = db.session.scalar(select(Language).where(Language.name == "Python"))
        tool_id = tool.id
        creator_id = creator.id
        category_id = category.id
        language_id = language.id

    response = client.post(
        f"/admin/edit/{tool_id}",
        data={
            "name": "Modern Dashboard",
            "description": "Updated admin description.",
            "data_link": "https://internal.example.com/modern-dashboard",
            "creator_id": str(creator_id),
            "category_id": str(category_id),
            "language_id": str(language_id),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Modern Dashboard" in response.data
    assert b"Tool updated successfully." in response.data

    with app.app_context():
        updated_tool = db.session.get(Tool, tool_id)
        assert updated_tool is not None
        assert updated_tool.name == "Modern Dashboard"
        assert updated_tool.description == "Updated admin description."


def test_admin_can_soft_delete_tool(client, app):
    _login_as_admin(client, app)

    with app.app_context():
        creator = _create_user("delete-user", USER_PASSWORD)
        tool = _create_tool("Retired Tool", creator)
        tool_id = tool.id

    response = client.post(f"/admin/delete/{tool_id}", follow_redirects=True)

    assert response.status_code == 200
    assert b"Tool archived successfully." in response.data
    assert b"Retired Tool" not in response.data

    with app.app_context():
        archived_tool = db.session.get(Tool, tool_id)
        assert archived_tool is not None
        assert archived_tool.is_active is False
