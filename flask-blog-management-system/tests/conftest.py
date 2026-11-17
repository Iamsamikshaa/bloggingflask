import pytest
from app import create_app
from app.models import db, Category, Post, Tag, User


@pytest.fixture
def app(tmp_path):
    """Create and configure a fresh app instance for each test."""
    application = create_app("testing")
    application.config["UPLOAD_FOLDER"] = str(tmp_path / "uploads")

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_user(app):
    def _make_user(
        full_name="Test Author",
        username="testauthor",
        email="author@example.com",
        password="StrongPassword123",
    ):
        user = User(full_name=full_name, username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    return _make_user


@pytest.fixture
def create_category(app):
    def _make_category(name="Engineering", slug="engineering", description="Tech notes"):
        cat = Category.query.filter_by(slug=slug).first()
        if cat is None:
            cat = Category(name=name, slug=slug, description=description)
            db.session.add(cat)
            db.session.commit()
        return cat

    return _make_category


@pytest.fixture
def create_post(app, create_category):
    def _make_post(
        author,
        title="Sample Editorial Post",
        slug=None,
        description="A clear summary description for testing.",
        content="<p>This is rich HTML body content for testing our Flask blog.</p>",
        category=None,
        tags=None,
        is_published=True,
    ):
        if category is None:
            category = create_category()
        if slug is None:
            slug = title.lower().replace(" ", "-")
        post = Post(
            title=title,
            slug=slug,
            description=description,
            content=content,
            author=author,
            category=category,
            is_published=is_published,
        )
        if tags:
            post.tags = tags
        db.session.add(post)
        db.session.commit()
        return post

    return _make_post


def login_client(client, identifier, password):
    return client.post(
        "/auth/login",
        data={"identifier": identifier, "password": password},
        follow_redirects=True,
    )
