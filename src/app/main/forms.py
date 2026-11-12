from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


def validate_medical_image(form, field):
    filename = (field.data.filename or "").lower()

    if not (
        filename.endswith(".dcm")
        or filename.endswith(".dicom")
        or filename.endswith(".nii")
        or filename.endswith(".nii.gz")
        or "." not in filename
    ):
        raise ValidationError(
            "Only DICOM (.dcm, .dicom) and NIfTI (.nii, .nii.gz) files are allowed."
        )

class AnalyzeForm(FlaskForm):
    frontal_image = FileField(
        label="Frontal chest X-ray image",
        validators=[
            FileRequired(message="Please select a frontal image."),
            validate_medical_image,
            ],
    )

    lateral_image = FileField(
        label="Lateral chest X-ray image",
        validators=[
            Optional(),
            validate_medical_image,
            ],
    )

    max_question_length = 512
    question = TextAreaField(
        label="Question",
        validators=[
            Optional(),
            Length(max=max_question_length, message=f"Question must be at most {max_question_length} characters.")
            ],
    )

    submit = SubmitField(label="Analyze")

class ReportEditForm(FlaskForm):
    content = TextAreaField(
        "Report",
        validators=[
            DataRequired(),
            Length(max=10000),
        ],
    )

    submit = SubmitField("Save revision")
    