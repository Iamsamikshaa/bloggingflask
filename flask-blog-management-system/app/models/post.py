import math
import re
from datetime import datetime, timezone

from app.models import db
from app.models.tag import post_tags


class Post(db.Model):
    """Blog article with rich HTML content, category, tags, and featured image."""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.String(400), nullable=False)
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(255), nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    author = db.relationship("User", back_populates="posts")
    category = db.relationship("Category", back_populates="posts")
    tags = db.relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
    )
    comments = db.relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="Comment.created_at.desc()",
        lazy="selectin",
    )

    @property
    def reading_time(self) -> int:
        text = re.sub(r"<[^>]+>", " ", self.content or "")
        words = len(text.split())
        return max(1, math.ceil(words / 200))

    @property
    def image_url(self) -> str | None:
        if not self.featured_image:
            return None
        if self.featured_image.startswith(("http://", "https://", "/")):
            return self.featured_image
        return f"/static/{self.featured_image}"

    def __repr__(self) -> str:
        return f"<Post {self.title}>"
