from flask import (
    Blueprint,
    send_file,
    abort,
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
import nibabel as nib
import numpy as np
import pydicom
from PIL import Image
from pydicom.pixel_data_handlers.util import apply_voi_lut
from werkzeug.utils import secure_filename
from src.app.main.forms import AnalyzeForm, ReportEditForm
from src.app.services.pipeline import analyze_image
from src.app.models import Analysis, AuditLog, ReportRevision, BoundingBox
from src.app.extensions import db
main_bp = Blueprint('main', __name__)

def _normalize_to_uint8(array) -> np.ndarray:
    array = np.asarray(array, dtype=np.float32)
    array = np.squeeze(array)

    while array.ndim > 2:
        array = array[..., array.shape[-1] // 2]

    finite = np.isfinite(array)
    if not finite.any():
        raise ValueError("Medical image contains no finite pixel values.")

    minimum = array[finite].min()
    maximum = array[finite].max()

    if maximum <= minimum:
        return np.zeros(array.shape, dtype=np.uint8)

    normalized = (array - minimum) / (maximum - minimum)
    return np.clip(normalized * 255, 0, 255).astype(np.uint8)


def _convert_medical_image(source: Path, destination: Path) -> None:
    name = source.name.lower()

    if name.endswith((".nii", ".nii.gz")):
        pixels = nib.load(str(source)).get_fdata()
    else:
        dataset = pydicom.dcmread(str(source))
        pixels = apply_voi_lut(dataset.pixel_array, dataset)

        if getattr(dataset, "PhotometricInterpretation", "") == "MONOCHROME1":
            pixels = np.max(pixels) - pixels

    image = Image.fromarray(_normalize_to_uint8(pixels), mode="L")
    image.save(destination, format="PNG")


def _save_upload(file_storage) -> tuple[str, Path]:
    original_name = secure_filename(file_storage.filename)
    lower_name = original_name.lower()
    extension = ".nii.gz" if lower_name.endswith(".nii.gz") else Path(lower_name).suffix

    unique_name = f"{uuid.uuid4().hex}{extension}"
    upload_dir = Path(current_app.config["UPLOAD_DIR"])

    upload_dir.mkdir(parents=True, exist_ok=True)
    source = upload_dir / unique_name
    converted = upload_dir / f"{uuid.uuid4().hex}.png"

    file_storage.save(source)

    try:
        _convert_medical_image(source, converted)
    finally:
        source.unlink(missing_ok=True)

    return original_name, converted

def _can_access_analysis(analysis):
    return (
        current_user.is_admin
        or current_user.role == "radiologist"
        or analysis.user_id == current_user.id
    )


@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('main/index.html')

@main_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    form = AnalyzeForm()
    if form.validate_on_submit():
        original_name, image_path = _save_upload(form.frontal_image.data)
        lateral_name = None
        lateral_path = None

        if form.lateral_image.data:
            lateral_name, lateral_path = _save_upload(form.lateral_image.data)

        k = current_app.config["TOP_K"]
        
        result = analyze_image(
            image_path=image_path,
            lateral_image_path=lateral_path,
            question=form.question.data or None,
            top_k=k,
            strategy="image_only",
        )

        analysis = Analysis(
            user_id=current_user.id,
            image_filename=original_name,
            lateral_filename=lateral_name,
            stored_image_name=image_path.name,
            stored_lateral_image_name=lateral_path.name if lateral_path else None,
            user_prompt=form.question.data or None,
            generated_report=result.report,
            top_k=k,
            retrieval_strategy="image_only",
            inference_time_ms=result.inference_time_ms,
            confidence_score=result.confidence_score,
            retrieved_cases=result.retrieved_cases,
        )
        db.session.add(analysis)
        db.session.flush()

        for box in result.bounding_boxes:
            analysis.bounding_boxes.append(
                BoundingBox(
                    label=box["label"],
                    view=box.get("view", "frontal"),
                    x0=box["x0"],
                    y0=box["y0"],
                    x1=box["x1"],
                    y1=box["y1"],
                )
            )



        revision = ReportRevision(
            analysis_id=analysis.id,
            author_id=current_user.id,
            revision_number=1,
            content=result.report,
            source="ai_generated",
        )
        db.session.add(revision)

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

@main_bp.route("/result/<int:analysis_id>/image")
@login_required
def analysis_image(analysis_id: int):
    analysis = db.session.get(Analysis, analysis_id)

    if analysis is None:
        abort(404)

    if not _can_access_analysis(analysis):
        abort(403)

    upload_dir = Path(current_app.config["UPLOAD_DIR"]).resolve()
    view = request.args.get("view", "frontal")
    image_name = (
        analysis.stored_lateral_image_name
        if view == "lateral"
        else analysis.stored_image_name
    )

    if not image_name:
        abort(404)

    image_path = (upload_dir / image_name).resolve()

    if upload_dir not in image_path.parents or not image_path.is_file():
        abort(404)

    return send_file(image_path)


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

@main_bp.route("/result/<int:analysis_id>/edit", methods=["GET", "POST"])
@login_required
def edit_result(analysis_id: int):
    analysis = db.session.get(Analysis, analysis_id)

    if analysis is None:
        flash("Analysis not found.", "warning")
        return redirect(url_for("main.history"))

    if not _can_access_analysis(analysis):
        flash("You do not have permission to edit this report.", "danger")
        return redirect(url_for("main.history"))

    form = ReportEditForm()

    latest_revision = (
        analysis.revisions[-1]
        if analysis.revisions
        else None
    )

    current_content = (
        latest_revision.content
        if latest_revision
        else analysis.generated_report
    )

    if form.validate_on_submit():
        next_version = (
            latest_revision.revision_number + 1
            if latest_revision
            else 1
        )

        revision = ReportRevision(
            analysis_id=analysis.id,
            author_id=current_user.id,
            revision_number=next_version,
            content=form.content.data,
            source="manual",
        )

        db.session.add(revision)

        AuditLog.log(
            event_type="report_edited",
            user_id=current_user.id,
            description=(
                f"Edited report for analysis {analysis.id}; "
                f"revision {next_version}"
            ),
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:255],
        )

        db.session.commit()

        flash("Report revision saved.", "success")
        return redirect(url_for("main.result", analysis_id=analysis.id))

    if request.method == "GET":
        form.content.data = current_content

    return render_template(
        "main/edit.html",
        form=form,
        analysis=analysis,
        current_content=current_content,
    )

@main_bp.route("/result/<int:analysis_id>/history")
@login_required
def result_history(analysis_id: int):
    analysis = db.session.get(Analysis, analysis_id)

    if analysis is None:
        flash("Analysis not found.", "warning")
        return redirect(url_for("main.history"))

    if not _can_access_analysis(analysis):
        flash("You do not have permission to view this history.", "danger")
        return redirect(url_for("main.history"))

    revisions = (
        ReportRevision.query
        .filter_by(analysis_id=analysis.id)
        .order_by(ReportRevision.revision_number.desc())
        .all()
    )

    return render_template(
        "main/revisions.html",
        analysis=analysis,
        revisions=revisions,
    )


@main_bp.route("/history")
@login_required
def history():
    query = Analysis.query

    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)

    analyses = query.order_by(Analysis.created_at.desc()).all()

    return render_template("main/history.html", analyses=analyses)