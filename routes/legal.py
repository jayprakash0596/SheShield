from datetime import date
from flask import Blueprint, render_template, request
from models import db, LegalResource

legal_bp = Blueprint("legal", __name__, url_prefix="/legal")


def seed_legal_resources_if_empty():
    """Seeds verified initial legal rights resources across Categories A-H if empty."""
    if LegalResource.query.first():
        return

    initial_resources = [
        # Category A: Constitutional and equality rights
        LegalResource(
            category="CONSTITUTIONAL",
            title_en="Right to Equality & Non-Discrimination",
            title_hi="समानता और गैर-भेदभाव का मौलिक अधिकार",
            summary_en="The Constitution guarantees equality before the law (Article 14) and prohibits discrimination on grounds of sex (Article 15). Special affirmative provisions for women are constitutionally protected.",
            summary_hi="संविधान कानून के समक्ष समानता (अनुच्छेद 14) की गारंटी देता है और लिंग के आधार पर किसी भी प्रकार के भेदभाव को रोकता है (अनुच्छेद 15)। महिलाओं के लिए विशेष कल्याणकारी प्रावधान सुरक्षित हैं।",
            legal_sections="Constitution of India, Articles 14, 15(1), 15(3), 21",
            applicability="All women citizens and persons across India.",
            action_steps_en="If facing institutional discrimination or violation of dignity, write to state human rights commissions or file a writ petition through legal aid.",
            action_steps_hi="यदि किसी संस्था में भेदभाव का सामना करना पड़ रहा है, तो राज्य मानवाधिकार आयोग या कानूनी सहायता के माध्यम से याचिका दायर की जा सकती है।",
            source_url="https://www.wcd.gov.in/",
            last_reviewed_at=date(2026, 1, 15),
            is_published=True
        ),
        # Category B: Domestic violence and family rights
        LegalResource(
            category="DOMESTIC_VIOLENCE",
            title_en="Protection from Domestic Violence (PWDVA)",
            title_hi="घरेलू हिंसा से महिलाओं का संरक्षण अधिनियम",
            summary_en="Protection of Women from Domestic Violence Act provides civil remedies including Protection Orders, Residence Orders, Monetary Relief, and Custody of children for women facing physical, emotional, verbal, or economic abuse.",
            summary_hi="यह कानून शारीरिक, मानसिक, मौखिक या आर्थिक शोषण का सामना करने वाली महिलाओं को सुरक्षा आदेश, निवास अधिकार, गुजारा भत्ता और बच्चों की कस्टडी जैसे त्वरित उपाय प्रदान करता है।",
            legal_sections="Protection of Women from Domestic Violence Act, 2005 (PWDVA), Sections 12, 18-22",
            applicability="Any woman who is or was in a domestic relationship living in a shared household.",
            action_steps_en="Approach a Protection Officer (PO), service provider, Magistrate, or visit the nearest One Stop Centre (OSC). Call helpline 181 for direct guidance.",
            action_steps_hi="संरक्षण अधिकारी (PO), मजिस्ट्रेट या निकटतम वन स्टॉप सेंटर (सखी केंद्र) से संपर्क करें। 181 हेल्पलाइन पर कॉल करें।",
            source_url="https://www.wcd.gov.in/",
            last_reviewed_at=date(2026, 2, 10),
            is_published=True
        ),
        # Category C: Workplace rights
        LegalResource(
            category="WORKPLACE",
            title_en="Prevention of Workplace Sexual Harassment (POSH)",
            title_hi="कार्यस्थल पर महिलाओं का यौन उत्पीड़न रोकथाम (POSH कानून)",
            summary_en="Every organisation with 10+ employees must establish an Internal Committee (IC) to hear sexual harassment complaints. Organizations with fewer employees fall under the District Local Committee (LC).",
            summary_hi="10 या अधिक कर्मचारियों वाले प्रत्येक संस्थान में आंतरिक शिकायत समिति (IC) होना अनिवार्य है। छोटे संस्थानों के लिए जिला स्तरीय स्थानीय समिति (LC) होती है।",
            legal_sections="Sexual Harassment of Women at Workplace Act, 2013 (POSH Act) & Rules",
            applicability="All women employees (full-time, contract, intern, visitor) in public and private sectors.",
            action_steps_en="File a written complaint to the Internal Committee within 3 months of the incident, or lodge a digital complaint on the government SHe-Box portal.",
            action_steps_hi="घटना के 3 महीने के भीतर अपनी आंतरिक समिति (IC) को लिखित शिकायत दें या केंद्र सरकार के SHe-Box पोर्टल पर शिकायत दर्ज करें।",
            source_url="https://shebox.wcd.gov.in/",
            last_reviewed_at=date(2026, 1, 20),
            is_published=True
        ),
        # Category D: Sexual offences and harassment
        LegalResource(
            category="SEXUAL_OFFENCES",
            title_en="Protections Against Stalking and Street Harassment",
            title_hi="पीछा करने (Stalking) और छेड़छाड़ के खिलाफ कानूनी अधिकार",
            summary_en="Physical following, monitoring online activities, or persistent unwanted advances constitutes the criminal offence of Stalking. Women have the right to file a Zero FIR at any police station regardless of jurisdiction.",
            summary_hi="पीछा करना, ऑनलाइन जासूसी करना या अनिच्छुक संपर्क साधना कानूनी अपराध है। महिला किसी भी नजदीकी थाने में 'जीरो एफआईआर' दर्ज करा सकती है।",
            legal_sections="Bharatiya Nyaya Sanhita (BNS) / IPC Section 354D, 354A",
            applicability="All women in public, private, and online spaces.",
            action_steps_en="Record dates, times, screenshots, or witness details. Call 112 or visit the nearest police station. Request women desk assistance.",
            action_steps_hi="तारीख, समय और डिजिटल सबूत सहेजें। तुरंत 112 या 1091 पर संपर्क करें और महिला हेल्पडेस्क से सहायता मांगें।",
            source_url="https://ncwapps.nic.in/onlinecomplaintsv2/",
            last_reviewed_at=date(2026, 2, 1),
            is_published=True
        ),
        # Category E: Cyber safety
        LegalResource(
            category="CYBER_SAFETY",
            title_en="Cyberstalking & Non-Consensual Image Sharing",
            title_hi="साइबर अपराध और तस्वीरों का अवैध दुरुपयोग",
            summary_en="Transmitting sexually explicit material, non-consensual photo sharing, and online blackmail are criminal acts. Victims can lodge complaints anonymously or formally on cybercrime.gov.in.",
            summary_hi="निजी तस्वीरें बिना सहमति के साझा करना या ब्लैकमेल करना गंभीर अपराध है। राष्ट्रीय साइबर अपराध पोर्टल पर गोपनीय या औपचारिक शिकायत दर्ज की जा सकती है।",
            legal_sections="Information Technology Act, 2000 (Sections 66E, 67, 67A) & BNS/IPC",
            applicability="Anyone targeted by digital harassment, extortion, or deepfakes in India.",
            action_steps_en="Never delete evidence: take screenshots including URLs, phone numbers, and profile links. Dial 1930 or submit via cybercrime.gov.in.",
            action_steps_hi="सबूत न मिटाएं: स्क्रीनशॉट और यूआरएल सुरक्षित रखें। 1930 पर कॉल करें या cybercrime.gov.in पर रिपोर्ट दर्ज करें।",
            source_url="https://cybercrime.gov.in/",
            last_reviewed_at=date(2026, 2, 5),
            is_published=True
        ),
        # Category F: Education and child protection
        LegalResource(
            category="CHILD_PROTECTION",
            title_en="Protection of Children from Sexual Offences (POCSO)",
            title_hi="पॉक्सो कानून (POCSO) और बालिकाओं की सुरक्षा",
            summary_en="Strict child protection framework for individuals below 18 years of age. Mandates child-friendly procedures, in-camera trials, and mandatory reporting by institutions.",
            summary_hi="18 वर्ष से कम उम्र के बच्चों के यौन उत्पीड़न के खिलाफ कड़ा कानून। इसमें बच्चे के अनुकूल सुनवाई और गोपनीयता का विशेष प्रावधान है।",
            legal_sections="POCSO Act, 2012 & Prohibition of Child Marriage Act, 2006",
            applicability="All children and minors under 18 years.",
            action_steps_en="Contact Childline at 1098 (24x7 emergency toll-free) or approach the District Child Welfare Committee (CWC).",
            action_steps_hi="24 घंटे मुफ्त हेल्पलाइन 1098 (चाइल्डलाइन) पर संपर्क करें या जिला बाल कल्याण समिति (CWC) से मदद लें।",
            source_url="https://www.wcd.gov.in/",
            last_reviewed_at=date(2026, 1, 10),
            is_published=True
        ),
        # Category G: Property and financial rights
        LegalResource(
            category="PROPERTY",
            title_en="Coparcenary Property and Inheritance Rights",
            title_hi="पैतृक संपत्ति में बेटियों का कानूनी अधिकार",
            summary_en="Daughters have equal coparcenary rights by birth in ancestral property. Women also have absolute ownership rights over their 'Stridhan' (gifts and personal assets).",
            summary_hi="पैतृक संपत्ति में बेटियों को बेटों के बराबर जन्मसिद्ध अधिकार प्राप्त है। स्त्रीधन (उपहार व आभूषण) पर केवल महिला का अनन्य अधिकार होता है।",
            legal_sections="Hindu Succession (Amendment) Act, 2005 & Relevant Personal Laws",
            applicability="Daughters, wives, and mothers under inheritance and succession laws.",
            action_steps_en="Consult a legal aid advocate through DLSA for partition or claim documentation if denied lawful rightful share.",
            action_steps_hi="यदि वैध हिस्से से वंचित किया जा रहा हो, तो जिला विधिक सेवा प्राधिकरण (DLSA) से निःशुल्क वकील की सहायता लें।",
            source_url="https://nalsa.gov.in/womens-assistance/",
            last_reviewed_at=date(2026, 1, 18),
            is_published=True
        ),
        # Category H: Free legal aid and government support
        LegalResource(
            category="FREE_LEGAL_AID",
            title_en="Free Legal Services by NALSA & DLSA",
            title_hi="नालसा (NALSA) के तहत मुफ्त कानूनी सहायता",
            summary_en="Under Section 12(c) of the Legal Services Authorities Act, ALL women in India are entitled to free legal aid, court counsel, and paperwork assistance regardless of their income.",
            summary_hi="कानूनी सेवा प्राधिकरण अधिनियम की धारा 12(c) के तहत भारत में प्रत्येक महिला आय सीमा की परवाह किए बिना निःशुल्क सरकारी वकील व सहायता की हकदार है।",
            legal_sections="Legal Services Authorities Act, 1987, Section 12(c)",
            applicability="All women across all Indian States and Union Territories.",
            action_steps_en="Visit the District Court DLSA front office, apply online via nalsa.gov.in, or call national toll-free legal helpline 15100.",
            action_steps_hi="जिला अदालत में DLSA कार्यालय जाएं, nalsa.gov.in पर आवेदन करें या 15100 विधिक हेल्पलाइन पर कॉल करें।",
            source_url="https://nalsa.gov.in/womens-assistance/",
            last_reviewed_at=date(2026, 2, 12),
            is_published=True
        )
    ]

    db.session.add_all(initial_resources)
    db.session.commit()


