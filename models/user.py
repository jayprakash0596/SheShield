from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(db.Model):
    """User account model for SheShield."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    profile = db.relationship("UserProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    trusted_contacts = db.relationship("TrustedContact", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    sos_events = db.relationship("SOSEvent", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    complaint_drafts = db.relationship("ComplaintDraft", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    safety_reports = db.relationship("UnsafeAreaReport", backref="user", lazy="dynamic")

    def set_password(self, password: str):
        """Hash and store user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify user password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class UserProfile(db.Model):
    """User profile and consent preferences."""
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=True)
    preferred_language = db.Column(db.String(10), default="en", nullable=False)  # 'en' or 'hi'
    blood_group = db.Column(db.String(10), nullable=True)
    emergency_notes = db.Column(db.Text, nullable=True)
    state = db.Column(db.String(80), nullable=True)
    district = db.Column(db.String(80), nullable=True)
    consent_share_location = db.Column(db.Boolean, default=True, nullable=False)
    consent_emergency_sms = db.Column(db.Boolean, default=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserProfile for User {self.user_id}>"
