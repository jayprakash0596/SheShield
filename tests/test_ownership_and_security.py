import pytest
from app import create_app
from models import db, User, UserProfile, ComplaintDraft, SOSEvent


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()

        # Seed User A
        user_a = User(username="user_a", is_admin=False)
        user_a.set_password("PasswordA123")
        db.session.add(user_a)

        # Seed User B
        user_b = User(username="user_b", is_admin=False)
        user_b.set_password("PasswordB123")
        db.session.add(user_b)

        # Seed Admin User
        admin_user = User(username="admin_boss", is_admin=True)
        admin_user.set_password("AdminPass123")
        db.session.add(admin_user)

        db.session.commit()

        # Create private draft belonging to User A
        draft_a = ComplaintDraft(
            user_id=user_a.id,
            reference_code="SH-CMP-TESTA",
            category="WORKPLACE_POSH",
            incident_description="Private confidential complaint narrative from user A.",
            generated_draft_text="Draft content A",
            status="READY_FOR_REVIEW"
        )
        db.session.add(draft_a)

        # Create private SOS event belonging to User A
        sos_a = SOSEvent(
            user_id=user_a.id,
            token="token-secret-user-a-12345",
            status="ACTIVE",
            latitude=19.0760,
            longitude=72.8777
        )
        db.session.add(sos_a)
        db.session.commit()

        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login_as(client, username, password):
    """Helper to authenticate a test client."""
    return client.post("/auth/login", data={"username": username, "password": password}, follow_redirects=True)


def test_complaint_ownership_isolation(client):
    """Ensure User B cannot view, edit, download, or delete User A's private complaint draft."""
    draft_a = ComplaintDraft.query.filter_by(reference_code="SH-CMP-TESTA").first()

    # Log in as User B
    login_as(client, "user_b", "PasswordB123")

    # User B attempts to view User A's draft -> 403 Forbidden
    res_view = client.get(f"/complaints/view/{draft_a.id}")
    assert res_view.status_code == 403

    # User B attempts to edit User A's draft -> 403 Forbidden
    res_edit = client.get(f"/complaints/edit/{draft_a.id}")
    assert res_edit.status_code == 403

    # User B attempts to download TXT of User A's draft -> 403 Forbidden
    res_txt = client.get(f"/complaints/download/txt/{draft_a.id}")
    assert res_txt.status_code == 403

    # User B attempts to delete User A's draft -> 403 Forbidden
    res_del = client.post(f"/complaints/delete/{draft_a.id}")
    assert res_del.status_code == 403

    # Ensure draft still exists in DB intact
    assert ComplaintDraft.query.filter_by(reference_code="SH-CMP-TESTA").first() is not None


def test_sos_event_ownership_isolation(client):
    """Ensure User B cannot monitor or resolve User A's private SOS event."""
    # Log in as User B
    login_as(client, "user_b", "PasswordB123")

    # User B attempts to view User A's private status page -> 403 Forbidden
    res_sos = client.get("/sos/status/token-secret-user-a-12345")
    assert res_sos.status_code == 403

    # User B attempts to resolve User A's event -> 403 Forbidden
    res_resolve = client.post("/sos/resolve/token-secret-user-a-12345", data={"action": "CANCELLED"})
    assert res_resolve.status_code == 403


def test_admin_access_control(client):
    """Ensure ordinary users are strictly forbidden from /admin/, but admins are authorized."""
    # Unauthenticated user -> redirected to login
    unauth_res = client.get("/admin/", follow_redirects=False)
    assert unauth_res.status_code == 302
    assert "/auth/login" in unauth_res.headers["Location"]

    # Ordinary User A tries to access admin -> 403 Forbidden
    login_as(client, "user_a", "PasswordA123")
    forbidden_res = client.get("/admin/")
    assert forbidden_res.status_code == 403

    # Logout and log in as verified Admin
    client.get("/auth/logout")
    login_as(client, "admin_boss", "AdminPass123")
    admin_res = client.get("/admin/")
    assert admin_res.status_code == 200
    assert b"Admin Dashboard" in admin_res.data
