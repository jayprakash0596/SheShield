import pytest
from app import create_app
from models import db, User, UserProfile


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_registration_and_login_flow(client):
    """Test valid registration, login, profile auto-creation, and logout."""
    # 1. Register new user
    res = client.post("/auth/register", data={
        "username": "priya_test",
        "email": "priya@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Account created successfully" in res.data or b"Please sign in" in res.data

    # Check user and profile in DB
    user = User.query.filter_by(username="priya_test").first()
    assert user is not None
    assert user.check_password("Password123!") is True
    assert user.check_password("WrongPassword") is False
    assert user.profile is not None

    # 2. Duplicate registration rejection
    dup_res = client.post("/auth/register", data={
        "username": "priya_test",
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    assert b"Username already exists" in dup_res.data

    # 3. Invalid login rejection
    bad_login = client.post("/auth/login", data={
        "username": "priya_test",
        "password": "WrongPassword"
    })
    assert b"Invalid username or password" in bad_login.data

    # 4. Successful login
    good_login = client.post("/auth/login", data={
        "username": "priya_test",
        "password": "Password123!"
    }, follow_redirects=True)
    assert good_login.status_code == 200
    assert b"Welcome back" in good_login.data or b"Dashboard" in good_login.data

    # 5. Access protected dashboard
    dash_res = client.get("/dashboard/")
    assert dash_res.status_code == 200
    assert b"priya_test" in dash_res.data

    # 6. Logout
    logout_res = client.get("/auth/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"signed out safely" in logout_res.data

    # 7. Unauthenticated access redirect
    unauth = client.get("/dashboard/", follow_redirects=False)
    assert unauth.status_code == 302
    assert "/auth/login" in unauth.headers["Location"]
