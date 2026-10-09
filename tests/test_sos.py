import io
import pytest
from app import create_app
from models import db, User, TrustedContact, SOSEvent, LocationUpdate, NotificationAttempt, EmergencyEvidence


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        user = User(username="sos_tester")
        user.set_password("SosPass123")
        db.session.add(user)
        db.session.commit()

        # Add a trusted contact
        contact = TrustedContact(
            user_id=user.id,
            name="Brother Rahul",
            phone_number="9876543210",
            relationship="Sibling",
            is_primary=True,
            notify_sms=True
        )
        db.session.add(contact)
        db.session.commit()

        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_sos_anonymous_trigger_and_mock(client):
    """Test that SOS trigger functions safely in mock mode without external carrier calls."""
    res = client.post("/sos/trigger", json={
        "latitude": 28.6139,
        "longitude": 77.2090,
        "accuracy": 15.0,
        "trigger_type": "MANUAL_BUTTON"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert "token" in data

    event = SOSEvent.query.filter_by(token=data["token"]).first()
    assert event is not None
    assert event.status == "ACTIVE"
    assert event.latitude == 28.6139

    # Verify notification attempt was recorded as MOCK_SENT
    notif = NotificationAttempt.query.filter_by(sos_event_id=event.id).first()
    assert notif is not None
    assert notif.status == "MOCK_SENT"
    assert "DEMO/MOCK MODE" in notif.provider_response


def test_sos_authenticated_flow_with_contacts(client):
    """Test authenticated SOS with contact notifications, breadcrumbs, and resolution."""
    # 1. Login
    client.post("/auth/login", data={"username": "sos_tester", "password": "SosPass123"})

    # 2. Trigger SOS
    res = client.post("/sos/trigger", json={
        "latitude": 12.9716,
        "longitude": 77.5946,
        "accuracy": 5.0
    })
    token = res.get_json()["token"]

    event = SOSEvent.query.filter_by(token=token).first()
    assert event.status == "ACTIVE"

    # Notification sent to Brother Rahul
    notif = NotificationAttempt.query.filter_by(sos_event_id=event.id).first()
    assert notif.contact_name == "Brother Rahul"
    assert notif.status == "MOCK_SENT"

    # 3. Add dynamic location update (breadcrumb)
    loc_res = client.post(f"/sos/update-location/{token}", json={
        "latitude": 12.9720,
        "longitude": 77.5950,
        "accuracy": 4.0
    })
    assert loc_res.status_code == 200

    breadcrumbs = LocationUpdate.query.filter_by(sos_event_id=event.id).all()
    assert len(breadcrumbs) >= 1

    # 4. Resolve the event
    resolve_res = client.post(f"/sos/resolve/{token}", data={
        "action": "RESOLVED",
        "notes": "Reached home safely."
    }, follow_redirects=True)
    assert resolve_res.status_code == 200

    event = SOSEvent.query.filter_by(token=token).first()
    assert event.status == "RESOLVED"
    assert event.resolution_notes == "Reached home safely."


def test_contact_management(client):
    """Test adding and deleting trusted contacts with ownership verification."""
    client.post("/auth/login", data={"username": "sos_tester", "password": "SosPass123"})

    # Add contact
    res = client.post("/sos/contacts", data={
        "name": "Sister Pooja",
        "phone_number": "9123456789",
        "relationship": "Sibling",
        "notify_sms": "y"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Sister Pooja" in res.data

    contact = TrustedContact.query.filter_by(name="Sister Pooja").first()
    assert contact is not None

    # Delete contact
    del_res = client.post(f"/sos/contacts/delete/{contact.id}", follow_redirects=True)
    assert del_res.status_code == 200
    assert TrustedContact.query.filter_by(name="Sister Pooja").first() is None


def test_sos_evidence_upload_and_serve(client):
    """Test emergency media evidence upload (photo and audio) and delivery."""
    # 1. Trigger SOS
    res = client.post("/sos/trigger", json={
        "latitude": 28.7041,
        "longitude": 77.1025,
        "accuracy": 8.0
    })
    assert res.status_code == 201
    token = res.get_json()["token"]

    # 2. Upload photo snapshot
    photo_data = (io.BytesIO(b"\xff\xd8\xff\xe0fake_jpeg_bytes"), "snapshot.jpg")
    photo_res = client.post(f"/sos/upload-evidence/{token}", data={
        "file": photo_data,
        "type": "IMAGE"
    }, content_type="multipart/form-data")
    assert photo_res.status_code == 201
    photo_json = photo_res.get_json()
    assert photo_json["success"] is True
    assert photo_json["type"] == "IMAGE"
    photo_id = photo_json["evidence_id"]

    # 3. Upload ambient audio clip
    audio_data = (io.BytesIO(b"fake_webm_audio_bytes_12345"), "ambient_voice.webm")
    audio_res = client.post(f"/sos/upload-evidence/{token}", data={
        "file": audio_data,
        "type": "AUDIO",
        "duration": "8.5"
    }, content_type="multipart/form-data")
    assert audio_res.status_code == 201
    audio_json = audio_res.get_json()
    assert audio_json["success"] is True
    assert audio_json["type"] == "AUDIO"
    audio_id = audio_json["evidence_id"]

    # 4. Verify retrieval of evidence
    ev_photo = client.get(f"/sos/evidence/{photo_id}")
    assert ev_photo.status_code == 200
    assert ev_photo.mimetype == "image/jpeg"
    assert ev_photo.data == b"\xff\xd8\xff\xe0fake_jpeg_bytes"

    ev_audio = client.get(f"/sos/evidence/{audio_id}")
    assert ev_audio.status_code == 200
    assert ev_audio.mimetype == "audio/webm"
    assert ev_audio.data == b"fake_webm_audio_bytes_12345"

    # 5. Verify live evidence polling endpoint
    poll_res = client.get(f"/sos/poll-evidence/{token}")
    assert poll_res.status_code == 200
    poll_json = poll_res.get_json()
    assert poll_json["status"] == "ACTIVE"
    assert len(poll_json["evidences"]) == 2


def test_sos_track_portal_for_trusted_contacts(client):
    """Test that trusted contacts can view live location and evidence via unguessable token without login."""
    # User triggers SOS
    client.post("/auth/login", data={"username": "sos_tester", "password": "SosPass123"})
    res = client.post("/sos/trigger", json={
        "latitude": 19.0760,
        "longitude": 72.8777,
        "accuracy": 10.0
    })
    token = res.get_json()["token"]

    # User uploads evidence
    photo_data = (io.BytesIO(b"\xff\xd8\xff\xe0fake_photo"), "snapshot.jpg")
    client.post(f"/sos/upload-evidence/{token}", data={
        "file": photo_data,
        "type": "IMAGE"
    }, content_type="multipart/form-data")

    # Log out user completely (simulating an external trusted contact tapping SMS link)
    client.get("/auth/logout")

    # Contact opens tracking URL /sos/track/<token> without being authenticated
    track_res = client.get(f"/sos/track/{token}")
    assert track_res.status_code == 200
    assert b"TRUSTED CONTACT EMERGENCY PORTAL" in track_res.data
    assert b"19.07600" in track_res.data
    assert b"CAMERA SNAPSHOT" in track_res.data

