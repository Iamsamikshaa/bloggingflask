import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    URL,
    ValidationError,
)

from app.models.user import User


class RegistrationForm(FlaskForm):
    """User account registration form with uniqueness checks."""

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Please enter your full name."),
            Length(min=2, max=120, message="Full name must be between 2 and 120 characters."),
        ],
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Please choose a username."),
            Length(min=3, max=64, message="Username must be between 3 and 64 characters."),
        ],
    )
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Please enter your email address."),
            Email(message="Please enter a valid email address."),
            Length(max=120),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Please enter a password."),
            Length(min=8, max=128, message="Password must be at least 8 characters long."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create Account")

    def validate_username(self, field):
        username = field.data.strip().lower()
        if not re.match(r"^[a-z0-9_.-]+$", username):
            raise ValidationError(
                "Username may only contain letters, numbers, underscores, hyphens, and dots."
            )
        if User.query.filter_by(username=username).first():
            raise ValidationError("That username is already taken. Please choose another.")

    def validate_email(self, field):
        email = field.data.strip().lower()
        if User.query.filter_by(email=email).first():
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    """Sign-in form supporting email or username."""

    identifier = StringField(
        "Email or Username",
        validators=[
            DataRequired(message="Please enter your email address or username."),
            Length(max=120),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Please enter your password.")],
    )
    remember_me = BooleanField("Keep me signed in")
    submit = SubmitField("Sign In")


class ProfileEditForm(FlaskForm):
    """Profile update form for authenticated authors."""

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(message="Full name is required."),
            Length(min=2, max=120),
        ],
    )
    bio = TextAreaField(
        "Short Bio",
        validators=[Optional(), Length(max=500, message="Bio cannot exceed 500 characters.")],
    )
    location = StringField(
        "Location",
        validators=[Optional(), Length(max=100)],
    )
    website = StringField(
        "Website URL",
        validators=[Optional(), URL(message="Please enter a valid URL starting with http:// or https://."), Length(max=200)],
    )
    submit = SubmitField("Save Profile")
