from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, SelectField,
    TextAreaField, FloatField, FileField
)
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Email, ValidationError
import re


def validate_indian_phone(form, field):
    """Validate 10-digit Indian phone number format if provided."""
    if field.data:
        cleaned = re.sub(r'[\s\-+]', '', field.data)
        if cleaned.startswith('91') and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if not (len(cleaned) == 10 and cleaned.isdigit()):
            raise ValidationError("Please enter a valid 10-digit mobile number.")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username / उपयोगकर्ता नाम",
        validators=[
            DataRequired(message="Username is required"),
            Length(min=3, max=40, message="Username must be between 3 and 40 characters")
        ]
    )
    email = StringField(
        "Email (Optional) / ईमेल (वैकल्पिक)",
        validators=[Optional(), Email(message="Please provide a valid email address"), Length(max=120)]
    )
    phone_number = StringField(
        "Mobile Number (Optional) / मोबाइल नंबर",
        validators=[Optional(), validate_indian_phone]
    )
    password = PasswordField(
        "Password / पासवर्ड",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=8, max=100, message="Password must be at least 8 characters long")
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password / पासवर्ड की पुष्टि करें",
        validators=[
            DataRequired(message="Please confirm your password"),
            EqualTo("password", message="Passwords must match")
        ]
    )
    submit = SubmitField("Create Account / खाता बनाएं")


class LoginForm(FlaskForm):
    username = StringField(
        "Username / उपयोगकर्ता नाम",
        validators=[DataRequired(message="Username is required")]
    )
    password = PasswordField(
        "Password / पासवर्ड",
        validators=[DataRequired(message="Password is required")]
    )
    submit = SubmitField("Sign In / प्रवेश करें")


class UserProfileForm(FlaskForm):
    full_name = StringField("Full Name / पूरा नाम", validators=[Optional(), Length(max=120)])
    preferred_language = SelectField(
        "Preferred Language / पसंदीदा भाषा",
        choices=[("en", "English"), ("hi", "हिंदी (Hindi)")],
        default="en"
    )
    blood_group = SelectField(
        "Blood Group / रक्त समूह",
        choices=[
            ("", "Select Blood Group (Optional)"),
            ("A+", "A+"), ("A-", "A-"),
            ("B+", "B+"), ("B-", "B-"),
            ("O+", "O+"), ("O-", "O-"),
            ("AB+", "AB+"), ("AB-", "AB-")
        ],
        validators=[Optional()]
    )
    emergency_notes = TextAreaField(
        "Emergency Medical / Personal Notes (Optional) / आपातकालीन नोट्स",
        validators=[Optional(), Length(max=500)]
    )
    state = StringField("State / राज्य", validators=[Optional(), Length(max=80)])
    district = StringField("District / जिला", validators=[Optional(), Length(max=80)])
    consent_share_location = BooleanField(
        "Allow location sharing with trusted contacts during active SOS",
        default=True
    )
    consent_emergency_sms = BooleanField(
        "Send automatic SMS alerts to trusted contacts upon SOS",
        default=True
    )
    submit = SubmitField("Update Profile / प्रोफाइल सहेजें")


class TrustedContactForm(FlaskForm):
    name = StringField(
        "Contact Name / संपर्क का नाम",
        validators=[DataRequired(message="Contact name is required"), Length(min=2, max=100)]
    )
    phone_number = StringField(
        "Mobile Number / मोबाइल नंबर (10 Digits)",
        validators=[DataRequired(message="Phone number is required"), validate_indian_phone]
    )
    relationship = SelectField(
        "Relationship / संबंध",
        choices=[
            ("Parent", "Parent / माता-पिता"),
            ("Spouse", "Spouse / जीवनसाथी"),
            ("Sibling", "Sibling / भाई-बहन"),
            ("Friend", "Friend / मित्र"),
            ("Colleague", "Colleague / सहकर्मी"),
            ("Guardian", "Guardian / अभिभावक"),
            ("Other", "Other / अन्य")
        ],
        default="Parent"
    )
    is_primary = BooleanField("Set as Primary Emergency Contact / प्राथमिक संपर्क बनाएं", default=False)
    notify_sms = BooleanField("Send SMS notifications during emergency / आपातकाल में SMS भेजें", default=True)
    submit = SubmitField("Save Contact / संपर्क जोड़ें")


