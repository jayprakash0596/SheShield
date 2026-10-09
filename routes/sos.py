import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, abort, send_file, current_app
from models import db, User, TrustedContact, SOSEvent, LocationUpdate, NotificationAttempt, EmergencyEvidence
from forms import TrustedContactForm
from services.auth_utils import login_required
from services.notifications import notification_service
from app import csrf

sos_bp = Blueprint("sos", __name__, url_prefix="/sos")


@sos_bp.route("/")
def index():
    """Emergency SOS main center. Accessible without login for immediate guidance."""
    user = None
    contacts = []
    active_sos = None
    if session.get("user_id"):
        user = db.session.get(User, session["user_id"])
        if user:
            contacts = TrustedContact.query.filter_by(user_id=user.id).all()
            active_sos = SOSEvent.query.filter_by(user_id=user.id, status="ACTIVE").order_by(SOSEvent.created_at.desc()).first()

    return render_template(
        "sos/index.html",
        user=user,
        contacts=contacts,
        active_sos=active_sos,
        sms_provider=notification_service.provider
    )


@sos_bp.route("/trigger", methods=["POST"])
def trigger():
    """
    Triggers an emergency SOS event with explicit consent.
    Can be triggered by logged in user or anonymous/demo mode.
    """
    data = request.get_json(silent=True) or request.form

    trigger_type = data.get("trigger_type", "MANUAL_BUTTON")
    lat_val = data.get("latitude")
    lng_val = data.get("longitude")
    accuracy_val = data.get("accuracy")

    try:
        latitude = float(lat_val) if lat_val is not None and str(lat_val).strip() != "" else None
        longitude = float(lng_val) if lng_val is not None and str(lng_val).strip() != "" else None
        accuracy = float(accuracy_val) if accuracy_val is not None and str(accuracy_val).strip() != "" else None
    except (ValueError, TypeError):
        latitude, longitude, accuracy = None, None, None

    user_id = session.get("user_id")
    event_token = uuid.uuid4().hex

    sos_event = SOSEvent(
        user_id=user_id,
        token=event_token,
        status="ACTIVE",
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy,
        trigger_type=trigger_type,
        created_at=datetime.utcnow()
    )
    db.session.add(sos_event)
    db.session.commit()

    # If coordinates are provided, record first location breadcrumb
    if latitude is not None and longitude is not None:
        loc_update = LocationUpdate(
            sos_event_id=sos_event.id,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            recorded_at=datetime.utcnow()
        )
        db.session.add(loc_update)
        db.session.commit()

    # Dispatch notifications to user's saved trusted contacts
    notification_results = []
    if user_id:
        contacts = TrustedContact.query.filter_by(user_id=user_id, notify_sms=True).all()
        for c in contacts:
            attempt = notification_service.send_sos_alert(sos_event, c)
            notification_results.append({
                "name": c.name,
                "phone": c.phone_number,
                "status": attempt.status,
                "channel": attempt.channel
            })
    else:
        # Anonymous or demo notification simulation
        class DemoContact:
            id = None
            name = "Demo Contact (Local Simulation)"
            phone_number = "9999999999"
        attempt = notification_service.send_sos_alert(sos_event, DemoContact())
        notification_results.append({
            "name": DemoContact.name,
            "phone": DemoContact.phone_number,
            "status": attempt.status,
            "channel": attempt.channel
        })

    if request.is_json:
        return jsonify({
            "success": True,
            "token": sos_event.token,
            "status": sos_event.status,
            "status_url": url_for("sos.status", token=sos_event.token),
            "notifications": notification_results
        }), 201

    flash("Emergency SOS activated. Immediate alerts simulated to your emergency contacts.", "danger")
    return redirect(url_for("sos.status", token=sos_event.token))


