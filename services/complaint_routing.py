"""
Complaint Routing Service.
Maps complaint categories to verified official government portals with clear context and warnings.
"""

OFFICIAL_AUTHORITY_MAPPINGS = {
    "DOMESTIC_VIOLENCE": {
        "portal_name": "National Commission for Women (NCW) & Local Protection Officer",
        "portal_url": "https://ncwapps.nic.in/onlinecomplaintsv2/",
        "authority_code": "NCW",
        "description": "NCW investigates complaints of domestic violence, cruelty, and women's rights deprivation.",
        "requirements": "Online registration requires mobile verification (OTP) and basic incident details.",
        "emergency_fallback": "For immediate physical danger, call 112 or Women Helpline 181 right now."
    },
    "DOWRY_HARASSMENT": {
        "portal_name": "National Commission for Women (NCW) Complaint Cell",
        "portal_url": "https://ncwapps.nic.in/onlinecomplaintsv2/",
        "authority_code": "NCW",
        "description": "NCW processes dowry harassment and domestic cruelty complaints directly.",
        "requirements": "Requires complainant details, respondent information, and written narrative.",
        "emergency_fallback": "Call 112 or local police women's desk if under threat of harm."
    },
    "WORKPLACE_POSH": {
        "portal_name": "SHe-Box (Ministry of Women and Child Development)",
        "portal_url": "https://shebox.wcd.gov.in/",
        "authority_code": "SHE_BOX",
        "description": "Centralized government portal for sexual harassment complaints in both organized and unorganized sectors.",
        "requirements": "Forwarded directly to your company's Internal Committee (IC) or District Local Committee (LC).",
        "emergency_fallback": "You can also submit this draft directly in writing to your organisation's Internal Committee presiding officer."
    },
    "CYBERCRIME": {
        "portal_name": "National Cyber Crime Reporting Portal (MHA)",
        "portal_url": "https://cybercrime.gov.in/",
        "authority_code": "CYBERCRIME",
        "description": "Official Ministry of Home Affairs portal for cyberstalking, non-consensual images, and digital blackmail.",
        "requirements": "Supports both anonymous reporting (for explicit photos) and citizen account registration (for criminal investigation).",
        "emergency_fallback": "Call National Cyber Financial Fraud / Crime Helpline at 1930."
    },
    "STALKING": {
        "portal_name": "National Commission for Women & State Police Portal",
        "portal_url": "https://ncwapps.nic.in/onlinecomplaintsv2/",
        "authority_code": "NCW",
        "description": "For persistent physical or digital stalking where immediate police FIR assistance is required.",
        "requirements": "Preserve location, vehicle details, screenshots, and witness contacts.",
        "emergency_fallback": "Call 112 immediately if the perpetrator is currently following you."
    },
    "SEXUAL_HARASSMENT": {
        "portal_name": "National Commission for Women (NCW)",
        "portal_url": "https://ncwapps.nic.in/onlinecomplaintsv2/",
        "authority_code": "NCW",
        "description": "NCW takes cognizance of sexual harassment incidents and coordinates with law enforcement.",
        "requirements": "Provide time, location, and identifiable descriptions.",
        "emergency_fallback": "Call 112 or 1091."
    },
    "CHILD_PROTECTION": {
        "portal_name": "Ministry of Women and Child Development / Childline 1098",
        "portal_url": "https://www.wcd.gov.in/",
        "authority_code": "WCD_CHILD",
        "description": "Child rights protection, POCSO reporting, and Child Welfare Committees.",
        "requirements": "Cases involving minors are treated with strict identity confidentiality under POCSO.",
        "emergency_fallback": "Call 1098 (24x7 toll-free Childline) immediately."
    },
    "PROPERTY_RIGHTS": {
        "portal_name": "NALSA Free Legal Services Authority",
        "portal_url": "https://nalsa.gov.in/womens-assistance/",
        "authority_code": "NALSA",
        "description": "Free legal aid, advocate appointment, and civil court counseling for inheritance and property denial.",
        "requirements": "Available to all women without court fee burdens.",
        "emergency_fallback": "Call National Legal Helpline 15100."
    },
    "OTHER": {
        "portal_name": "National Commission for Women (NCW)",
        "portal_url": "https://ncwapps.nic.in/onlinecomplaintsv2/",
        "authority_code": "NCW",
        "description": "Statutory body addressing violations of women's constitutional and civil safeguards.",
        "requirements": "Citizen registration on official portal.",
        "emergency_fallback": "Call 112 in emergency."
    }
}


def get_routing_for_category(category: str) -> dict:
    """Return routing instructions and official URL for a given category."""
    return OFFICIAL_AUTHORITY_MAPPINGS.get(category, OFFICIAL_AUTHORITY_MAPPINGS["OTHER"])
