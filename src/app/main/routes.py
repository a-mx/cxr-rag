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
    login_required,
    current_user
)
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from src.app.main.forms import AnalyzeForm
from src.app.services.pipeline import analyze_image
from src.app.models import Analysis, AuditLog
from src.app.extensions import db
main_bp = Blueprint('main', __name__)

def _save_upload(file_storage) -> tuple[str, Path]:
    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[-1].lower()

    unique_name = f"{uuid.uuid4().hex}.{extension}"
    upload_dir = Path(current_app.config["UPLOAD_DIR"])

    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / unique_name

    file_storage.save(dest)
    return original_name, dest


@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('main/index.html')

@main_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    form = AnalyzeForm()
    if form.validate_on_submit():
        original_name, image_path = _save_upload(form.image.data)

        k = current_app.config["TOP_K"]
        
        result = analyze_image(
            image_path=image_path,
            question=form.question.data or None,
            top_k=k,
            strategy="image_only",
        )

        analysis = Analysis(
            user_id=current_user.id,
            image_filename=original_name,
            user_prompt=form.question.data or None,
            generated_report=result.report,
            top_k=5,
            retrieval_strategy="image_only",
            inference_time_ms=result.inference_time_ms,
            confidence_score=result.confidence_score,
            retrieved_cases=result.retrieved_cases,
        )
        db.session.add(analysis)

        AuditLog.log(
            event_type="analysis",
            user_id=current_user.id,
            description=f"Analyzed image: {original_name}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:255],
        )

        db.session.commit()

        flash("Analysis completed successfully.", "success")
        return redirect(url_for("main.result", analysis_id=analysis.id))
    
    return render_template('main/analyze.html', form=form)


@main_bp.route("/result/<int:analysis_id>")
@login_required
def result(analysis_id: int):
    analysis = db.session.get(Analysis, analysis_id)

    if analysis is None:
        flash("Analysis not found.", "warning")
        return redirect(url_for("main.history"))

    if not current_user.is_admin and analysis.user_id != current_user.id:
        flash("You do not have permission to view this analysis.", "danger")
        return redirect(url_for("main.history"))

    return render_template("main/result.html", analysis=analysis)


@main_bp.route("/history")
@login_required
def history():
    query = Analysis.query

    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    analyses = query.order_by(Analysis.created_at.desc()).all()

    return render_template("main/history.html", analyses=analyses)