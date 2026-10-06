from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class AnalyzeForm(FlaskForm):
    allowed_image_types=["jpg", "png"]

    image = FileField(
        label="Chest X-ray image",
        validators=[FileRequired(message="Please select an image."),
                    FileAllowed(allowed_image_types, message=f"Allowed image types are {', '.join(allowed_image_types)}")],
    )
    max_question_length = 512
    question = TextAreaField(
        label="Question",
        validators=[Optional(),
                    Length(max=max_question_length, message=f"Question must be at most {max_question_length} characters.")],
    )

    submit = SubmitField(label="Analyze")
    