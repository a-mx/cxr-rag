from flask import Blueprint, render_template
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
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('main/index.html')

@main_bp.route('/analyze')
@login_required
def analyze():
    if not current_user.is_authenticated:
        flash("You are not logged in", "warning")
        return redirect(url_for("main.index"))
    return render_template('main/analyze.html')