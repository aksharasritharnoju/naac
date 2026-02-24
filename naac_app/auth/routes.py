from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from naac_app.models import User
from naac_app import db

auth_bp = Blueprint("auth", __name__)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

def current_user():
    if "user_id" not in session:
        return None
    return User.query.get(session["user_id"])

@auth_bp.route("/", methods=["GET"])
def home():
    if "user_id" in session:
        return redirect(url_for("dash.dashboard"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash("Login successful.", "success")
            return redirect(url_for("dash.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/users/create", methods=["POST"])
@login_required
def create_user():
    # Admin only
    if session.get("role") != "Admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("dash.dashboard"))

    username = (request.form.get("new_username") or "").strip()
    password = request.form.get("new_password") or ""
    role = (request.form.get("new_role") or "Staff").strip()

    if not username or not password:
        flash("Username and password required.", "warning")
        return redirect(url_for("dash.dashboard"))

    if User.query.filter_by(username=username).first():
        flash("Username already exists.", "warning")
        return redirect(url_for("dash.dashboard"))

    u = User(username=username, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    flash("User created.", "success")
    return redirect(url_for("dash.dashboard"))