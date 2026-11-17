from app.models import db

post_tags = db.Table(
    "post_tags",
    db.Column(
        "post_id",
        db.Integer,
        db.ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tag(db.Model):
    """Topic tag associated with posts via many-to-many relationship."""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False, index=True)

    posts = db.relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"
