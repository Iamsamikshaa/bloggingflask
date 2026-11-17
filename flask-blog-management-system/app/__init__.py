import os
from datetime import datetime, timezone
from flask import Flask, render_template
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config_by_name
from app.models import db, migrate, login_manager, csrf


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Ensure SQLite enforces ON DELETE CASCADE and foreign key constraints."""
    module_name = type(dbapi_connection).__module__
    if "sqlite3" in module_name:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for FolioPress Blog Management System."""
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Respect X-Forwarded-* headers when running behind reverse proxies / Docker / Gunicorn
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access that page."
    login_manager.login_message_category = "warning"
    login_manager.session_protection = "strong"

    from app.routes import main_bp, auth_bp, posts_bp, comments_bp, profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(profile_bp)

    _register_error_handlers(app)
    _register_template_helpers(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _register_template_helpers(app: Flask) -> None:
    @app.template_filter("format_date")
    def format_date(dt: datetime | None, fmt: str = "%b %d, %Y") -> str:
        if dt is None:
            return ""
        return dt.strftime(fmt)

    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.now(timezone.utc).year,
            "site_name": "FolioPress",
            "enable_zip_download": os.environ.get("ENABLE_ZIP_DOWNLOAD", "false").lower() == "true",
        }
