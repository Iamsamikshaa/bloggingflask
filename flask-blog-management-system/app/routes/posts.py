from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import FileStorage

from app.forms.comment_forms import CommentForm, EditCommentForm
from app.forms.post_forms import PostForm
from app.models import db, Category, Comment, Post, Tag
from app.models.category import slugify_text
from app.utils import (
    delete_uploaded_image,
    generate_unique_slug,
    sanitize_html,
    save_uploaded_image,
)

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


def _sync_post_tags(post: Post, raw_tags: str | None) -> None:
    """Parse comma-separated tag names and synchronize Post.tags."""
    if not raw_tags:
        post.tags = []
        return

    tag_names = []
    seen_slugs = set()
    for part in raw_tags.split(","):
        cleaned = part.strip()
        if not cleaned:
            continue
        slug = slugify_text(cleaned)[:60]
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        tag_names.append((cleaned[:50], slug))

    tags = []
    for name, slug in tag_names:
        tag = Tag.query.filter_by(slug=slug).first()
        if tag is None:
            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
        tags.append(tag)
    post.tags = tags


def _populate_categories(form: PostForm) -> None:
    categories = Category.query.order_by(Category.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]


@posts_bp.route("/dashboard")
@login_required
def dashboard():
    """Author workspace listing the signed-in user's published and draft articles."""
    user_posts = (
        Post.query.options(joinedload(Post.category))
        .filter_by(user_id=current_user.id)
        .order_by(Post.updated_at.desc(), Post.id.desc())
        .all()
    )
    published_count = sum(1 for p in user_posts if p.is_published)
    draft_count = len(user_posts) - published_count
    total_comments = (
        Comment.query.join(Post, Comment.post_id == Post.id)
        .filter(Post.user_id == current_user.id)
        .count()
    )

    return render_template(
        "posts/dashboard.html",
        posts=user_posts,
        published_count=published_count,
        draft_count=draft_count,
        total_comments=total_comments,
    )


@posts_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new blog post with rich text and optional featured image."""
    form = PostForm()
    _populate_categories(form)

    if not form.category_id.choices:
        default_cat = Category(
            name="General",
            slug="general",
            description="General essays and notes.",
        )
        db.session.add(default_cat)
        db.session.commit()
        _populate_categories(form)

    if form.validate_on_submit():
        uploaded_path = None
        if isinstance(form.featured_image.data, FileStorage) and form.featured_image.data.filename:
            uploaded_path = save_uploaded_image(form.featured_image.data)
            if uploaded_path is None:
                flash(
                    "Uploaded file is not a valid image (JPG, PNG, WEBP, or GIF).",
                    "danger",
                )
                return render_template("posts/create.html", form=form), 400

        post = Post(
            title=form.title.data.strip(),
            slug=generate_unique_slug(Post, form.title.data),
            description=form.description.data.strip(),
            content=sanitize_html(form.content.data),
            featured_image=uploaded_path,
            is_published=bool(form.is_published.data),
            user_id=current_user.id,
            category_id=form.category_id.data,
        )
        _sync_post_tags(post, form.tags.data)
        db.session.add(post)
        db.session.commit()

        flash("Your post has been created successfully.", "success")
        return redirect(url_for("posts.detail", slug=post.slug))

    return render_template("posts/create.html", form=form)


@posts_bp.route("/<slug>")
def detail(slug: str):
    """Display an individual blog post along with its comments."""
    post = (
        Post.query.options(
            joinedload(Post.author),
            joinedload(Post.category),
        )
        .filter_by(slug=slug)
        .first_or_404()
    )

    if not post.is_published and (
        not current_user.is_authenticated or post.user_id != current_user.id
    ):
        abort(404)

    comment_form = CommentForm()
    edit_comment_form = EditCommentForm()

    related_posts = []
    if post.category_id:
        related_posts = (
            Post.query.filter(
                Post.category_id == post.category_id,
                Post.id != post.id,
                Post.is_published.is_(True),
            )
            .order_by(Post.created_at.desc())
            .limit(3)
            .all()
        )

    return render_template(
        "posts/detail.html",
        post=post,
        comment_form=comment_form,
        edit_comment_form=edit_comment_form,
        related_posts=related_posts,
    )


@posts_bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id: int):
    """Edit an existing blog post (author-only)."""
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    if post.user_id != current_user.id:
        abort(403)

    form = PostForm(obj=post)
    _populate_categories(form)

    if request.method == "GET":
        form.tags.data = ", ".join(tag.name for tag in post.tags)

    if form.validate_on_submit():
        if form.remove_image.data and post.featured_image:
            delete_uploaded_image(post.featured_image)
            post.featured_image = None

        if isinstance(form.featured_image.data, FileStorage) and form.featured_image.data.filename:
            new_image = save_uploaded_image(form.featured_image.data)
            if new_image is None:
                flash(
                    "Uploaded file is not a valid image (JPG, PNG, WEBP, or GIF).",
                    "danger",
                )
                return render_template("posts/edit.html", form=form, post=post), 400
            if post.featured_image:
                delete_uploaded_image(post.featured_image)
            post.featured_image = new_image

        new_title = form.title.data.strip()
        if new_title != post.title:
            post.slug = generate_unique_slug(Post, new_title, existing_id=post.id)
        post.title = new_title
        post.description = form.description.data.strip()
        post.content = sanitize_html(form.content.data)
        post.category_id = form.category_id.data
        post.is_published = bool(form.is_published.data)
        _sync_post_tags(post, form.tags.data)

        db.session.commit()
        flash("Post updated successfully.", "success")
        return redirect(url_for("posts.detail", slug=post.slug))

    return render_template("posts/edit.html", form=form, post=post)


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id: int):
    """Delete an existing blog post (author-only)."""
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    if post.user_id != current_user.id:
        abort(403)

    delete_uploaded_image(post.featured_image)
    db.session.delete(post)
    db.session.commit()

    flash("Your post has been deleted.", "info")
    return redirect(url_for("posts.dashboard"))
