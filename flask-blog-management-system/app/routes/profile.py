from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app.forms.auth_forms import ProfileEditForm
from app.models import db, Comment, Post, User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Allow authenticated users to update their public author profile."""
    form = ProfileEditForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.bio = (form.bio.data or "").strip()
        current_user.location = (form.location.data or "").strip()
        current_user.website = (form.website.data or "").strip()
        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("profile.view", username=current_user.username))

    return render_template("profile/edit.html", form=form)


@profile_bp.route("/<username>")
def view(username: str):
    """Public author profile page with paginated published articles."""
    user = User.query.filter_by(username=username.lower()).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("POSTS_PER_PAGE", 6)

    pagination = (
        Post.query.options(joinedload(Post.category))
        .filter_by(user_id=user.id, is_published=True)
        .order_by(Post.created_at.desc(), Post.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    total_comments_written = Comment.query.filter_by(user_id=user.id).count()

    return render_template(
        "profile/view.html",
        profile_user=user,
        posts=pagination.items,
        pagination=pagination,
        total_comments_written=total_comments_written,
    )
