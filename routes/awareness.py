from datetime import date
from flask import Blueprint, render_template, request
from models import db, AwarenessArticle, SelfHelpGroup

awareness_bp = Blueprint("awareness", __name__, url_prefix="/awareness")


def seed_awareness_data_if_empty():
    """Seed initial educational awareness articles and self-help group directory records."""
    if not AwarenessArticle.query.first():
        articles = [
            AwarenessArticle(
                title="Preserving Digital Evidence for Cybercrime Reporting",
                slug="preserving-digital-evidence",
                category="CYBER_SAFETY",
                summary="Crucial steps for capturing screenshots, metadata, and message logs safely when facing online harassment or extortion.",
                content="""When facing cyber threats, stalking, or non-consensual image sharing, your initial reaction might be to block the perpetrator and delete chats. However, preserving digital evidence is essential for effective police investigation:

1. Screenshot Everything with Context:
Capture full conversations including timestamps, phone numbers, WhatsApp/Telegram IDs, and profile URLs. Ensure the system clock and device battery status are visible in screenshots.

2. Do Not Alter or Crop Images:
Save the raw screenshot files directly without cropping or editing. Digital forensic examiners check metadata (EXIF data and file timestamps).

3. Export Chat Backups:
On messaging apps, use the 'Export Chat' feature (with media) and store it securely in cloud storage or an offline USB drive.

4. Record Profile URLs:
Perpetrators frequently delete or change social media handles. Save the exact profile URL (e.g. instagram.com/username) rather than just display names.

5. Report Promptly:
Dial 1930 immediately or submit directly to cybercrime.gov.in. Evidence on server logs (IP logs) can expire after 30 to 90 days as per data retention limits.""",
                source_url="https://cybercrime.gov.in/",
                last_reviewed_at=date(2026, 1, 20),
                is_published=True
            ),
            AwarenessArticle(
                title="Understanding Zero FIR: Filing at Any Police Station in India",
                slug="understanding-zero-fir",
                category="PERSONAL_SAFETY",
                summary="Your constitutional right to register a Zero FIR at any police station regardless of geographical jurisdiction.",
                content="""Following the Justice Verma Committee recommendations, Indian criminal law explicitly mandates the concept of 'Zero FIR':

1. What is a Zero FIR?
A Zero FIR can be lodged at any police station across India, regardless of where the incident occurred. It is numbered as '0' initially and subsequently transferred to the jurisdictional police station for full investigation.

2. Mandatory Registration:
Police officers cannot refuse to register an FIR on the grounds of lack of territorial jurisdiction if a cognizable offence against a woman is alleged. Refusal to register can attract disciplinary and penal action under Section 166A IPC / BNSS.

3. Statements Recorded by Women Officers:
For offences involving sexual assault or harassment, the law mandates that the victim's statement must be recorded by a woman police officer or at the victim's residence.

4. Free Copy of FIR:
The complainant is legally entitled to receive a certified copy of the registered FIR immediately and free of cost.""",
                source_url="https://www.wcd.gov.in/",
                last_reviewed_at=date(2026, 2, 1),
                is_published=True
            ),
            AwarenessArticle(
                title="Pradhan Mantri Matru Vandana Yojana & One Stop Centres (OSC)",
                slug="pm-mvy-and-one-stop-centres",
                category="GOVT_SCHEMES",
                summary="Government schemes providing maternity cash assistance and integrated crisis support for women in distress.",
                content="""The Ministry of Women and Child Development operates several key welfare frameworks:

1. One Stop Centres (Sakhi Centres):
Established across districts to support women affected by violence in private and public spaces. They provide emergency medical aid, police facilitation, legal counseling, psychological support, and temporary shelter under one roof. (Toll-Free Helpline: 181).

2. Pradhan Mantri Matru Vandana Yojana (PMMVY):
A direct benefit transfer (DBT) maternity incentive scheme providing financial support for pregnant women and lactating mothers for health, nutrition, and wage loss compensation.

3. Beti Bachao Beti Padhao:
A nationwide initiative ensuring the survival, protection, and education of the girl child across all states.""",
                source_url="https://www.wcd.gov.in/",
                last_reviewed_at=date(2026, 1, 15),
                is_published=True
            )
        ]
        db.session.add_all(articles)
        db.session.commit()

    if not SelfHelpGroup.query.first():
        groups = [
            SelfHelpGroup(
                name="Prerna Mahila Bachat Gat",
                initiative_type="Organic Agro-Products & Handloom",
                state="Maharashtra",
                district="Pune",
                description="Community-led cooperative of 24 women specializing in indigenous grain preservation, jaggery processing, and natural cloth weaving.",
                public_contact="Authorized Coordinator: prerna.pune@community-shg.org",
                is_verified=True
            ),
            SelfHelpGroup(
                name="Kiran Gramin Vikas Samiti",
                initiative_type="Traditional Handicrafts & Jute Crafts",
                state="West Bengal",
                district="Nadia",
                description="Artisan collective preserving traditional terracotta and eco-friendly jute handicraft production, supporting financial independence for rural mothers.",
                public_contact="Nadia District SHG Federation Contact Cell",
                is_verified=True
            ),
            SelfHelpGroup(
                name="Shakti Self-Reliant Women Collective",
                initiative_type="Solar Lamp Assembly & Clean Energy",
                state="Rajasthan",
                district="Udaipur",
                description="Grassroots initiative training rural women in solar appliance repair, clean cookstove dissemination, and household micro-savings.",
                public_contact="Udaipur Women's Development Project Desk",
                is_verified=True
            )
        ]
        db.session.add_all(groups)
        db.session.commit()


@awareness_bp.route("/")
def index():
    """Educational awareness articles and initiatives hub."""
    seed_awareness_data_if_empty()
    category = request.args.get("category", "")
    query = AwarenessArticle.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)
    articles = query.order_by(AwarenessArticle.created_at.desc()).all()
    shg_count = SelfHelpGroup.query.filter_by(is_verified=True).count()

    return render_template(
        "awareness/index.html",
        articles=articles,
        shg_count=shg_count,
        selected_category=category
    )


@awareness_bp.route("/article/<slug>")
def article_detail(slug):
    """Read a full educational awareness article."""
    article = AwarenessArticle.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("awareness/article.html", article=article)


@awareness_bp.route("/shg")
def shg_directory():
    """Non-commercial informational directory of women-led self-help groups (EARN section)."""
    seed_awareness_data_if_empty()
    state_filter = request.args.get("state", "").strip()
    query = SelfHelpGroup.query.filter_by(is_verified=True)
    if state_filter:
        query = query.filter(SelfHelpGroup.state.ilike(f"%{state_filter}%"))
    groups = query.order_by(SelfHelpGroup.state, SelfHelpGroup.name).all()
    return render_template("awareness/shg_directory.html", groups=groups, state_filter=state_filter)
