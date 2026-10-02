from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    Regexp,
    ValidationError,
)

from src.app.models import User


class RegisterForm(FlaskForm):

    username = StringField(
        validators=[
            DataRequired(message="Username is required."),
            Length(
                min=3,
                max=64,
                message="Username must be between 3 and 64 characters.",
            ),
            Regexp(
                r"^[a-zA-Z0-9_.-]+$",
                message="Only letters, digits, dots, underscores and dashes are allowed.",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(
                min=8,
                max=128,
                message="Password must be at least 8 characters long.",
            ),
        ],
    )

    password_confirm = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(message="Password confirmation is required."),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Register")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("This username is already taken.")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(message="Please provide a username.")],
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Please provide a password.")],
    )

    remember_me = BooleanField("Remember me")

    submit = SubmitField("Log in")