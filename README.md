# SheShield (शीशील्ड) 🛡️
### Full-Stack Women's Safety, Legal Rights & Emergency Support Platform (India)

SheShield ek privacy-focused, accessible aur full-stack web platform hai jo India mein women aur girls ke liye banaya gaya hai. Yeh application emergency safety assistance, bilingual legal awareness (हिंदी व English), guided complaint drafting, official government portal routing, aur community hazard mapping provide karta hai.

> 📖 **Comprehensive Technical & Architecture Docs:** Detailed database schemas, API specs, and workflow diagrams are documented in [DOCUMENTATION.md](file:///e:/shild/DOCUMENTATION.md).

---

## 🌟 Key Features (मुख्य विशेषताएं)

1. **🚨 Emergency SOS, Evidence Capture & Trusted Contacts:**
   - One-touch emergency trigger explicit consent ke sath.
   - **📸 Automatic Camera Snapshot:** Background emergency camera snapshot capture aur encrypted storage (`EmergencyEvidence`).
   - **🎙️ 8-Second Ambient Voice Recording:** Aas-pass ka voice/ambient audio recording MediaRecorder API ke through automatic capture aur upload.
   - **🛡️ Evidence Vault:** In-browser audio player aur photo gallery with tap-to-expand and download capabilities.
   - **📱 Trusted Contact Live Portal (`/sos/track/<token>`):** Unguessable 32-character capability token link through which family/police can view live GPS and listen to audio evidence without login.
   - **📨 Carrier SMS Integration:** Real Twilio SMS delivery (+91 E.164 normalization) with automatic fallback to safe local Mock mode.
   - GPS coordinate capture aur dynamic breadcrumb updates.
   - Pre-configured trusted contacts management (Primary contact, SMS notification preferences).
   - Emergency resolution & false alarm cancellation flow.
   - Direct helpline shortcuts: **112 (National Emergency), 1091 (Women Helpline), 181 (Women in Distress), 1098 (Childline), 1930 (Cyber Fraud)**.

2. **⚖️ Bilingual Legal Rights Library (कानूनी अधिकार):**
   - Verified statutory protections across 8 major categories (Constitutional, Domestic Violence PWDVA, Workplace POSH, Sexual Offences, Cyber Safety, Child Protection POCSO, Property Rights, Free Legal Aid NALSA).
   - Full bilingual support: Simple English and सरल हिंदी parallel explanations.
   - Search filter by keyword and category chips.
   - Direct links to official statutory authority sources.

3. **✍️ Guided Complaint Draft Assistant (शिकायत मसौदा):**
   - 7-step complaint structuring wizard.
   - Sensitive details optional (complainant safety first).
   - Structured document generation with factual narratives without fabricating facts.
   - Direct editing of the generated draft.
   - Instant download as plain text (**TXT**) and formatted **PDF** (via ReportLab).
   - Category-based routing to verified official government portals (**NCW, SHe-Box, Cybercrime.gov.in, NALSA**).
   - Honest submission status: *Draft Saved*, *Ready for Portal*, *External Portal Opened*.

4. **🗺️ Community Safety Map & Routes:**
   - Interactive Leaflet map powered by OpenStreetMap tiles.
   - Drop pins to report infrastructural hazards (poor lighting, isolated roads).
   - Mandatory administrative moderation queue before community reports go public.
   - Geolocation detection & route destination inputs.
   - Honest disclaimer: Maps provide environmental awareness, not guarantee of absolute personal safety.

5. **🤝 Awareness & Self-Help Group (EARN) Directory:**
   - Educational awareness articles (Zero FIR, preserving digital cyber evidence, government schemes).
   - Lightweight, non-commercial directory of women-led Self-Help Groups (SHGs).
   - *Strictly no e-commerce, no shopping carts, no payments.*

6. **📱 Feature-Phone & Low Bandwidth Interface (`/lite`):**
   - Ultra-fast, low-data interface designed for 2G/3G mobile browsers and basic feature phones.
   - Three pillars: **PROTECT** (Call 112, trusted contacts), **KNOW** (Legal basics), **EARN** (SHG directory).
   - Explicit instructions for keypad phones without GPS/Internet.

7. **🛡️ Protected Administrative Dashboard (`/admin/`):**
   - Moderate community safety hazard reports (Approve / Reject).
   - Manage and update legal resources and source URLs.
   - Publish awareness articles.
   - Aggregated platform statistics (no exposure of sensitive private complaint narratives or live locations).
   - Cryptographic administrative audit trail (`AdminAuditLog`).

---

## 🛠️ Technology Stack (तकनीकी स्टैक)

- **Backend:** Python 3.10+ / 3.13, Flask 3.1, Flask Blueprints, Flask-WTF, WTForms.
- **Database:** SQLAlchemy ORM, SQLite (local development), PostgreSQL ready for production.
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Custom Design System with Deep Navy, Purple, Teal, and SOS Red), Vanilla JavaScript (ES6+), Jinja2 Templates.
- **Maps:** Leaflet JS + OpenStreetMap Tile Layer.
- **PDF Engine:** ReportLab for structured legal document export.
- **Testing:** pytest, Flask Test Client.
- **Security:** CSRF Protection, Password Hashing (Werkzeug Scrypt/PBKDF2), HTTPOnly Lax Cookies, Security Response Headers (CSP, X-Frame-Options, X-Content-Type-Options).

