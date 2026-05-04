from sqlalchemy import select

from models import Team, User, db


ADMIN_PASSWORD = "AdminPass123!"
USER_PASSWORD = "UserPass123!"


def _create_user(username: str, password: str, role: str = "user") -> User:
    team = db.session.scalar(select(Team).where(Team.name == "Platform Engineering"))
    if team is None:
        team = Team(name="Platform Engineering")
        db.session.add(team)
        db.session.flush()

    user = User(username=username, password_hash="", role=role, team=team)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def test_user_password_is_hashed_and_verifiable(app):
    with app.app_context():
        user = _create_user("hash-user", USER_PASSWORD)

        assert user.password_hash != USER_PASSWORD
        assert user.check_password(USER_PASSWORD) is True
        assert user.check_password("wrong-password") is False


def test_login_and_logout_update_navbar(client, app):
    with app.app_context():
        _create_user("analyst", USER_PASSWORD)

    anonymous_home = client.get("/")
    assert anonymous_home.status_code == 200
    assert b"Log In" in anonymous_home.data
    assert b"Log Out" not in anonymous_home.data

    login_response = client.post(
        "/login",
        data={"username": "analyst", "password": USER_PASSWORD},
        follow_redirects=True,
    )

    assert login_response.status_code == 200
    assert b"Welcome, analyst" in login_response.data
    assert b"Log Out" in login_response.data

    logout_response = client.get("/logout", follow_redirects=True)

    assert logout_response.status_code == 200
    assert b"Log In" in logout_response.data
    assert b"Log Out" not in logout_response.data


def test_admin_required_blocks_standard_users_and_allows_admins(client, app):
    with app.app_context():
        _create_user("standard-user", USER_PASSWORD)
        _create_user("admin-user", ADMIN_PASSWORD, role="admin")

    unauthenticated_response = client.get("/admin")
    assert unauthenticated_response.status_code == 403
    assert b"Admin access required" in unauthenticated_response.data

    client.post(
        "/login",
        data={"username": "standard-user", "password": USER_PASSWORD},
        follow_redirects=True,
    )
    standard_response = client.get("/admin")
    assert standard_response.status_code == 403
    assert b"Admin access required" in standard_response.data

    client.get("/logout", follow_redirects=True)
    client.post(
        "/login",
        data={"username": "admin-user", "password": ADMIN_PASSWORD},
        follow_redirects=True,
    )
    admin_response = client.get("/admin")

    assert admin_response.status_code == 200
    assert b"Admin Dashboard" in admin_response.data
