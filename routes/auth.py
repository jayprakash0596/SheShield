from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User, UserProfile
from forms import RegistrationForm, LoginForm
from services.auth_utils import check_rate_limit, clear_rate_limit

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User account registration."""
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        existing_user = User.query.filter_by(username=form.username.data.strip()).first()
        if existing_user:
            flash("Username already exists. Please choose a different username. / यह उपयोगकर्ता नाम पहले से मौजूद है।", "danger")
            return render_template("auth/register.html", form=form)

        # Check if optional email already exists
        if form.email.data:
            existing_email = User.query.filter_by(email=form.email.data.strip().lower()).first()
            if existing_email:
                flash("Email already registered. / यह ईमेल पहले से पंजीकृत है।", "danger")
                return render_template("auth/register.html", form=form)

        # Create new user
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower() if form.email.data else None,
            phone_number=form.phone_number.data.strip() if form.phone_number.data else None,
            is_admin=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # Get user.id for profile

        # Create user profile
        profile = UserProfile(
            user_id=user.id,
            preferred_language="en",
            consent_share_location=True,
            consent_emergency_sms=True
        )
        db.session.add(profile)
        db.session.commit()

        flash("Account created successfully! Please sign in to continue. / खाता सफलतापूर्वक बनाया गया! कृपया लॉगिन करें।", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User authentication with rate limiting and secure session."""
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        client_ip = request.remote_addr or "127.0.0.1"
        rate_key = f"login:{client_ip}:{form.username.data.strip()}"

        # Rate limiting check (max 10 attempts in 5 minutes)
        if not check_rate_limit(rate_key, max_attempts=10, window_seconds=300):
            flash("Too many failed login attempts. Please wait 5 minutes before trying again. / अत्यधिक विफल प्रयास। कृपया 5 मिनट बाद पुनः प्रयास करें।", "danger")
            return render_template("auth/login.html", form=form), 429

        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("This account has been deactivated. Please contact support.", "danger")
                return render_template("auth/login.html", form=form), 403

            # Reset rate limiter
            clear_rate_limit(rate_key)

            # Establish session
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin

            flash(f"Welcome back, {user.username}! / वापस स्वागत है!", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("dashboard.index"))
        else:
            flash("Invalid username or password. / अमान्य उपयोगकर्ता नाम या पासवर्ड।", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    """Terminate user session securely."""
    session.clear()
    flash("You have been signed out safely. / आप सुरक्षित रूप से लॉग आउट हो गए हैं।", "info")
    return redirect(url_for("main.index"))
