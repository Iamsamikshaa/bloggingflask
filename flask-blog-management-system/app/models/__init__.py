from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag, post_tags
from app.models.post import Post
from app.models.comment import Comment

__all__ = [
    "db",
    "migrate",
    "login_manager",
    "csrf",
    "User",
    "Category",
    "Tag",
    "Post",
    "Comment",
    "post_tags",
]