@sos_bp.route("/status/<token>")
def status(token):
    """
    Authorized emergency status and monitoring page.
    Requires matching user_id or authorized event token.
    """
    sos_event = SOSEvent.query.filter_by(token=token).first_or_404()

    # Authorization verification: if event has user_id, ensure user owns it or is admin
    if sos_event.user_id:
        if not session.get("user_id"):
            flash("Please sign in to monitor this private emergency event.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("user_id") != sos_event.user_id and not session.get("is_admin"):
            abort(403)

    notifications = NotificationAttempt.query.filter_by(sos_event_id=sos_event.id).all()
    updates = LocationUpdate.query.filter_by(sos_event_id=sos_event.id).order_by(LocationUpdate.recorded_at.desc()).all()
    evidences = EmergencyEvidence.query.filter_by(sos_event_id=sos_event.id).order_by(EmergencyEvidence.created_at.desc()).all()

    return render_template(
        "sos/status.html",
        event=sos_event,
        notifications=notifications,
        updates=updates,
        evidences=evidences,
        sms_provider=notification_service.provider
    )


@sos_bp.route("/upload-evidence/<token>", methods=["POST"])
@csrf.exempt
def upload_evidence(token):
    """
    Accepts background media evidence (photo, ambient audio, video) recorded during SOS.
    """
    sos_event = SOSEvent.query.filter_by(token=token).first_or_404()

    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No media file provided"}), 400

    evidence_type = request.form.get("type", "AUDIO").upper()
    if evidence_type not in ("AUDIO", "IMAGE", "VIDEO"):
        evidence_type = "AUDIO"

    duration_str = request.form.get("duration", "0")
    try:
        duration = float(duration_str)
    except (ValueError, TypeError):
        duration = 0.0

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if not ext or len(ext) > 5:
        ext = "webm" if evidence_type == "AUDIO" else "jpg"

    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_code = uuid.uuid4().hex[:6]
    safe_name = f"evidence_{sos_event.token[:8]}_{evidence_type.lower()}_{timestamp_str}_{unique_code}.{ext}"

    upload_dir = os.path.join(current_app.config.get("UPLOAD_FOLDER"), "evidence")
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, safe_name)
    file.save(full_path)
    file_size = os.path.getsize(full_path)

    evidence = EmergencyEvidence(
        sos_event_id=sos_event.id,
        evidence_type=evidence_type,
        filename=safe_name,
        file_path=full_path,
        file_size_bytes=file_size,
        duration_seconds=duration,
        created_at=datetime.utcnow()
    )
    db.session.add(evidence)
    db.session.commit()

    return jsonify({
        "success": True,
        "evidence_id": evidence.id,
        "type": evidence.evidence_type,
        "url": url_for("sos.serve_evidence", evidence_id=evidence.id)
    }), 201


@sos_bp.route("/evidence/<int:evidence_id>")
def serve_evidence(evidence_id):
    """Securely serves media evidence for an emergency event."""
    evidence = db.get_or_404(EmergencyEvidence, evidence_id)
    if not os.path.exists(evidence.file_path):
        abort(404)

    mimetype = None
    if evidence.evidence_type == "AUDIO":
        mimetype = "audio/webm"
    elif evidence.evidence_type == "IMAGE":
        mimetype = "image/jpeg"
    elif evidence.evidence_type == "VIDEO":
        mimetype = "video/webm"

    return send_file(evidence.file_path, mimetype=mimetype, as_attachment=False)


@sos_bp.route("/track/<token>")
def track(token):
    """
    Public emergency tracking portal for trusted contacts and first responders.
    Accessible without account login via the unique 32-character unguessable token.
    """
    sos_event = SOSEvent.query.filter_by(token=token).first_or_404()
    victim_user = db.session.get(User, sos_event.user_id) if sos_event.user_id else None

    notifications = NotificationAttempt.query.filter_by(sos_event_id=sos_event.id).all()
    updates = LocationUpdate.query.filter_by(sos_event_id=sos_event.id).order_by(LocationUpdate.recorded_at.desc()).all()
    evidences = EmergencyEvidence.query.filter_by(sos_event_id=sos_event.id).order_by(EmergencyEvidence.created_at.desc()).all()

    return render_template(
        "sos/track.html",
        event=sos_event,
        victim=victim_user,
        notifications=notifications,
        updates=updates,
        evidences=evidences
    )


@sos_bp.route("/poll-evidence/<token>")
def poll_evidence(token):
    """Live API polling for newly uploaded emergency evidence."""
    sos_event = SOSEvent.query.filter_by(token=token).first_or_404()
    evidences = EmergencyEvidence.query.filter_by(sos_event_id=sos_event.id).order_by(EmergencyEvidence.created_at.desc()).all()
    return jsonify({
        "status": sos_event.status,
        "latitude": sos_event.latitude,
        "longitude": sos_event.longitude,
        "accuracy": sos_event.accuracy,
        "evidences": [
            {
                "id": e.id,
                "type": e.evidence_type,
                "url": url_for("sos.serve_evidence", evidence_id=e.id),
                "created_at": e.created_at.strftime("%I:%M:%S %p"),
                "duration": round(e.duration_seconds, 1) if e.duration_seconds else 0
            }
            for e in evidences
        ]
    })



