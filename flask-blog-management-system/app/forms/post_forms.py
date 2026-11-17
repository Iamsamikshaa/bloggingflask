from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, Optional, ValidationError
import re


class PostForm(FlaskForm):
    """Form for creating and editing blog posts with Quill.js rich content."""

    title = StringField(
        "Article Title",
        validators=[
            DataRequired(message="Please provide a title for your post."),
            Length(min=4, max=200, message="Title must be between 4 and 200 characters."),
        ],
    )
    description = TextAreaField(
        "Short Description",
        validators=[
            DataRequired(message="Please provide a short summary or deck."),
            Length(min=10, max=400, message="Description must be between 10 and 400 characters."),
        ],
    )
    content = TextAreaField(
        "Article Content",
        validators=[
            DataRequired(message="Article content cannot be empty."),
        ],
    )
    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[DataRequired(message="Please choose a category.")],
    )
    tags = StringField(
        "Tags (comma-separated)",
        validators=[Optional(), Length(max=250)],
    )
    featured_image = FileField(
        "Featured Image",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png", "webp", "gif"],
                "Images only (JPG, PNG, WEBP, GIF).",
            ),
        ],
    )
    remove_image = BooleanField("Remove current featured image")
    is_published = BooleanField("Publish immediately", default=True)
    submit = SubmitField("Save Post")

    def validate_content(self, field):
        stripped = re.sub(r"<[^>]+>", "", field.data or "").replace("&nbsp;", " ").strip()
        if len(stripped) < 15:
            raise ValidationError("Article content must contain at least 15 characters of text.")
