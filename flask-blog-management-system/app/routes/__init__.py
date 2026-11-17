from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.posts import posts_bp
from app.routes.comments import comments_bp
from app.routes.profile import profile_bp

__all__ = ["main_bp", "auth_bp", "posts_bp", "comments_bp", "profile_bp"]
