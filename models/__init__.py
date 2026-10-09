from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import all models for registry
from models.user import User, UserProfile
from models.safety import TrustedContact, SOSEvent, LocationUpdate, UnsafeAreaReport, NotificationAttempt, EmergencyEvidence
from models.complaint import ComplaintDraft
from models.resources import LegalResource, AwarenessArticle, SelfHelpGroup, AdminAuditLog

__all__ = [
    "db",
    "User",
    "UserProfile",
    "TrustedContact",
    "SOSEvent",
    "LocationUpdate",
    "UnsafeAreaReport",
    "NotificationAttempt",
    "EmergencyEvidence",
    "ComplaintDraft",
    "LegalResource",
    "AwarenessArticle",
    "SelfHelpGroup",
    "AdminAuditLog",
]
