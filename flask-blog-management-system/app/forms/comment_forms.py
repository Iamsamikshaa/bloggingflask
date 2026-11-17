from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    """Form for submitting a new comment on a blog post."""

    body = TextAreaField(
        "Write a comment",
        validators=[
            DataRequired(message="Please write a comment before submitting."),
            Length(min=2, max=2000, message="Comment must be between 2 and 2,000 characters."),
        ],
    )
    submit = SubmitField("Post Comment")


class EditCommentForm(FlaskForm):
    """Form for updating an existing comment."""

    body = TextAreaField(
        "Comment",
        validators=[
            DataRequired(message="Comment cannot be empty."),
            Length(min=2, max=2000, message="Comment must be between 2 and 2,000 characters."),
        ],
    )
    submit = SubmitField("Save Changes")
