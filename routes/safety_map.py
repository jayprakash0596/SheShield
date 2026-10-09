from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from models import db, UnsafeAreaReport
from forms import UnsafeAreaReportForm
from services.routing_service import geocode_location, calculate_best_and_safe_routes
from app import csrf

safety_map_bp = Blueprint("safety_map", __name__, url_prefix="/map")


@safety_map_bp.route("/")
def index():
    """Interactive Community Safety Map using Leaflet & OpenStreetMap."""
    form = UnsafeAreaReportForm()
    # Default center: New Delhi / India geographic center
    default_lat = 28.6139
    default_lng = 77.2090
    return render_template(
        "safety_map/index.html",
        form=form,
        default_lat=default_lat,
        default_lng=default_lng
    )


@safety_map_bp.route("/api/reports")
def api_reports():
    """
    Returns verified/approved safety reports for map rendering.
    Filters out private personally identifiable information.
    """
    # Fetch only APPROVED reports for public view, plus PENDING reports belonging to current user
    user_id = session.get("user_id")
    if user_id:
        reports = UnsafeAreaReport.query.filter(
            (UnsafeAreaReport.status == "APPROVED") |
            ((UnsafeAreaReport.user_id == user_id) & (UnsafeAreaReport.status == "PENDING"))
        ).all()
    else:
        reports = UnsafeAreaReport.query.filter_by(status="APPROVED").all()

    result = []
    for r in reports:
        result.append({
            "id": r.id,
            "title": r.title,
            "category": r.category,
            "description": r.description,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "address": r.address or "Location marker",
            "status": r.status,
            "created_at": r.created_at.strftime("%d %b %Y")
        })

    return jsonify(result), 200


@safety_map_bp.route("/report", methods=["POST"])
def submit_report():
    """Submit a community safety concern for review."""
    form = UnsafeAreaReportForm()
    if form.validate_on_submit():
        user_id = session.get("user_id")
        report = UnsafeAreaReport(
            user_id=user_id,
            title=form.title.data.strip(),
            category=form.category.data,
            description=form.description.data.strip(),
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            address=form.address.data.strip() if form.address.data else None,
            status="PENDING",  # Requires administrative moderation before public listing
            created_at=datetime.utcnow()
        )
        db.session.add(report)
        db.session.commit()

        if request.is_json:
            return jsonify({
                "success": True,
                "message": "Safety report submitted. It will appear publicly after administrative moderation."
            }), 201

        flash("Safety report submitted! It will be reviewed by platform moderators to prevent spam.", "info")
        return redirect(url_for("safety_map.index"))

    if request.is_json:
        return jsonify({"success": False, "errors": form.errors}), 400

    flash("Could not submit report. Please check the coordinates and fields.", "danger")
    return redirect(url_for("safety_map.index"))


@safety_map_bp.route("/api/routes", methods=["GET", "POST"])
@csrf.exempt
def api_routes():
    """
    Calculates both Best / Fastest Route and Safe Route (well-lit, highway corridors,
    police checkpoints, hazard-avoidance) between start and destination.
    """
    data = request.get_json(silent=True) or request.args
    if request.method == "POST" and not request.is_json and request.form:
        data = request.form

    start_query = (data.get("start") or "").strip()
    dest_query = (data.get("destination") or data.get("dest") or "").strip()

    user_lat = data.get("user_lat")
    user_lng = data.get("user_lng")

    # Resolve Start location
    start_loc = None
    if (not start_query or start_query.lower() in ("my location", "current location", "here")) and user_lat and user_lng:
        try:
            ulat = float(user_lat)
            ulng = float(user_lng)
            start_loc = (ulat, ulng, "Your Current Location (वर्तमान स्थान)")
        except (ValueError, TypeError):
            pass

    if not start_loc and start_query:
        start_loc = geocode_location(start_query)

    if not start_loc:
        return jsonify({
            "success": False,
            "error": "Start location not found. Please type a valid location or click 'Use Current Location'."
        }), 400

    # Resolve Destination
    if not dest_query:
        return jsonify({
            "success": False,
            "error": "Please enter a destination (गंतव्य स्थान दर्ज करें)."
        }), 400

    dest_loc = geocode_location(dest_query)
    if not dest_loc:
        return jsonify({
            "success": False,
            "error": f"Could not find destination '{dest_query}'. Please check spelling or specify city name."
        }), 400

    # Query community hazard reports safely
    hazard_list = []
    try:
        hazards = UnsafeAreaReport.query.filter_by(status="APPROVED").all()
        hazard_list = [
            {"lat": h.latitude, "lng": h.longitude, "category": h.category, "title": h.title}
            for h in hazards
        ]
    except Exception as db_err:
        pass

    from services.routing_service import calculate_best_and_safe_routes
    route_result = calculate_best_and_safe_routes(
        start_lat=start_loc[0],
        start_lng=start_loc[1],
        dest_lat=dest_loc[0],
        dest_lng=dest_loc[1],
        hazard_reports=hazard_list
    )

    return jsonify({
        "success": True,
        "start": {
            "lat": start_loc[0],
            "lng": start_loc[1],
            "name": start_loc[2]
        },
        "destination": {
            "lat": dest_loc[0],
            "lng": dest_loc[1],
            "name": dest_loc[2]
        },
        "safe_route": route_result["safe_route"],
        "fastest_route": route_result["fastest_route"],
        "direct_distance_km": route_result["direct_distance_km"]
    }), 200

