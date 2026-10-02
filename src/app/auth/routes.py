from datetime import datetime, timezone
import os
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)
from sqlalchemy.exc import IntegrityError

from src.app.auth import auth_bp
from src.app.auth.forms import LoginForm, RegisterForm
from src.app.extensions import db
from src.app.models import User, AuditLog


def _log_event(event_type: str, user_id: int | None, description: str = "") -> None:
    AuditLog.log(
        event_type=event_type,
        user_id=user_id,
        description=description,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "")[:255],
    )
    db.session.commit()

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in.", "warning")
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
        )
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username or email is already taken.", "danger")
            return render_template("auth/register.html", form=form)

        _log_event(
            event_type="register",
            user_id=user.id,
            description=f"New account created: {user.username}",
        )

        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "warning")
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()

        stored_hash = (
            user.password_hash
            if user
            else current_app.config.get("EXAMPLE_PASSWORD_HASH")
        )
        password_ok = User.check_password(stored_hash, form.password.data)
        if not user or not password_ok:
            _log_event(
                event_type="login_failed",
                user_id=user.id if user else None,
                description=f"Failed login attempt for username: {form.username.data}",
            )
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", form=form)

        if not user.is_active:
            _log_event(
                event_type="login_blocked",
                user_id=user.id,
                description="Attempted login on deactivated account",
            )
            flash("This account has been deactivated.", "warning")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        _log_event(
            event_type="login",
            user_id=user.id,
            description=f"Successful login: {user.username}",
        )

        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("main.index"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    user_id = current_user.id
    username = current_user.username

    logout_user()

    _log_event(
        event_type="logout",
        user_id=user_id,
        description=f"User logged out: {username}",
    )

    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))