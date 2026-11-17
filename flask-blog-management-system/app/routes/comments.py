from flask import Blueprint, abort, flash, redirect, url_for
from flask_login import current_user, login_required

from app.forms.comment_forms import CommentForm, EditCommentForm
from app.models import db, Comment, Post

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/posts/<int:post_id>/comments", methods=["POST"])
@login_required
def create(post_id: int):
    """Create a comment on a published post."""
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    if not post.is_published and post.user_id != current_user.id:
        abort(404)

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data.strip(),
            user_id=current_user.id,
            post_id=post.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been published.", "success")
    else:
        for errors in form.errors.values():
            for err in errors:
                flash(err, "danger")

    return redirect(url_for("posts.detail", slug=post.slug) + "#comments")


@comments_bp.route("/comments/<int:comment_id>/edit", methods=["POST"])
@login_required
def edit(comment_id: int):
    """Edit an existing comment (owner-only)."""
    comment = db.session.get(Comment, comment_id)
    if comment is None:
        abort(404)
    if comment.user_id != current_user.id:
        abort(403)

    form = EditCommentForm()
    post_slug = comment.post.slug
    if form.validate_on_submit():
        comment.body = form.body.data.strip()
        db.session.commit()
        flash("Comment updated.", "success")
    else:
        for errors in form.errors.values():
            for err in errors:
                flash(err, "danger")

    return redirect(url_for("posts.detail", slug=post_slug) + "#comments")


@comments_bp.route("/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete(comment_id: int):
    """Delete an existing comment (owner-only)."""
    comment = db.session.get(Comment, comment_id)
    if comment is None:
        abort(404)
    if comment.user_id != current_user.id:
        abort(403)

    post_slug = comment.post.slug
    db.session.delete(comment)
    db.session.commit()
    flash("Comment removed.", "info")
    return redirect(url_for("posts.detail", slug=post_slug) + "#comments")
