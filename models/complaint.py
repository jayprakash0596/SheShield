import uuid
from datetime import datetime
from models import db


class ComplaintDraft(db.Model):
    """Complaint draft created, edited, and managed privately by the user."""
    __tablename__ = "complaint_drafts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    reference_code = db.Column(db.String(32), unique=True, nullable=False, index=True, default=lambda: f"SH-CMP-{uuid.uuid4().hex[:8].upper()}")
    
    # Complainant Details (Optional where sensitive)
    full_name = db.Column(db.String(120), nullable=True)
    age_group = db.Column(db.String(30), nullable=True)  # e.g., '18-24', '25-34', '35-49', '50+', 'Under 18'
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    preferred_language = db.Column(db.String(10), default="en", nullable=False)

    # Incident Details
    category = db.Column(db.String(60), nullable=False)  # DOMESTIC_VIOLENCE, WORKPLACE_POSH, CYBERCRIME, STALKING, SEXUAL_HARASSMENT, DOWRY, CHILD_PROTECTION, PROPERTY, OTHER
    incident_date = db.Column(db.String(30), nullable=True)
    state = db.Column(db.String(80), nullable=True)
    district = db.Column(db.String(80), nullable=True)
    incident_location = db.Column(db.String(255), nullable=True)
    person_involved = db.Column(db.String(255), nullable=True)
    incident_description = db.Column(db.Text, nullable=False)
    is_ongoing = db.Column(db.Boolean, default=False, nullable=False)
    requested_assistance = db.Column(db.Text, nullable=True)
    
    # Attachment info
    attachment_filename = db.Column(db.String(255), nullable=True)
    attachment_original_name = db.Column(db.String(255), nullable=True)

    # Generated structured document text
    generated_draft_text = db.Column(db.Text, nullable=True)
    
    # Workflow status
    status = db.Column(db.String(30), default="DRAFT", nullable=False)  # 'DRAFT', 'SAVED', 'READY_FOR_PORTAL', 'EXTERNAL_PORTAL_OPENED'
    official_portal_target = db.Column(db.String(100), nullable=True)  # 'NCW', 'SHE_BOX', 'CYBERCRIME', 'NALSA'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ComplaintDraft {self.reference_code} [{self.category}]>"
