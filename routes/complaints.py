import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    session, send_file, abort, current_app, Response
)
from models import db, ComplaintDraft
from forms import ComplaintDraftForm
from services.auth_utils import login_required
from services.complaint_generator import generate_structured_complaint
from services.complaint_routing import get_routing_for_category
from services.pdf_generator import generate_complaint_pdf

complaints_bp = Blueprint("complaints", __name__, url_prefix="/complaints")


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has safe allowed extension."""
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "png", "jpg", "jpeg", "txt"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def verify_draft_ownership(draft: ComplaintDraft):
    """Ensure user owns this draft or abort with 403."""
    user_id = session.get("user_id")
    # If draft is associated with a user, ensure current session user owns it (or is admin)
    if draft.user_id:
        if not user_id:
            flash("Please sign in to access this draft.", "warning")
            abort(403)
        if draft.user_id != user_id and not session.get("is_admin"):
            abort(403)


@complaints_bp.route("/")
def index():
    """Complaint workflow guide and entry page."""
    user_drafts_count = 0
    if session.get("user_id"):
        user_drafts_count = ComplaintDraft.query.filter_by(user_id=session["user_id"]).count()
    return render_template("complaints/index.html", user_drafts_count=user_drafts_count)


@complaints_bp.route("/new", methods=["GET", "POST"])
def new():
    """Create a new structured complaint draft."""
    form = ComplaintDraftForm()

    # Pre-select category if passed in query string from legal library
    pre_cat = request.args.get("category")
    if request.method == "GET" and pre_cat and pre_cat in dict(form.category.choices):
        form.category.data = pre_cat

    if form.validate_on_submit():
        user_id = session.get("user_id")
        ref_code = f"SH-CMP-{uuid.uuid4().hex[:8].upper()}"

        # Handle optional supporting attachment
        saved_filename = None
        orig_filename = None
        if form.supporting_doc.data and hasattr(form.supporting_doc.data, "filename"):
            file = form.supporting_doc.data
            if file.filename != "":
                if not allowed_file(file.filename):
                    flash("Unsupported file format. Please upload PDF, PNG, JPG, or TXT.", "danger")
                    return render_template("complaints/form.html", form=form)
                
                orig_filename = secure_filename(file.filename)
                saved_filename = f"{ref_code}_{orig_filename}"
                upload_folder = current_app.config.get("UPLOAD_FOLDER")
                file.save(os.path.join(upload_folder, saved_filename))

        # Prepare data dict for generator
        data_dict = {
            "reference_code": ref_code,
            "full_name": form.full_name.data.strip() if form.full_name.data else None,
            "age_group": form.age_group.data,
            "phone_number": form.phone_number.data.strip() if form.phone_number.data else None,
            "email": form.email.data.strip() if form.email.data else None,
            "preferred_language": form.preferred_language.data,
            "category": form.category.data,
            "incident_date": form.incident_date.data.strip() if form.incident_date.data else None,
            "state": form.state.data.strip() if form.state.data else None,
            "district": form.district.data.strip() if form.district.data else None,
            "incident_location": form.incident_location.data.strip() if form.incident_location.data else None,
            "person_involved": form.person_involved.data.strip() if form.person_involved.data else None,
            "incident_description": form.incident_description.data.strip(),
            "is_ongoing": form.is_ongoing.data,
            "requested_assistance": form.requested_assistance.data.strip() if form.requested_assistance.data else None,
            "attachment_original_name": orig_filename
        }

        generated_text = generate_structured_complaint(data_dict)
        routing_info = get_routing_for_category(form.category.data)

        draft = ComplaintDraft(
            user_id=user_id,
            reference_code=ref_code,
            full_name=data_dict["full_name"],
            age_group=data_dict["age_group"],
            phone_number=data_dict["phone_number"],
            email=data_dict["email"],
            preferred_language=data_dict["preferred_language"],
            category=data_dict["category"],
            incident_date=data_dict["incident_date"],
            state=data_dict["state"],
            district=data_dict["district"],
            incident_location=data_dict["incident_location"],
            person_involved=data_dict["person_involved"],
            incident_description=data_dict["incident_description"],
            is_ongoing=data_dict["is_ongoing"],
            requested_assistance=data_dict["requested_assistance"],
            attachment_filename=saved_filename,
            attachment_original_name=orig_filename,
            generated_draft_text=generated_text,
            status="READY_FOR_REVIEW",
            official_portal_target=routing_info.get("authority_code")
        )
        db.session.add(draft)
        db.session.commit()

        flash(f"Complaint draft '{ref_code}' created successfully! Review and edit below.", "success")
        return redirect(url_for("complaints.view", draft_id=draft.id))

    return render_template("complaints/form.html", form=form)


@complaints_bp.route("/view/<int:draft_id>")
def view(draft_id):
    """Preview structured complaint draft with download and official portal options."""
    draft = db.get_or_404(ComplaintDraft, draft_id)
    verify_draft_ownership(draft)
    routing = get_routing_for_category(draft.category)
    return render_template("complaints/view.html", draft=draft, routing=routing)


@complaints_bp.route("/edit/<int:draft_id>", methods=["GET", "POST"])
def edit(draft_id):
    """Edit the generated draft text directly before submitting or downloading."""
    draft = db.get_or_404(ComplaintDraft, draft_id)
    verify_draft_ownership(draft)

    if request.method == "POST":
        updated_text = request.form.get("draft_text", "").strip()
        if not updated_text:
            flash("Draft content cannot be empty.", "danger")
        else:
            draft.generated_draft_text = updated_text
            draft.status = "READY_FOR_PORTAL"
            draft.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Draft updated successfully!", "success")
            return redirect(url_for("complaints.view", draft_id=draft.id))

    return render_template("complaints/edit.html", draft=draft)


@complaints_bp.route("/download/txt/<int:draft_id>")
def download_txt(draft_id):
    """Download complaint draft as clean plain text document (.txt)."""
    draft = db.get_or_404(ComplaintDraft, draft_id)
    verify_draft_ownership(draft)

    filename = f"{draft.reference_code}.txt"
    return Response(
        draft.generated_draft_text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@complaints_bp.route("/download/pdf/<int:draft_id>")
def download_pdf(draft_id):
    """Download complaint draft as styled PDF (.pdf)."""
    draft = db.get_or_404(ComplaintDraft, draft_id)
    verify_draft_ownership(draft)

    pdf_stream = generate_complaint_pdf(draft.generated_draft_text, draft.reference_code)
    filename = f"{draft.reference_code}.pdf"
    return send_file(
        pdf_stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )


@complaints_bp.route("/portal/<int:draft_id>")
def continue_to_portal(draft_id):
    """
    Guidance page before opening official government portal.
    Updates status honestly to 'EXTERNAL_PORTAL_OPENED'.
    """
    draft = db.get_or_404(ComplaintDraft, draft_id)
    verify_draft_ownership(draft)
    routing = get_routing_for_category(draft.category)

    # Authoritative status update
    draft.status = "EXTERNAL_PORTAL_OPENED"
    db.session.commit()

    return render_template("complaints/portal_guide.html", draft=draft, routing=routing)


@complaints_bp.route("/delete/<int:draft_id>", methods=["POST"])
def delete(draft_id):
    """Permanently delete a user's own complaint draft."""
    draft = db.get_or_404(ComplaintDraft, draft_id)
    verify_draft_ownership(draft)

    # Clean up attachment file if present
    if draft.attachment_filename:
        upload_folder = current_app.config.get("UPLOAD_FOLDER")
        file_path = os.path.join(upload_folder, draft.attachment_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    ref = draft.reference_code
    db.session.delete(draft)
    db.session.commit()
    flash(f"Draft '{ref}' permanently deleted. All associated data removed.", "info")
    return redirect(url_for("complaints.my_drafts") if session.get("user_id") else url_for("complaints.index"))


@complaints_bp.route("/my-drafts")
@login_required
def my_drafts():
    """List of all drafts belonging to current user."""
    drafts = ComplaintDraft.query.filter_by(user_id=session["user_id"]).order_by(ComplaintDraft.updated_at.desc()).all()
    return render_template("complaints/my_drafts.html", drafts=drafts)