class UnsafeAreaReportForm(FlaskForm):
    title = StringField(
        "Issue Summary / समस्या शीर्षक",
        validators=[DataRequired(message="Title is required"), Length(min=5, max=150)]
    )
    category = SelectField(
        "Category / श्रेणी",
        choices=[
            ("POOR_LIGHTING", "Poor Street Lighting / खराब स्ट्रीट लाइट"),
            ("ISOLATED_AREA", "Isolated / Desolate Stretch / सुनसान क्षेत्र"),
            ("HARASSMENT_PRONE", "Harassment / Eve-Teasing Concern / छेड़छाड़ प्रवण क्षेत्र"),
            ("ROAD_HAZARD", "Broken Road / Blocked Pathway / सड़क बाधा"),
            ("OTHER", "Other Safety Concern / अन्य सुरक्षा चिंता")
        ],
        default="POOR_LIGHTING"
    )
    description = TextAreaField(
        "Detailed Description / विस्तृत विवरण",
        validators=[DataRequired(message="Description is required"), Length(min=10, max=1000)]
    )
    latitude = FloatField("Latitude", validators=[DataRequired(message="Latitude is required")])
    longitude = FloatField("Longitude", validators=[DataRequired(message="Longitude is required")])
    address = StringField("Location / Landmark Address", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Submit Safety Report / रिपोर्ट दर्ज करें")


class ComplaintDraftForm(FlaskForm):
    full_name = StringField("Full Name / पूरा नाम", validators=[Optional(), Length(max=120)])
    age_group = SelectField(
        "Age Group / आयु वर्ग",
        choices=[
            ("", "Select Age Group"),
            ("Under 18", "Under 18 (Minor / नाबालिग)"),
            ("18-24", "18 - 24 years"),
            ("25-34", "25 - 34 years"),
            ("35-49", "35 - 49 years"),
            ("50+", "50 years and above")
        ],
        validators=[Optional()]
    )
    phone_number = StringField("Contact Number (Optional) / फोन नंबर", validators=[Optional(), validate_indian_phone])
    email = StringField("Email Address (Optional) / ईमेल", validators=[Optional(), Email()])
    preferred_language = SelectField(
        "Preferred Language for Draft / मसौदे की भाषा",
        choices=[("en", "English"), ("hi", "हिंदी (Hindi)")],
        default="en"
    )
    category = SelectField(
        "Complaint Category / शिकायत की श्रेणी",
        choices=[
            ("DOMESTIC_VIOLENCE", "Domestic Violence / घरेलू हिंसा"),
            ("DOWRY_HARASSMENT", "Dowry Harassment / दहेज उत्पीड़न"),
            ("WORKPLACE_POSH", "Workplace Sexual Harassment (POSH) / कार्यस्थल पर यौन उत्पीड़न"),
            ("CYBERCRIME", "Cyber Harassment / Online Blackmail / साइबर अपराध"),
            ("STALKING", "Stalking / पीछा करना"),
            ("SEXUAL_HARASSMENT", "Sexual Harassment in Public / छेड़छाड़"),
            ("CHILD_PROTECTION", "Child Protection / बाल उत्पीड़न"),
            ("PROPERTY_RIGHTS", "Property & Inheritance Denial / संपत्ति अधिकार"),
            ("OTHER", "Other Rights Issue / अन्य महिला अधिकार मुद्दा")
        ],
        validators=[DataRequired()]
    )
    incident_date = StringField("Date / Approx Period of Incident / घटना की तारीख", validators=[Optional(), Length(max=50)])
    state = StringField("State / राज्य", validators=[Optional(), Length(max=80)])
    district = StringField("District / जिला", validators=[Optional(), Length(max=80)])
    incident_location = StringField("Location of Incident (Optional) / घटना स्थल", validators=[Optional(), Length(max=255)])
    person_involved = StringField("Person(s) / Organization Involved (Optional) / संबंधित व्यक्ति या संस्था", validators=[Optional(), Length(max=255)])
    incident_description = TextAreaField(
        "Description of Incident / घटना का विवरण",
        validators=[
            DataRequired(message="Incident description is required so the draft has meaningful context."),
            Length(min=20, max=4000, message="Description should be at least 20 characters.")
        ]
    )
    is_ongoing = BooleanField("Is this incident or harassment currently ongoing? / क्या यह उत्पीड़न अभी भी जारी है?")
    requested_assistance = TextAreaField(
        "Assistance Requested / चाही गई सहायता (e.g., Protection order, investigation, removal of online content)",
        validators=[Optional(), Length(max=1000)]
    )
    supporting_doc = FileField("Supporting Evidence / Document (PDF, Image, Max 5MB) (Optional)")
    consent_acknowledgement = BooleanField(
        "I understand SheShield generates this draft for my personal use. This does not automatically register an official police or government FIR.",
        validators=[DataRequired(message="You must acknowledge the legal draft disclaimer.")]
    )
    submit = SubmitField("Generate Structured Draft / शिकायत मसौदा तैयार करें")


class LegalResourceForm(FlaskForm):
    category = SelectField(
        "Category",
        choices=[
            ("CONSTITUTIONAL", "Constitutional & Equality Rights"),
            ("DOMESTIC_VIOLENCE", "Domestic Violence & Family"),
            ("WORKPLACE", "Workplace Rights (POSH)"),
            ("SEXUAL_OFFENCES", "Sexual Offences & Harassment"),
            ("CYBER_SAFETY", "Cyber Safety & Online Crimes"),
            ("CHILD_PROTECTION", "Education & Child Protection"),
            ("PROPERTY", "Property & Financial Rights"),
            ("FREE_LEGAL_AID", "Free Legal Aid & Government Schemes")
        ]
    )
    title_en = StringField("Title (English)", validators=[DataRequired(), Length(max=200)])
    title_hi = StringField("Title (Hindi)", validators=[DataRequired(), Length(max=200)])
    summary_en = TextAreaField("Summary (English)", validators=[DataRequired(), Length(max=1000)])
    summary_hi = TextAreaField("Summary (Hindi)", validators=[DataRequired(), Length(max=1000)])
    details_en = TextAreaField("Detailed Explanation (English)", validators=[Optional()])
    details_hi = TextAreaField("Detailed Explanation (Hindi)", validators=[Optional()])
    legal_sections = StringField("Applicable Acts / Sections", validators=[Optional(), Length(max=255)])
    applicability = StringField("Applicability / Who is covered", validators=[Optional(), Length(max=255)])
    action_steps_en = TextAreaField("Action Steps (English)", validators=[Optional()])
    action_steps_hi = TextAreaField("Action Steps (Hindi)", validators=[Optional()])
    source_url = StringField("Official Source Link", validators=[Optional(), Length(max=255)])
    is_published = BooleanField("Published", default=True)
    submit = SubmitField("Save Legal Resource")


class AwarenessArticleForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    category = SelectField(
        "Category",
        choices=[
            ("PERSONAL_SAFETY", "Personal Safety Guidance"),
            ("CYBER_SAFETY", "Cyber Safety & Digital Hygiene"),
            ("GOVT_SCHEMES", "Government Schemes & Welfare"),
            ("COMMUNITY_ANNOUNCEMENT", "Community Safety Announcements")
        ]
    )
    summary = TextAreaField("Summary", validators=[DataRequired(), Length(max=500)])
    content = TextAreaField("Article Content", validators=[DataRequired()])
    source_url = StringField("Official Reference Link", validators=[Optional(), Length(max=255)])
    is_published = BooleanField("Published", default=True)
    submit = SubmitField("Save Article")


class SelfHelpGroupForm(FlaskForm):
    name = StringField("Group Name", validators=[DataRequired(), Length(max=150)])
    initiative_type = StringField("Initiative Type", validators=[DataRequired(), Length(max=100)])
    state = StringField("State", validators=[DataRequired(), Length(max=80)])
    district = StringField("District", validators=[DataRequired(), Length(max=80)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=1000)])
    public_contact = StringField("Public Authorized Contact", validators=[Optional(), Length(max=150)])
    is_verified = BooleanField("Verified", default=True)
    submit = SubmitField("Save Self-Help Group")
