from flask import Blueprint, render_template, redirect, url_for, session
from models import db, User, TrustedContact, SOSEvent, ComplaintDraft
from services.auth_utils import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    """User dashboard view."""
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # Fetch user data enforcing ownership
    contacts = TrustedContact.query.filter_by(user_id=user.id).all()
    drafts = ComplaintDraft.query.filter_by(user_id=user.id).order_by(ComplaintDraft.updated_at.desc()).all()
    active_sos = SOSEvent.query.filter_by(user_id=user.id, status="ACTIVE").order_by(SOSEvent.created_at.desc()).first()
    recent_sos = SOSEvent.query.filter_by(user_id=user.id).order_by(SOSEvent.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard/index.html",
        user=user,
        contacts=contacts,
        drafts=drafts,
        active_sos=active_sos,
        recent_sos=recent_sos
    )
