from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from models import (
    db, User, LegalResource, AwarenessArticle, UnsafeAreaReport,
    SelfHelpGroup, AdminAuditLog, SOSEvent, ComplaintDraft
)
from forms import LegalResourceForm, AwarenessArticleForm, SelfHelpGroupForm
from services.auth_utils import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def log_admin_action(action: str, target_type: str, target_id: str, details: str = ""):
    """Records an administrative audit log."""
    log = AdminAuditLog(
        admin_id=session.get("user_id"),
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        details=details,
        ip_address=request.remote_addr or "127.0.0.1",
        created_at=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()


@admin_bp.route("/")
@admin_required
def index():
    """Admin dashboard overview with aggregated statistics and audit trail."""
    stats = {
        "users_count": User.query.count(),
        "pending_reports_count": UnsafeAreaReport.query.filter_by(status="PENDING").count(),
        "approved_reports_count": UnsafeAreaReport.query.filter_by(status="APPROVED").count(),
        "legal_resources_count": LegalResource.query.count(),
        "articles_count": AwarenessArticle.query.count(),
        "shg_count": SelfHelpGroup.query.count(),
        "active_sos_count": SOSEvent.query.filter_by(status="ACTIVE").count(),
        "drafts_count": ComplaintDraft.query.count()
    }
    recent_logs = AdminAuditLog.query.order_by(AdminAuditLog.created_at.desc()).limit(10).all()
    pending_reports = UnsafeAreaReport.query.filter_by(status="PENDING").order_by(UnsafeAreaReport.created_at.desc()).limit(5).all()

    return render_template("admin/index.html", stats=stats, recent_logs=recent_logs, pending_reports=pending_reports)


@admin_bp.route("/reports")
@admin_required
def reports():
    """Moderate community safety reports."""
    filter_status = request.args.get("status", "PENDING")
    query = UnsafeAreaReport.query
    if filter_status:
        query = query.filter_by(status=filter_status)
    items = query.order_by(UnsafeAreaReport.created_at.desc()).all()
    return render_template("admin/reports.html", reports=items, filter_status=filter_status)


@admin_bp.route("/reports/moderate/<int:report_id>", methods=["POST"])
@admin_required
def moderate_report(report_id):
    """Approve or reject a community safety report."""
    report = db.get_or_404(UnsafeAreaReport, report_id)
    action = request.form.get("action")  # 'APPROVE' or 'REJECT'
    notes = request.form.get("moderation_notes", "").strip()

    if action == "APPROVE":
        report.status = "APPROVED"
    elif action == "REJECT":
        report.status = "REJECTED"
    else:
        flash("Invalid moderation action.", "danger")
        return redirect(url_for("admin.reports"))

    report.moderation_notes = notes
    db.session.commit()

    log_admin_action(f"MODERATE_{action}", "UnsafeAreaReport", report.id, f"Marked as {report.status}. Notes: {notes}")
    flash(f"Report '{report.title}' has been marked as {report.status}.", "success")
    return redirect(url_for("admin.reports"))


@admin_bp.route("/legal", methods=["GET", "POST"])
@admin_required
def legal_resources():
    """List and create legal rights educational resources."""
    form = LegalResourceForm()
    if form.validate_on_submit():
        res = LegalResource(
            category=form.category.data,
            title_en=form.title_en.data.strip(),
            title_hi=form.title_hi.data.strip(),
            summary_en=form.summary_en.data.strip(),
            summary_hi=form.summary_hi.data.strip(),
            details_en=form.details_en.data.strip() if form.details_en.data else None,
            details_hi=form.details_hi.data.strip() if form.details_hi.data else None,
            legal_sections=form.legal_sections.data.strip() if form.legal_sections.data else None,
            applicability=form.applicability.data.strip() if form.applicability.data else None,
            action_steps_en=form.action_steps_en.data.strip() if form.action_steps_en.data else None,
            action_steps_hi=form.action_steps_hi.data.strip() if form.action_steps_hi.data else None,
            source_url=form.source_url.data.strip() if form.source_url.data else None,
            last_reviewed_at=date.today(),
            is_published=form.is_published.data
        )
        db.session.add(res)
        db.session.commit()
        log_admin_action("CREATE_LEGAL_RESOURCE", "LegalResource", res.id, f"Created {res.title_en}")
        flash("Legal resource created successfully!", "success")
        return redirect(url_for("admin.legal_resources"))

    resources = LegalResource.query.order_by(LegalResource.created_at.desc()).all()
    return render_template("admin/legal.html", form=form, resources=resources)


@admin_bp.route("/articles", methods=["GET", "POST"])
@admin_required
def articles():
    """List and create awareness articles."""
    form = AwarenessArticleForm()
    if form.validate_on_submit():
        import re
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', form.title.data.lower()).strip('-')
        # Check slug uniqueness
        existing = AwarenessArticle.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{datetime.utcnow().strftime('%s')}"

        art = AwarenessArticle(
            title=form.title.data.strip(),
            slug=slug,
            category=form.category.data,
            summary=form.summary.data.strip(),
            content=form.content.data.strip(),
            source_url=form.source_url.data.strip() if form.source_url.data else None,
            last_reviewed_at=date.today(),
            is_published=form.is_published.data
        )
        db.session.add(art)
        db.session.commit()
        log_admin_action("CREATE_ARTICLE", "AwarenessArticle", art.id, f"Created {art.title}")
        flash("Article published successfully!", "success")
        return redirect(url_for("admin.articles"))

    all_articles = AwarenessArticle.query.order_by(AwarenessArticle.created_at.desc()).all()
    return render_template("admin/articles.html", form=form, articles=all_articles)


@admin_bp.route("/audit-logs")
@admin_required
def audit_logs():
    """View administrative audit history."""
    logs = AdminAuditLog.query.order_by(AdminAuditLog.created_at.desc()).all()
    return render_template("admin/audit_logs.html", logs=logs)

