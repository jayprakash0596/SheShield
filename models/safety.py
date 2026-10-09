import uuid
from datetime import datetime
from models import db


class TrustedContact(db.Model):
    """Emergency contacts for an authenticated user."""
    __tablename__ = "trusted_contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    relationship = db.Column(db.String(50), nullable=True)  # e.g., Parent, Sister, Friend, Colleague
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    notify_sms = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TrustedContact {self.name} ({self.phone_number})>"


class SOSEvent(db.Model):
    """Emergency event record created when SOS is triggered."""
    __tablename__ = "sos_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)  # 'ACTIVE', 'RESOLVED', 'CANCELLED'
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    accuracy = db.Column(db.Float, nullable=True)
    location_address = db.Column(db.String(255), nullable=True)
    trigger_type = db.Column(db.String(30), default="MANUAL_BUTTON", nullable=False)  # 'MANUAL_BUTTON', 'DEMO_MODE'
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    location_updates = db.relationship("LocationUpdate", backref="sos_event", lazy="dynamic", cascade="all, delete-orphan")
    notifications = db.relationship("NotificationAttempt", backref="sos_event", lazy="dynamic", cascade="all, delete-orphan")
    evidences = db.relationship("EmergencyEvidence", backref="sos_event", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SOSEvent {self.id} [{self.status}]>"


class LocationUpdate(db.Model):
    """Breadcrumb location updates during an active SOS event."""
    __tablename__ = "location_updates"

    id = db.Column(db.Integer, primary_key=True)
    sos_event_id = db.Column(db.Integer, db.ForeignKey("sos_events.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LocationUpdate {self.latitude}, {self.longitude}>"


class UnsafeAreaReport(db.Model):
    """Community-sourced safety and hazard report for the safety map."""
    __tablename__ = "unsafe_area_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="POOR_LIGHTING", nullable=False)  # POOR_LIGHTING, ISOLATED_AREA, HARASSMENT_PRONE, ROAD_HAZARD, OTHER
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default="PENDING", nullable=False)  # 'PENDING', 'APPROVED', 'REJECTED'
    moderation_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UnsafeAreaReport {self.title} [{self.status}]>"


class NotificationAttempt(db.Model):
    """Audit log of SMS/notification dispatch for SOS events."""
    __tablename__ = "notification_attempts"

    id = db.Column(db.Integer, primary_key=True)
    sos_event_id = db.Column(db.Integer, db.ForeignKey("sos_events.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = db.Column(db.Integer, nullable=True)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    channel = db.Column(db.String(20), default="SMS", nullable=False)  # 'SMS', 'MOCK'
    status = db.Column(db.String(20), default="ATTEMPTED", nullable=False)  # 'ATTEMPTED', 'DELIVERED', 'FAILED', 'MOCK_SENT'
    provider_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<NotificationAttempt {self.contact_name}: {self.status}>"


class EmergencyEvidence(db.Model):
    """Captured media evidence (audio recording, camera snapshot, video clip) associated with an SOS event."""
    __tablename__ = "emergency_evidences"

    id = db.Column(db.Integer, primary_key=True)
    sos_event_id = db.Column(db.Integer, db.ForeignKey("sos_events.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = db.Column(db.String(20), nullable=False)  # 'AUDIO', 'IMAGE', 'VIDEO'
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size_bytes = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<EmergencyEvidence {self.id} [{self.evidence_type}] for SOS {self.sos_event_id}>"

