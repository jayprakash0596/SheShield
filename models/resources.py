from datetime import datetime
from models import db


class LegalResource(db.Model):
    """Verified women's legal rights educational resource in Hindi and English."""
    __tablename__ = "legal_resources"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # CONSTITUTIONAL, DOMESTIC_VIOLENCE, WORKPLACE, SEXUAL_OFFENCES, CYBER_SAFETY, CHILD_PROTECTION, PROPERTY, FREE_LEGAL_AID
    title_en = db.Column(db.String(200), nullable=False)
    title_hi = db.Column(db.String(200), nullable=False)
    summary_en = db.Column(db.Text, nullable=False)
    summary_hi = db.Column(db.Text, nullable=False)
    legal_sections = db.Column(db.String(255), nullable=True)  # e.g., "PWDVA 2005, Sections 18-22", "POSH Act 2013"
    applicability = db.Column(db.Text, nullable=True)
    action_steps_en = db.Column(db.Text, nullable=True)
    action_steps_hi = db.Column(db.Text, nullable=True)
    source_url = db.Column(db.String(255), nullable=True)
    last_reviewed_at = db.Column(db.Date, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LegalResource {self.category}: {self.title_en}>"


class AwarenessArticle(db.Model):
    """Educational awareness and safety information articles."""
    __tablename__ = "awareness_articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), default="PERSONAL_SAFETY", nullable=False)  # PERSONAL_SAFETY, CYBER_SAFETY, GOVT_SCHEMES, COMMUNITY_ANNOUNCEMENT
    summary = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(255), nullable=True)
    last_reviewed_at = db.Column(db.Date, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AwarenessArticle {self.title}>"


class SelfHelpGroup(db.Model):
    """Lightweight informational directory of women-led self-help groups (EARN section)."""
    __tablename__ = "self_help_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    initiative_type = db.Column(db.String(100), nullable=False)  # Handicrafts, Organic farming, Food processing, Community care
    state = db.Column(db.String(80), nullable=False)
    district = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    public_contact = db.Column(db.String(150), nullable=True)
    is_verified = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SelfHelpGroup {self.name}>"


class AdminAuditLog(db.Model):
    """Audit log for sensitive administrative operations."""
    __tablename__ = "admin_audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # e.g., 'APPROVE_REPORT', 'UPDATE_RESOURCE', 'PUBLISH_ARTICLE'
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AdminAuditLog {self.action} by Admin {self.admin_id}>"
