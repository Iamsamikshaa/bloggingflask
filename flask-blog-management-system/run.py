import os
import click
from app import create_app
from app.models import db
from app.seed import seed_database

app = create_app(os.environ.get("FLASK_CONFIG", "development"))


@app.cli.command("init-db")
def init_db_command():
    """Create database tables directly if not using migrations."""
    db.create_all()
    click.echo("Initialized the database schema.")


@app.cli.command("seed")
def seed_command():
    """Seed the database with sample editorial posts, authors, and categories."""
    db.create_all()
    inserted = seed_database()
    if inserted:
        click.echo("Seeded sample categories, tags, authors, posts, and comments.")
    else:
        click.echo("Database already contains posts; skipping seed.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_database()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
