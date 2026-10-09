import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file with override
load_dotenv(BASE_DIR / ".env", override=True)


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "sheshield-dev-secret-key-2026-unsecure-change-in-prod")
    
    # Database configuration (Neon PostgreSQL or local SQLite fallback)
    _db_url = os.environ.get("DATABASE_URL")
    if not _db_url:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'sheshield.db'}"
    else:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    
    # Session & Security Cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # True in Production over HTTPS
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour token expiration
    
    # Upload limits (5MB max upload to prevent DoS)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = BASE_DIR / "instance" / "uploads"
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "txt"}
    
    # Notification & External service settings
    SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "mock")  # 'mock', 'twilio', 'fast2sms'
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", os.environ.get("TWILIO_PHONE_NUMBER", ""))
    TWILIO_PHONE_NUMBER = TWILIO_FROM_NUMBER


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    ENV = "development"


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False  # Simplify automated client tests while test_security checks CSRF explicitly
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SMS_PROVIDER = "mock"


class ProductionConfig(Config):
    """Production environment configuration with hardened security settings."""
    DEBUG = False
    ENV = "production"
    SESSION_COOKIE_SECURE = True  # Enforce HTTPS
    PREFERRED_URL_SCHEME = "https"


# Map environment names to config classes
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
