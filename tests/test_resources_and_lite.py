import pytest
from app import create_app
from models import db, User, UnsafeAreaReport, LegalResource, AwarenessArticle, SelfHelpGroup


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()

        # Admin user
        admin = User(username="admin_user", is_admin=True)
        admin.set_password("AdminPass")
        db.session.add(admin)
        db.session.commit()

        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_map_report_submission_and_moderation(client):
    """Test safety report submission (PENDING by default) and admin approval."""
    # 1. Submit report
    res = client.post("/map/report", data={
        "title": "Broken Streetlights on Ring Road",
        "category": "POOR_LIGHTING",
        "description": "Entire stretch between bus stop and market is pitch dark after 7 PM.",
        "latitude": 28.5355,
        "longitude": 77.3910,
        "address": "Ring Road Sector 18"
    }, follow_redirects=True)
    assert res.status_code == 200

    report = UnsafeAreaReport.query.first()
    assert report is not None
    assert report.status == "PENDING"

    # Ensure unapproved report does not appear in public API for unauthenticated anonymous users
    api_res = client.get("/map/api/reports")
    assert api_res.status_code == 200
    assert len(api_res.get_json()) == 0

    # 2. Admin logs in and approves report
    client.post("/auth/login", data={"username": "admin_user", "password": "AdminPass"})
    mod_res = client.post(f"/admin/reports/moderate/{report.id}", data={
        "action": "APPROVE",
        "moderation_notes": "Verified infrastructural hazard."
    }, follow_redirects=True)
    assert mod_res.status_code == 200

    assert report.status == "APPROVED"

    # Public API now returns the approved report
    api_res2 = client.get("/map/api/reports")
    assert len(api_res2.get_json()) == 1
    assert api_res2.get_json()[0]["title"] == "Broken Streetlights on Ring Road"


def test_legal_rights_bilingual_and_search(client):
    """Test legal rights library seeding, search filter, and Hindi/English rendering."""
    res = client.get("/legal/")
    assert res.status_code == 200
    assert b"Domestic Violence" in res.data or b"PWDVA" in res.data

    # Search query
    search_res = client.get("/legal/?q=POSH")
    assert search_res.status_code == 200
    assert b"POSH" in search_res.data

    # Hindi toggle
    hi_res = client.get("/legal/?lang=hi")
    assert hi_res.status_code == 200
    assert "अधिनियम".encode("utf-8") in hi_res.data


def test_lite_feature_phone_interface(client):
    """Test that /lite renders clean HTML with PROTECT, KNOW, EARN pillars and emergency numbers."""
    lite_res = client.get("/lite/")
    assert lite_res.status_code == 200
    assert b"SheShield Lite" in lite_res.data
    assert b"112" in lite_res.data
    assert b"PROTECT" in lite_res.data
    assert b"KNOW" in lite_res.data
    assert b"EARN" in lite_res.data


def test_route_preview_safe_and_fastest_routes(client):
    """Test intelligent safe route and fastest route discovery API."""
    res = client.post("/map/api/routes", json={
        "start": "coer university",
        "destination": "modipuram"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "start" in data
    assert "destination" in data
    assert "safe_route" in data
    assert "fastest_route" in data
    assert data["safe_route"]["safety_score"] >= 90
    assert len(data["safe_route"]["coordinates"]) > 0
    assert len(data["fastest_route"]["coordinates"]) > 0
    assert len(data["safe_route"]["checkpoints"]) >= 1

