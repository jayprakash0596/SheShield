from flask import Blueprint, render_template, redirect, url_for, flash, session
from models import db, User, UserProfile
from forms import UserProfileForm
from services.auth_utils import login_required

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def edit():
    """View and update authenticated user profile and privacy preferences."""
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    form = UserProfileForm()

    if form.validate_on_submit():
        profile.full_name = form.full_name.data.strip() if form.full_name.data else None
        profile.preferred_language = form.preferred_language.data
        profile.blood_group = form.blood_group.data if form.blood_group.data else None
        profile.emergency_notes = form.emergency_notes.data.strip() if form.emergency_notes.data else None
        profile.state = form.state.data.strip() if form.state.data else None
        profile.district = form.district.data.strip() if form.district.data else None
        profile.consent_share_location = form.consent_share_location.data
        profile.consent_emergency_sms = form.consent_emergency_sms.data

        db.session.commit()
        flash("Profile and privacy settings saved successfully! / आपकी प्रोफाइल सहेज ली गई है!", "success")
        return redirect(url_for("profile.edit"))

    elif not form.is_submitted():
        # Pre-fill existing values
        form.full_name.data = profile.full_name
        form.preferred_language.data = profile.preferred_language
        form.blood_group.data = profile.blood_group or ""
        form.emergency_notes.data = profile.emergency_notes
        form.state.data = profile.state
        form.district.data = profile.district
        form.consent_share_location.data = profile.consent_share_location
        form.consent_emergency_sms.data = profile.consent_emergency_sms

    return render_template("profile/edit.html", form=form, user=user, profile=profile)