@legal_bp.route("/")
def index():
    """Browse and search women's legal rights library in English and Hindi."""
    seed_legal_resources_if_empty()

    category = request.args.get("category", "").strip().upper()
    search_query = request.args.get("q", "").strip()
    lang = request.args.get("lang", "en")  # 'en' or 'hi'

    query = LegalResource.query.filter_by(is_published=True)

    if category:
        query = query.filter_by(category=category)

    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(
            (LegalResource.title_en.ilike(search_filter)) |
            (LegalResource.title_hi.ilike(search_filter)) |
            (LegalResource.summary_en.ilike(search_filter)) |
            (LegalResource.summary_hi.ilike(search_filter)) |
            (LegalResource.legal_sections.ilike(search_filter))
        )

    resources = query.order_by(LegalResource.category).all()

    categories = [
        ("CONSTITUTIONAL", "Constitutional & Equality / समानता"),
        ("DOMESTIC_VIOLENCE", "Domestic Violence & Family / घरेलू हिंसा"),
        ("WORKPLACE", "Workplace Rights (POSH) / कार्यस्थल"),
        ("SEXUAL_OFFENCES", "Sexual Offences / अपराध रोकथाम"),
        ("CYBER_SAFETY", "Cyber Safety / साइबर सुरक्षा"),
        ("CHILD_PROTECTION", "Child Protection / बाल सुरक्षा"),
        ("PROPERTY", "Property & Stridhan / संपत्ति अधिकार"),
        ("FREE_LEGAL_AID", "Free Legal Aid (NALSA) / मुफ्त कानूनी मदद")
    ]

    return render_template(
        "legal/index.html",
        resources=resources,
        categories=categories,
        selected_category=category,
        search_query=search_query,
        lang=lang
    )


@legal_bp.route("/<int:resource_id>")
def detail(resource_id):
    """Detailed view for an individual legal rights resource."""
    resource = db.first_or_404(db.select(LegalResource).filter_by(id=resource_id, is_published=True))
    lang = request.args.get("lang", "en")
    return render_template("legal/detail.html", resource=resource, lang=lang)
