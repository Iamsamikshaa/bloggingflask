from flask import Blueprint, current_app, render_template, request
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from app.models import db, Category, Post, Tag

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Homepage with search, category/tag filtering, and 6-per-page pagination."""
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "", type=str).strip()
    category_slug = request.args.get("category", "", type=str).strip()
    tag_slug = request.args.get("tag", "", type=str).strip()

    query = (
        Post.query.options(
            joinedload(Post.author),
            joinedload(Post.category),
        )
        .filter(Post.is_published.is_(True))
    )

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Post.title.ilike(pattern),
                Post.description.ilike(pattern),
                Post.content.ilike(pattern),
            )
        )

    active_category = None
    if category_slug:
        active_category = Category.query.filter_by(slug=category_slug).first()
        if active_category:
            query = query.filter(Post.category_id == active_category.id)
        else:
            query = query.filter(Post.id == -1)

    active_tag = None
    if tag_slug:
        active_tag = Tag.query.filter_by(slug=tag_slug).first()
        if active_tag:
            query = query.filter(Post.tags.any(Tag.id == active_tag.id))
        else:
            query = query.filter(Post.id == -1)

    query = query.order_by(Post.created_at.desc(), Post.id.desc())

    per_page = current_app.config.get("POSTS_PER_PAGE", 6)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    categories_with_counts = (
        db.session.query(Category, func.count(Post.id).label("post_count"))
        .outerjoin(
            Post,
            (Post.category_id == Category.id) & (Post.is_published.is_(True)),
        )
        .group_by(Category.id)
        .order_by(Category.name.asc())
        .all()
    )

    popular_tags = (
        Tag.query.join(Tag.posts)
        .filter(Post.is_published.is_(True))
        .group_by(Tag.id)
        .order_by(func.count(Post.id).desc(), Tag.name.asc())
        .limit(12)
        .all()
    )

    has_active_filters = bool(q or category_slug or tag_slug)

    return render_template(
        "main/index.html",
        posts=pagination.items,
        pagination=pagination,
        categories_with_counts=categories_with_counts,
        popular_tags=popular_tags,
        search_query=q,
        selected_category=category_slug,
        selected_tag=tag_slug,
        active_category=active_category,
        active_tag=active_tag,
        has_active_filters=has_active_filters,
    )


@main_bp.route("/about")
def about():
    """Editorial publication overview page."""
    total_posts = Post.query.filter_by(is_published=True).count()
    total_categories = Category.query.count()
    total_tags = Tag.query.count()
    return render_template(
        "main/about.html",
        total_posts=total_posts,
        total_categories=total_categories,
        total_tags=total_tags,
    )
