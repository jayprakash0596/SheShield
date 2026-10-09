import pytest
from app import create_app
from models import db, User, ComplaintDraft


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        user = User(username="complainant_user")
        user.set_password("SecurePass123")
        db.session.add(user)
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_complaint_full_lifecycle(client):
    """Test complaint draft creation, preview, edit, PDF/TXT download, portal routing, and deletion."""
    # 1. Login
    client.post("/auth/login", data={"username": "complainant_user", "password": "SecurePass123"})

    # 2. Invalid form rejection (description too short, consent unchecked)
    bad_res = client.post("/complaints/new", data={
        "category": "WORKPLACE_POSH",
        "incident_description": "Short",
        "consent_acknowledgement": "n"
    })
    assert bad_res.status_code == 200
    assert ComplaintDraft.query.count() == 0

    # 3. Valid draft creation
    valid_res = client.post("/complaints/new", data={
        "category": "WORKPLACE_POSH",
        "preferred_language": "en",
        "full_name": "Meera Patel",
        "age_group": "25-34",
        "phone_number": "9876543210",
        "incident_date": "10 February 2026",
        "state": "Karnataka",
        "district": "Bengaluru",
        "incident_location": "Office Conference Hall",
        "incident_description": "The senior manager persistently passed sexually coloured remarks during late evening meetings.",
        "is_ongoing": "y",
        "requested_assistance": "Inquiry by Internal Committee and workplace transfer.",
        "consent_acknowledgement": "y"
    }, follow_redirects=True)
    assert valid_res.status_code == 200

    draft = ComplaintDraft.query.first()
    assert draft is not None
    assert draft.category == "WORKPLACE_POSH"
    assert "Meera Patel" in draft.generated_draft_text
    assert "Internal Committee" in draft.generated_draft_text
    assert draft.status == "READY_FOR_REVIEW"

    # 4. View Draft
    view_res = client.get(f"/complaints/view/{draft.id}")
    assert view_res.status_code == 200
    assert b"Meera Patel" in view_res.data
    assert b"SHe-Box" in view_res.data

    # 5. Direct Editing
    edit_res = client.post(f"/complaints/edit/{draft.id}", data={
        "draft_text": "Updated complaint text with additional witness corroboration details."
    }, follow_redirects=True)
    assert edit_res.status_code == 200
    assert draft.generated_draft_text == "Updated complaint text with additional witness corroboration details."
    assert draft.status == "READY_FOR_PORTAL"

    # 6. TXT Download
    txt_res = client.get(f"/complaints/download/txt/{draft.id}")
    assert txt_res.status_code == 200
    assert txt_res.mimetype == "text/plain"
    assert b"Updated complaint text" in txt_res.data

    # 7. PDF Download
    pdf_res = client.get(f"/complaints/download/pdf/{draft.id}")
    assert pdf_res.status_code == 200
    assert pdf_res.mimetype == "application/pdf"
    assert len(pdf_res.data) > 500  # Valid generated binary PDF stream

    # 8. Portal Routing Guidance
    portal_res = client.get(f"/complaints/portal/{draft.id}")
    assert portal_res.status_code == 200
    assert b"shebox.wcd.gov.in" in portal_res.data
    assert draft.status == "EXTERNAL_PORTAL_OPENED"

    # 9. Deletion
    del_res = client.post(f"/complaints/delete/{draft.id}", follow_redirects=True)
    assert del_res.status_code == 200
    assert ComplaintDraft.query.filter_by(id=draft.id).first() is None
