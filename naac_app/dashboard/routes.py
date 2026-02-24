from flask import Blueprint, render_template, session
from naac_app.auth.routes import login_required
from naac_app.models import Document, User
from naac_app.naac_rules import NAAC_MAPPING

dash_bp = Blueprint("dash", __name__, url_prefix="/dashboard")

@dash_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    total = Document.query.count()
    valid = Document.query.filter_by(validation_status="VALID").count()
    partial = Document.query.filter_by(validation_status="PARTIAL").count()
    fail = Document.query.filter_by(validation_status="FAIL").count()

    # Criterion readiness: percent of VALID within each criterion
    readiness = []
    for c in NAAC_MAPPING.keys():
        c_total = Document.query.filter_by(predicted_criterion=c).count()
        c_valid = Document.query.filter_by(predicted_criterion=c, validation_status="VALID").count()
        pct = 0 if c_total == 0 else round((c_valid / c_total) * 100, 1)
        readiness.append({"criterion": c, "total": c_total, "valid": c_valid, "pct": pct})

    users = []
    if session.get("role") == "Admin":
        users = User.query.order_by(User.created_at.desc()).all()

    return render_template(
        "dashboard.html",
        total=total, valid=valid, partial=partial, fail=fail,
        readiness=readiness,
        is_admin=(session.get("role") == "Admin"),
        users=users
    )