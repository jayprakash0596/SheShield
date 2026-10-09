from datetime import datetime


def generate_structured_complaint(data: dict) -> str:
    """
    Generates a structured, formal complaint draft based strictly on user-provided facts.
    Does not invent facts, sections, or allegations.
    """
    category = data.get("category", "OTHER")
    lang = data.get("preferred_language", "en")
    
    # Map category to intended official authority recipient
    recipient_mapping = {
        "DOMESTIC_VIOLENCE": "To: The Protection Officer / Magistrate\nUnder the Protection of Women from Domestic Violence Act, 2005",
        "DOWRY_HARASSMENT": "To: The Station House Officer (SHO) / Superintendent of Police\nWomen Safety & Crime Against Women Cell",
        "WORKPLACE_POSH": "To: The Presiding Officer, Internal Committee (IC) / Local Committee (LC)\nUnder Sexual Harassment of Women at Workplace Act, 2013",
        "CYBERCRIME": "To: The Cyber Crime Cell / National Cyber Crime Reporting Portal (cybercrime.gov.in)",
        "STALKING": "To: The Station House Officer (SHO) / Police Station In-Charge",
        "SEXUAL_HARASSMENT": "To: The Station House Officer (SHO) / Women Police Desk",
        "CHILD_PROTECTION": "To: The Child Welfare Committee (CWC) / Special Juvenile Police Unit",
        "PROPERTY_RIGHTS": "To: The District Legal Services Authority (DLSA) / Competent Civil Authority",
        "OTHER": "To: The Competent Authority / Women Grievance Cell"
    }

    recipient_text = recipient_mapping.get(category, recipient_mapping["OTHER"])
    
    ref_code = data.get("reference_code", "SH-CMP-DRAFT")
    full_name = data.get("full_name") or "[Name Withheld / Not Disclosed]"
    age_group = data.get("age_group") or "[Age Group Not Specified]"
    phone = data.get("phone_number") or "[Contact Number Not Specified]"
    email = data.get("email") or "[Email Not Specified]"
    
    state = data.get("state") or "[State Not Specified]"
    district = data.get("district") or "[District Not Specified]"
    location = data.get("incident_location") or "[Specific Location Withheld for Safety]"
    incident_date = data.get("incident_date") or "[Date / Timeline to be verified]"
    persons_involved = data.get("person_involved") or "[Details not specified in this draft]"
    description = data.get("incident_description") or ""
    is_ongoing = "YES — Continuing concern" if data.get("is_ongoing") else "NO — Past incident"
    requested_assistance = data.get("requested_assistance") or "Immediate inquiry, protection order, and necessary statutory relief as per applicable law."
    attachment_name = data.get("attachment_original_name") or "None attached"

    draft_date = datetime.utcnow().strftime("%d %B %Y")

    if lang == "hi":
        draft = f"""संदर्भ कोड: {ref_code}
दिनांक: {draft_date}

प्रेषित:
{recipient_text}

विषय: {category.replace('_', ' ')} के संबंध में औपचारिक शिकायत मसौदा।

महोदय / महोदया,

मैं सादर निवेदन करती हूँ कि अधोहस्ताक्षरी द्वारा निम्नानुसार विवरण प्रस्तुत किया जा रहा है:

1. शिकायतकर्ता का विवरण:
   - नाम: {full_name}
   - आयु वर्ग: {age_group}
   - संपर्क नंबर: {phone}
   - ईमेल: {email}
   - जिला व राज्य: {district}, {state}

2. घटना का विवरण एवं समय:
   - घटना की तारीख / अवधि: {incident_date}
   - घटना का स्थान: {location}
   - संलिप्त व्यक्ति / संस्था: {persons_involved}
   - क्या उत्पीड़न वर्तमान में भी जारी है?: {is_ongoing}

3. घटना का वास्तविक वृत्तांत:
{description}

4. चाही गई सहायता व कानूनी उपचार:
{requested_assistance}

5. संलग्न साक्ष्य / दस्तावेज:
{attachment_name}

घोषणा:
उपरोक्त विवरण मेरे सर्वोत्तम ज्ञान और विश्वास के अनुसार सत्य है। यह दस्तावेज शीशील्ड (SheShield) सहायता मंच पर निजी रिकॉर्ड एवं आधिकारिक पोर्टल पर प्रस्तुति हेतु तैयार किया गया है।

हस्ताक्षर / आवेदक:
{full_name}
"""
    else:
        draft = f"""Reference ID: {ref_code}
Date: {draft_date}

{recipient_text}

SUBJECT: Formal Complaint regarding {category.replace('_', ' ').title()}.

Respected Authority,

I am submitting the following statement of facts for your immediate consideration and appropriate legal action:

1. COMPLAINANT PARTICULARS:
   - Name: {full_name}
   - Age Group: {age_group}
   - Contact Number: {phone}
   - Email: {email}
   - Jurisdiction: {district}, {state}

2. INCIDENT PARTICULARS:
   - Date / Timeline of Incident: {incident_date}
   - Location of Occurrence: {location}
   - Person(s) / Organisation Involved: {persons_involved}
   - Status: {is_ongoing}

3. STATEMENT OF FACTS & INCIDENT NARRATIVE:
{description}

4. RELIEF & ASSISTANCE REQUESTED:
{requested_assistance}

5. SUPPORTING EVIDENCE / ATTACHMENTS:
{attachment_name}

VERIFICATION:
I state that the facts stated above are true to the best of my knowledge and belief. This draft has been prepared privately on SheShield for personal submission to the appropriate statutory authority.

Sincerely,

{full_name}
"""
    return draft