---

## 📂 Project Structure (प्रोजेक्ट डायरेक्टरी)

```text
e:/shild/
├── app.py                     # Application factory, CLI commands, security headers
├── config.py                  # Dev, Test, Prod configuration profiles
├── forms.py                   # Flask-WTF validated form definitions
├── requirements.txt           # Python application dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Version control exclusions
├── models/                    # SQLAlchemy database models
│   ├── __init__.py            # DB instance and model exports
│   ├── user.py                # User, UserProfile
│   ├── safety.py              # TrustedContact, SOSEvent, LocationUpdate, UnsafeAreaReport, NotificationAttempt
│   ├── complaint.py           # ComplaintDraft
│   └── resources.py           # LegalResource, AwarenessArticle, SelfHelpGroup, AdminAuditLog
├── routes/                    # Modular Flask Blueprints
│   ├── main.py                # Landing page & health check
│   ├── auth.py                # Registration, login with rate-limiting, logout
│   ├── dashboard.py           # Authenticated user dashboard
│   ├── sos.py                 # Emergency SOS triggers, breadcrumbs, status, contacts
│   ├── safety_map.py          # Leaflet map & community reports API
│   ├── legal.py               # Bilingual legal rights library
│   ├── complaints.py          # Draft creation, edit, TXT/PDF export, portal routing
│   ├── awareness.py           # Educational guides & SHG directory
│   ├── profile.py             # User profile & privacy consent settings
│   ├── admin.py               # Protected admin control center & audit logs
│   └── lite.py                # Lightweight /lite 2G interface
├── services/                  # Business logic & integrations
│   ├── auth_utils.py          # @login_required, @admin_required, rate-limiting
│   ├── notifications.py       # Notification abstraction & safe mock provider
│   ├── complaint_generator.py # Structured legal draft compiler
│   ├── complaint_routing.py   # Category-to-official portal routing
│   └── pdf_generator.py       # ReportLab PDF compilation
├── static/
│   ├── css/main.css           # Complete accessible design system
│   └── js/main.js             # Mobile nav, ESC quick exit, CSRF helpers
├── templates/                 # Accessible Jinja2 HTML templates
│   ├── base.html              # Layout, helplines ribbon, quick exit, accessibility
│   ├── index.html             # Landing page
│   ├── auth/                  # Login & registration views
│   ├── dashboard/             # User safety center
│   ├── sos/                   # SOS hub, tracking, contacts, history
│   ├── safety_map/            # Map and hazard submission
│   ├── legal/                 # Legal library list and detail views
│   ├── complaints/            # Draft wizard, preview, edit, portal guide
│   ├── awareness/             # Articles & SHG directory
│   ├── profile/               # Profile & consent preferences
│   ├── admin/                 # Admin panel, moderation queue, audit logs
│   ├── lite/                  # Low-data /lite interface
│   └── errors/                # 400, 403, 404, 500 error templates
└── tests/                     # Comprehensive pytest test suite
    ├── test_phase1_foundation.py
    ├── test_auth.py
    ├── test_ownership_and_security.py
    ├── test_complaints.py
    ├── test_sos.py
    └── test_resources_and_lite.py
```