@sos_bp.route("/resolve/<token>", methods=["POST"])
def resolve(token):
    """
    Safely resolves or cancels an active SOS event.
    Enforces authorization on backend.
    """
    sos_event = SOSEvent.query.filter_by(token=token).first_or_404()

    # Verify authorization
    if sos_event.user_id:
        if session.get("user_id") != sos_event.user_id and not session.get("is_admin"):
            abort(403)

    action = request.form.get("action", "RESOLVED")
    notes = request.form.get("notes", "").strip()

    sos_event.status = "CANCELLED" if action == "CANCELLED" else "RESOLVED"
    sos_event.resolution_notes = notes or ("Event marked safe by user." if action == "RESOLVED" else "False alarm cancelled.")
    sos_event.resolved_at = datetime.utcnow()
    db.session.commit()

    flash(f"Emergency event has been marked as {sos_event.status.lower()}. Status updated.", "success")
    return redirect(url_for("sos.status", token=sos_event.token))


@sos_bp.route("/resend-alert/<token>", methods=["POST"])
def resend_alert(token):
    """Manually re-dispatch emergency SMS alerts to trusted contacts."""
    sos_event = SOSEvent.query.filter_by(token=token).first_or_404()

    if sos_event.user_id:
        if not session.get("user_id"):
            flash("Please sign in to manage this emergency event.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("user_id") != sos_event.user_id and not session.get("is_admin"):
            abort(403)

    if sos_event.status != "ACTIVE":
        flash("This SOS event is already resolved or cancelled.", "warning")
        return redirect(url_for("sos.status", token=token))

    dispatched = 0
    if sos_event.user_id:
        contacts = TrustedContact.query.filter_by(user_id=sos_event.user_id, notify_sms=True).all()
        for c in contacts:
            notification_service.send_sos_alert(sos_event, c)
            dispatched += 1
    else:
        class DemoContact:
            id = None
            name = "Demo Contact"
            phone_number = "9999999999"
        notification_service.send_sos_alert(sos_event, DemoContact())
        dispatched += 1

    flash(f"Emergency alert re-dispatched to {dispatched} contact(s) via {notification_service.provider.upper()}.", "success")
    return redirect(url_for("sos.status", token=token))


@sos_bp.route("/update-location/<token>", methods=["POST"])
def update_location(token):
    """Add dynamic GPS breadcrumbs during active event."""
    sos_event = SOSEvent.query.filter_by(token=token).first_or_404()
    if sos_event.status != "ACTIVE":
        return jsonify({"error": "Event is no longer active"}), 400

    data = request.get_json(silent=True) or request.form
    try:
        lat = float(data.get("latitude"))
        lng = float(data.get("longitude"))
        acc = float(data.get("accuracy", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinates"}), 400

    update = LocationUpdate(
        sos_event_id=sos_event.id,
        latitude=lat,
        longitude=lng,
        accuracy=acc,
        recorded_at=datetime.utcnow()
    )
    # Update latest coordinates on main event
    sos_event.latitude = lat
    sos_event.longitude = lng
    sos_event.accuracy = acc
    db.session.add(update)
    db.session.commit()

    return jsonify({"success": True, "recorded_at": update.recorded_at.isoformat()}), 200


@sos_bp.route("/contacts", methods=["GET", "POST"])
@login_required
def contacts():
    """Manage trusted emergency contacts."""
    user_id = session["user_id"]
    form = TrustedContactForm()

    if form.validate_on_submit():
        # If set as primary, unset other primary contacts for this user
        if form.is_primary.data:
            TrustedContact.query.filter_by(user_id=user_id, is_primary=True).update({"is_primary": False})

        new_contact = TrustedContact(
            user_id=user_id,
            name=form.name.data.strip(),
            phone_number=form.phone_number.data.strip(),
            relationship=form.relationship.data,
            is_primary=form.is_primary.data,
            notify_sms=form.notify_sms.data
        )
        db.session.add(new_contact)
        db.session.commit()
        flash(f"Emergency contact '{new_contact.name}' added successfully!", "success")
        return redirect(url_for("sos.contacts"))

    contact_list = TrustedContact.query.filter_by(user_id=user_id).order_by(TrustedContact.is_primary.desc(), TrustedContact.created_at.desc()).all()
    return render_template("sos/contacts.html", form=form, contacts=contact_list)


@sos_bp.route("/contacts/delete/<int:contact_id>", methods=["POST"])
@login_required
def delete_contact(contact_id):
    """Delete a trusted contact ensuring user ownership."""
    contact = TrustedContact.query.filter_by(id=contact_id, user_id=session["user_id"]).first_or_404()
    contact_name = contact.name
    db.session.delete(contact)
    db.session.commit()
    flash(f"Contact '{contact_name}' deleted.", "info")
    return redirect(url_for("sos.contacts"))


@sos_bp.route("/history")
@login_required
def history():
    """View personal emergency event history."""
    events = SOSEvent.query.filter_by(user_id=session["user_id"]).order_by(SOSEvent.created_at.desc()).all()
    return render_template("sos/history.html", events=events)
