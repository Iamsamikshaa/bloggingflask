import os
from app import create_app
from app.models import db
from app.seed import seed_database

app = create_app(os.environ.get("FLASK_CONFIG", "production"))

with app.app_context():
    db.create_all()
    if os.environ.get("AUTO_SEED", "true").lower() == "true":
        seed_database()