---

## 🚀 Local Setup & Installation (लोकल सेटअप कैसे करें)

### Step 1: Prerequisites
- Python 3.10 or higher installed (`python --version`).
- Git and Windows PowerShell / Terminal.

### Step 2: Create and Activate Virtual Environment
```powershell
# Navigate to the project directory
cd e:\shild

# Create a virtual environment
python -m venv .venv

# Activate in Windows PowerShell
.venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
*(Default settings automatically use SQLite and MOCK SMS mode, which works out of the box without any external API keys).*

### Step 5: Initialize Database & Create Administrator
Initialize the SQLite database and create a secure admin account:
```powershell
# Initialize tables
.venv\Scripts\flask.exe --app app init-db

# Create an administrator account (Username & Password)
.venv\Scripts\flask.exe --app app create-admin admin MySecureAdminPass123!
```

### Step 6: Start the Development Server
```powershell
python app.py
```
Open your browser and navigate to:
👉 **http://127.0.0.1:5000**

---

## 🧪 Running Automated Tests (परीक्षण कैसे चलाएं)

SheShield comes with a complete, automated test suite covering authentication, backend data ownership isolation, complaint lifecycle, PDF/TXT exports, mock emergency notifications, and admin moderation:

```powershell
.venv\Scripts\pytest.exe -v
```
All 13 test suites execute and validate:
- **`test_auth.py`**: User registration, duplicate username rejection, password verification, session logout.
- **`test_ownership_and_security.py`**: Strict validation that User B cannot read, edit, or delete User A's private drafts or emergency events; ordinary users cannot access `/admin/`.
- **`test_complaints.py`**: Full drafting workflow, validation error handling, ReportLab PDF generation, TXT export, and portal routing.
- **`test_sos.py`**: SOS event triggering, GPS breadcrumb tracking, mock SMS delivery log verification, and event resolution.
- **`test_resources_and_lite.py`**: Hazard report submission, admin moderation approval, legal rights bilingual search, and `/lite` feature-phone rendering.

---

## ⚙️ Configuration & Third-Party Integrations (इंटीग्रेशन गाइड)

### 1. SMS Notification Service
By default, `SMS_PROVIDER=mock` is set in configuration. When SOS is triggered, alerts are safely logged into the database and application log without making telecommunication network calls.

To enable real SMS in production:
1. Obtain an authorized Twilio account SID, Auth Token, and sender phone number.
2. In `.env`:
   ```env
   SMS_PROVIDER=twilio
   TWILIO_ACCOUNT_SID=your_actual_sid
   TWILIO_AUTH_TOKEN=your_actual_token
   TWILIO_FROM_NUMBER=+1234567890
   ```
3. If credentials are missing, SheShield automatically logs a graceful `FAILED` status and directs the user to dial 112 directly.

### 2. Interactive Map & Routing
SheShield uses standard **OpenStreetMap (OSM)** tiles via Leaflet without requiring commercial API keys or payment tokens. 

---

## 🔒 Security & Privacy Architecture (सुरक्षा और गोपनीयता)

- **Zero Fabricated Government Claims:** SheShield clearly identifies as an educational and assistance platform. It never fakes police dispatch or automated FIR registrations.
- **Explicit Consent:** Location is captured only after the user checks explicit consent on the confirmation modal.
- **Backend Ownership Enforcement:** Every private database operation (viewing drafts, deleting contacts, downloading documents) authoritatively checks `session['user_id'] == resource.user_id` on the server.
- **Data Minimization:** Complainant names, phone numbers, and exact locations are strictly optional during complaint preparation.
- **Emergency Quick Exit:** Pressing the top Quick Exit button or pressing **ESC 3 times** immediately redirects the browser to Google and clears history state.

---

## 📄 License & Disclaimer
SheShield is provided for informational and emergency educational purposes. For immediate physical threats or emergencies, users must always contact official state authorities by dialing **112**.

