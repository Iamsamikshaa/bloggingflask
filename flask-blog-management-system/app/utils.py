import os
import re
import uuid
import bleach
from flask import current_app
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

ALLOWED_HTML_TAGS = [
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "s",
    "blockquote",
    "pre",
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "ul",
    "ol",
    "li",
    "a",
    "hr",
    "span",
]

ALLOWED_HTML_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "span": ["class"],
    "pre": ["class"],
    "code": ["class"],
}


def sanitize_html(raw_html: str) -> str:
    """Sanitize rich HTML produced by Quill.js to prevent XSS."""
    if not raw_html:
        return ""
    cleaned = bleach.clean(
        raw_html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        protocols=["http", "https", "mailto"],
        strip=True,
    )
    return bleach.linkify(cleaned)


def generate_unique_slug(model_cls, title: str, existing_id: int | None = None) -> str:
    """Create a URL-safe unique slug for a model with a `slug` column."""
    base = re.sub(r"[^a-z0-9\s-]", "", title.strip().lower())
    base = re.sub(r"[\s-]+", "-", base).strip("-") or "post"
    base = base[:180]

    candidate = base
    counter = 2
    while True:
        existing = model_cls.query.filter_by(slug=candidate).first()
        if existing is None or (existing_id is not None and existing.id == existing_id):
            return candidate
        candidate = f"{base}-{counter}"
        counter += 1


def save_uploaded_image(file_storage) -> str | None:
    """Validate and save an uploaded featured image, returning relative static path."""
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    if "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[1].lower()
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp", "gif"})
    if ext not in allowed:
        return None

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    dest_path = os.path.join(upload_dir, unique_name)

    try:
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as img:
            img.verify()
        file_storage.stream.seek(0)
        file_storage.save(dest_path)
    except (UnidentifiedImageError, OSError):
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return None

    return f"uploads/{unique_name}"


def delete_uploaded_image(relative_path: str | None) -> None:
    """Delete a user-uploaded file if it resides inside static/uploads."""
    if not relative_path or not relative_path.startswith("uploads/"):
        return
    filename = os.path.basename(relative_path)
    full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass
