from flask import Blueprint, render_template, request, session
from models import TrustedContact, SelfHelpGroup, LegalResource

lite_bp = Blueprint("lite", __name__, url_prefix="/lite")


@lite_bp.route("/")
def index():
    """
    Lightweight, low-bandwidth interface for 2G/feature-phones.
    Contains three core pillars: PROTECT, KNOW, EARN.
    """
    lang = request.args.get("lang", "en")
    user_id = session.get("user_id")

    contacts = []
    if user_id:
        contacts = TrustedContact.query.filter_by(user_id=user_id).all()

    # Short summary legal resources for basic browsers
    legal_snippets = LegalResource.query.filter_by(is_published=True).limit(6).all()

    # Self Help Groups
    shg_groups = SelfHelpGroup.query.filter_by(is_verified=True).limit(6).all()

    return render_template(
        "lite/index.html",
        lang=lang,
        contacts=contacts,
        legal_snippets=legal_snippets,
        shg_groups=shg_groups
    )
