import time
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort

# Simple in-memory rate limiting for login attempts by IP/username
_login_attempts = {}


def login_required(f):
    """Decorator to enforce authenticated session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access this page. / कृपया आगे बढ़ने के लिए लॉग इन करें।", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to enforce administrative privileges on backend."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Administrator login required.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if not session.get("is_admin"):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def check_rate_limit(key: str, max_attempts: int = 10, window_seconds: int = 300) -> bool:
    """
    Check if an identifier (IP or username) has exceeded max attempts within the time window.
    Returns True if allowed, False if rate limited.
    """
    now = time.time()
    attempts = _login_attempts.get(key, [])
    # Filter attempts within current sliding window
    attempts = [t for t in attempts if now - t < window_seconds]
    if len(attempts) >= max_attempts:
        _login_attempts[key] = attempts
        return False
    attempts.append(now)
    _login_attempts[key] = attempts
    return True


def clear_rate_limit(key: str):
    """Clear rate limiting history on successful authentication."""
    if key in _login_attempts:
        del _login_attempts[key]
