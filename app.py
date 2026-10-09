import os
from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFProtect
from config import config_by_name
from models import db, User, UserProfile

csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory for SheShield."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Ensure instance and upload directories exist
    upload_folder = app.config.get("UPLOAD_FOLDER")
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.sos import sos_bp
    from routes.safety_map import safety_map_bp
    from routes.legal import legal_bp
    from routes.complaints import complaints_bp
    from routes.awareness import awareness_bp
    from routes.profile import profile_bp
    from routes.admin import admin_bp
    from routes.lite import lite_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(sos_bp)
    from routes.sos import upload_evidence
    csrf.exempt(upload_evidence)
    app.register_blueprint(safety_map_bp)
    from routes.safety_map import api_routes
    csrf.exempt(api_routes)
    app.register_blueprint(legal_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(awareness_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(lite_bp)

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy (permits Leaflet tiles, fonts, and inline styles)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://*.tile.openstreetmap.org https://unpkg.com; "
            "connect-src 'self';"
        )
        return response

    # Health Check API
    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "app": "SheShield",
            "version": "1.0.0",
            "environment": app.config.get("ENV", "development")
        }), 200

    # Custom Error Handlers
    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        if request.is_json:
            return jsonify({"error": "Bad Request", "message": "CSRF token missing or expired"}), 400
        from flask import flash, redirect
        flash("Your session security token expired or page was refreshed. Please submit again.", "warning")
        return redirect(request.referrer or request.url or url_for("main.index"))

    @app.errorhandler(400)
    def bad_request_error(error):
        if request.is_json:
            return jsonify({"error": "Bad Request", "message": str(error)}), 400
        return render_template("errors/400.html", error=error), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.is_json:
            return jsonify({"error": "Forbidden", "message": "Access denied"}), 403
        return render_template("errors/403.html", error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_json:
            return jsonify({"error": "Not Found", "message": "The requested resource was not found"}), 404
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.is_json:
            return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500
        return render_template("errors/500.html", error=error), 500

    # CLI Commands
    import click

    @app.cli.command("init-db")
    def init_db():
        """Initialize database tables."""
        db.create_all()
        click.echo("Database initialized successfully.")

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("password")
    def create_admin(username, password):
        """Create or promote an administrator account securely."""
        db.create_all()
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_admin = True
            user.set_password(password)
            click.echo(f"Existing user '{username}' promoted to Administrator.")
        else:
            user = User(username=username, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            click.echo(f"Administrator account '{username}' created successfully.")
        db.session.commit()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
