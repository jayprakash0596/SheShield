import pytest
from app import create_app
from models import db


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_health_check(client):
    """Test that the /api/health endpoint returns 200 and correct status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert json_data["app"] == "SheShield"
    assert json_data["version"] == "1.0.0"


def test_security_headers(client):
    """Test that basic security headers are set on responses."""
    response = client.get("/api/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert "Content-Security-Policy" in response.headers
